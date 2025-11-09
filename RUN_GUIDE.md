# 🚀 CloudFlux AI - Complete Run Guide

## Prerequisites

Before running, ensure you have:
- Python 3.8+ installed
- Node.js 14+ and npm installed
- Git installed

---

## 📥 Step 1: Clone the Repository

```bash
git clone https://github.com/Adityas221b/Cloudflux1.git
cd Cloudflux1/cloudflux-ai
```

---

## 🐍 Step 2: Backend Setup

### 2.1 Navigate to Backend
```bash
cd backend
```

### 2.2 Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 2.3 Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 Setup Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use any text editor
```

**Required .env variables:**
```bash
# Database
DATABASE_URL=sqlite:///./cloudflux.db

# JWT Secret
SECRET_KEY=your-super-secret-key-change-this-in-production

# AWS Credentials (optional for full features)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1

# Azure Credentials (optional)
AZURE_STORAGE_CONNECTION_STRING=your-azure-connection

# GCP Credentials (optional)
GCP_PROJECT_ID=your-gcp-project
# Place gcp-credentials.json in backend folder if using GCP

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### 2.5 Initialize Database (Optional)
```bash
python init_database.py
```

### 2.6 Train ML Models (Optional - will auto-generate if missing)
```bash
python train_ml_model.py
```

### 2.7 Run Backend Server
```bash
# Method 1: Using uvicorn directly (RECOMMENDED)
uvicorn unified_app:app --host 0.0.0.0 --port 8000 --reload

# Method 2: Using Python directly
python unified_app.py

# Method 3: Using system Python and specific path
/usr/bin/python3 unified_app.py
```

**Backend will start at:** `http://localhost:8000`

---

## ⚛️ Step 3: Frontend Setup (New Terminal)

### 3.1 Navigate to Frontend (open NEW terminal)
```bash
cd /path/to/Cloudflux1/cloudflux-ai/frontend
```

### 3.2 Install Node Dependencies
```bash
npm install
```

### 3.3 Setup Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env
```

**Frontend .env:**
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### 3.4 Run Frontend Development Server
```bash
npm start
```

**Frontend will start at:** `http://localhost:3000`

---

## 🎯 Step 4: Access the Application

### 4.1 Open Browser
```
http://localhost:3000
```

### 4.2 Login
- **Default Username:** `admin`
- **Default Password:** `admin123`

(Create account if these don't work - registration should be available)

---

## 🔥 Quick Start Commands (If Already Setup)

### Start Backend
```bash
# Terminal 1
cd /path/to/cloudflux-ai/backend
source venv/bin/activate  # if using venv
uvicorn unified_app:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend
```bash
# Terminal 2
cd /path/to/cloudflux-ai/frontend
npm start
```

---

## 🐳 Alternative: Using Docker (If Available)

### Build and Run with Docker Compose
```bash
cd /path/to/cloudflux-ai
docker-compose up --build
```

---

## 🛠️ Development Commands

### Backend

#### Run with auto-reload (development)
```bash
uvicorn unified_app:app --reload --host 0.0.0.0 --port 8000
```

#### Run tests
```bash
pytest tests/
```

#### Install new dependency
```bash
pip install package-name
pip freeze > requirements.txt
```

### Frontend

#### Run development server
```bash
npm start
```

#### Build for production
```bash
npm run build
```

#### Run tests
```bash
npm test
```

#### Install new dependency
```bash
npm install package-name
```

---

## 🐛 Troubleshooting

### Backend Issues

#### Port 8000 already in use
```bash
# Kill existing process
pkill -f "uvicorn"

# Or find and kill specific process
lsof -ti:8000 | xargs kill -9

# Then restart
uvicorn unified_app:app --reload
```

#### Module not found errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific missing module
pip install module-name
```

#### Database errors
```bash
# Delete and recreate database
rm cloudflux.db
python init_database.py
```

### Frontend Issues

#### Port 3000 already in use
```bash
# Kill existing process
pkill -f "node"

# Or use different port
PORT=3001 npm start
```

#### Module not found
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Build errors
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules
npm install
```

---

## 📊 Verify Everything is Running

### Check Backend Health
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "CloudFlux AI API",
  "version": "1.0",
  "status": "running"
}
```

### Check WebSocket Connection
```bash
curl http://localhost:8000/ws
```

### Check Frontend
Open browser: `http://localhost:3000`

---

## 🔄 Full Restart Process

If something goes wrong, restart everything:

```bash
# 1. Kill all processes
pkill -f "uvicorn"
pkill -f "node"

# 2. Start backend
cd /path/to/cloudflux-ai/backend
source venv/bin/activate
uvicorn unified_app:app --reload

# 3. Start frontend (new terminal)
cd /path/to/cloudflux-ai/frontend
npm start
```

---

## 📝 Environment-Specific Commands

### For Your Current Setup (Netapp folder)
```bash
# Backend
cd /home/bitreaper/Desktop/Netapp/cloudflux-ai/backend
source /home/bitreaper/Desktop/Netapp/.venv/bin/activate
uvicorn unified_app:app --host 0.0.0.0 --port 8000 --reload

# Frontend (new terminal)
cd /home/bitreaper/Desktop/Netapp/cloudflux-ai/frontend
npm start
```

---

## 🌟 Production Deployment

### Backend (Production)
```bash
# Install production dependencies
pip install -r requirements-production.txt

# Run with gunicorn (production server)
gunicorn unified_app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (Production)
```bash
# Build optimized production bundle
npm run build

# Serve with static server
npx serve -s build -l 3000
```

---

## 🎓 Features to Test After Running

1. **Login** - Test authentication
2. **Overview Dashboard** - View analytics and charts
3. **Placement Optimizer** - See HOT/WARM/COLD tier recommendations
4. **Migrations** - Create cloud-to-cloud transfer jobs
5. **ML Insights** - Generate predictions
6. **Real-Time Stream** - Watch live data events
7. **Alerts** - Configure policy triggers
8. **Cloud Storage** - View files across AWS/Azure/GCP

---

## 📞 Support

If you encounter issues:
1. Check terminal logs for error messages
2. Verify all dependencies are installed
3. Ensure ports 3000 and 8000 are free
4. Check .env files are configured correctly
5. Try the full restart process

---

## 🚀 Quick Reference Card

| Component | Command | URL |
|-----------|---------|-----|
| Backend | `uvicorn unified_app:app --reload` | http://localhost:8000 |
| Frontend | `npm start` | http://localhost:3000 |
| API Docs | - | http://localhost:8000/docs |
| Stop Backend | `pkill -f uvicorn` | - |
| Stop Frontend | `pkill -f node` or Ctrl+C | - |

---

**Happy Coding! 🎉**

For NetApp Hackathon: Make sure to test all features and have demo data ready!
