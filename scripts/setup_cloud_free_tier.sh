#!/bin/bash

# CloudFlux AI - Quick Setup for Free Tier Cloud Integration
# This script helps you set up free tier accounts and configure API keys

echo "🚀 CloudFlux AI - Free Tier Cloud Integration Setup"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env exists
if [ -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file already exists. Backing up to .env.backup${NC}"
    cp .env .env.backup
fi

echo -e "${BLUE}📋 Step 1: Sign up for FREE cloud accounts${NC}"
echo ""
echo "1️⃣  AWS Free Tier (12 months free)"
echo "   → Sign up: https://aws.amazon.com/free/"
echo "   → Benefits: 5GB S3 storage, 20,000 GET requests, 2,000 PUT requests/month"
echo ""
echo "2️⃣  Azure Free Tier (12 months free)"
echo "   → Sign up: https://azure.microsoft.com/free/"
echo "   → Benefits: 5GB Blob storage, 20,000 read ops, 10,000 write ops/month"
echo ""
echo "3️⃣  GCP Free Tier (Always free)"
echo "   → Sign up: https://cloud.google.com/free"
echo "   → Benefits: 5GB Cloud Storage, 5,000 Class A ops, 50,000 Class B ops/month"
echo ""
read -p "Press Enter when you've signed up for the accounts you want to use..."

echo ""
echo -e "${BLUE}📋 Step 2: Get your API credentials${NC}"
echo ""

# AWS Setup
echo -e "${GREEN}🔑 AWS Credentials${NC}"
read -p "Do you have AWS credentials? (y/n): " has_aws
if [ "$has_aws" = "y" ]; then
    echo "Get your AWS credentials:"
    echo "  1. Go to AWS Console: https://console.aws.amazon.com/"
    echo "  2. Navigate to: IAM → Users → Create User"
    echo "  3. Attach policy: AmazonS3FullAccess"
    echo "  4. Security Credentials → Create Access Key"
    echo ""
    read -p "AWS Access Key ID: " aws_key
    read -sp "AWS Secret Access Key: " aws_secret
    echo ""
    read -p "AWS Region [us-east-1]: " aws_region
    aws_region=${aws_region:-us-east-1}
    read -p "AWS S3 Bucket Name [cloudflux-demo-bucket]: " aws_bucket
    aws_bucket=${aws_bucket:-cloudflux-demo-bucket}
else
    aws_key=""
    aws_secret=""
    aws_region="us-east-1"
    aws_bucket="cloudflux-demo-bucket"
fi
echo ""

# Azure Setup
echo -e "${GREEN}🔑 Azure Credentials${NC}"
read -p "Do you have Azure credentials? (y/n): " has_azure
if [ "$has_azure" = "y" ]; then
    echo "Get your Azure credentials:"
    echo "  1. Go to Azure Portal: https://portal.azure.com/"
    echo "  2. Navigate to: Storage Accounts → Create"
    echo "  3. Go to: Access Keys → Show keys"
    echo ""
    read -p "Azure Storage Account Name: " azure_account
    read -sp "Azure Storage Account Key: " azure_key
    echo ""
    read -p "Azure Container Name [cloudflux-container]: " azure_container
    azure_container=${azure_container:-cloudflux-container}
else
    azure_account=""
    azure_key=""
    azure_container="cloudflux-container"
fi
echo ""

# GCP Setup
echo -e "${GREEN}🔑 GCP Credentials${NC}"
read -p "Do you have GCP credentials? (y/n): " has_gcp
if [ "$has_gcp" = "y" ]; then
    echo "Get your GCP credentials:"
    echo "  1. Go to GCP Console: https://console.cloud.google.com/"
    echo "  2. Create a new project"
    echo "  3. Enable Cloud Storage API"
    echo "  4. IAM → Service Accounts → Create"
    echo "  5. Create Key (JSON) and download"
    echo ""
    read -p "GCP Project ID: " gcp_project
    read -p "Path to GCP credentials JSON [./gcp-credentials.json]: " gcp_creds
    gcp_creds=${gcp_creds:-./gcp-credentials.json}
    read -p "GCP Bucket Name [cloudflux-gcp-bucket]: " gcp_bucket
    gcp_bucket=${gcp_bucket:-cloudflux-gcp-bucket}
else
    gcp_project=""
    gcp_creds=""
    gcp_bucket="cloudflux-gcp-bucket"
fi
echo ""

# Generate JWT secret
echo -e "${BLUE}🔐 Generating JWT Secret Key...${NC}"
jwt_secret=$(openssl rand -hex 32)
echo "JWT Secret generated ✅"
echo ""

# Create .env file
echo -e "${BLUE}📝 Creating .env file...${NC}"
cat > .env << EOF
# CloudFlux AI - Environment Configuration
# Generated on $(date)

# ====================================
# DATABASE CONFIGURATION
# ====================================
DATABASE_URL=sqlite:///./cloudflux.db

# ====================================
# AWS CREDENTIALS
# ====================================
AWS_ACCESS_KEY_ID=$aws_key
AWS_SECRET_ACCESS_KEY=$aws_secret
AWS_REGION=$aws_region
AWS_S3_BUCKET=$aws_bucket

# ====================================
# AZURE CREDENTIALS
# ====================================
AZURE_STORAGE_ACCOUNT_NAME=$azure_account
AZURE_STORAGE_ACCOUNT_KEY=$azure_key
AZURE_CONTAINER_NAME=$azure_container

# ====================================
# GCP CREDENTIALS
# ====================================
GOOGLE_APPLICATION_CREDENTIALS=$gcp_creds
GCP_PROJECT_ID=$gcp_project
GCP_BUCKET_NAME=$gcp_bucket

# ====================================
# JWT AUTHENTICATION
# ====================================
JWT_SECRET_KEY=$jwt_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# ====================================
# APPLICATION SETTINGS
# ====================================
APP_ENV=development
DEBUG=True
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# ====================================
# DEMO MODE
# ====================================
DEMO_MODE=False
USE_MOCK_DATA=False
EOF

echo -e "${GREEN}✅ .env file created successfully!${NC}"
echo ""

# Install dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
read -p "Install cloud provider SDKs? (y/n): " install_deps
if [ "$install_deps" = "y" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "Creating virtual environment..."
        python -m venv venv
        source venv/bin/activate
    fi
    
    pip install --upgrade pip
    pip install fastapi==0.121.0 uvicorn==0.38.0 pydantic==2.12.0 pydantic-settings==2.5.2
    
    if [ ! -z "$aws_key" ]; then
        echo "Installing boto3 (AWS SDK)..."
        pip install boto3==1.34.144
    fi
    
    if [ ! -z "$azure_account" ]; then
        echo "Installing azure-storage-blob (Azure SDK)..."
        pip install azure-storage-blob==12.19.0
    fi
    
    if [ ! -z "$gcp_project" ]; then
        echo "Installing google-cloud-storage (GCP SDK)..."
        pip install google-cloud-storage==2.14.0
    fi
    
    echo -e "${GREEN}✅ Dependencies installed!${NC}"
fi
echo ""

# Create buckets/containers
echo -e "${BLUE}🪣 Cloud Storage Setup${NC}"
echo ""
echo "You'll need to create storage buckets/containers manually:"
echo ""

if [ ! -z "$aws_key" ]; then
    echo "AWS S3 Bucket:"
    echo "  aws s3 mb s3://$aws_bucket --region $aws_region"
    echo "  Or create at: https://console.aws.amazon.com/s3/"
    echo ""
fi

if [ ! -z "$azure_account" ]; then
    echo "Azure Container:"
    echo "  az storage container create --name $azure_container --account-name $azure_account"
    echo "  Or create at: https://portal.azure.com/"
    echo ""
fi

if [ ! -z "$gcp_project" ]; then
    echo "GCP Bucket:"
    echo "  gsutil mb gs://$gcp_bucket"
    echo "  Or create at: https://console.cloud.google.com/storage/"
    echo ""
fi

# Summary
echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Create storage buckets/containers (see commands above)"
echo "  2. Start backend: uvicorn simple_app:app --reload"
echo "  3. Test connection: curl http://localhost:8000/api/cloud/status"
echo ""
echo "Configuration saved to: .env"
echo "Backup saved to: .env.backup (if existed)"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Never commit .env to git!${NC}"
echo "The .env file is already in .gitignore"
echo ""
echo "Happy hacking! 🚀"
