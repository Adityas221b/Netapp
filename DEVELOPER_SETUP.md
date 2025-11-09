# 🚀 CloudFlux AI - Developer Setup Guide

## Quick Setup (10 minutes)

### Prerequisites
- Python 3.11+ 
- Node.js 16+
- npm or yarn
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/Adityas221b/Netapp.git
cd Netapp/cloudflux-ai
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Update .env with your credentials
nano .env  # Edit the placeholder values with your actual cloud credentials

# Start backend
uvicorn unified_app:app --host 0.0.0.0 --port 8000 --reload
```

✅ Backend running at `http://localhost:8000`

### Step 3: Frontend Setup

Open a **new terminal**:
```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm start
```

✅ Frontend running at `http://localhost:3000`

---

## ⚙️ Environment Configuration

### Required Cloud Credentials

#### AWS Setup
1. Go to AWS IAM Console
2. Create new IAM user (e.g., `cloudflux-api-user`)
3. Attach policy: `AmazonS3FullAccess`
4. Generate Access Key ID and Secret Access Key
5. Add to `.env`:
   ```
   AWS_ACCESS_KEY_ID=your_key_id
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   AWS_S3_BUCKET=your_bucket_name
   ```

#### Azure Setup
1. Go to Storage Account settings
2. Navigate to "Access Keys"
3. Copy Account Name and Account Key
4. Add to `.env`:
   ```
   AZURE_STORAGE_ACCOUNT_NAME=your_account
   AZURE_STORAGE_ACCOUNT_KEY=your_key
   AZURE_CONTAINER_NAME=your_container
   ```

#### GCP Setup
1. Go to GCP Console → Service Accounts
2. Create new service account
3. Generate JSON key file
4. Download and save as `gcp-credentials.json` in `backend/`
5. Add to `.env`:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json
   GCP_PROJECT_ID=your_project_id
   GCP_BUCKET_NAME=your_bucket_name
   ```

---

## 🧪 Testing the Setup

### Test Backend
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "cloud_providers": {
      "total_connected": 3
    }
  }
}
```

### Test API with Data
```bash
# Get authentication token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"

# Copy the access_token from response

# Fetch cloud objects
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/api/data/objects
```

### Test Frontend
Open http://localhost:3000 in your browser and verify:
- ✅ Dashboard loads without errors
- ✅ Cloud data displays (AWS, Azure, GCP objects)
- ✅ Charts and analytics render correctly
- ✅ Can view object details and metadata

---

## 📁 Project Structure

```
cloudflux-ai/
├── backend/
│   ├── app/                    # Main application code
│   │   ├── api/               # API endpoints
│   │   ├── services/          # Cloud service integration
│   │   ├── models.py          # Data models
│   │   └── main.py            # Core logic
│   ├── ml_models/             # Trained ML models
│   ├── unified_app.py         # FastAPI main app
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables (template)
│   └── gcp-credentials.json   # GCP service account (template)
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API client
│   │   └── App.js
│   ├── package.json           # npm dependencies
│   └── .env                   # Frontend config
└── infrastructure/            # Docker & Kubernetes files
```

---

## 🔧 Common Development Tasks

### Add New API Endpoint

**File:** `backend/app/api/custom.py`
```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/custom", tags=["custom"])

@router.get("/myendpoint")
async def my_endpoint():
    return {"message": "Hello from custom endpoint"}
```

**Register in:** `backend/unified_app.py`
```python
from app.api import custom
app.include_router(custom.router)
```

### Add New Frontend Component

**File:** `frontend/src/components/MyComponent.js`
```javascript
import React from 'react';

export default function MyComponent() {
  return (
    <div>
      <h1>My New Component</h1>
    </div>
  );
}
```

**Use in:** `frontend/src/components/Dashboard/index.js`
```javascript
import MyComponent from '../MyComponent';

// Inside Dashboard component:
<MyComponent />
```

### Update Dependencies

```bash
# Backend
pip install -r requirements.txt
pip install --upgrade package_name

# Frontend
npm install
npm update package_name
```

---

## 🐛 Debugging

### Backend Debug Mode
```bash
# Set debug environment
export DEBUG=True
uvicorn unified_app:app --reload --log-level debug
```

### Frontend Debug
```bash
# Check browser console (F12)
# Check React DevTools extension
# Check network tab for API calls
```

### View Logs

**Backend:**
```bash
tail -f /tmp/backend.log  # Or check stdout
```

**Frontend:**
```bash
# Check browser console
# Or check npm output
```

---

## 📦 Production Deployment

### Using Docker

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Kubernetes

```bash
# Apply configurations
kubectl apply -f infrastructure/kubernetes/

# Check deployment
kubectl get pods -n cloudflux

# View logs
kubectl logs -n cloudflux deployment/backend

# Scale deployment
kubectl scale deployment backend --replicas=3 -n cloudflux
```

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] All API keys removed from code
- [ ] Environment variables properly configured
- [ ] JWT_SECRET_KEY changed to a strong random value
- [ ] HTTPS/SSL enabled for all endpoints
- [ ] CORS configured appropriately
- [ ] Database credentials secured
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] Audit logging enabled
- [ ] Regular backups scheduled

---

## 📚 Useful Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/
- **AWS SDK (boto3):** https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- **Azure SDK:** https://learn.microsoft.com/en-us/python/api/overview/azure/storage
- **GCP Client Library:** https://cloud.google.com/python/docs/reference

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check port 8000 is available
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Retry
uvicorn unified_app:app --port 8000
```

### Frontend blank/errors
```bash
# Clear cache
npm cache clean --force

# Reinstall
rm -rf node_modules package-lock.json
npm install

# Check backend health
curl http://localhost:8000/health
```

### Cloud connection fails
```bash
# Test AWS credentials
aws s3 ls --profile default

# Test Azure
az storage blob list --account-name your_account --container-name your_container

# Test GCP
gcloud auth activate-service-account --key-file=gcp-credentials.json
gsutil ls gs://your_bucket
```

---

## 💡 Pro Tips

1. **Use `.env.local`** for development - never commit sensitive data
2. **Enable auto-format** in your IDE (Prettier for JS, black for Python)
3. **Use git hooks** to prevent committing secrets
4. **Keep dependencies updated** for security patches
5. **Write tests** for new features (run with `pytest` and `npm test`)
6. **Use logging** instead of print statements
7. **Profile performance** with `locust` or similar tools
8. **Monitor in production** with health checks and alerts

---

## 🎯 Next Steps

1. Complete the setup guide above
2. Run the health check test
3. Load some sample data
4. Explore the API documentation at `/docs`
5. Test the frontend dashboard
6. Read the `IMPLEMENTATION_GUIDE.md` for full documentation

---

**Happy coding!** 🚀
