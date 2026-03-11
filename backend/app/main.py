from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.seed_db import seed
from app.routers import auth, breeds, tournaments, entries, matches, admin, leaderboards
from app.websocket_manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed()
    yield
    # shutdown if needed


app = FastAPI(title="Gamefowl Derby API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(breeds.router)
app.include_router(tournaments.router)
app.include_router(entries.router)
app.include_router(matches.router)
app.include_router(admin.router)
app.include_router(leaderboards.router)

# Serve breed images from resources/breed pics (mount at /breed-pics)
breed_pics = Path(__file__).resolve().parent.parent.parent / "resources" / "breed pics"
if breed_pics.exists():
    app.mount("/breed-pics", StaticFiles(directory=str(breed_pics)), name="breed-pics")


@app.websocket("/ws/tournaments/{tournament_id}")
async def websocket_tournament(websocket: WebSocket, tournament_id: int):
    await websocket.accept()
    await manager.subscribe_tournament(tournament_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.unsubscribe_tournament(tournament_id, websocket)


@app.get("/health")
def health():
    return {"status": "ok"}
