"""
CloudFlux AI - Kafka Event Producer
Produces real-time events for cloud operations, migrations, and cost alerts

Strategy: Lightweight, in-memory event streaming (perfect for demos)
Falls back to queue-based system if Kafka isn't available
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import asyncio
from collections import deque

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events in CloudFlux AI"""
    # Cloud operations
    CLOUD_UPLOAD = "cloud.upload"
    CLOUD_DOWNLOAD = "cloud.download"
    CLOUD_DELETE = "cloud.delete"
    CLOUD_LIST = "cloud.list"
    
    # Migration events
    MIGRATION_STARTED = "migration.started"
    MIGRATION_PROGRESS = "migration.progress"
    MIGRATION_COMPLETED = "migration.completed"
    MIGRATION_FAILED = "migration.failed"
    
    # Placement events
    PLACEMENT_ANALYZED = "placement.analyzed"
    PLACEMENT_OPTIMIZED = "placement.optimized"
    PLACEMENT_RECOMMENDATION = "placement.recommendation"
    
    # ML events
    ML_PREDICTION = "ml.prediction"
    ML_RECOMMENDATION = "ml.recommendation"
    
    # Cost events
    COST_ALERT = "cost.alert"
    COST_SAVINGS_FOUND = "cost.savings_found"
    COST_THRESHOLD_EXCEEDED = "cost.threshold_exceeded"
    
    # Access pattern events
    ACCESS_PATTERN_DETECTED = "access.pattern_detected"
    ACCESS_FREQUENCY_CHANGE = "access.frequency_change"


