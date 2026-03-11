"""Pairing, match resolution, elimination, tie-breakers."""
import random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Tournament, Entry, Match, BreedTrait, MatchStatus, EntryStatus, TournamentStatus
from app.derby_modifiers import apply_derby_modifiers, apply_keep_modifiers


def parse_rating_string(s: str) -> list[int]:
    parts = s.split(".")
    nums = [int(x) for x in parts if x.isdigit()]
    if len(nums) == 4:
        nums.append(5)
    return (nums + [5] * 5)[:5]


async def get_traits_for_breed_derby(db: AsyncSession, breed_id: int, derby_type: str) -> tuple[int, int, int, int, int]:
    r = await db.execute(
        select(BreedTrait).where(BreedTrait.breed_id == breed_id, BreedTrait.derby_type == derby_type)
    )
    t = r.scalar_one_or_none()
    if not t:
        return (5, 5, 5, 5, 5)
    return (t.power, t.speed, t.intelligence, t.stamina, t.accuracy)


def resolve_match(power_a: tuple, power_b: tuple, seed: int | None = None) -> int:
    """Returns 1 if A wins, 2 if B wins. Weighted sum + randomness. Accepts float tuples."""
    if seed is not None:
        random.seed(seed)
    weights = (0.25, 0.2, 0.2, 0.2, 0.15)
    score_a = sum(w * p for w, p in zip(weights, power_a)) + random.uniform(0, 1)
    score_b = sum(w * p for w, p in zip(weights, power_b)) + random.uniform(0, 1)
    return 1 if score_a >= score_b else 2


async def get_adjusted_traits_for_entry(
    db: AsyncSession,
    entry: Entry,
    derby_type: str,
) -> tuple[float, float, float, float, float]:
    """Base breed traits for this derby, then derby modifiers, then keep modifiers."""
    base = await get_traits_for_breed_derby(db, entry.breed_id, derby_type)
    after_derby = apply_derby_modifiers(base, derby_type)
    keep_type = getattr(entry, "keep_type", None) or "bench"
    return apply_keep_modifiers(after_derby, keep_type)


def can_still_win(wins: int, losses: int, total_rounds: int, leader_wins: int) -> bool:
    """True if this entry can still tie or beat leader (by wins)."""
    max_possible_wins = wins + (total_rounds - wins - losses)
    return max_possible_wins >= leader_wins


async def mark_eliminated(db: AsyncSession, tournament_id: int, total_rounds: int) -> None:
    entries = await db.execute(
        select(Entry).where(Entry.tournament_id == tournament_id, Entry.status == EntryStatus.ACTIVE.value)
    )
    all_entries = list(entries.scalars().all())
    if not all_entries:
        return
    leader_wins = max(e.wins for e in all_entries)
    for e in all_entries:
        if not can_still_win(e.wins, e.losses, total_rounds, leader_wins):
            e.status = EntryStatus.ELIMINATED.value
    await db.flush()


async def get_entries_for_round(db: AsyncSession, tournament_id: int, round_number: int, is_tie_breaker: bool) -> list[Entry]:
    """For round 1: all active entries (or tied leaders for tie-breaker). For round N: winners from previous round."""
    if round_number == 1:
        if is_tie_breaker:
            return await get_tied_leader_entries(db, tournament_id)
        r = await db.execute(
            select(Entry).where(Entry.tournament_id == tournament_id, Entry.status == EntryStatus.ACTIVE.value)
        )
        return list(r.scalars().all())
    # Winners from previous round
    r = await db.execute(
        select(Match).where(
            Match.tournament_id == tournament_id,
            Match.round_number == round_number - 1,
            Match.status == MatchStatus.PLAYED.value,
            Match.winner_entry_id.isnot(None),
        )
    )
    matches = r.scalars().all()
    winner_ids = {m.winner_entry_id for m in matches if m.winner_entry_id}
    r2 = await db.execute(
        select(Match).where(
            Match.tournament_id == tournament_id,
            Match.round_number == round_number - 1,
            Match.status == MatchStatus.BYE.value,
        )
    )
    for m in r2.scalars().all():
        winner_ids.add(m.entry_a_id or m.entry_b_id)
    winner_ids.discard(None)
    if not winner_ids:
        return []
    r3 = await db.execute(
        select(Entry).where(
            Entry.id.in_(winner_ids),
            Entry.tournament_id == tournament_id,
            Entry.status == EntryStatus.ACTIVE.value,
        )
    )
    return list(r3.scalars().all())


