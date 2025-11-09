"""Migration API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from datetime import datetime
import asyncio

from app.models.data_models import MigrationJob, CloudProvider, StorageTier
from app.api.data import data_objects_store

router = APIRouter()

# In-memory migration jobs store
migration_jobs_store = {}


@router.post("/jobs", response_model=MigrationJob)
async def create_migration_job(
    file_id: str,
    dest_cloud: CloudProvider,
    dest_tier: StorageTier
):
    """Create a new migration job."""
    if file_id not in data_objects_store:
        raise HTTPException(status_code=404, detail="Data object not found")
    
    obj = data_objects_store[file_id]
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    
    # Simulate transfer cost calculation
    transfer_cost = obj.size_gb * 0.01  # $0.01 per GB
    estimated_duration = int(obj.size_gb * 10)  # 10 seconds per GB
    
    job = MigrationJob(
        job_id=job_id,
        file_id=file_id,
        source_cloud=obj.current_cloud,
        source_tier=obj.current_tier,
        dest_cloud=dest_cloud,
        dest_tier=dest_tier,
        size_gb=obj.size_gb,
        transfer_cost=round(transfer_cost, 4),
        estimated_duration_sec=estimated_duration,
        status="pending"
    )
    
    migration_jobs_store[job_id] = job
    
    # Start migration in background
    asyncio.create_task(simulate_migration(job_id))
    
    return job


async def simulate_migration(job_id: str):
    """Simulate migration progress."""
    job = migration_jobs_store[job_id]
    job.status = "in_progress"
    job.started_at = datetime.now()
    
    # Simulate progress
    for progress in range(0, 101, 10):
        await asyncio.sleep(1)  # Simulate work
        job.progress_pct = progress
        
        if progress == 100:
            job.status = "completed"
            job.completed_at = datetime.now()
            
            # Update data object
            if job.file_id in data_objects_store:
                obj = data_objects_store[job.file_id]
                obj.current_cloud = job.dest_cloud
                obj.current_tier = job.dest_tier
                obj.storage_location = f"{job.dest_cloud.value}://{job.dest_tier.value}/{job.file_id}"


@router.get("/jobs", response_model=List[MigrationJob])
async def list_migration_jobs(status: str = None):
    """List all migration jobs."""
    jobs = list(migration_jobs_store.values())
    
    if status:
        jobs = [job for job in jobs if job.status == status]
    
    # Sort by created time (most recent first)
    jobs.sort(key=lambda x: x.started_at or datetime.min, reverse=True)
    
    return jobs


@router.get("/jobs/{job_id}", response_model=MigrationJob)
async def get_migration_job(job_id: str):
    """Get migration job status."""
    if job_id not in migration_jobs_store:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    return migration_jobs_store[job_id]


@router.delete("/jobs/{job_id}")
async def cancel_migration_job(job_id: str):
    """Cancel a migration job."""
    if job_id not in migration_jobs_store:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    job = migration_jobs_store[job_id]
    
    if job.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot cancel completed job")
    
    job.status = "cancelled"
    
    return {"message": f"Migration job {job_id} cancelled"}


@router.post("/estimate")
async def estimate_migration_cost(
    file_id: str,
    dest_cloud: CloudProvider,
    dest_tier: StorageTier
):
    """Estimate migration cost and duration."""
    if file_id not in data_objects_store:
        raise HTTPException(status_code=404, detail="Data object not found")
    
    obj = data_objects_store[file_id]
    
    # Cost calculation
    transfer_cost = obj.size_gb * 0.01  # $0.01 per GB
    source_storage_cost = obj.monthly_cost
    
    # Estimate destination cost
    from app.services.classifier import classifier
    dest_cost = classifier.costs[dest_tier] * obj.size_gb
    
    estimated_duration = int(obj.size_gb * 10)  # 10 seconds per GB
    
    return {
        "file_id": file_id,
        "size_gb": obj.size_gb,
        "transfer_cost": round(transfer_cost, 4),
        "current_monthly_cost": round(source_storage_cost, 4),
        "destination_monthly_cost": round(dest_cost, 4),
        "monthly_savings": round(source_storage_cost - dest_cost, 4),
        "estimated_duration_sec": estimated_duration,
        "estimated_duration_readable": f"{estimated_duration // 60}m {estimated_duration % 60}s"
    }
