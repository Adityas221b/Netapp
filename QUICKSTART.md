# 🚀 Quick Start Guide - Get Running in 5 Minutes

## Prerequisites Check

```bash
# Check if you have everything
docker --version          # Should be 20.10+
docker-compose --version  # Should be 2.0+
python3 --version        # Should be 3.11+
```

If any command fails, install the missing tool first.

---

## Step 1: Start the Platform (2 minutes)

```bash
# Navigate to project
cd /home/bitreaper/Desktop/Netapp/cloudflux-ai

# Run setup script
./scripts/setup.sh
```

This will:
- ✅ Create `.env` file
- ✅ Create directories
- ✅ Start all Docker services
- ✅ Check service health

**Wait for:** "Setup Complete! 🎉"

---

## Step 2: Verify Services (30 seconds)

```bash
# Check all services are running
cd infrastructure/docker
docker-compose ps

# Should show 6 services: zookeeper, kafka, redis, postgres, backend, frontend
```

**Expected output:** All services "Up" ✅

---

## Step 3: Test the API (1 minute)

```bash
# Run API tests
cd ../../scripts
./test_api.sh
```

**Expected:** All 8 tests pass ✅

---

## Step 4: Create Demo Data (1 minute)

```bash
# Create 100 sample data objects
curl -X POST "http://localhost:8000/api/data/objects/batch-create?count=100"

# View the data distribution
curl http://localhost:8000/api/data/tiers/distribution | jq
```

**Expected output:**
```json
{
  "count_by_tier": {
    "hot": 30,
    "warm": 45,
    "cold": 25
  },
  "total_objects": 100
}
```

---

## Step 5: Check Analytics (30 seconds)

```bash
# Get cost breakdown
curl http://localhost:8000/api/analytics/costs | jq

# Get potential savings
curl http://localhost:8000/api/analytics/savings | jq
```

**Look for:** `potential_monthly_savings` and `potential_annual_savings`

---

## 🎉 You're Ready!

### What's Working:
- ✅ All backend services
- ✅ Data classification
- ✅ ML predictions
- ✅ Cost analytics
- ✅ Migration APIs
- ✅ Kafka streaming

### Access Points:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Analytics:** http://localhost:8000/api/analytics/overview

---

## Quick Demo Commands

### Demo 1: Classification
```bash
# Create 100 files
curl -X POST "http://localhost:8000/api/data/objects/batch-create?count=100"

# View distribution
curl http://localhost:8000/api/data/tiers/distribution | jq

# Check costs
curl http://localhost:8000/api/analytics/costs | jq
```

### Demo 2: ML Predictions
```bash
# Train model
curl -X POST "http://localhost:8000/api/ml/train" | jq

# Get recommendations
curl http://localhost:8000/api/ml/recommendations | jq
```

### Demo 3: Kafka Streaming
```bash
# Terminal 1: Start producer
cd kafka/producers
python3 data_generator.py --rate 10

# Terminal 2: Start consumer
cd kafka/consumers
python3 classifier_consumer.py
```

### Demo 4: Migration
```bash
# Get a file ID
FILE_ID=$(curl -s http://localhost:8000/api/data/objects | jq -r '.[0].file_id')

# Estimate migration
curl -X POST "http://localhost:8000/api/migration/estimate" \
  -H "Content-Type: application/json" \
  -d "{\"file_id\":\"$FILE_ID\",\"dest_cloud\":\"gcp\",\"dest_tier\":\"cold\"}" | jq

# Create migration job
curl -X POST "http://localhost:8000/api/migration/jobs" \
  -H "Content-Type: application/json" \
  -d "{\"file_id\":\"$FILE_ID\",\"dest_cloud\":\"gcp\",\"dest_tier\":\"cold\"}" | jq
```

---

## Troubleshooting

### Services won't start?
```bash
cd infrastructure/docker
docker-compose down -v
docker-compose up -d --build
```

### Port already in use?
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :5432
sudo lsof -i :9092

# Kill the process or change port in docker-compose.yml
```

### Backend not responding?
```bash
# Check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Can't connect to Kafka?
```bash
# Check Kafka logs
docker-compose logs kafka

# Restart Kafka and Zookeeper
docker-compose restart zookeeper kafka
```

---

## Stop Everything

```bash
cd infrastructure/docker
docker-compose down

# To remove volumes too (clean slate):
docker-compose down -v
```

---

## Next Steps

1. ✅ Platform running
2. ✅ Demo data created
3. ✅ APIs tested
4. → Build React frontend
5. → Create Kubernetes manifests
6. → Prepare presentation

---

## Need Help?

- **API Documentation:** http://localhost:8000/docs
- **Check Logs:** `docker-compose logs -f [service]`
- **Health Status:** `curl http://localhost:8000/health`
- **Service Status:** `docker-compose ps`

---

**Time to complete: ~5 minutes**
**Result: Fully functional CloudFlux AI backend! 🎉**

**Now go explore the API docs and create amazing demos!** 🚀
