"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "CloudFlux AI"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    
    # Database
    database_url: str = "postgresql://cloudflux:cloudflux123@localhost:5432/cloudflux_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_cache_ttl: int = 3600  # 1 hour
    
    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_ingestion: str = "data-ingestion"
    kafka_topic_classification: str = "classification"
    kafka_topic_migration: str = "migration-events"
    kafka_topic_analytics: str = "analytics"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Cloud Providers
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    
    azure_storage_connection_string: Optional[str] = None
    azure_container_name: Optional[str] = None
    
    gcp_project_id: Optional[str] = None
    gcp_bucket_name: Optional[str] = None
    
    # Storage Costs (per GB per month in USD)
    cost_hot_storage: float = 0.023  # AWS S3 Standard
    cost_warm_storage: float = 0.0125  # AWS S3 IA
    cost_cold_storage: float = 0.004  # AWS S3 Glacier
    
    # Latency (in milliseconds)
    latency_hot: int = 10
    latency_warm: int = 50
    latency_cold: int = 3000
    
    # ML Model
    ml_model_path: str = "/ml/models/access_predictor.pkl"
    ml_training_data_path: str = "/ml/data/training_data.csv"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
