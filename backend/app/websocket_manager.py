from collections import defaultdict
from typing import Set
import json

class ConnectionManager:
    def __init__(self):
        self.tournament_subscriptions: dict[int, Set] = defaultdict(set)

    async def subscribe_tournament(self, tournament_id: int, websocket):
        self.tournament_subscriptions[tournament_id].add(websocket)

    def unsubscribe_tournament(self, tournament_id: int, websocket):
        self.tournament_subscriptions[tournament_id].discard(websocket)

    async def broadcast_tournament(self, tournament_id: int, event: str, payload: dict | None = None):
        msg = json.dumps({"event": event, "tournament_id": tournament_id, "payload": payload or {}})
        dead = set()
        for ws in self.tournament_subscriptions[tournament_id]:
            try:
                await ws.send_text(msg)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.tournament_subscriptions[tournament_id].discard(ws)


manager = ConnectionManager()