async def create_pairings_for_round(
    db: AsyncSession,
    tournament_id: int,
    round_number: int,
    is_tie_breaker: bool,
) -> list[Match]:
    entries = await get_entries_for_round(db, tournament_id, round_number, is_tie_breaker)
    random.shuffle(entries)
    matches = []
    i = 0
    while i < len(entries):
        if i + 1 < len(entries):
            m = Match(
                tournament_id=tournament_id,
                round_number=round_number,
                entry_a_id=entries[i].id,
                entry_b_id=entries[i + 1].id,
                status=MatchStatus.PENDING.value,
                is_tie_breaker=is_tie_breaker,
            )
            matches.append(m)
            db.add(m)
            i += 2
        else:
            bye = Match(
                tournament_id=tournament_id,
                round_number=round_number,
                entry_a_id=entries[i].id,
                entry_b_id=None,
                status=MatchStatus.BYE.value,
                winner_entry_id=entries[i].id,
                is_tie_breaker=is_tie_breaker,
            )
            matches.append(bye)
            db.add(bye)
            entries[i].wins += 1
            i += 1
    await db.flush()
    return matches


async def resolve_pending_matches_for_round(
    db: AsyncSession,
    tournament_id: int,
    round_number: int,
    derby_type: str,
) -> None:
    r = await db.execute(
        select(Match).where(
            Match.tournament_id == tournament_id,
            Match.round_number == round_number,
            Match.status == MatchStatus.PENDING.value,
        )
    )
    for match in r.scalars().all():
        if not match.entry_a_id or not match.entry_b_id:
            continue
        entry_a = await db.get(Entry, match.entry_a_id)
        entry_b = await db.get(Entry, match.entry_b_id)
        if not entry_a or not entry_b:
            continue
        traits_a = await get_adjusted_traits_for_entry(db, entry_a, derby_type)
        traits_b = await get_adjusted_traits_for_entry(db, entry_b, derby_type)
        winner = 1 if resolve_match(traits_a, traits_b) == 1 else 2
        winner_id = entry_a.id if winner == 1 else entry_b.id
        loser_id = entry_b.id if winner == 1 else entry_a.id
        match.winner_entry_id = winner_id
        match.status = MatchStatus.PLAYED.value
        from datetime import datetime
        match.played_at = datetime.utcnow()
        winner_entry = await db.get(Entry, winner_id)
        loser_entry = await db.get(Entry, loser_id)
        if winner_entry:
            winner_entry.wins += 1
        if loser_entry:
            loser_entry.losses += 1
    await db.flush()


async def get_tied_leader_entries(db: AsyncSession, tournament_id: int) -> list[Entry]:
    r = await db.execute(
        select(Entry).where(Entry.tournament_id == tournament_id, Entry.status == EntryStatus.ACTIVE.value)
    )
    entries = list(r.scalars().all())
    if not entries:
        return []
    best_wins = max(e.wins for e in entries)
    best_entries = [e for e in entries if e.wins == best_wins]
    best_losses = min(e.losses for e in best_entries)
    return [e for e in best_entries if e.losses == best_losses]


async def advance_tournament_round(db: AsyncSession, tournament: Tournament) -> str | None:
    """
    Create next round pairings and resolve them. Returns event name for WebSocket or None if tournament finished.
    """
    derby_type = tournament.derby_type
    total_rounds = tournament.total_rounds
    current = tournament.current_round
    is_tie_breaker = tournament.is_tie_breaker

    if not is_tie_breaker and current >= total_rounds:
        tied = await get_tied_leader_entries(db, tournament.id)
        if len(tied) <= 1:
            if tied:
                tournament.winner_entry_id = tied[0].id
            tournament.status = TournamentStatus.FINISHED.value
            await db.commit()
            return "tournament_finished"
        tournament.is_tie_breaker = True
        tournament.current_round = 0
        await db.commit()
        return "tie_breaker_start"

    next_round = current + 1
    await create_pairings_for_round(db, tournament.id, next_round, tournament.is_tie_breaker)
    await resolve_pending_matches_for_round(db, tournament.id, next_round, derby_type)
    await mark_eliminated(db, tournament.id, total_rounds if not is_tie_breaker else 999)

    tournament.current_round = next_round
    await db.flush()

    event = "round_completed"
    if tournament.is_tie_breaker:
        tied = await get_tied_leader_entries(db, tournament.id)
        if len(tied) == 1:
            tournament.winner_entry_id = tied[0].id
            tournament.status = TournamentStatus.FINISHED.value
            event = "tournament_finished"
    await db.commit()
    return event
