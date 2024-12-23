#/classes/WebSocketManager.py

from dataclasses import dataclass, field
from typing import List

from fastapi.websockets import WebSocket

from lib.validator import validate_message

@dataclass
class WebSocketManager:
    connections: List[WebSocket] = field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True  # Allow non-Pydantic types like WebSocket
    
    @property
    def get_connections_count(self):
        return len(self.connections)
    
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)
    
    async def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)
    
    async def broadcast_message(self, message: dict):
        for ws in list(self.connections):
            try:
                await ws.send_json(message)
            except Exception:
                await self.disconnect(ws)
    
    async def send_message(self, ws: WebSocket, message: dict):
        try:
            await ws.send_json(message)
        except Exception:
            await self.disconnect(ws)
    
    async def get_message(self, websocket):
        data = await websocket.receive_text()
        msg = validate_message(data)
        return msg
            
    