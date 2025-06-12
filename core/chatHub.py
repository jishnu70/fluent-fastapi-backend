from typing import Dict, Set
from fastapi import WebSocket

class ChatHub:
    def __init__(self) -> None:
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    async def disconnect(self, websocket: WebSocket, user_id: int):
        self.active_connections[user_id].discard(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def send_to(self, user_id: int, data: dict):
        for ws in self.active_connections.get(user_id, set()):
            await ws.send_json(data)

chatHub = ChatHub()

def get_chatHub():
    return chatHub
