"""
CloudFlux AI - Real-Time Streaming API Routes
WebSocket endpoints for live event streaming to frontend
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional, List
import asyncio
import json
import logging

from ..streaming.event_producer import event_producer, EventType
from ..auth import decode_access_token

router = APIRouter(prefix="/api/stream", tags=["Real-Time Streaming"])

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_queues: dict[WebSocket, asyncio.Queue] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Create event queue for this connection
        queue = event_producer.subscribe()
        self.connection_queues[websocket] = queue
        
        logger.info(f"✅ WebSocket connected (Total: {len(self.active_connections)})")
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "Connected to CloudFlux AI real-time stream",
            "timestamp": asyncio.get_event_loop().time()
        })
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Unsubscribe from events
        if websocket in self.connection_queues:
            queue = self.connection_queues[websocket]
            event_producer.unsubscribe(queue)
            del self.connection_queues[websocket]
        
        logger.info(f"❌ WebSocket disconnected (Total: {len(self.active_connections)})")
    
    async def send_event(self, websocket: WebSocket, event: dict):
        """Send an event to a specific WebSocket"""
        try:
            await websocket.send_json(event)
        except Exception as e:
            logger.error(f"Error sending event: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients"""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for dead in dead_connections:
            self.disconnect(dead)


# Singleton connection manager
manager = ConnectionManager()


@router.websocket("/events")
async def websocket_events(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time event streaming
    
    Connect to receive live events:
    - Cloud operations (upload, download, delete)
    - Migration progress updates
    - Placement recommendations
    - ML predictions
    - Cost alerts
    - Access pattern changes
    
    Usage:
        ws://localhost:8000/api/stream/events?token=YOUR_JWT_TOKEN
        or ws://localhost:8000/api/stream/events (without token - will receive all events)
    """
    # Optional: Validate token (allow connection without token for demo)
    user_id = None
    if token:
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            logger.info(f"✅ WebSocket authenticated: user {user_id}")
        except Exception as e:
            logger.warning(f"⚠️  Invalid token for WebSocket (allowing unauthenticated): {e}")
    else:
        logger.info("✅ WebSocket connected without authentication (demo mode)")
    
    await manager.connect(websocket)
    
    try:
        # Get the event queue for this connection
        queue = manager.connection_queues.get(websocket)
        
        if not queue:
            await websocket.close(code=1011, reason="Failed to subscribe to events")
            return
        
        # Keep connection alive and stream events
        while True:
            # Wait for new events
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                
                # Filter events by user if authenticated
                if user_id and event.get("user_id") and event["user_id"] != user_id:
                    continue
                
                # Send event to client
                await manager.send_event(websocket, event)
                
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": asyncio.get_event_loop().time()
                })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.get("/events/recent")
async def get_recent_events(
    limit: int = Query(50, ge=1, le=500),
    event_type: Optional[str] = Query(None)
):
    """
    Get recent events from history
    
    Query Parameters:
    - limit: Number of events to return (1-500)
    - event_type: Filter by event type (optional)
    
    Returns list of recent events in reverse chronological order
    """
    # Parse event type if provided
    filter_type = None
    if event_type:
        try:
            filter_type = EventType(event_type)
        except ValueError:
            pass
    
    events = event_producer.get_recent_events(
        limit=limit,
        event_type=filter_type
    )
    
    return {
        "total": len(events),
        "limit": limit,
        "events": events
    }


@router.get("/events/stats")
async def get_event_stats():
    """
    Get streaming statistics
    
    Returns information about:
    - Total events produced
    - Active WebSocket connections
    - Event type distribution
    - System status
    """
    stats = event_producer.get_event_stats()
    
    return {
        "streaming_status": "active",
        "statistics": stats,
        "websocket_connections": len(manager.active_connections),
        "features": {
            "real_time_events": True,
            "event_history": True,
            "event_filtering": True,
            "websocket_streaming": True
        }
    }


@router.post("/events/test")
async def emit_test_event(
    event_type: str = Query(..., description="Type of test event"),
    message: str = Query("Test event", description="Test message")
):
    """
    Emit a test event (for development/demo)
    
    Useful for testing WebSocket connections and event flow
    """
    # Map string to EventType
    try:
        evt_type = EventType(event_type)
    except ValueError:
        evt_type = EventType.CLOUD_UPLOAD  # Default
    
    await event_producer.produce_event(
        event_type=evt_type,
        data={
            "test": True,
            "message": message,
            "generated_at": asyncio.get_event_loop().time()
        },
        source="test-endpoint"
    )
    
    return {
        "status": "success",
        "message": "Test event emitted",
        "event_type": event_type,
        "active_subscribers": len(event_producer.subscribers)
    }


@router.get("/events/types")
async def get_event_types():
    """
    Get all available event types
    
    Returns list of event types that can be streamed
    """
    return {
        "event_types": [
            {
                "type": evt.value,
                "name": evt.name,
                "category": evt.value.split('.')[0]
            }
            for evt in EventType
        ],
        "categories": {
            "cloud": "Cloud storage operations",
            "migration": "Data migration events",
            "placement": "Data placement optimization",
            "ml": "Machine learning predictions",
            "cost": "Cost monitoring and alerts",
            "access": "Access pattern analysis"
        }
    }


@router.websocket("/events/filtered")
async def websocket_filtered_events(
    websocket: WebSocket,
    event_types: Optional[str] = Query(None, description="Comma-separated event types"),
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint with event filtering
    
    Only receive specific event types:
    
    Usage:
        ws://localhost:8000/api/stream/events/filtered?event_types=migration.started,migration.completed
    """
    # Parse event type filters
    filters = []
    if event_types:
        for evt_str in event_types.split(','):
            try:
                filters.append(EventType(evt_str.strip()))
            except ValueError:
                pass
    
    # Validate token
    user_id = None
    if token:
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
        except Exception as e:
            logger.warning(f"Invalid token: {e}")
    
    await manager.connect(websocket)
    
    try:
        queue = manager.connection_queues.get(websocket)
        if not queue:
            await websocket.close(code=1011, reason="Failed to subscribe")
            return
        
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                
                # Filter by event type
                if filters and event.get("type"):
                    if not any(f.value == event["type"] for f in filters):
                        continue
                
                # Filter by user
                if user_id and event.get("user_id") and event["user_id"] != user_id:
                    continue
                
                await manager.send_event(websocket, event)
                
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "heartbeat"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.on_event("startup")
async def startup_event():
    """Start the event producer on app startup"""
    await event_producer.start()
    logger.info("🚀 Real-time streaming started")


@router.on_event("shutdown")
async def shutdown_event():
    """Stop the event producer on app shutdown"""
    await event_producer.stop()
    logger.info("🛑 Real-time streaming stopped")
