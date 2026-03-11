from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import Match, Entry, User, Breed
from app.schemas import MatchResponse

router = APIRouter(prefix="/api/matches", tags=["matches"])


async def _enrich_match(m: Match, db) -> MatchResponse:
    entry_a = await db.get(Entry, m.entry_a_id) if m.entry_a_id else None
    entry_b = await db.get(Entry, m.entry_b_id) if m.entry_b_id else None
    u_a = await db.get(User, entry_a.user_id) if entry_a else None
    u_b = await db.get(User, entry_b.user_id) if entry_b else None
    b_a = await db.get(Breed, entry_a.breed_id) if entry_a else None
    b_b = await db.get(Breed, entry_b.breed_id) if entry_b else None
    return MatchResponse(
        id=m.id,
        tournament_id=m.tournament_id,
        round_number=m.round_number,
        entry_a_id=m.entry_a_id,
        entry_b_id=m.entry_b_id,
        winner_entry_id=m.winner_entry_id,
        status=m.status,
        is_tie_breaker=m.is_tie_breaker,
        played_at=m.played_at,
        entry_a_username=u_a.username if u_a else None,
        entry_b_username=u_b.username if u_b else None,
        entry_a_breed=b_a.name if b_a else None,
        entry_b_breed=b_b.name if b_b else None,
    )


@router.get("/tournaments/{tournament_id}", response_model=list[MatchResponse])
async def list_matches(tournament_id: int, db=Depends(get_db)):
    r = await db.execute(
        select(Match).where(Match.tournament_id == tournament_id).order_by(Match.round_number, Match.id)
    )
    matches = r.scalars().all()
    return [await _enrich_match(m, db) for m in matches]


@router.get("/by-id/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, db=Depends(get_db)):
    """Single match for arena/result view (announcer, result text)."""
    m = await db.get(Match, match_id)
    if not m:
        from fastapi import HTTPException
        raise HTTPException(404, "Match not found")
    return await _enrich_match(m, db)
