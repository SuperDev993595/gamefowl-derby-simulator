from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from app.database import get_db
from app.models import Tournament, Entry
from app.schemas import TournamentCreate, TournamentUpdate, TournamentResponse
from app.auth import get_current_user, require_admin
from app.models import User

router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])


@router.get("", response_model=list[TournamentResponse])
async def list_tournaments(
    status: str | None = Query(None),
    db=Depends(get_db),
):
    q = select(Tournament).order_by(Tournament.created_at.desc())
    if status:
        q = q.where(Tournament.status == status)
    r = await db.execute(q)
    tournaments = r.scalars().all()
    out = []
    for t in tournaments:
        count_r = await db.execute(select(func.count(Entry.id)).where(Entry.tournament_id == t.id))
        entry_count = count_r.scalar() or 0
        out.append(TournamentResponse(
            id=t.id,
            name=t.name,
            derby_type=t.derby_type,
            total_rounds=t.total_rounds,
            start_at=t.start_at,
            prize_tier=getattr(t, "prize_tier", "standard"),
            status=t.status,
            current_round=t.current_round,
            is_tie_breaker=t.is_tie_breaker,
            winner_entry_id=t.winner_entry_id,
            created_at=t.created_at,
            entry_count=entry_count,
        ))
    return out


@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(tournament_id: int, db=Depends(get_db)):
    t = await db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    count_r = await db.execute(select(func.count(Entry.id)).where(Entry.tournament_id == t.id))
    return TournamentResponse(
        id=t.id,
        name=t.name,
        derby_type=t.derby_type,
        total_rounds=t.total_rounds,
        start_at=t.start_at,
        prize_tier=getattr(t, "prize_tier", "standard"),
        status=t.status,
        current_round=t.current_round,
        is_tie_breaker=t.is_tie_breaker,
        winner_entry_id=t.winner_entry_id,
        created_at=t.created_at,
        entry_count=count_r.scalar() or 0,
    )


@router.post("", response_model=TournamentResponse)
async def create_tournament(
    data: TournamentCreate,
    db=Depends(get_db),
    user: User = Depends(require_admin),
):
    prize_tier = (data.prize_tier or "standard").lower()
    if prize_tier not in ("standard", "grand", "prestigious"):
        prize_tier = "standard"
    t = Tournament(
        name=data.name,
        derby_type=data.derby_type,
        total_rounds=min(20, max(10, data.total_rounds)),
        start_at=data.start_at,
        prize_tier=prize_tier,
        status="draft",
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return TournamentResponse(
        id=t.id,
        name=t.name,
        derby_type=t.derby_type,
        total_rounds=t.total_rounds,
        start_at=t.start_at,
        prize_tier=t.prize_tier,
        status=t.status,
        current_round=t.current_round,
        is_tie_breaker=t.is_tie_breaker,
        winner_entry_id=t.winner_entry_id,
        created_at=t.created_at,
        entry_count=0,
    )


@router.patch("/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: int,
    data: TournamentUpdate,
    db=Depends(get_db),
    user: User = Depends(require_admin),
):
    t = await db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    if t.status not in ("draft", "scheduled"):
        raise HTTPException(400, "Cannot update running or finished tournament")
    if data.name is not None:
        t.name = data.name
    if data.derby_type is not None:
        t.derby_type = data.derby_type
    if data.total_rounds is not None:
        t.total_rounds = min(20, max(10, data.total_rounds))
    if data.start_at is not None:
        t.start_at = data.start_at
    if data.prize_tier is not None:
        pt = data.prize_tier.lower()
        if pt in ("standard", "grand", "prestigious"):
            t.prize_tier = pt
    await db.commit()
    await db.refresh(t)
    count_r = await db.execute(select(func.count(Entry.id)).where(Entry.tournament_id == t.id))
    return TournamentResponse(
        id=t.id, name=t.name, derby_type=t.derby_type, total_rounds=t.total_rounds,
        start_at=t.start_at, prize_tier=getattr(t, "prize_tier", "standard"), status=t.status, current_round=t.current_round,
        is_tie_breaker=t.is_tie_breaker, winner_entry_id=t.winner_entry_id,
        created_at=t.created_at, entry_count=count_r.scalar() or 0,
    )
