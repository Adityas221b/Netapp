#!/bin/bash

# CloudFlux AI - Frontend Start Script
# Automatically installs dependencies and starts the React development server

set -e

echo "🚀 CloudFlux AI - Frontend Startup"
echo "=================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "   Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js version: $(node --version)"
echo "✓ npm version: $(npm --version)"

# Navigate to frontend directory
cd "$(dirname "$0")"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo ""
    echo "📦 Installing dependencies..."
    npm install
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

# Check if backend is running
echo ""
echo "🔍 Checking backend API..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend API is running at http://localhost:8000"
else
    echo "⚠️  Warning: Backend API is not responding"
    echo "   Please start the backend first:"
    echo "   cd ../backend && uvicorn app.main:app --reload"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start development server
echo ""
echo "🌐 Starting React development server..."
echo "   Frontend will be available at: http://localhost:3000"
echo "   Press Ctrl+C to stop"
echo ""

npm start
