# CloudFlux AI - Production Backend with Real Cloud Integration

This upgrade adds real cloud provider integration using free tier APIs!

## 🚀 Quick Setup (30 minutes)

### Step 1: Get Free API Keys

#### AWS (Free Tier - 12 months)
1. Sign up: https://aws.amazon.com/free/
2. Navigate to: AWS Console → IAM → Users → Create User
3. Attach policy: `AmazonS3FullAccess`
4. Security Credentials → Create Access Key
5. Copy `Access Key ID` and `Secret Access Key`

**Free Tier Limits:**
- 5GB S3 storage
- 20,000 GET requests
- 2,000 PUT requests per month

#### Azure (Free Tier - 12 months)
1. Sign up: https://azure.microsoft.com/free/
2. Navigate to: Azure Portal → Storage Accounts → Create
3. Get credentials: Storage Account → Access Keys
4. Copy `Storage Account Name` and `Key1`

**Free Tier Limits:**
- 5GB Blob storage
- 20,000 read operations
- 10,000 write operations per month

#### GCP (Free Tier - Always Free)
1. Sign up: https://cloud.google.com/free
2. Create project: GCP Console → New Project
3. Enable Cloud Storage API
4. Create Service Account: IAM → Service Accounts → Create
5. Create JSON key: Actions → Create Key → JSON
6. Download `gcp-credentials.json`

**Free Tier Limits:**
- 5GB Cloud Storage
- 5,000 Class A operations
- 50,000 Class B operations per month

---

### Step 2: Configure Environment Variables

```bash
cd /home/bitreaper/Desktop/Netapp/cloudflux-ai/backend

# Copy example to .env
cp .env.example .env

# Edit with your credentials
nano .env  # or use any text editor
```

**Minimal .env for demo:**
```bash
# Database (use SQLite for quick start)
DATABASE_URL=sqlite:///./cloudflux.db

# JWT Secret (generate one)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# AWS
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=us-east-1
AWS_S3_BUCKET=cloudflux-demo-bucket

# Azure
AZURE_STORAGE_ACCOUNT_NAME=your_account
AZURE_STORAGE_ACCOUNT_KEY=your_key
AZURE_CONTAINER_NAME=cloudflux-container

# GCP
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json
GCP_PROJECT_ID=your-project-id
GCP_BUCKET_NAME=cloudflux-gcp-bucket

# Demo mode
DEMO_MODE=False
USE_MOCK_DATA=False
```

---

### Step 3: Install Additional Dependencies

```bash
cd backend
source venv/bin/activate

# Install cloud provider SDKs
pip install boto3==1.34.0                    # AWS SDK
pip install azure-storage-blob==12.19.0      # Azure SDK
pip install google-cloud-storage==2.14.0     # GCP SDK

# Install database and auth
pip install sqlalchemy==2.0.25               # Database ORM
pip install psycopg2-binary==2.9.9           # PostgreSQL driver (or use SQLite)
pip install python-jose[cryptography]==3.3.0 # JWT
pip install passlib[bcrypt]==1.7.4           # Password hashing
pip install python-multipart==0.0.6          # Form data

# Save requirements
pip freeze > requirements-production.txt
```

---

### Step 4: Create Cloud Storage Buckets

#### AWS S3 Bucket
```bash
# Using AWS CLI (install with: pip install awscli)
aws configure  # Enter your credentials
aws s3 mb s3://cloudflux-demo-bucket --region us-east-1
```

#### Azure Blob Container
```bash
# Using Azure CLI (install with: pip install azure-cli)
az login
az storage container create --name cloudflux-container --account-name your_account
```

#### GCP Cloud Storage Bucket
```bash
# Using gcloud CLI (install from: https://cloud.google.com/sdk/docs/install)
gcloud auth login
gcloud config set project your-project-id
gsutil mb gs://cloudflux-gcp-bucket
```

**Or create manually through web consoles** (easier for first time!)

---

### Step 5: Update Backend Configuration

