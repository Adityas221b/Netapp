"""
CloudFlux AI - Migration Routes
API endpoints for cloud-to-cloud file migration
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import uuid
import asyncio

from app.database import get_db
from app.models import MigrationJob, AuditLog
from app.auth import get_current_active_user
from app.services.migration_service import migration_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/migration", tags=["Migration"])

# In-memory storage for when database is not available
_in_memory_jobs = []

# ==================== Request/Response Models ====================

class MigrationRequest(BaseModel):
    source_provider: str  # AWS, AZURE, GCP
    dest_provider: str
    file_names: List[str]
    source_container: Optional[str] = None
    dest_container: Optional[str] = None
    priority: str = "normal"  # low, normal, high

class MigrationJobResponse(BaseModel):
    id: str  # Changed from job_id to match database model
    source_cloud: str
    dest_cloud: str
    status: str
    total_files: int
    files_completed: int
    files_failed: int
    progress_percentage: float
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ==================== Migration Endpoints ====================

@router.post("/migrate", response_model=dict)
async def migrate_files(
    request: MigrationRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Migrate files between cloud providers
    
    **Requires Authentication**
    
    - **source_provider**: Source cloud (AWS, AZURE, or GCP)
    - **dest_provider**: Destination cloud (AWS, AZURE, or GCP)
    - **file_names**: List of file names to migrate
    - **source_container**: Optional source bucket/container name
    - **dest_container**: Optional destination bucket/container name
    - **priority**: Migration priority (low, normal, high)
    
    Returns migration job details
    """
    # Validate providers
    valid_providers = ["AWS", "AZURE", "GCP"]
    source = request.source_provider.upper()
    dest = request.dest_provider.upper()
    
    if source not in valid_providers:
        raise HTTPException(status_code=400, detail=f"Invalid source provider: {source}")
    if dest not in valid_providers:
        raise HTTPException(status_code=400, detail=f"Invalid destination provider: {dest}")
    if source == dest:
        raise HTTPException(status_code=400, detail="Source and destination cannot be the same")
    
    if not request.file_names:
        raise HTTPException(status_code=400, detail="No files specified")
    
    # Check migration service availability (allow demo mode to work without real credentials)
    status = migration_service.get_status()
    demo_mode = not any([status["aws_available"], status["azure_available"], status["gcp_available"]])
    
    if not demo_mode:
        # Only check if we have real cloud connections
        if source == "AWS" and not status["aws_available"]:
            raise HTTPException(status_code=503, detail="AWS migration not available")
        if source == "AZURE" and not status["azure_available"]:
            raise HTTPException(status_code=503, detail="Azure migration not available")
        if source == "GCP" and not status["gcp_available"]:
            raise HTTPException(status_code=503, detail="GCP migration not available")
        if dest == "AWS" and not status["aws_available"]:
            raise HTTPException(status_code=503, detail="AWS migration not available")
        if dest == "AZURE" and not status["azure_available"]:
            raise HTTPException(status_code=503, detail="Azure migration not available")
        if dest == "GCP" and not status["gcp_available"]:
            raise HTTPException(status_code=503, detail="GCP migration not available")
    
    # Get user ID
    user_id = current_user.get("user_id") if isinstance(current_user, dict) else current_user.id
    user_email = current_user.get("email") if isinstance(current_user, dict) else current_user.email
    
    job_id = str(uuid.uuid4())
    job_data = {
        "id": job_id,
        "source_cloud": source,
        "dest_cloud": dest,
        "source_bucket": request.source_container or "default",
        "dest_bucket": request.dest_container or "default",
        "priority": request.priority,
        "status": "running",
        "total_files": len(request.file_names),
        "files_completed": 0,
        "files_failed": 0,
        "progress_percentage": 0.0,
        "user_id": user_id,
        "started_at": datetime.now(),
        "created_at": datetime.now(),
        "completed_at": None
    }
    
    # Try to save to database, fall back to in-memory storage
    try:
        job = MigrationJob(**job_data)
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Create audit log
        audit = AuditLog(
            id=str(uuid.uuid4()),
            action="migrate",
            entity_type="migration_job",
            entity_id=job.id,
            user_id=user_id,
            user_email=user_email,
            description=f"Started migration: {source} → {dest} ({len(request.file_names)} files)"
        )
        db.add(audit)
        db.commit()
        
        logger.info(f"📦 Migration job created in database: {job.id} by {user_email}")
    except Exception as e:
        logger.warning(f"⚠️  Database unavailable, using in-memory storage: {e}")
        # Store in memory instead
        _in_memory_jobs.append(job_data)
        logger.info(f"📦 Migration job created in-memory: {job_id} by {user_email}")
    
    # Determine if we should use real migration or demo mode
    # Use real migration if both source and destination providers are available
    source_available = (source == "AWS" and status.get("aws_available")) or \
                      (source == "AZURE" and status.get("azure_available")) or \
                      (source == "GCP" and status.get("gcp_available"))
    dest_available = (dest == "AWS" and status.get("aws_available")) or \
                    (dest == "AZURE" and status.get("azure_available")) or \
                    (dest == "GCP" and status.get("gcp_available"))
    
    use_real_migration = source_available and dest_available
    
    logger.info(f"📦 Migration job created: {job_id} by {user_email} (real_migration={use_real_migration})")
    
    # Start background task - use real migration if available, otherwise simulate
    if use_real_migration:
        background_tasks.add_task(
            execute_real_migration, 
            job_id, 
            source,
            dest,
            request.file_names,
            request.source_container,
            request.dest_container
        )
    else:
        background_tasks.add_task(simulate_demo_migration, job_id, len(request.file_names))
    
    return {
        "job_id": job_id,
        "status": "running",
        "message": f"Migration started: {len(request.file_names)} files from {source} to {dest}",
        "total_files": len(request.file_names),
        "source_provider": source,
        "dest_provider": dest,
        "created_at": job_data["created_at"].isoformat(),
        "mode": "real" if use_real_migration else "demo"
    }




