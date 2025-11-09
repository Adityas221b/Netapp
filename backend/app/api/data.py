"""Data management API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import random
import uuid

from app.models.data_models import (
    DataObject, StorageTier, CloudProvider, 
    ClassificationResult
)
from app.services.classifier import classifier

router = APIRouter()

# In-memory storage for demo (replace with database in production)
data_objects_store = {}


@router.post("/objects", response_model=DataObject)
async def create_data_object(
    file_name: str,
    size_gb: float,
    content_type: Optional[str] = None
):
    """Create a new data object and classify it."""
    file_id = f"file_{uuid.uuid4().hex[:8]}"
    
    # Simulate some access history
    access_count = random.randint(0, 150)
    last_accessed = datetime.now() - timedelta(days=random.randint(0, 120))
    
    # Classify the data
    classification = classifier.classify(
        file_id=file_id,
        access_frequency=access_count,
        last_accessed=last_accessed,
        size_gb=size_gb
    )
    
    data_object = DataObject(
        file_id=file_id,
        file_name=file_name,
        size_gb=size_gb,
        content_type=content_type or "application/octet-stream",
        current_tier=classification.tier,
        current_cloud=CloudProvider.MOCK,
        storage_location=f"mock://{classification.tier}/{file_id}",
        last_accessed=last_accessed,
        access_count_30d=access_count,
        access_count_90d=int(access_count * 2.5),
        monthly_cost=classification.estimated_cost_per_month
    )
    
    data_objects_store[file_id] = data_object
    
    return data_object


@router.get("/objects", response_model=List[DataObject])
async def list_data_objects(
    tier: Optional[StorageTier] = None,
    cloud: Optional[CloudProvider] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """List all data objects with optional filters."""
    objects = list(data_objects_store.values())
    
    if tier:
        objects = [obj for obj in objects if obj.current_tier == tier]
    
    if cloud:
        objects = [obj for obj in objects if obj.current_cloud == cloud]
    
    return objects[:limit]


@router.get("/objects/{file_id}", response_model=DataObject)
async def get_data_object(file_id: str):
    """Get a specific data object."""
    if file_id not in data_objects_store:
        raise HTTPException(status_code=404, detail="Data object not found")
    
    return data_objects_store[file_id]


@router.post("/objects/{file_id}/classify", response_model=ClassificationResult)
async def classify_data_object(file_id: str):
    """Reclassify a data object."""
    if file_id not in data_objects_store:
        raise HTTPException(status_code=404, detail="Data object not found")
    
    obj = data_objects_store[file_id]
    
    classification = classifier.classify(
        file_id=file_id,
        access_frequency=obj.access_count_30d,
        last_accessed=obj.last_accessed,
        size_gb=obj.size_gb
    )
    
    # Update object with new classification
    obj.current_tier = classification.tier
    obj.monthly_cost = classification.estimated_cost_per_month
    
    return classification


@router.delete("/objects/{file_id}")
async def delete_data_object(file_id: str):
    """Delete a data object."""
    if file_id not in data_objects_store:
        raise HTTPException(status_code=404, detail="Data object not found")
    
    del data_objects_store[file_id]
    
    return {"message": f"Data object {file_id} deleted successfully"}


@router.post("/objects/batch-create")
async def batch_create_objects(count: int = Query(100, ge=1, le=1000)):
    """Create multiple data objects for demo purposes."""
    created_objects = []
    
    file_types = ["video/mp4", "application/json", "text/plain", "image/jpeg", "application/pdf"]
    
    for i in range(count):
        file_name = f"demo_file_{i}_{uuid.uuid4().hex[:6]}.dat"
        size_gb = round(random.uniform(0.1, 50), 2)
        content_type = random.choice(file_types)
        
        obj = await create_data_object(file_name, size_gb, content_type)
        created_objects.append(obj)
    
    return {
        "message": f"Created {count} data objects",
        "sample": created_objects[:5]
    }


@router.get("/tiers/distribution")
async def get_tier_distribution():
    """Get distribution of data across storage tiers."""
    distribution = {
        StorageTier.HOT: 0,
        StorageTier.WARM: 0,
        StorageTier.COLD: 0
    }
    
    total_size = {
        StorageTier.HOT: 0.0,
        StorageTier.WARM: 0.0,
        StorageTier.COLD: 0.0
    }
    
    for obj in data_objects_store.values():
        distribution[obj.current_tier] += 1
        total_size[obj.current_tier] += obj.size_gb
    
    return {
        "count_by_tier": {tier.value: count for tier, count in distribution.items()},
        "size_by_tier_gb": {tier.value: round(size, 2) for tier, size in total_size.items()},
        "total_objects": len(data_objects_store),
        "total_size_gb": round(sum(total_size.values()), 2)
    }