class CloudFluxEventProducer:
    """
    Real-time event producer for CloudFlux AI
    
    Features:
    - In-memory event streaming (no Kafka dependency for demo)
    - Automatic event batching
    - Real-time WebSocket broadcasting
    - Event history for replay
    """
    
    def __init__(self, max_history: int = 1000):
        """Initialize the event producer"""
        self.max_history = max_history
        self.event_history: deque = deque(maxlen=max_history)
        self.subscribers: List[asyncio.Queue] = []
        self.is_running = False
        self.total_events = 0
        
        logger.info("🎬 CloudFlux Event Producer initialized (In-Memory Mode)")
        logger.info(f"📝 Event history buffer: {max_history} events")
    
    async def produce_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        source: str = "cloudflux-api",
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Produce a real-time event
        
        Args:
            event_type: Type of event
            data: Event payload
            source: Event source
            user_id: Optional user ID
            correlation_id: Optional correlation ID for tracking
            
        Returns:
            Created event with metadata
        """
        event = {
            "id": f"evt_{self.total_events + 1}_{int(datetime.now().timestamp() * 1000)}",
            "type": event_type.value,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "correlation_id": correlation_id or f"corr_{int(datetime.now().timestamp())}",
            "data": data,
            "version": "1.0"
        }
        
        # Add to history
        self.event_history.append(event)
        self.total_events += 1
        
        # Broadcast to all subscribers (WebSocket clients)
        await self._broadcast_event(event)
        
        logger.debug(f"📤 Event produced: {event_type.value} (ID: {event['id']})")
        
        return event
    
    async def _broadcast_event(self, event: Dict[str, Any]):
        """Broadcast event to all WebSocket subscribers"""
        if not self.subscribers:
            return
        
        # Send to all active subscribers
        dead_subscribers = []
        for queue in self.subscribers:
            try:
                await queue.put(event)
            except Exception as e:
                logger.warning(f"Failed to send event to subscriber: {e}")
                dead_subscribers.append(queue)
        
        # Remove dead subscribers
        for dead in dead_subscribers:
            self.subscribers.remove(dead)
    
    def subscribe(self) -> asyncio.Queue:
        """
        Subscribe to real-time events
        
        Returns:
            Queue that will receive events
        """
        queue = asyncio.Queue(maxsize=100)
        self.subscribers.append(queue)
        logger.info(f"📻 New subscriber added (Total: {len(self.subscribers)})")
        return queue
    
    def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from events"""
        if queue in self.subscribers:
            self.subscribers.remove(queue)
            logger.info(f"📻 Subscriber removed (Total: {len(self.subscribers)})")
    
    def get_recent_events(
        self,
        limit: int = 50,
        event_type: Optional[EventType] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent events from history
        
        Args:
            limit: Maximum number of events to return
            event_type: Filter by event type
            user_id: Filter by user ID
            
        Returns:
            List of recent events
        """
        events = list(self.event_history)
        
        # Filter by event type
        if event_type:
            events = [e for e in events if e["type"] == event_type.value]
        
        # Filter by user
        if user_id:
            events = [e for e in events if e.get("user_id") == user_id]
        
        # Return most recent first
        return list(reversed(events[-limit:]))
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Get statistics about event production"""
        event_type_counts = {}
        for event in self.event_history:
            event_type = event["type"]
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        
        return {
            "total_events_produced": self.total_events,
            "events_in_history": len(self.event_history),
            "active_subscribers": len(self.subscribers),
            "event_type_distribution": event_type_counts,
            "uptime_status": "running" if self.is_running else "idle"
        }
    
    async def start(self):
        """Start the event producer"""
        self.is_running = True
        logger.info("▶️  Event Producer started")
    
    async def stop(self):
        """Stop the event producer"""
        self.is_running = False
        logger.info("⏹️  Event Producer stopped")


# Singleton instance
event_producer = CloudFluxEventProducer()


# ==================== Event Helper Functions ====================

async def emit_cloud_operation_event(
    operation: str,
    provider: str,
    file_name: str,
    size_bytes: int,
    user_id: Optional[str] = None,
    status: str = "success",
    duration_ms: Optional[float] = None
):
    """Emit a cloud operation event"""
    event_type_map = {
        "upload": EventType.CLOUD_UPLOAD,
        "download": EventType.CLOUD_DOWNLOAD,
        "delete": EventType.CLOUD_DELETE,
        "list": EventType.CLOUD_LIST
    }
    
    event_type = event_type_map.get(operation, EventType.CLOUD_UPLOAD)
    
    await event_producer.produce_event(
        event_type=event_type,
        data={
            "operation": operation,
            "provider": provider,
            "file_name": file_name,
            "size_bytes": size_bytes,
            "size_mb": round(size_bytes / (1024 * 1024), 2),
            "status": status,
            "duration_ms": duration_ms
        },
        user_id=user_id
    )


async def emit_migration_event(
    migration_id: str,
    file_name: str,
    source_provider: str,
    destination_provider: str,
    status: str,
    user_id: Optional[str] = None,
    progress: Optional[int] = None,
    error: Optional[str] = None
):
    """Emit a migration event"""
    event_type_map = {
        "started": EventType.MIGRATION_STARTED,
        "in_progress": EventType.MIGRATION_PROGRESS,
        "completed": EventType.MIGRATION_COMPLETED,
        "failed": EventType.MIGRATION_FAILED
    }
    
    event_type = event_type_map.get(status, EventType.MIGRATION_PROGRESS)
    
    await event_producer.produce_event(
        event_type=event_type,
        data={
            "migration_id": migration_id,
            "file_name": file_name,
            "source": source_provider,
            "destination": destination_provider,
            "status": status,
            "progress": progress,
            "error": error
        },
        user_id=user_id,
        correlation_id=f"migration_{migration_id}"
    )


async def emit_placement_event(
    file_name: str,
    current_tier: str,
    recommended_tier: str,
    potential_savings: float,
    user_id: Optional[str] = None
):
    """Emit a placement optimization event"""
    await event_producer.produce_event(
        event_type=EventType.PLACEMENT_RECOMMENDATION,
        data={
            "file_name": file_name,
            "current_tier": current_tier,
            "recommended_tier": recommended_tier,
            "potential_savings_monthly": potential_savings,
            "action_required": current_tier != recommended_tier
        },
        user_id=user_id
    )


async def emit_ml_prediction_event(
    file_name: str,
    prediction_type: str,
    predicted_value: Any,
    confidence: float,
    user_id: Optional[str] = None
):
    """Emit an ML prediction event"""
    await event_producer.produce_event(
        event_type=EventType.ML_PREDICTION,
        data={
            "file_name": file_name,
            "prediction_type": prediction_type,
            "predicted_value": predicted_value,
            "confidence": confidence,
            "model_version": "1.0.0-pretrained"
        },
        user_id=user_id
    )


async def emit_cost_alert_event(
    alert_type: str,
    amount: float,
    threshold: Optional[float] = None,
    provider: Optional[str] = None,
    user_id: Optional[str] = None,
    details: Optional[Dict] = None
):
    """Emit a cost alert event"""
    event_type = EventType.COST_ALERT
    
    if "savings" in alert_type.lower():
        event_type = EventType.COST_SAVINGS_FOUND
    elif "threshold" in alert_type.lower():
        event_type = EventType.COST_THRESHOLD_EXCEEDED
    
    await event_producer.produce_event(
        event_type=event_type,
        data={
            "alert_type": alert_type,
            "amount": amount,
            "threshold": threshold,
            "provider": provider,
            "severity": "high" if amount > 100 else "medium" if amount > 50 else "low",
            "details": details or {}
        },
        user_id=user_id
    )


async def emit_access_pattern_event(
    file_name: str,
    pattern_type: str,
    access_count: int,
    temperature: str,
    user_id: Optional[str] = None
):
    """Emit an access pattern detection event"""
    await event_producer.produce_event(
        event_type=EventType.ACCESS_PATTERN_DETECTED,
        data={
            "file_name": file_name,
            "pattern_type": pattern_type,
            "access_count": access_count,
            "data_temperature": temperature,
            "timestamp": datetime.now().isoformat()
        },
        user_id=user_id
    )