async def execute_real_migration(
    job_id: str, 
    source_provider: str, 
    dest_provider: str, 
    file_names: List[str],
    source_container: Optional[str] = None,
    dest_container: Optional[str] = None
):
    """Execute real cloud-to-cloud file migration"""
    logger.info(f"🚀 Starting REAL migration: {job_id} ({len(file_names)} files)")
    logger.info(f"   Source: {source_provider} ({source_container or 'default'})")
    logger.info(f"   Destination: {dest_provider} ({dest_container or 'default'})")
    
    # Find job in in-memory storage
    job_data = next((j for j in _in_memory_jobs if j["id"] == job_id), None)
    if not job_data:
        logger.error(f"❌ Job not found in memory: {job_id}")
        return
    
    try:
        # Update job status
        job_data["status"] = "running"
        
        # Execute real migration using migration_service
        result = await migration_service.migrate_multiple_files(
            source_provider=source_provider,
            dest_provider=dest_provider,
            file_names=file_names,
            source_container=source_container,
            dest_container=dest_container,
            max_concurrent=3
        )
        
        # Update job with real results
        job_data["files_completed"] = result["successful"]
        job_data["files_failed"] = result["failed"]
        job_data["progress_percentage"] = 100.0
        job_data["status"] = "completed"
        job_data["completed_at"] = datetime.now()
        
        logger.info(f"✅ REAL migration completed: {job_id}")
        logger.info(f"   Successful: {result['successful']}/{result['total_files']}")
        logger.info(f"   Total transferred: {result['total_size_mb']} MB")
        logger.info(f"   Duration: {result['total_duration_seconds']}s")
        logger.info(f"   Speed: {result['avg_speed_mbps']} MB/s")
        
    except Exception as e:
        logger.error(f"❌ REAL migration failed: {job_id} - {e}")
        job_data["status"] = "failed"
        job_data["progress_percentage"] = 0.0
        job_data["completed_at"] = datetime.now()


async def simulate_demo_migration(job_id: str, total_files: int):
    """Simulate migration progress in demo mode"""
    logger.info(f"🎭 Starting demo migration simulation: {job_id}")
    
    # Find job in in-memory storage
    job_data = next((j for j in _in_memory_jobs if j["id"] == job_id), None)
    if not job_data:
        logger.error(f"❌ Job not found in memory: {job_id}")
        return
    
    try:
        # Simulate progress
        for i in range(total_files + 1):
            await asyncio.sleep(2)  # Simulate processing time
            job_data["files_completed"] = i
            job_data["progress_percentage"] = (i / total_files) * 100 if total_files > 0 else 100
            logger.info(f"📊 Migration progress ({job_id}): {job_data['progress_percentage']:.1f}%")
        
        # Mark as completed
        job_data["status"] = "completed"
        job_data["files_completed"] = total_files
        job_data["files_failed"] = 0
        job_data["progress_percentage"] = 100.0
        job_data["completed_at"] = datetime.now()
        logger.info(f"✅ Demo migration completed: {job_id}")
        
    except Exception as e:
        logger.error(f"❌ Demo migration failed ({job_id}): {e}")
        job_data["status"] = "failed"
        job_data["completed_at"] = datetime.now()


@router.get("/jobs", response_model=List[MigrationJobResponse])
async def get_migration_jobs(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Get migration jobs for current user
    
    **Requires Authentication**
    
    Returns list of migration jobs sorted by creation date (newest first)
    """
    user_id = current_user.get("user_id") if isinstance(current_user, dict) else current_user.id
    
    try:
        jobs = db.query(MigrationJob)\
            .filter(MigrationJob.user_id == user_id)\
            .order_by(MigrationJob.created_at.desc())\
            .limit(limit)\
            .all()
        return jobs
    except Exception as e:
        logger.warning(f"⚠️  Database unavailable, returning in-memory jobs: {e}")
        # Return in-memory jobs for the current user
        user_jobs = [j for j in _in_memory_jobs if j["user_id"] == user_id]
        user_jobs.sort(key=lambda x: x["created_at"], reverse=True)
        return user_jobs[:limit]

@router.get("/jobs/{job_id}", response_model=MigrationJobResponse)
async def get_migration_job(
    job_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific migration job
    
    **Requires Authentication**
    """
    user_id = current_user.get("user_id") if isinstance(current_user, dict) else current_user.id
    
    job = db.query(MigrationJob)\
        .filter(MigrationJob.id == job_id)\
        .filter(MigrationJob.user_id == user_id)\
        .first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    
    return job

@router.get("/status")
async def get_migration_status(current_user = Depends(get_current_active_user)):
    """
    Get migration service status
    
    **Requires Authentication**
    
    Shows which cloud providers are available for migration
    """
    status = migration_service.get_status()
    
    return {
        "service": "migration",
        "providers": {
            "aws": {
                "available": status["aws_available"],
                "name": "Amazon S3"
            },
            "azure": {
                "available": status["azure_available"],
                "name": "Azure Blob Storage"
            },
            "gcp": {
                "available": status["gcp_available"],
                "name": "Google Cloud Storage"
            }
        },
        "supported_routes": [
            "AWS → AZURE",
            "AWS → GCP",
            "AZURE → AWS",
            "AZURE → GCP",
            "GCP → AWS",
            "GCP → AZURE"
        ]
    }