Create `backend/app/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./cloudflux.db"
    
    # AWS
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "cloudflux-demo-bucket"
    
    # Azure
    azure_storage_account_name: Optional[str] = None
    azure_storage_account_key: Optional[str] = None
    azure_container_name: str = "cloudflux-container"
    
    # GCP
    google_application_credentials: Optional[str] = None
    gcp_project_id: Optional[str] = None
    gcp_bucket_name: str = "cloudflux-gcp-bucket"
    
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # App
    demo_mode: bool = False
    use_mock_data: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

### Step 6: Create Real Cloud Service

Create `backend/app/services/cloud_service.py`:

```python
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class CloudService:
    def __init__(self):
        self.aws_s3 = None
        self.azure_blob = None
        self.gcp_storage = None
        
        # Initialize AWS S3
        if settings.aws_access_key_id:
            try:
                self.aws_s3 = boto3.client(
                    's3',
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region
                )
                logger.info("AWS S3 client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize AWS S3: {e}")
        
        # Initialize Azure Blob
        if settings.azure_storage_account_name:
            try:
                connection_string = f"DefaultEndpointsProtocol=https;AccountName={settings.azure_storage_account_name};AccountKey={settings.azure_storage_account_key};EndpointSuffix=core.windows.net"
                self.azure_blob = BlobServiceClient.from_connection_string(connection_string)
                logger.info("Azure Blob client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Azure Blob: {e}")
        
        # Initialize GCP Storage
        if settings.gcp_project_id:
            try:
                self.gcp_storage = storage.Client(project=settings.gcp_project_id)
                logger.info("GCP Storage client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize GCP Storage: {e}")
    
    async def list_objects(self, provider: str, bucket: str = None):
        """List objects from cloud provider"""
        if provider.lower() == "aws" and self.aws_s3:
            bucket = bucket or settings.aws_s3_bucket
            response = self.aws_s3.list_objects_v2(Bucket=bucket)
            return response.get('Contents', [])
        
        elif provider.lower() == "azure" and self.azure_blob:
            container = bucket or settings.azure_container_name
            container_client = self.azure_blob.get_container_client(container)
            return list(container_client.list_blobs())
        
        elif provider.lower() == "gcp" and self.gcp_storage:
            bucket_name = bucket or settings.gcp_bucket_name
            bucket = self.gcp_storage.bucket(bucket_name)
            return list(bucket.list_blobs())
        
        return []
    
    async def get_object_metadata(self, provider: str, bucket: str, key: str):
        """Get object metadata from cloud provider"""
        if provider.lower() == "aws" and self.aws_s3:
            response = self.aws_s3.head_object(Bucket=bucket, Key=key)
            return {
                "size": response['ContentLength'],
                "last_modified": response['LastModified'],
                "storage_class": response.get('StorageClass', 'STANDARD')
            }
        
        elif provider.lower() == "azure" and self.azure_blob:
            container_client = self.azure_blob.get_container_client(bucket)
            blob_client = container_client.get_blob_client(key)
            properties = blob_client.get_blob_properties()
            return {
                "size": properties.size,
                "last_modified": properties.last_modified,
                "storage_class": properties.blob_tier
            }
        
        elif provider.lower() == "gcp" and self.gcp_storage:
            bucket = self.gcp_storage.bucket(bucket)
            blob = bucket.get_blob(key)
            return {
                "size": blob.size,
                "last_modified": blob.updated,
                "storage_class": blob.storage_class
            }
        
        return None

cloud_service = CloudService()
```

---

### Step 7: Run with Real Integration

```bash
cd backend
source venv/bin/activate

# Start with real cloud integration
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or fall back to demo mode
uvicorn simple_app:app --reload --host 0.0.0.0 --port 8000
```

---

## 🎯 Testing Real Integration

### Test AWS S3
```bash
# List buckets
curl http://localhost:8000/api/cloud/aws/buckets

# List objects
curl http://localhost:8000/api/cloud/aws/objects?bucket=cloudflux-demo-bucket
```

### Test Azure Blob
```bash
# List containers
curl http://localhost:8000/api/cloud/azure/containers

# List blobs
curl http://localhost:8000/api/cloud/azure/blobs?container=cloudflux-container
```

### Test GCP Storage
```bash
# List buckets
curl http://localhost:8000/api/cloud/gcp/buckets

