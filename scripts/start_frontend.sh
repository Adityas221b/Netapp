#!/bin/bash

# CloudFlux AI - Simple Start Script
# Run this from anywhere in the project

echo "🚀 Starting CloudFlux AI..."
echo ""

# Get to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "📂 Project: $PROJECT_ROOT"
echo ""

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend already running"
else
    echo "❌ Backend not running. Please run setup first:"
    echo "   cd $PROJECT_ROOT"
    echo "   bash scripts/minimal_start.sh"
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend..."
cd "$PROJECT_ROOT/frontend"
npm start
