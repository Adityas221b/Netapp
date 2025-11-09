#!/bin/bash

# Quick test script for CloudFlux AI

set -e

echo "======================================"
echo "CloudFlux AI - Quick Test"
echo "======================================"
echo ""

BASE_URL="http://localhost:8000"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

test_passed=0
test_failed=0

# Test function
test_endpoint() {
    endpoint=$1
    description=$2
    
    echo -n "Testing: $description... "
    
    if curl -s -f "$BASE_URL$endpoint" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((test_passed++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((test_failed++))
    fi
}

# Run tests
echo "Running API tests..."
echo ""

test_endpoint "/health" "Health check"
test_endpoint "/" "Root endpoint"
test_endpoint "/api/data/objects" "List data objects"
test_endpoint "/api/data/tiers/distribution" "Tier distribution"
test_endpoint "/api/analytics/overview" "Analytics overview"
test_endpoint "/api/analytics/costs" "Cost breakdown"
test_endpoint "/api/ml/model-info" "ML model info"
test_endpoint "/api/migration/jobs" "Migration jobs"

echo ""
echo "======================================"
echo "Test Results"
echo "======================================"
echo -e "${GREEN}Passed: $test_passed${NC}"
echo -e "${RED}Failed: $test_failed${NC}"
echo ""

if [ $test_failed -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed. Check if services are running."
    exit 1
fi
