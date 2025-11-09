import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  Alert,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  TrendingUp as OptimizeIcon,
  AttachMoney as MoneyIcon,
  Speed as SpeedIcon,
  CloudQueue as CloudIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  ArrowForward as ArrowIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import './PlacementOptimizer.css';

const PlacementOptimizer = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [tierDistribution, setTierDistribution] = useState(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    totalRecommendations: 0,
    totalMonthlySavings: 0,
    totalAnnualSavings: 0
  });

  // Load recommendations
  const loadRecommendations = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      // Get recommendations
      const recResponse = await fetch('http://localhost:8000/api/placement/recommendations', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const recData = await recResponse.json();
      
      setRecommendations(recData.recommendations || []);
      setStats({
        totalRecommendations: recData.total_recommendations || 0,
        totalMonthlySavings: recData.total_monthly_savings || 0,
        totalAnnualSavings: recData.total_annual_savings || 0
      });
      
      // Get tier distribution
      const distResponse = await fetch('http://localhost:8000/api/placement/tier-distribution', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const distData = await distResponse.json();
      
      setTierDistribution(distData);
      
    } catch (error) {
      console.error('Failed to load placement data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecommendations();
  }, []);

  // Get tier color
  const getTierColor = (tier) => {
    const colors = {
      'HOT': '#ff6b6b',
      'WARM': '#feca57',
      'COLD': '#48dbfb',
      'ARCHIVE': '#9b59b6'
    };
    return colors[tier] || '#95a5a6';
  };

  // Get priority color
  const getPriorityColor = (priority) => {
    const colors = {
      'HIGH': 'error',
      'MEDIUM': 'warning',
      'LOW': 'info'
    };
    return colors[priority] || 'default';
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            🎯 Data Placement Optimizer
          </Typography>
          <Typography variant="body2" color="textSecondary">
            AI-powered recommendations with temperature-based tiering
          </Typography>
        </Box>
        
        <Button
          variant="contained"
          color="primary"
          startIcon={<RefreshIcon />}
          onClick={loadRecommendations}
          disabled={loading}
        >
          Refresh Analysis
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Optimization Opportunities
                  </Typography>
                  <Typography variant="h3" sx={{ mt: 1 }}>
                    {stats.totalRecommendations}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.8 }}>
                    Files can be optimized
                  </Typography>
                </Box>
                <OptimizeIcon sx={{ fontSize: 50, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Monthly Savings
                  </Typography>
                  <Typography variant="h3" sx={{ mt: 1 }}>
                    ${stats.totalMonthlySavings.toFixed(2)}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.8 }}>
                    Potential cost reduction
                  </Typography>
                </Box>
                <MoneyIcon sx={{ fontSize: 50, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Annual Savings
                  </Typography>
                  <Typography variant="h3" sx={{ mt: 1 }}>
                    ${stats.totalAnnualSavings.toFixed(2)}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.8 }}>
                    Yearly cost optimization
                  </Typography>
                </Box>
                <SpeedIcon sx={{ fontSize: 50, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Temperature Classification */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          🌡️ Temperature-Based Classification
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <Card sx={{ border: '2px solid #ff6b6b', background: 'rgba(255, 107, 107, 0.1)' }}>
              <CardContent>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h2">🔥</Typography>
                  <Typography variant="h5" sx={{ color: '#ff6b6b', fontWeight: 'bold' }}>
                    HOT
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1, mb: 2 }}>
                    Frequently accessed data<br />
                    (&lt;7 days, &lt;1GB)
                  </Typography>
                  <Chip label="Premium Storage" size="small" sx={{ bgcolor: '#ff6b6b', color: 'white' }} />
                  {tierDistribution && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" color="textSecondary">
                        {tierDistribution.distribution.HOT.count} files
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {tierDistribution.distribution.HOT.size_gb} GB
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        ${tierDistribution.distribution.HOT.cost_monthly}/mo
                      </Typography>
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card sx={{ border: '2px solid #feca57', background: 'rgba(254, 202, 87, 0.1)' }}>
              <CardContent>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h2">☀️</Typography>
                  <Typography variant="h5" sx={{ color: '#feca57', fontWeight: 'bold' }}>
                    WARM
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1, mb: 2 }}>
                    Moderately accessed<br />
                    (&lt;30 days, &lt;10GB)
                  </Typography>
                  <Chip label="Standard Storage" size="small" sx={{ bgcolor: '#feca57', color: 'white' }} />
                  {tierDistribution && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" color="textSecondary">
                        {tierDistribution.distribution.WARM.count} files
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {tierDistribution.distribution.WARM.size_gb} GB
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        ${tierDistribution.distribution.WARM.cost_monthly}/mo
                      </Typography>
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card sx={{ border: '2px solid #48dbfb', background: 'rgba(72, 219, 251, 0.1)' }}>
              <CardContent>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h2">❄️</Typography>
                  <Typography variant="h5" sx={{ color: '#48dbfb', fontWeight: 'bold' }}>
                    COLD
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1, mb: 2 }}>
                    Rarely accessed<br />
                    (&gt;30 days, &gt;10GB)
                  </Typography>
                  <Chip label="Archive Storage" size="small" sx={{ bgcolor: '#48dbfb', color: 'white' }} />
                  {tierDistribution && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" color="textSecondary">
                        {tierDistribution.distribution.COLD.count} files
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {tierDistribution.distribution.COLD.size_gb} GB
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        ${tierDistribution.distribution.COLD.cost_monthly}/mo
                      </Typography>
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card sx={{ border: '2px solid #9b59b6', background: 'rgba(155, 89, 182, 0.1)' }}>
              <CardContent>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h2">🗄️</Typography>
                  <Typography variant="h5" sx={{ color: '#9b59b6', fontWeight: 'bold' }}>
                    ARCHIVE
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1, mb: 2 }}>
                    Long-term storage<br />
                    (Compliance, backup)
                  </Typography>
                  <Chip label="Deep Archive" size="small" sx={{ bgcolor: '#9b59b6', color: 'white' }} />
                  {tierDistribution && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" color="textSecondary">
                        {tierDistribution.distribution.ARCHIVE.count} files
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {tierDistribution.distribution.ARCHIVE.size_gb} GB
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        ${tierDistribution.distribution.ARCHIVE.cost_monthly}/mo
                      </Typography>
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* Recommendations Table */}
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            💡 Optimization Recommendations
          </Typography>
          <Chip 
            label={`${recommendations.length} opportunities`} 
            color="primary" 
            size="small"
          />
        </Box>
        
        <Divider sx={{ mb: 2 }} />

        {loading ? (
          <Box sx={{ py: 3 }}>
            <LinearProgress />
            <Typography variant="body2" color="textSecondary" sx={{ mt: 2, textAlign: 'center' }}>
              Analyzing your cloud data...
            </Typography>
          </Box>
        ) : recommendations.length === 0 ? (
          <Alert severity="success" icon={<CheckIcon />}>
            🎉 Excellent! All your data is optimally placed. No recommendations at this time.
          </Alert>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>File Name</strong></TableCell>
                  <TableCell><strong>Provider</strong></TableCell>
                  <TableCell><strong>Current → Recommended</strong></TableCell>
                  <TableCell><strong>Temperature</strong></TableCell>
                  <TableCell><strong>Monthly Savings</strong></TableCell>
                  <TableCell><strong>Priority</strong></TableCell>
                  <TableCell><strong>Action</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recommendations.map((rec, index) => (
                  <TableRow key={index} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CloudIcon fontSize="small" color="primary" />
                        <Typography variant="body2">{rec.file_name}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip label={rec.provider} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip 
                          label={rec.current_tier} 
                          size="small" 
                          sx={{ 
                            bgcolor: getTierColor(rec.current_tier),
                            color: 'white',
                            fontWeight: 'bold'
                          }}
                        />
                        <ArrowIcon fontSize="small" />
                        <Chip 
                          label={rec.recommended_tier} 
                          size="small" 
                          sx={{ 
                            bgcolor: getTierColor(rec.recommended_tier),
                            color: 'white',
                            fontWeight: 'bold'
                          }}
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={rec.data_temperature} 
                        size="small"
                        sx={{ 
                          bgcolor: getTierColor(rec.data_temperature),
                          color: 'white'
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold" color="success.main">
                        ${rec.monthly_savings}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        ${rec.annual_savings}/year
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={rec.priority} 
                        size="small" 
                        color={getPriorityColor(rec.priority)}
                      />
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Migrate to recommended tier">
                        <Button 
                          variant="contained" 
                          size="small" 
                          color="primary"
                          startIcon={<OptimizeIcon />}
                        >
                          Optimize
                        </Button>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Box>
  );
};

export default PlacementOptimizer;
