"""Data models for CloudFlux AI."""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class StorageTier(str, Enum):
    """Storage tier classifications."""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class CloudProvider(str, Enum):
    """Cloud provider types."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    MOCK = "mock"


class DataObject(BaseModel):
    """Data object model."""
    file_id: str
    file_name: str
    size_gb: float = Field(gt=0)
    content_type: Optional[str] = None
    current_tier: StorageTier
    current_cloud: CloudProvider
    storage_location: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = None
    access_count_30d: int = 0
    access_count_90d: int = 0
    avg_latency_ms: Optional[int] = None
    monthly_cost: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class ClassificationResult(BaseModel):
    """Result of data classification."""
    file_id: str
    tier: StorageTier
    reason: str
    estimated_cost_per_month: float
    latency_ms: int
    access_frequency: int
    days_since_access: int
    confidence: float = 1.0


class MigrationJob(BaseModel):
    """Migration job model."""
    job_id: str
    file_id: str
    source_cloud: CloudProvider
    source_tier: StorageTier
    dest_cloud: CloudProvider
    dest_tier: StorageTier
    status: str = "pending"
    progress_pct: int = 0
    size_gb: float
    transfer_cost: float = 0.0
    estimated_duration_sec: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class MLPrediction(BaseModel):
    """ML prediction model."""
    file_id: str
    prediction_date: str
    predicted_accesses: int
    recommended_tier: StorageTier
    confidence_score: float
    reasoning: str


class CostSavings(BaseModel):
    """Cost savings calculation."""
    current_monthly_cost: float
    recommended_monthly_cost: float
    monthly_savings: float
    savings_percentage: float
    annual_savings: float
