#!/bin/bash

# CloudFlux AI - Docker-based Quick Start
# This avoids Python version compatibility issues by using Docker

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     CloudFlux AI - Docker Quick Start                     ║"
echo "║  Intelligent Multi-Cloud Data Orchestration Platform     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "📂 Project root: $PROJECT_ROOT"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

echo "✓ Docker: $(docker --version | cut -d ' ' -f 3)"
echo "✓ Docker Compose: $(docker-compose --version | cut -d ' ' -f 4)"
echo ""

# Step 1: Start infrastructure
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1/4: Starting Infrastructure Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_ROOT/infrastructure/docker"

# Stop any existing containers
docker-compose down 2>/dev/null || true

echo "Starting services (Zookeeper, Kafka, Redis, PostgreSQL, Backend)..."
docker-compose up -d

echo "Waiting for services to initialize (30 seconds)..."
sleep 30

# Check if backend is healthy
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2/4: Verifying Backend API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend API is healthy at http://localhost:8000"
        break
    fi
    sleep 2
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend API not responding, checking logs..."
        docker-compose logs backend | tail -20
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3/4: Generating Demo Data"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Creating 100 sample data objects..."
curl -s -X POST "http://localhost:8000/api/data/objects/batch-create?count=100" > /dev/null 2>&1 || echo "⚠️  Demo data creation skipped (backend may still be starting)"

echo "Training ML model..."
curl -s -X POST "http://localhost:8000/api/ml/train" > /dev/null 2>&1 || echo "⚠️  ML training skipped"

echo "✅ Demo data setup complete"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4/4: Frontend Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_ROOT/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
    echo "✅ Frontend dependencies installed"
else
    echo "✅ Frontend dependencies already installed"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                   🎉 SETUP COMPLETE! 🎉                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Services Running:"
echo "  🎨 Frontend:       Ready to start"
echo "  🌐 Backend API:    http://localhost:8000"
echo "  📖 API Docs:       http://localhost:8000/docs"
echo "  ⚡ Kafka:          localhost:9092"
echo "  🗄️  PostgreSQL:    localhost:5432"
echo "  💾 Redis:          localhost:6379"
echo ""
echo "🚀 Start the Frontend:"
echo ""
echo "  cd $PROJECT_ROOT/frontend"
echo "  npm start"
echo ""
echo "  Then open: http://localhost:3000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🛠️  Management Commands:"
echo ""
echo "  View backend logs:"
echo "    docker-compose -f infrastructure/docker/docker-compose.yml logs backend"
echo ""
echo "  Stop all services:"
echo "    docker-compose -f infrastructure/docker/docker-compose.yml down"
echo ""
echo "  Restart backend:"
echo "    docker-compose -f infrastructure/docker/docker-compose.yml restart backend"
echo ""
echo "✨ Ready to demo! Good luck! 🏆"
echo ""
