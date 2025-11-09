"""
CloudFlux AI - Enhanced Configuration with Real Cloud Support
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings with cloud provider credentials"""
    
    # ====================================
    # DATABASE CONFIGURATION
    # ====================================
    database_url: str = "sqlite:///./cloudflux.db"
    
    # ====================================
    # AWS CREDENTIALS
    # ====================================
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "cloudflux-demo-bucket"
    
    # ====================================
    # AZURE CREDENTIALS
    # ====================================
    azure_storage_account_name: Optional[str] = None
    azure_storage_account_key: Optional[str] = None
    azure_container_name: str = "cloudflux-container"
    
    # ====================================
    # GCP CREDENTIALS
    # ====================================
    google_application_credentials: Optional[str] = None
    gcp_project_id: Optional[str] = None
    gcp_bucket_name: str = "cloudflux-gcp-bucket"
    
    # ====================================
    # JWT AUTHENTICATION
    # ====================================
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # ====================================
    # KAFKA CONFIGURATION
    # ====================================
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_data_ingestion: str = "data-ingestion"
    kafka_topic_classification: str = "data-classification"
    
    # ====================================
    # REDIS CONFIGURATION
    # ====================================
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # ====================================
    # APPLICATION SETTINGS
    # ====================================
    app_env: str = "development"
    debug: bool = True
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # ====================================
    # ML MODEL SETTINGS
    # ====================================
    ml_model_path: str = "./models/"
    min_training_samples: int = 100
    model_retrain_interval_hours: int = 24
    
    # ====================================
    # DEMO MODE
    # ====================================
    demo_mode: bool = True
    use_mock_data: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"
    
    @property
    def cors_origins_list(self):
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def has_aws_credentials(self):
        """Check if AWS credentials are configured"""
        return bool(self.aws_access_key_id and self.aws_secret_access_key)
    
    @property
    def has_azure_credentials(self):
        """Check if Azure credentials are configured"""
        return bool(self.azure_storage_account_name and self.azure_storage_account_key)
    
    @property
    def has_gcp_credentials(self):
        """Check if GCP credentials are configured"""
        return bool(self.gcp_project_id)


# Global settings instance
settings = Settings()
