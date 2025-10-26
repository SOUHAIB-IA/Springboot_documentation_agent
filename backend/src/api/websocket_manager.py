from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: Dict[str, Any]):
        """Broadcasts a JSON message to all connected clients."""
        message_str = json.dumps(data)
        for connection in self.active_connections:
            await connection.send_text(message_str)

manager = ConnectionManager()