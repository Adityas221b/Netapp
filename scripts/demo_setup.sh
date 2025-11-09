#!/bin/bash

# CloudFlux AI - Complete Demo Setup Script
# Sets up the entire platform for demonstration

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     CloudFlux AI - Complete Platform Demo Setup          ║"
echo "║  Intelligent Multi-Cloud Data Orchestration Platform     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}📂 Project root: $PROJECT_ROOT${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 1/6: Checking Prerequisites${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker: $(docker --version)${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose: $(docker-compose --version)${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python: $(python3 --version)${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js: $(node --version)${NC}"
echo -e "${GREEN}✓ npm: $(npm --version)${NC}"

echo ""

# Step 2: Start Infrastructure
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 2/6: Starting Infrastructure Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$PROJECT_ROOT/infrastructure/docker"
echo "Starting Zookeeper, Kafka, Redis, PostgreSQL..."
docker-compose up -d zookeeper kafka redis postgres

echo "Waiting 15 seconds for services to initialize..."
sleep 15

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Infrastructure services started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start infrastructure services${NC}"
    exit 1
fi

echo ""

# Step 3: Install Backend Dependencies
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 3/6: Installing Backend Dependencies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$PROJECT_ROOT/backend"
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing Python packages..."
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install backend dependencies${NC}"
    exit 1
fi

echo ""

# Step 4: Install Frontend Dependencies
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 4/6: Installing Frontend Dependencies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$PROJECT_ROOT/frontend"
if [ ! -d "node_modules" ]; then
    echo "Installing npm packages..."
    npm install
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    else
        echo -e "${RED}❌ Failed to install frontend dependencies${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi

echo ""

# Step 5: Start Backend
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 5/6: Starting Backend API Server${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$PROJECT_ROOT/backend"
source venv/bin/activate

# Start backend in background
echo "Starting FastAPI backend..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

# Wait for backend to start
echo "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend API is running at http://localhost:8000${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start${NC}"
        exit 1
    fi
done

echo ""

# Step 6: Generate Demo Data
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 6/6: Generating Demo Data${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo "Creating 100 sample data objects..."
curl -s -X POST "http://localhost:8000/api/data/objects/batch-create?count=100" > /dev/null

echo "Training ML model with synthetic data..."
curl -s -X POST "http://localhost:8000/api/ml/train" > /dev/null

sleep 2
echo -e "${GREEN}✓ Demo data generated successfully${NC}"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Platform Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}📊 Access Points:${NC}"
echo ""
echo -e "  🎨 Frontend Dashboard:  ${GREEN}http://localhost:3000${NC}"
echo -e "  🌐 Backend API:         ${GREEN}http://localhost:8000${NC}"
echo -e "  📖 API Documentation:   ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  📚 ReDoc:              ${GREEN}http://localhost:8000/redoc${NC}"
echo ""

echo -e "${YELLOW}🚀 Next Steps:${NC}"
echo ""
echo "  1. Start the frontend:"
echo -e "     ${BLUE}cd $PROJECT_ROOT/frontend && npm start${NC}"
echo ""
echo "  2. Open your browser to: ${GREEN}http://localhost:3000${NC}"
echo ""
echo "  3. Explore the platform:"
echo "     • Dashboard - View metrics and charts"
echo "     • Migration Monitor - Create and track migrations"
echo "     • ML Insights - View AI predictions"
echo ""

echo -e "${YELLOW}🛠️  Management Commands:${NC}"
echo ""
echo "  • Stop backend:  kill \$(cat $PROJECT_ROOT/backend/backend.pid)"
echo "  • View logs:     tail -f $PROJECT_ROOT/backend/backend.log"
echo "  • Stop services: cd infrastructure/docker && docker-compose down"
echo ""

echo -e "${YELLOW}📝 Demo Workflow:${NC}"
echo ""
echo "  1. Open dashboard - see 100 objects distributed across tiers"
echo "  2. Check cost savings - view potential monthly savings"
echo "  3. Go to ML Insights - see optimization recommendations"
echo "  4. Create migration - simulate cloud data transfer"
echo "  5. Monitor progress - watch real-time updates"
echo ""

echo -e "${GREEN}Happy Hacking! 🎉${NC}"
echo ""

# Save important info
cat > "$PROJECT_ROOT/DEMO_INFO.txt" << EOF
CloudFlux AI - Demo Session Information
Generated: $(date)

Services Running:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Zookeeper:   localhost:2181
✓ Kafka:       localhost:9092
✓ Redis:       localhost:6379
✓ PostgreSQL:  localhost:5432
✓ Backend API: http://localhost:8000
✓ Frontend:    http://localhost:3000 (start with npm start)

Backend PID: $BACKEND_PID
Backend Logs: $PROJECT_ROOT/backend/backend.log

Demo Data:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 100 sample data objects created
✓ ML model trained with synthetic data
✓ Ready for demonstration

Quick Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Start Frontend:
  cd $PROJECT_ROOT/frontend && npm start

Stop Backend:
  kill $BACKEND_PID

Stop All Services:
  cd $PROJECT_ROOT/infrastructure/docker && docker-compose down

Restart Backend:
  cd $PROJECT_ROOT/backend
  source venv/bin/activate
  uvicorn app.main:app --reload

Test API:
  cd $PROJECT_ROOT/scripts && ./test_api.sh

API Endpoints:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Health:        GET  /health
Data Objects:  GET  /api/data/objects
Analytics:     GET  /api/analytics/overview
Costs:         GET  /api/analytics/costs
Migrations:    GET  /api/migration/jobs
ML Predict:    POST /api/ml/predict/{file_id}
Train Model:   POST /api/ml/train

Troubleshooting:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Check backend logs: tail -f $PROJECT_ROOT/backend/backend.log
• Check service status: cd infrastructure/docker && docker-compose ps
• Verify API health: curl http://localhost:8000/health
• Frontend issues: Check browser console (F12)

EOF

echo -e "${GREEN}✓ Demo info saved to: DEMO_INFO.txt${NC}"
