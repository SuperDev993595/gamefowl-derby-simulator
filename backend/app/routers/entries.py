from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import Entry, Tournament, User, Breed, EntryRooster
from app.schemas import EntryCreate, EntryResponse, StandingsRow, EntryRoosterResponse
from app.auth import require_user
from app.config import settings, entry_cost_for_tier

router = APIRouter(prefix="/api/entries", tags=["entries"])

MAX_ROOSTERS = 10


@router.post("/tournaments/{tournament_id}/enter", response_model=EntryResponse)
async def enter_tournament(
    tournament_id: int,
    data: EntryCreate,
    db=Depends(get_db),
    user: User = Depends(require_user),
):
    t = await db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    if t.status not in ("draft", "scheduled"):
        raise HTTPException(400, "Registration closed")
    breed_ids = data.breed_ids if data.breed_ids else []
    if not breed_ids or len(breed_ids) > MAX_ROOSTERS:
        raise HTTPException(400, f"Select 1 to {MAX_ROOSTERS} roosters")
    cost = entry_cost_for_tier(getattr(t, "prize_tier", "standard"))
    if user.token_balance < cost:
        raise HTTPException(400, "Insufficient tokens")
    keep_type = (data.keep_type or "bench").lower()
    if keep_type not in ("bench", "flypen"):
        keep_type = "bench"
    entry = Entry(
        tournament_id=tournament_id,
        user_id=user.id,
        breed_id=breed_ids[0],
        keep_type=keep_type,
        token_cost_paid=cost,
    )
    db.add(entry)
    await db.flush()
    for idx, bid in enumerate(breed_ids):
        db.add(EntryRooster(entry_id=entry.id, breed_id=bid, slot_index=idx))
    user.token_balance -= cost
    await db.commit()
    await db.refresh(entry)
    await db.refresh(user)
    r = await db.execute(
        select(EntryRooster, Breed)
        .join(Breed, EntryRooster.breed_id == Breed.id)
        .where(EntryRooster.entry_id == entry.id)
        .order_by(EntryRooster.slot_index)
    )
    lineup = [EntryRoosterResponse(breed_id=er.breed_id, breed_name=b.name, slot_index=er.slot_index) for er, b in r.all()]
    breed = await db.get(Breed, entry.breed_id)
    return EntryResponse(
        id=entry.id,
        tournament_id=entry.tournament_id,
        user_id=entry.user_id,
        breed_id=entry.breed_id,
        keep_type=entry.keep_type,
        token_cost_paid=entry.token_cost_paid,
        status=entry.status,
        wins=entry.wins,
        losses=entry.losses,
        created_at=entry.created_at,
        username=user.username,
        breed_name=breed.name if breed else None,
        lineup=lineup,
    )


@router.get("/tournaments/{tournament_id}/standings", response_model=list[StandingsRow])
async def standings(tournament_id: int, db=Depends(get_db)):
    r = await db.execute(
        select(Entry, User)
        .join(User, Entry.user_id == User.id)
        .where(Entry.tournament_id == tournament_id)
        .order_by(Entry.wins.desc(), Entry.losses.asc())
    )
    rows = []
    for entry, u in r.all():
        breed = await db.get(Breed, entry.breed_id)
        breed_name = breed.name if breed else ""
        rows.append(StandingsRow(
            entry_id=entry.id,
            username=u.username,
            breed_name=breed_name,
            wins=entry.wins,
            losses=entry.losses,
            status=entry.status,
        ))
    return rows
