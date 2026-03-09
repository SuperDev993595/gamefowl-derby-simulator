from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.database import get_db
from app.models import Entry, Tournament, User, Breed
from app.schemas import EntryCreate, EntryResponse, StandingsRow
from app.auth import require_user
from app.config import settings

router = APIRouter(prefix="/api/entries", tags=["entries"])


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
    if user.token_balance < settings.entry_cost_tokens:
        raise HTTPException(400, "Insufficient tokens")
    entry = Entry(
        tournament_id=tournament_id,
        user_id=user.id,
        breed_id=data.breed_id,
        token_cost_paid=settings.entry_cost_tokens,
    )
    db.add(entry)
    user.token_balance -= settings.entry_cost_tokens
    await db.commit()
    await db.refresh(entry)
    await db.refresh(user)
    breed = await db.get(Breed, entry.breed_id)
    return EntryResponse(
        id=entry.id,
        tournament_id=entry.tournament_id,
        user_id=entry.user_id,
        breed_id=entry.breed_id,
        token_cost_paid=entry.token_cost_paid,
        status=entry.status,
        wins=entry.wins,
        losses=entry.losses,
        created_at=entry.created_at,
        username=user.username,
        breed_name=breed.name if breed else None,
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
