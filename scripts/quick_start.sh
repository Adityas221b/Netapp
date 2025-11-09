#!/bin/bash

# CloudFlux AI - Quick Fix for Python 3.13 Compatibility
# This script fixes the scikit-learn compatibility issue and starts the platform

set -e

echo "🔧 CloudFlux AI - Quick Fix & Start"
echo "===================================="
echo ""

cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "📍 Project root: $PROJECT_ROOT"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1-2)
echo "🐍 Python version: $PYTHON_VERSION"

# For Python 3.13, we need to use scikit-learn without compiling from source
if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "⚠️  Python 3.13 detected - using pre-built wheels"
    echo ""
fi

# Step 1: Backend setup
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1/3: Setting up Backend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_ROOT/backend"

# Remove old venv if exists
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

# Create new venv
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies without scikit-learn first
echo "Installing core dependencies..."
pip install --upgrade pip setuptools wheel -q

# Install packages one by one to avoid compilation issues
echo "Installing FastAPI and Uvicorn..."
pip install -q fastapi==0.104.1 uvicorn[standard]==0.24.0

echo "Installing Pydantic..."
pip install -q pydantic==2.5.0 pydantic-settings==2.1.0

echo "Installing data science libraries..."
pip install -q numpy==1.26.2 pandas==2.1.3

# For Python 3.13, install pre-built scikit-learn
echo "Installing scikit-learn (this may take a moment)..."
if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    # Use latest stable version with Python 3.13 support
    pip install -q scikit-learn
else
    pip install -q scikit-learn==1.4.2
fi

# Skip TensorFlow for Python 3.13 (not yet supported)
if [[ "$PYTHON_VERSION" != "3.13" ]]; then
    echo "Installing TensorFlow..."
    pip install -q tensorflow==2.15.0
else
    echo "⚠️  Skipping TensorFlow (not yet compatible with Python 3.13)"
fi

echo "Installing cloud SDKs..."
pip install -q boto3==1.34.0 azure-storage-blob==12.19.0 google-cloud-storage==2.13.0

echo "Installing other dependencies..."
pip install -q kafka-python==2.0.2 redis==5.0.1 psycopg2-binary==2.9.9 sqlalchemy==2.0.23 python-multipart==0.0.6

echo "✅ Backend dependencies installed"
echo ""

# Step 2: Start Backend
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2/3: Starting Backend API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Kill any existing backend process
if [ -f "backend.pid" ]; then
    OLD_PID=$(cat backend.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Stopping old backend process..."
        kill $OLD_PID 2>/dev/null || true
    fi
    rm backend.pid
fi

# Start backend in background
echo "Starting FastAPI server..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

# Wait for backend to start
echo "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend API running at http://localhost:8000"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start. Check backend.log for details"
        exit 1
    fi
done

echo ""

# Step 3: Frontend setup
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3/3: Frontend Instructions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "✅ Backend is ready!"
echo ""
echo "Now start the frontend in a new terminal:"
echo ""
echo "  cd $PROJECT_ROOT/frontend"
echo "  npm install"
echo "  npm start"
echo ""
echo "Or use this one-liner:"
echo "  cd $PROJECT_ROOT/frontend && npm install && npm start"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Services:"
echo "  Backend API:  http://localhost:8000"
echo "  API Docs:     http://localhost:8000/docs"
echo "  Frontend:     http://localhost:3000 (after npm start)"
echo ""
echo "🛠️  Management:"
echo "  Stop backend:  kill $BACKEND_PID"
echo "  View logs:     tail -f $PROJECT_ROOT/backend/backend.log"
echo ""
