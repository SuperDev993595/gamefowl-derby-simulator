"""Leaderboards: top players, top breeds, seasonal rankings."""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from app.database import get_db
from app.models import Entry, User, Breed, Tournament

router = APIRouter(prefix="/api/leaderboards", tags=["leaderboards"])


@router.get("/players")
async def top_players(
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
):
    """Top players by total wins across all entries."""
    r = await db.execute(
        select(User.id, User.username, func.sum(Entry.wins).label("total_wins"))
        .join(Entry, Entry.user_id == User.id)
        .group_by(User.id, User.username)
        .order_by(func.sum(Entry.wins).desc())
        .limit(limit)
    )
    rows = r.all()
    return [
        {"rank": i + 1, "username": row.username, "total_wins": row.total_wins or 0}
        for i, row in enumerate(rows)
    ]


@router.get("/breeds")
async def top_breeds(
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
):
    """Top breeds by total wins (aggregate of all entries with that breed)."""
    r = await db.execute(
        select(Breed.id, Breed.name, func.sum(Entry.wins).label("total_wins"))
        .join(Entry, Entry.breed_id == Breed.id)
        .group_by(Breed.id, Breed.name)
        .order_by(func.sum(Entry.wins).desc())
        .limit(limit)
    )
    rows = r.all()
    return [
        {"rank": i + 1, "breed_name": row.name, "total_wins": row.total_wins or 0}
        for i, row in enumerate(rows)
    ]


@router.get("/seasonal")
async def seasonal(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
):
    """Top players by wins in tournaments finished in the last N days."""
    since = datetime.utcnow() - timedelta(days=days)
    r = await db.execute(
        select(User.id, User.username, func.sum(Entry.wins).label("season_wins"))
        .join(Entry, Entry.user_id == User.id)
        .join(Tournament, Entry.tournament_id == Tournament.id)
        .where(Tournament.status == "finished", Tournament.created_at >= since)
        .group_by(User.id, User.username)
        .order_by(func.sum(Entry.wins).desc())
        .limit(limit)
    )
    rows = r.all()
    return [
        {"rank": i + 1, "username": row.username, "season_wins": row.season_wins or 0}
        for i, row in enumerate(rows)
    ]