# List objects
curl http://localhost:8000/api/cloud/gcp/objects?bucket=cloudflux-gcp-bucket
```

---

## 💰 Cost Tracking with Real Pricing

### AWS S3 Pricing (as of 2025)
- Standard: $0.023/GB/month
- Infrequent Access: $0.0125/GB/month
- Glacier: $0.004/GB/month

### Azure Blob Pricing
- Hot: $0.0184/GB/month
- Cool: $0.01/GB/month
- Archive: $0.002/GB/month

### GCP Storage Pricing
- Standard: $0.020/GB/month
- Nearline: $0.010/GB/month
- Coldline: $0.004/GB/month

---

## 🔒 Security Best Practices

### 1. Never Commit API Keys
```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "gcp-credentials.json" >> .gitignore
```

### 2. Use Environment Variables
```bash
# Set temporarily
export AWS_ACCESS_KEY_ID=your_key

# Or use .env file (already configured)
```

### 3. Rotate Keys Regularly
- AWS: IAM → Users → Security Credentials → Rotate Keys
- Azure: Storage Accounts → Access Keys → Regenerate
- GCP: Service Accounts → Keys → Create New Key

---

## 🚀 Deployment Checklist

- [ ] Get AWS free tier account and credentials
- [ ] Get Azure free tier account and credentials
- [ ] Get GCP free tier account and credentials
- [ ] Create storage buckets in all 3 clouds
- [ ] Configure `.env` file with real credentials
- [ ] Install cloud SDKs (`boto3`, `azure-storage-blob`, `google-cloud-storage`)
- [ ] Test connection to each cloud provider
- [ ] Update `simple_app.py` to use real cloud service
- [ ] Test API endpoints with real data
- [ ] Update frontend to show real cloud data

---

## 📊 What You Get

### With Free Tiers:
- ✅ Real cloud provider integration
- ✅ Actual cost calculation based on provider pricing
- ✅ Real data from AWS/Azure/GCP
- ✅ Multi-cloud migration capabilities
- ✅ Live tier classification
- ✅ No monthly costs (within free limits)

### Free Tier Totals:
- **15GB total storage** (5GB × 3 providers)
- **Hundreds of thousands of requests** per month
- **Perfect for hackathon demo and small projects**

---

## 🎬 Demo Flow with Real Integration

1. **Show real AWS bucket**: "Here's live data from my AWS S3 bucket"
2. **Show real Azure container**: "Same data mirrored in Azure"
3. **Show real GCP bucket**: "And in Google Cloud"
4. **Trigger migration**: "Watch as we move data between clouds"
5. **Show cost savings**: "Using real provider pricing"

**This is 10x more impressive than mock data!** 🔥

---

## 🐛 Troubleshooting

### AWS Connection Issues
```bash
# Test AWS credentials
aws s3 ls --profile default

# Check boto3 connection
python -c "import boto3; s3=boto3.client('s3'); print(s3.list_buckets())"
```

### Azure Connection Issues
```bash
# Test Azure credentials
az storage account list

# Check azure-storage-blob
python -c "from azure.storage.blob import BlobServiceClient; print('Azure SDK OK')"
```

### GCP Connection Issues
```bash
# Test GCP credentials
gcloud auth list

# Check google-cloud-storage
python -c "from google.cloud import storage; print('GCP SDK OK')"
```

---

## 🎯 Next Steps

1. **Get API keys** (30 minutes) - Sign up for all 3 cloud providers
2. **Configure .env** (5 minutes) - Add credentials
3. **Install SDKs** (5 minutes) - Run pip install commands
4. **Test connections** (10 minutes) - Verify each cloud provider
5. **Update backend** (15 minutes) - Integrate cloud service
6. **Demo!** (3 minutes) - Show real multi-cloud orchestration

**Total time: ~1 hour to go from mock to real!**

---

Need help? Check the troubleshooting section or refer to:
- AWS Docs: https://docs.aws.amazon.com/s3/
- Azure Docs: https://learn.microsoft.com/azure/storage/
- GCP Docs: https://cloud.google.com/storage/docs

**Let's make this demo REAL!** 🚀
