# CloudFlux AI - Frontend

Modern React-based dashboard for CloudFlux AI's intelligent multi-cloud data orchestration platform.

## Features

- **Real-time Dashboard**: Live metrics, cost analysis, and tier distribution visualization
- **Migration Monitor**: Track and manage multi-cloud data migrations with progress monitoring
- **ML Insights**: AI-powered predictions and optimization recommendations
- **Interactive Charts**: Beautiful visualizations using Recharts
- **Material-UI Design**: Modern, responsive UI with Material Design components
- **Auto-refresh**: Real-time data updates every 5-30 seconds

## Technology Stack

- React 18.2
- Material-UI (MUI) 5.14
- Recharts 2.10 (charting library)
- React Router 6.20 (navigation)
- Axios (API client)
- Socket.io (WebSocket support)

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm start
```

The app will open at http://localhost:3000 with hot-reload enabled.

### Build for Production

```bash
npm run build
```

Creates optimized production build in `build/` directory.

### Docker

```bash
docker build -t cloudflux-frontend .
docker run -p 3000:3000 cloudflux-frontend
```

## Project Structure

```
frontend/
├── public/
│   └── index.html              # HTML template
├── src/
│   ├── components/
│   │   ├── Dashboard.js        # Main dashboard with metrics
│   │   ├── MigrationMonitor.js # Migration job tracking
│   │   ├── MLInsights.js       # ML predictions & recommendations
│   │   ├── TierDistributionChart.js   # Pie chart for tier distribution
│   │   ├── CostBreakdownChart.js      # Bar chart for cost analysis
│   │   └── TrendsChart.js      # Line chart for historical trends
│   ├── services/
│   │   └── api.js              # API client with all endpoints
│   ├── App.js                  # Main app with routing & layout
│   ├── index.js                # React entry point
│   └── index.css               # Global styles
├── package.json
├── Dockerfile
└── .env                        # Environment configuration
```

## Environment Variables

Create a `.env` file:

```
REACT_APP_API_URL=http://localhost:8000
```

## Components

### Dashboard
- **Overview Cards**: Total objects, costs, savings, performance
- **Tier Distribution**: Pie chart showing HOT/WARM/COLD breakdown
- **Cost Breakdown**: Bar chart comparing current vs optimized costs
- **Historical Trends**: Line chart with 7-day data history
- **Migration Stats**: Active job counts and status

### Migration Monitor
- **Job Table**: Real-time migration job tracking with progress bars
- **Create Job**: Dialog for starting new migrations
- **Job Management**: Cancel in-progress jobs
- **Auto-refresh**: Updates every 5 seconds

### ML Insights
- **Model Status**: Training info and accuracy metrics
- **Recommendations**: List of tier optimization suggestions
- **Confidence Scores**: Visual indicators for prediction confidence
- **Train Model**: Manual model training trigger

## API Integration

The frontend connects to backend endpoints:

```javascript
// Data Management
GET  /api/data/objects
POST /api/data/objects
GET  /api/data/tiers/distribution

// Analytics
GET  /api/analytics/overview
GET  /api/analytics/costs
GET  /api/analytics/performance
GET  /api/analytics/trends

// Migration
GET  /api/migration/jobs
POST /api/migration/jobs
DELETE /api/migration/jobs/{id}

// ML
POST /api/ml/predict/{id}
POST /api/ml/train
GET  /api/ml/recommendations
```

## Customization

### Theme
Edit `src/App.js` to customize the Material-UI theme:

```javascript
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
});
```

### Auto-refresh Intervals
Update intervals in component `useEffect`:

```javascript
const interval = setInterval(loadData, 30000); // 30 seconds
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Lazy loading for components
- Optimized re-renders with React.memo
- API call batching
- Efficient chart rendering

## Troubleshooting

### CORS Issues
Ensure backend has CORS enabled for http://localhost:3000

### API Connection Failed
Check that `REACT_APP_API_URL` points to running backend

### Charts Not Rendering
Verify Recharts is installed: `npm install recharts`

## License

MIT License - See root LICENSE file
