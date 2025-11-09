# 🎨 Frontend Quick Start Guide

## Prerequisites Check

```bash
# Check Node.js (need 18+)
node --version

# Check npm
npm --version

# If not installed, download from: https://nodejs.org/
```

## Installation

```bash
cd frontend
npm install
```

This installs:
- React 18.2
- Material-UI 5.14
- Recharts 2.10
- Axios, React Router, Socket.io

## Starting the Frontend

### Option 1: Using Start Script (Recommended)

```bash
./start.sh
```

The script will:
- ✅ Check Node.js installation
- ✅ Install dependencies if needed
- ✅ Verify backend is running
- ✅ Start development server

### Option 2: Manual Start

```bash
npm start
```

## Accessing the Dashboard

Open your browser to: **http://localhost:3000**

You should see:
- 📊 Dashboard with metrics and charts
- 🔄 Migration Monitor (left sidebar)
- 🧠 ML Insights (left sidebar)

## Features Overview

### 1. Dashboard (/)
**What you'll see:**
- 4 metric cards: Total Objects, Monthly Cost, Potential Savings, Avg Latency
- Pie chart: Storage tier distribution (HOT/WARM/COLD)
- Bar chart: Cost breakdown (current vs optimized)
- Line chart: 7-day historical trends
- Migration activity stats

**Actions:**
- Click "Refresh" to update data
- Auto-refreshes every 30 seconds
- View real-time metrics

### 2. Migration Monitor (/migrations)
**What you'll see:**
- Table of all migration jobs
- Progress bars for active migrations
- Job details: source/target providers, tier, size, cost

**Actions:**
- Click "New Migration" to create a job
- Select source provider (AWS/AZURE/GCP)
- Select target provider
- Choose target tier (HOT/WARM/COLD)
- Set data size in GB
- Track progress in real-time
- Cancel in-progress jobs

### 3. ML Insights (/ml-insights)
**What you'll see:**
- Model status card: training info, accuracy
- Recommendations list: tier optimization suggestions
- Confidence scores for each prediction

**Actions:**
- Click "Train Model" to train with synthetic data
- View optimization recommendations
- See predicted access patterns
- Check potential savings per file

## Demo Workflow

### Step 1: Generate Test Data
```bash
# In backend terminal
curl -X POST http://localhost:8000/api/data/objects/batch-create?count=100
```

### Step 2: View Dashboard
- Go to http://localhost:3000
- See 100 objects distributed across tiers
- Check cost metrics

### Step 3: Train ML Model
- Navigate to "ML Insights"
- Click "Train Model"
- Wait 10-15 seconds
- View recommendations

### Step 4: Create Migration
- Navigate to "Migration Monitor"
- Click "New Migration"
- Fill in:
  - Source: AWS
  - Target: AZURE
  - Tier: WARM
  - Size: 50 GB
- Click "Create Job"
- Watch progress bar update

### Step 5: Monitor Real-time Updates
- Keep dashboard open
- Watch metrics update every 30 seconds
- See migration progress in real-time

## Configuration

### Change API URL
Edit `frontend/.env`:
```
REACT_APP_API_URL=http://your-backend-url:8000
```

### Change Auto-refresh Interval
Edit component files:
```javascript
// Dashboard.js - line ~50
const interval = setInterval(loadData, 30000); // 30 seconds

// MigrationMonitor.js - line ~40
const interval = setInterval(loadJobs, 5000); // 5 seconds
```

### Customize Theme
Edit `frontend/src/App.js`:
```javascript
const theme = createTheme({
  palette: {
    primary: { main: '#YOUR_COLOR' },
    secondary: { main: '#YOUR_COLOR' },
  },
});
```

## Troubleshooting

### Issue: "Backend API is not responding"
**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start backend
cd backend
uvicorn app.main:app --reload
```

### Issue: "CORS Error"
**Solution:** Backend should have CORS enabled for http://localhost:3000
Check `backend/app/main.py` has:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Charts Not Rendering
**Solution:**
```bash
# Reinstall recharts
npm install recharts
```

### Issue: "Port 3000 already in use"
**Solution:**
```bash
# Find process using port 3000
lsof -i :3000

# Kill it
kill -9 <PID>

# Or use different port
PORT=3001 npm start
```

### Issue: Blank Page
**Solution:**
1. Check browser console for errors (F12)
2. Clear browser cache
3. Rebuild: `rm -rf node_modules && npm install`

## Production Build

```bash
# Create optimized build
npm run build

# Serve with static server
npm install -g serve
serve -s build -p 3000
```

## Docker Deployment

```bash
# Build image
docker build -t cloudflux-frontend .

# Run container
docker run -p 3000:3000 \
  -e REACT_APP_API_URL=http://backend:8000 \
  cloudflux-frontend
```

## Development Tips

### Hot Reload
- Changes auto-refresh
- No need to restart server
- If not working, restart npm start

### Component Structure
```
Dashboard.js          → Main metrics view
MigrationMonitor.js   → Job tracking
MLInsights.js         → AI predictions
TierDistributionChart → Pie chart
CostBreakdownChart    → Bar chart
TrendsChart          → Line chart
```

### Adding New Pages
1. Create component in `src/components/`
2. Add route in `App.js`:
   ```javascript
   <Route path="/my-page" element={<MyComponent />} />
   ```
3. Add menu item in `App.js`:
   ```javascript
   { text: 'My Page', icon: <Icon />, path: '/my-page' }
   ```

### API Calls
Use service functions from `src/services/api.js`:
```javascript
import { dataAPI, analyticsAPI, migrationAPI, mlAPI } from '../services/api';

// Example
const response = await analyticsAPI.getOverview();
const data = response.data;
```

## Performance Tips

- Dashboard auto-refresh: 30s
- Migration monitor: 5s
- Disable auto-refresh if too many API calls
- Use React DevTools for component profiling

## Browser Support

✅ Chrome (recommended)
✅ Firefox
✅ Safari
✅ Edge

❌ IE11 (not supported)

## Next Steps

1. ✅ Start frontend
2. ✅ Generate test data
3. ✅ Explore dashboard
4. ✅ Create migrations
5. ✅ Train ML model
6. ✅ View recommendations
7. 🎯 Demo to judges!

## Support

- Documentation: `/frontend/README.md`
- Backend API Docs: http://localhost:8000/docs
- Issues: Check console (F12) for errors
