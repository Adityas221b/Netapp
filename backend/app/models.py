"""
CloudFlux AI - Database Models
SQLAlchemy ORM models for production system
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
from enum import Enum

def generate_uuid():
    return str(uuid.uuid4())


# Enums for Pydantic compatibility
class StorageTier(str, Enum):
    """Storage tier classification"""
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    ARCHIVE = "ARCHIVE"


class CloudProvider(str, Enum):
    """Supported cloud providers"""
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"
    MOCK = "MOCK"

# ==================== User Management ====================

class User(Base):
    """User account for authentication"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    data_objects = relationship("DataObject", back_populates="owner")
    migration_jobs = relationship("MigrationJob", back_populates="user")

# ==================== Data Objects ====================

class DataObject(Base):
    """Represents a file/object in cloud storage"""
    __tablename__ = "data_objects"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, index=True)
    size_bytes = Column(Integer, nullable=False)
    size_gb = Column(Float, nullable=False)
    
    # Classification
    tier = Column(String, nullable=False, index=True)  # HOT, WARM, COLD
    confidence_score = Column(Float)
    
    # Cloud provider info
    provider = Column(String, nullable=False, index=True)  # AWS, AZURE, GCP
    bucket_name = Column(String, nullable=False)
    storage_class = Column(String)
    region = Column(String)
    
    # Metadata
    file_type = Column(String)
    content_type = Column(String)
    etag = Column(String)
    metadata_json = Column(JSON)  # Additional cloud-specific metadata
    
    # Access tracking
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_modified_at = Column(DateTime(timezone=True))
    
    # Foreign keys
    owner_id = Column(String, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="data_objects")

# ==================== Migration Jobs ====================

class MigrationJob(Base):
    """Tracks data migration between cloud providers"""
    __tablename__ = "migration_jobs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    
    # Source and destination
    source_cloud = Column(String, nullable=False)  # AWS, AZURE, GCP
    dest_cloud = Column(String, nullable=False)
    source_bucket = Column(String, nullable=False)
    dest_bucket = Column(String, nullable=False)
    
    # Job configuration
    file_pattern = Column(String)  # Pattern to match files
    tier_filter = Column(String)   # HOT, WARM, COLD
    priority = Column(String, default="normal")  # low, normal, high
    
    # Status
    status = Column(String, nullable=False, default="queued", index=True)
    # Status: queued, running, paused, completed, failed, cancelled
    
    # Progress tracking
    total_files = Column(Integer, default=0)
    files_completed = Column(Integer, default=0)
    files_failed = Column(Integer, default=0)
    total_size_bytes = Column(Integer, default=0)
    transferred_bytes = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)
    
    # Performance metrics
    transfer_speed_mbps = Column(Float)
    estimated_completion_time = Column(DateTime(timezone=True))
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Cost tracking
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    user_id = Column(String, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="migration_jobs")

# ==================== Audit Log ====================

class AuditLog(Base):
    """Tracks all important actions for compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    
    # What happened
    action = Column(String, nullable=False, index=True)  # create, update, delete, migrate, classify
    entity_type = Column(String, nullable=False)  # user, data_object, migration_job
    entity_id = Column(String, nullable=False, index=True)
    
    # Who did it
    user_id = Column(String, ForeignKey("users.id"))
    user_email = Column(String)
    ip_address = Column(String)
    
    # Details
    description = Column(Text)
    changes_json = Column(JSON)  # Before/after values
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

# ==================== ML Model Metrics ====================

class MLModelMetrics(Base):
    """Tracks ML model performance over time"""
    __tablename__ = "ml_model_metrics"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    
    # Model info
    model_version = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # RandomForest, NeuralNetwork, etc.
    
    # Training metrics
    training_samples = Column(Integer)
    training_duration_seconds = Column(Float)
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    
    # Per-tier metrics
    hot_tier_accuracy = Column(Float)
    warm_tier_accuracy = Column(Float)
    cold_tier_accuracy = Column(Float)
    
    # Feature importance
    feature_importance_json = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=False)
    
    # Timestamps
    trained_at = Column(DateTime(timezone=True), server_default=func.now())
    deployed_at = Column(DateTime(timezone=True))

# ==================== Cost Analytics ====================

class CostSnapshot(Base):
    """Daily snapshots of cloud costs for historical analysis"""
    __tablename__ = "cost_snapshots"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    
    # Date
    snapshot_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Per-provider costs
    aws_cost = Column(Float, default=0.0)
    azure_cost = Column(Float, default=0.0)
    gcp_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Per-tier costs
    hot_tier_cost = Column(Float, default=0.0)
    warm_tier_cost = Column(Float, default=0.0)
    cold_tier_cost = Column(Float, default=0.0)
    
    # Storage breakdown
    total_objects = Column(Integer)
    total_size_gb = Column(Float)
    
    # Per-tier object counts
    hot_tier_count = Column(Integer, default=0)
    warm_tier_count = Column(Integer, default=0)
    cold_tier_count = Column(Integer, default=0)
    
    # Optimization potential
    optimized_cost = Column(Float)
    potential_savings = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
