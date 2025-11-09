#!/bin/bash

# CloudFlux AI Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "======================================"
echo "CloudFlux AI - Setup Script"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "${YELLOW}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi
echo "${GREEN}✅ Docker found${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "${YELLOW}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi
echo "${GREEN}✅ Docker Compose found${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "${YELLOW}⚠️  Python 3 not found. Some scripts may not work.${NC}"
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"
fi

echo ""
echo "Setting up CloudFlux AI..."
echo ""

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "Creating .env file..."
    cp backend/.env.example backend/.env
    echo "${GREEN}✅ Created .env file${NC}"
else
    echo "${YELLOW}⚠️  .env file already exists${NC}"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p ml/models
mkdir -p ml/data
mkdir -p backend/logs
echo "${GREEN}✅ Directories created${NC}"

# Navigate to docker directory
cd infrastructure/docker

echo ""
echo "======================================"
echo "Starting Docker services..."
echo "======================================"
echo ""

# Start services
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U cloudflux &> /dev/null; then
    echo "${GREEN}✅ PostgreSQL is ready${NC}"
else
    echo "${YELLOW}⚠️  PostgreSQL is not ready yet${NC}"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping &> /dev/null; then
    echo "${GREEN}✅ Redis is ready${NC}"
else
    echo "${YELLOW}⚠️  Redis is not ready yet${NC}"
fi

# Check Backend
if curl -s http://localhost:8000/health &> /dev/null; then
    echo "${GREEN}✅ Backend API is ready${NC}"
else
    echo "${YELLOW}⚠️  Backend API is not ready yet (may need more time)${NC}"
fi

echo ""
echo "======================================"
echo "Setup Complete! 🎉"
echo "======================================"
echo ""
echo "Services available at:"
echo "  🌐 API:          http://localhost:8000"
echo "  📊 API Docs:     http://localhost:8000/docs"
echo "  🎨 Dashboard:    http://localhost:3000 (when frontend is ready)"
echo "  🗄️  PostgreSQL:  localhost:5432"
echo "  💾 Redis:        localhost:6379"
echo "  ⚡ Kafka:        localhost:9092"
echo ""
echo "Useful commands:"
echo "  View logs:       docker-compose logs -f"
echo "  Stop services:   docker-compose down"
echo "  Restart:         docker-compose restart"
echo ""
echo "Next steps:"
echo "  1. Visit http://localhost:8000/docs to explore the API"
echo "  2. Create demo data: curl -X POST http://localhost:8000/api/data/objects/batch-create?count=100"
echo "  3. Check analytics: curl http://localhost:8000/api/analytics/overview"
echo ""
echo "Happy hacking! 🚀"
