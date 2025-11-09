"""
CloudFlux AI - Cloud Migration Service
Handles actual file transfers between AWS S3, Azure Blob Storage, and GCP Cloud Storage
"""
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from io import BytesIO
import os

logger = logging.getLogger(__name__)

class MigrationService:
    """Service for migrating files between cloud providers"""
    
    def __init__(self):
        self.aws_s3 = None
        self.azure_blob = None
        self.gcp_storage = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize cloud provider clients"""
        # Load environment variables
        env_vars = {}
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#') and '=' in line:
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value
        
        # Initialize AWS S3
        try:
            import boto3
            self.aws_s3 = boto3.client(
                's3',
                aws_access_key_id=env_vars.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=env_vars.get('AWS_SECRET_ACCESS_KEY'),
                region_name=env_vars.get('AWS_REGION', 'us-east-1')
            )
            self.aws_bucket = env_vars.get('AWS_S3_BUCKET')
            logger.info("✅ AWS S3 migration client initialized")
        except Exception as e:
            logger.warning(f"⚠️  AWS S3 migration client not available: {e}")
        
        # Initialize Azure Blob Storage
        try:
            from azure.storage.blob import BlobServiceClient
            account_name = env_vars.get('AZURE_STORAGE_ACCOUNT_NAME')
            account_key = env_vars.get('AZURE_STORAGE_ACCOUNT_KEY')
            connection_string = (
                f"DefaultEndpointsProtocol=https;"
                f"AccountName={account_name};"
                f"AccountKey={account_key};"
                f"EndpointSuffix=core.windows.net"
            )
            self.azure_blob = BlobServiceClient.from_connection_string(connection_string)
            self.azure_container = env_vars.get('AZURE_CONTAINER_NAME', 'cloudflux-container')
            logger.info("✅ Azure Blob migration client initialized")
        except Exception as e:
            logger.warning(f"⚠️  Azure Blob migration client not available: {e}")
        
        # Initialize GCP Cloud Storage
        try:
            from google.cloud import storage
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './gcp-credentials.json'
            self.gcp_storage = storage.Client(project=env_vars.get('GCP_PROJECT_ID'))
            self.gcp_bucket_name = env_vars.get('GCP_BUCKET_NAME')
            logger.info("✅ GCP Storage migration client initialized")
        except Exception as e:
            logger.warning(f"⚠️  GCP Storage migration client not available: {e}")
    
    async def download_from_aws(self, key: str, bucket: Optional[str] = None) -> bytes:
        """Download file from AWS S3"""
        if not self.aws_s3:
            raise Exception("AWS S3 not initialized")
        
        bucket = bucket or self.aws_bucket
        
        try:
            logger.info(f"📥 Downloading from AWS S3: {bucket}/{key}")
            response = self.aws_s3.get_object(Bucket=bucket, Key=key)
            data = response['Body'].read()
            logger.info(f"✅ Downloaded {len(data)} bytes from AWS S3")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to download from AWS: {e}")
            raise
    
    async def upload_to_aws(self, key: str, data: bytes, bucket: Optional[str] = None) -> Dict[str, Any]:
        """Upload file to AWS S3"""
        if not self.aws_s3:
            raise Exception("AWS S3 not initialized")
        
        bucket = bucket or self.aws_bucket
        
        try:
            logger.info(f"📤 Uploading to AWS S3: {bucket}/{key} ({len(data)} bytes)")
            self.aws_s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=data
            )
            logger.info(f"✅ Uploaded to AWS S3: {key}")
            return {"provider": "AWS", "bucket": bucket, "key": key, "size": len(data)}
        except Exception as e:
            logger.error(f"❌ Failed to upload to AWS: {e}")
            raise
    
    async def download_from_azure(self, blob_name: str, container: Optional[str] = None) -> bytes:
        """Download blob from Azure Blob Storage"""
        if not self.azure_blob:
            raise Exception("Azure Blob Storage not initialized")
        
        container = container or self.azure_container
        
        try:
            logger.info(f"📥 Downloading from Azure: {container}/{blob_name}")
            container_client = self.azure_blob.get_container_client(container)
            blob_client = container_client.get_blob_client(blob_name)
            data = blob_client.download_blob().readall()
            logger.info(f"✅ Downloaded {len(data)} bytes from Azure")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to download from Azure: {e}")
            raise
    
    async def upload_to_azure(self, blob_name: str, data: bytes, container: Optional[str] = None) -> Dict[str, Any]:
        """Upload blob to Azure Blob Storage"""
        if not self.azure_blob:
            raise Exception("Azure Blob Storage not initialized")
        
        container = container or self.azure_container
        
        try:
            logger.info(f"📤 Uploading to Azure: {container}/{blob_name} ({len(data)} bytes)")
            container_client = self.azure_blob.get_container_client(container)
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(data, overwrite=True)
            logger.info(f"✅ Uploaded to Azure: {blob_name}")
            return {"provider": "AZURE", "container": container, "blob": blob_name, "size": len(data)}
        except Exception as e:
            logger.error(f"❌ Failed to upload to Azure: {e}")
            raise
    
    async def download_from_gcp(self, blob_name: str, bucket: Optional[str] = None) -> bytes:
        """Download object from GCP Cloud Storage"""
        if not self.gcp_storage:
            raise Exception("GCP Cloud Storage not initialized")
        
        bucket_name = bucket or self.gcp_bucket_name
        
        try:
            logger.info(f"📥 Downloading from GCP: {bucket_name}/{blob_name}")
            bucket = self.gcp_storage.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            data = blob.download_as_bytes()
            logger.info(f"✅ Downloaded {len(data)} bytes from GCP")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to download from GCP: {e}")
            raise
    
    async def upload_to_gcp(self, blob_name: str, data: bytes, bucket: Optional[str] = None) -> Dict[str, Any]:
        """Upload object to GCP Cloud Storage"""
        if not self.gcp_storage:
            raise Exception("GCP Cloud Storage not initialized")
        
        bucket_name = bucket or self.gcp_bucket_name
        
        try:
            logger.info(f"📤 Uploading to GCP: {bucket_name}/{blob_name} ({len(data)} bytes)")
            bucket = self.gcp_storage.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(data)
            logger.info(f"✅ Uploaded to GCP: {blob_name}")
            return {"provider": "GCP", "bucket": bucket_name, "blob": blob_name, "size": len(data)}
        except Exception as e:
            logger.error(f"❌ Failed to upload to GCP: {e}")
            raise
    
    async def migrate_file(
        self,
        source_provider: str,
        dest_provider: str,
        file_name: str,
        source_container: Optional[str] = None,
        dest_container: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Migrate a single file between cloud providers
        
        Args:
            source_provider: Source cloud (AWS, AZURE, GCP)
            dest_provider: Destination cloud (AWS, AZURE, GCP)
            file_name: Name of the file to migrate
            source_container: Optional source bucket/container
            dest_container: Optional destination bucket/container
        
        Returns:
            Migration result dictionary
        """
        source_provider = source_provider.upper()
        dest_provider = dest_provider.upper()
        
        if source_provider == dest_provider:
            raise ValueError("Source and destination providers cannot be the same")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Download from source
            logger.info(f"🔄 Starting migration: {source_provider} → {dest_provider} ({file_name})")
            
            if source_provider == "AWS":
                data = await self.download_from_aws(file_name, source_container)
            elif source_provider == "AZURE":
                data = await self.download_from_azure(file_name, source_container)
            elif source_provider == "GCP":
                data = await self.download_from_gcp(file_name, source_container)
            else:
                raise ValueError(f"Invalid source provider: {source_provider}")
            
            # Step 2: Upload to destination
            if dest_provider == "AWS":
                result = await self.upload_to_aws(file_name, data, dest_container)
            elif dest_provider == "AZURE":
                result = await self.upload_to_azure(file_name, data, dest_container)
            elif dest_provider == "GCP":
                result = await self.upload_to_gcp(file_name, data, dest_container)
            else:
                raise ValueError(f"Invalid destination provider: {dest_provider}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ Migration completed in {duration:.2f}s")
            
            return {
                "status": "success",
                "source_provider": source_provider,
                "dest_provider": dest_provider,
                "file_name": file_name,
                "size_bytes": len(data),
                "duration_seconds": round(duration, 2),
                "transfer_speed_mbps": round((len(data) / 1024 / 1024) / duration, 2) if duration > 0 else 0,
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat()
            }
        
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.error(f"❌ Migration failed: {e}")
            
            return {
                "status": "failed",
                "source_provider": source_provider,
                "dest_provider": dest_provider,
                "file_name": file_name,
                "error": str(e),
                "duration_seconds": round(duration, 2),
                "started_at": start_time.isoformat(),
                "failed_at": end_time.isoformat()
            }
    
    async def migrate_multiple_files(
        self,
        source_provider: str,
        dest_provider: str,
        file_names: List[str],
        source_container: Optional[str] = None,
        dest_container: Optional[str] = None,
        max_concurrent: int = 3
    ) -> Dict[str, Any]:
        """
        Migrate multiple files concurrently
        
        Args:
            source_provider: Source cloud provider
            dest_provider: Destination cloud provider
            file_names: List of file names to migrate
            source_container: Optional source bucket/container
            dest_container: Optional destination bucket/container
            max_concurrent: Maximum concurrent migrations
        
        Returns:
            Summary of all migrations
        """
        logger.info(f"🚀 Starting batch migration: {len(file_names)} files from {source_provider} to {dest_provider}")
        
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def migrate_with_semaphore(file_name):
            async with semaphore:
                return await self.migrate_file(
                    source_provider,
                    dest_provider,
                    file_name,
                    source_container,
                    dest_container
                )
        
        # Execute migrations concurrently
        tasks = [migrate_with_semaphore(file_name) for file_name in file_names]
        results = await asyncio.gather(*tasks)
        
        # Calculate statistics
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'failed']
        
        total_bytes = sum(r.get('size_bytes', 0) for r in successful)
        total_duration = sum(r.get('duration_seconds', 0) for r in results)
        
        summary = {
            "status": "completed",
            "total_files": len(file_names),
            "successful": len(successful),
            "failed": len(failed),
            "total_bytes_transferred": total_bytes,
            "total_size_mb": round(total_bytes / 1024 / 1024, 2),
            "total_duration_seconds": round(total_duration, 2),
            "avg_speed_mbps": round((total_bytes / 1024 / 1024) / total_duration, 2) if total_duration > 0 else 0,
            "results": results
        }
        
        logger.info(f"✅ Batch migration completed: {len(successful)}/{len(file_names)} successful")
        
        return summary
    
    def get_status(self) -> Dict[str, bool]:
        """Get migration service status"""
        return {
            "aws_available": self.aws_s3 is not None,
            "azure_available": self.azure_blob is not None,
            "gcp_available": self.gcp_storage is not None
        }


# Global migration service instance
migration_service = MigrationService()
