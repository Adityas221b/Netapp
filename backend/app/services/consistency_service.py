"""
Data Consistency and Synchronization Service
Handles distributed data consistency, conflict resolution, and failure recovery
"""
import logging
import asyncio
import hashlib
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import redis

logger = logging.getLogger(__name__)


class ConflictResolutionStrategy(Enum):
    """Strategies for resolving data conflicts"""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MANUAL_RESOLUTION = "manual_resolution"
    SIZE_BASED = "size_based"  # Keep larger file
    TIMESTAMP_BASED = "timestamp_based"


@dataclass
class DataVersion:
    """Represents a version of data"""
    version_id: str
    file_id: str
    provider: str
    location: str
    size_bytes: int
    checksum: str
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class SyncResult:
    """Result of a synchronization operation"""
    success: bool
    file_id: str
    synced_providers: List[str]
    conflicts_resolved: int
    errors: List[str]
    duration_seconds: float


class DataConsistencyManager:
    """
    Manages data consistency across distributed cloud environments
    
    Features:
    - Distributed locking with Redis
    - Conflict detection and resolution
    - Checksum verification
    - Retry mechanisms for network failures
    - Event sourcing for audit trail
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize consistency manager"""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("✅ Redis connection established for distributed locking")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {e}. Using in-memory locks.")
            self.redis_client = None
        
        self.lock_timeout = 30  # seconds
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
        # In-memory fallback for locks
        self.local_locks: Dict[str, bool] = {}
    
    def calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA-256 checksum of data"""
        return hashlib.sha256(data).hexdigest()
    
    async def acquire_lock(self, resource_id: str, timeout: int = None) -> bool:
        """
        Acquire distributed lock for a resource
        
        Args:
            resource_id: Unique identifier for the resource
            timeout: Lock timeout in seconds
            
        Returns:
            True if lock acquired, False otherwise
        """
        timeout = timeout or self.lock_timeout
        lock_key = f"lock:{resource_id}"
        
        if self.redis_client:
            try:
                # Try to set lock with expiry (NX = only if not exists)
                result = self.redis_client.set(
                    lock_key,
                    datetime.now().isoformat(),
                    nx=True,
                    ex=timeout
                )
                
                if result:
                    logger.debug(f"🔒 Lock acquired: {resource_id}")
                    return True
                else:
                    logger.debug(f"⏳ Lock already held: {resource_id}")
                    return False
            except Exception as e:
                logger.error(f"❌ Redis lock error: {e}")
                # Fallback to local lock
                pass
        
        # In-memory fallback
        if resource_id not in self.local_locks or not self.local_locks[resource_id]:
            self.local_locks[resource_id] = True
            logger.debug(f"🔒 Local lock acquired: {resource_id}")
            return True
        
        return False
    
    async def release_lock(self, resource_id: str):
        """Release distributed lock"""
        lock_key = f"lock:{resource_id}"
        
        if self.redis_client:
            try:
                self.redis_client.delete(lock_key)
                logger.debug(f"🔓 Lock released: {resource_id}")
            except Exception as e:
                logger.error(f"❌ Redis unlock error: {e}")
        
        # Also clear local lock
        if resource_id in self.local_locks:
            self.local_locks[resource_id] = False
    
    async def verify_data_integrity(
        self,
        file_id: str,
        data: bytes,
        expected_checksum: str
    ) -> bool:
        """
        Verify data integrity using checksum
        
        Args:
            file_id: File identifier
            data: File data
            expected_checksum: Expected SHA-256 checksum
            
        Returns:
            True if data is intact, False otherwise
        """
        actual_checksum = self.calculate_checksum(data)
        
        if actual_checksum == expected_checksum:
            logger.info(f"✅ Integrity verified: {file_id}")
            return True
        else:
            logger.error(
                f"❌ Integrity check failed for {file_id}. "
                f"Expected: {expected_checksum[:8]}..., "
                f"Got: {actual_checksum[:8]}..."
            )
            return False
    
    async def detect_conflicts(
        self,
        versions: List[DataVersion]
    ) -> Optional[List[DataVersion]]:
        """
        Detect conflicts between different versions of data
        
        Args:
            versions: List of data versions from different sources
            
        Returns:
            List of conflicting versions, or None if no conflicts
        """
        if len(versions) <= 1:
            return None
        
        # Group by checksum
        checksum_groups = {}
        for version in versions:
            if version.checksum not in checksum_groups:
                checksum_groups[version.checksum] = []
            checksum_groups[version.checksum].append(version)
        
        # If all have same checksum, no conflict
        if len(checksum_groups) == 1:
            logger.info(f"✅ No conflicts detected. All versions match.")
            return None
        
        # Conflict detected
        logger.warning(f"⚠️ Conflict detected: {len(checksum_groups)} different versions")
        return versions
    
    async def resolve_conflict(
        self,
        versions: List[DataVersion],
        strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.LAST_WRITE_WINS
    ) -> DataVersion:
        """
        Resolve conflict between data versions using specified strategy
        
        Args:
            versions: Conflicting data versions
            strategy: Resolution strategy
            
        Returns:
            Winning version
        """
        if strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
            # Keep most recent version
            winner = max(versions, key=lambda v: v.timestamp)
            logger.info(f"🏆 Conflict resolved (LAST_WRITE_WINS): {winner.provider}")
            return winner
        
        elif strategy == ConflictResolutionStrategy.FIRST_WRITE_WINS:
            # Keep oldest version
            winner = min(versions, key=lambda v: v.timestamp)
            logger.info(f"🏆 Conflict resolved (FIRST_WRITE_WINS): {winner.provider}")
            return winner
        
        elif strategy == ConflictResolutionStrategy.SIZE_BASED:
            # Keep largest file
            winner = max(versions, key=lambda v: v.size_bytes)
            logger.info(f"🏆 Conflict resolved (SIZE_BASED): {winner.provider}")
            return winner
        
        else:
            # Default to last write wins
            winner = max(versions, key=lambda v: v.timestamp)
            logger.info(f"🏆 Conflict resolved (default): {winner.provider}")
            return winner
    
    async def synchronize_with_retry(
        self,
        file_id: str,
        source_provider: str,
        target_providers: List[str],
        download_func,
        upload_func
    ) -> SyncResult:
        """
        Synchronize data across providers with retry logic
        
        Args:
            file_id: File to synchronize
            source_provider: Source provider
            target_providers: Target providers
            download_func: Function to download data
            upload_func: Function to upload data
            
        Returns:
            Synchronization result
        """
        start_time = datetime.now()
        synced = []
        errors = []
        conflicts = 0
        
        # Acquire lock
        lock_acquired = await self.acquire_lock(file_id)
        if not lock_acquired:
            return SyncResult(
                success=False,
                file_id=file_id,
                synced_providers=[],
                conflicts_resolved=0,
                errors=["Failed to acquire lock"],
                duration_seconds=0
            )
        
        try:
            # Download from source with retry
            data = None
            for attempt in range(self.max_retries):
                try:
                    data = await download_func(source_provider, file_id)
                    break
                except Exception as e:
                    logger.warning(f"⚠️ Download attempt {attempt + 1} failed: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                    else:
                        errors.append(f"Download failed after {self.max_retries} attempts")
                        return SyncResult(
                            success=False,
                            file_id=file_id,
                            synced_providers=[],
                            conflicts_resolved=0,
                            errors=errors,
                            duration_seconds=(datetime.now() - start_time).total_seconds()
                        )
            
            # Calculate checksum
            checksum = self.calculate_checksum(data)
            
            # Upload to targets with retry
            for target in target_providers:
                for attempt in range(self.max_retries):
                    try:
                        await upload_func(target, file_id, data)
                        synced.append(target)
                        logger.info(f"✅ Synced to {target}")
                        break
                    except Exception as e:
                        logger.warning(f"⚠️ Upload to {target} attempt {attempt + 1} failed: {e}")
                        if attempt == self.max_retries - 1:
                            errors.append(f"Upload to {target} failed")
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return SyncResult(
                success=len(errors) == 0,
                file_id=file_id,
                synced_providers=synced,
                conflicts_resolved=conflicts,
                errors=errors,
                duration_seconds=duration
            )
        
        finally:
            # Always release lock
            await self.release_lock(file_id)
    
    async def handle_network_failure(
        self,
        operation: str,
        func,
        *args,
        **kwargs
    ) -> Any:
        """
        Handle network failures with exponential backoff retry
        
        Args:
            operation: Description of operation
            func: Function to execute
            *args, **kwargs: Arguments for function
            
        Returns:
            Result of function execution
        """
        for attempt in range(self.max_retries):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(
                    f"⚠️ {operation} failed (attempt {attempt + 1}/{self.max_retries}): {e}. "
                    f"Retrying in {wait_time}s..."
                )
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ {operation} failed after {self.max_retries} attempts")
                    raise
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log event for audit trail (event sourcing)
        
        Args:
            event_type: Type of event
            data: Event data
        """
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Store in Redis if available
        if self.redis_client:
            try:
                event_key = f"event:{event_type}:{datetime.now().timestamp()}"
                self.redis_client.setex(
                    event_key,
                    86400,  # 24 hour TTL
                    json.dumps(event)
                )
            except Exception as e:
                logger.warning(f"⚠️ Failed to log event: {e}")
        
        logger.info(f"📝 Event logged: {event_type}")


# Global instance
consistency_manager = DataConsistencyManager()
