from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete, update
from app.database import get_db
from app.models import Tournament, Entry, User, Match
from app.auth import require_admin
from app.services.tournament_engine import advance_tournament_round
from app.config import entry_cost_for_tier, winner_bonus_for_tier
from app.websocket_manager import manager

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/tournaments/{tournament_id}/start")
async def start_tournament(
    tournament_id: int,
    db=Depends(get_db),
    user=Depends(require_admin),
):
    t = await db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    if t.status not in ("draft", "scheduled"):
        raise HTTPException(400, "Already started or finished")
    t.status = "running"
    await db.commit()
    return {"status": "running"}


@router.post("/tournaments/{tournament_id}/advance-round")
async def advance_round(
    tournament_id: int,
    db=Depends(get_db),
    user=Depends(require_admin),
):
    t = await db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    if t.status != "running":
        raise HTTPException(400, "Tournament is not running")
    event = await advance_tournament_round(db, t)
    await db.refresh(t)
    if event == "tournament_finished" and t.winner_entry_id:
        winner_entry = await db.get(Entry, t.winner_entry_id)
        if winner_entry:
            winner_user = await db.get(User, winner_entry.user_id)
            if winner_user:
                from sqlalchemy import func
                sum_r = await db.execute(
                    select(func.coalesce(func.sum(Entry.token_cost_paid), 0)).where(Entry.tournament_id == tournament_id)
                )
                pool = int(sum_r.scalar() or 0)
                tier = getattr(t, "prize_tier", "standard")
                bonus = winner_bonus_for_tier(tier)
                winner_user.token_balance += pool + bonus
                await db.commit()
    await manager.broadcast_tournament(tournament_id, event, {"current_round": t.current_round})
    return {"event": event, "current_round": t.current_round}


@router.post("/tournaments/{tournament_id}/restart")
async def restart_tournament(
    tournament_id: int,
    db=Depends(get_db),
    user=Depends(require_admin),
):
    t = await db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    await db.execute(delete(Match).where(Match.tournament_id == tournament_id))
    await db.execute(update(Entry).where(Entry.tournament_id == tournament_id).values(status="active", wins=0, losses=0))
    t.status = "draft"
    t.current_round = 0
    t.winner_entry_id = None
    t.is_tie_breaker = False
    await db.commit()
    return {"status": "draft"}


@router.post("/tournaments/{tournament_id}/clone")
async def clone_tournament(
    tournament_id: int,
    db=Depends(get_db),
    user=Depends(require_admin),
):
    t = await db.get(Tournament, tournament_id)
    if not t:
        raise HTTPException(404, "Tournament not found")
    new_t = Tournament(
        name=t.name + " (Clone)",
        derby_type=t.derby_type,
        total_rounds=t.total_rounds,
        start_at=t.start_at,
        prize_tier=getattr(t, "prize_tier", "standard"),
        status="draft",
    )
    db.add(new_t)
    await db.commit()
    await db.refresh(new_t)
    return {"id": new_t.id, "name": new_t.name}
