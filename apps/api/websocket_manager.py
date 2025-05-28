"""
WebSocket connection manager for real-time updates.

Handles multiple WebSocket connections and broadcasting messages.
"""

from typing import List, Set
from fastapi import WebSocket
import json
import logging
from datetime import datetime

from apps.api.models import WebSocketMessage


logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: List[WebSocket] = []
        self.connection_ids: Set[str] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        connection_id = f"ws_{datetime.utcnow().timestamp()}"
        self.connection_ids.add(connection_id)
        logger.info(f"WebSocket connected: {connection_id}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket disconnected")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: WebSocketMessage):
        """Broadcast a message to all connected clients."""
        # Convert message to JSON
        message_json = message.model_dump_json()
        
        # Track disconnected clients
        disconnected = []
        
        # Send to all active connections
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
        
        logger.info(f"Broadcasted {message.event} to {len(self.active_connections)} clients")
    
    async def broadcast_json(self, data: dict):
        """Broadcast raw JSON data to all connected clients."""
        message = WebSocketMessage(
            event=data.get("event", "unknown"),
            data=data.get("data", {})
        )
        await self.broadcast(message)
    
    async def disconnect_all(self):
        """Disconnect all active connections."""
        for connection in self.active_connections[:]:
            try:
                await connection.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
            self.disconnect(connection)
        
        logger.info("All WebSocket connections closed")
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)