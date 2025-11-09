import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Badge,
  IconButton,
  Divider,
  Alert,
  LinearProgress
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  CloudDownload as DownloadIcon,
  TrendingUp as TrendingIcon,
  AttachMoney as MoneyIcon,
  Speed as SpeedIcon,
  Notifications as NotificationIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  CheckCircle as SuccessIcon
} from '@mui/icons-material';
import './RealTimeStream.css';

const RealTimeStream = () => {
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState({
    totalEvents: 0,
    activeConnections: 0,
    eventsPerSecond: 0
  });
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  
  const wsRef = useRef(null);
  const eventsRef = useRef([]);
  const maxEvents = 50; // Keep last 50 events

  // Connect to WebSocket
  const connectWebSocket = () => {
    try {
      const token = localStorage.getItem('token');
      const wsUrl = `ws://localhost:8000/ws/stream`;
      
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('✅ WebSocket connected');
        setIsConnected(true);
        setConnectionStatus('connected');
        setIsStreaming(true);
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'event') {
            // New event received
            const newEvent = message.data;
            eventsRef.current = [newEvent, ...eventsRef.current].slice(0, maxEvents);
            setEvents([...eventsRef.current]);
            
            // Update stats
            setStats(prev => ({
              ...prev,
              totalEvents: prev.totalEvents + 1
            }));
          } else if (message.type === 'heartbeat') {
            // Heartbeat - update connection count
            setStats(prev => ({
              ...prev,
              activeConnections: message.subscribers || 0
            }));
          } else if (message.type === 'connection') {
            console.log('📡 Connection established:', message.message);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      wsRef.current.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setConnectionStatus('error');
      };
      
      wsRef.current.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        setIsConnected(false);
        setConnectionStatus('disconnected');
        setIsStreaming(false);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnectionStatus('error');
    }
  };

  // Disconnect WebSocket
  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  // Toggle streaming
  const toggleStreaming = () => {
    if (isStreaming) {
      disconnectWebSocket();
    } else {
      connectWebSocket();
    }
  };

  // Simulate cloud activity
  const simulateActivity = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/stream/simulate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      console.log('✨ Simulation started:', data);
    } catch (error) {
      console.error('Failed to simulate activity:', error);
    }
  };

  // Load stream stats
  const loadStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/stream/stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      setStats({
        totalEvents: data.total_events_produced || 0,
        activeConnections: data.active_websocket_connections || 0,
        eventsPerSecond: 0
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  // Auto-connect on mount
  useEffect(() => {
    loadStats();
    connectWebSocket();
    
    return () => {
      disconnectWebSocket();
    };
  }, []);

  // Get event icon
  const getEventIcon = (eventType) => {
    if (eventType.includes('upload')) return <UploadIcon color="primary" />;
    if (eventType.includes('download')) return <DownloadIcon color="info" />;
    if (eventType.includes('cost')) return <MoneyIcon color="success" />;
    if (eventType.includes('access')) return <SpeedIcon color="warning" />;
    if (eventType.includes('migration')) return <TrendingIcon color="secondary" />;
    return <NotificationIcon />;
  };

  // Get event color
  const getEventColor = (eventType) => {
    if (eventType.includes('cost')) return 'success';
    if (eventType.includes('alert')) return 'error';
    if (eventType.includes('migration')) return 'info';
    if (eventType.includes('access')) return 'warning';
    return 'default';
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            🌊 Real-time Data Streaming
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Live cloud operations with Kafka-like event streaming
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            color={isStreaming ? "error" : "primary"}
            startIcon={isStreaming ? <PauseIcon /> : <PlayIcon />}
            onClick={toggleStreaming}
          >
            {isStreaming ? 'Stop Stream' : 'Start Stream'}
          </Button>
          
          <Button
            variant="outlined"
            color="secondary"
            startIcon={<RefreshIcon />}
            onClick={simulateActivity}
            disabled={!isConnected}
          >
            Simulate Activity
          </Button>
        </Box>
      </Box>

      {/* Connection Status */}
      <Alert 
        severity={isConnected ? "success" : "warning"}
        sx={{ mb: 3 }}
        icon={isConnected ? <SuccessIcon /> : <WarningIcon />}
      >
        {isConnected 
          ? `🟢 Connected - Streaming live events from real cloud data`
          : `🔴 Disconnected - Click "Start Stream" to connect`}
      </Alert>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Events
                  </Typography>
                  <Typography variant="h4">
                    {stats.totalEvents.toLocaleString()}
                  </Typography>
                </Box>
                <NotificationIcon sx={{ fontSize: 40, color: 'primary.main', opacity: 0.5 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Connections
                  </Typography>
                  <Typography variant="h4">
                    {stats.activeConnections}
                  </Typography>
                </Box>
                <Badge badgeContent={isConnected ? "Live" : "0"} color="success">
                  <SpeedIcon sx={{ fontSize: 40, color: 'success.main', opacity: 0.5 }} />
                </Badge>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Stream Status
                  </Typography>
                  <Typography variant="h6" color={isStreaming ? "success.main" : "error.main"}>
                    {isStreaming ? '🟢 Active' : '🔴 Inactive'}
                  </Typography>
                </Box>
                <TrendingIcon sx={{ fontSize: 40, color: 'info.main', opacity: 0.5 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Event Stream */}
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            📡 Live Event Stream
          </Typography>
          <Chip 
            label={`${events.length} events`} 
            color="primary" 
            size="small"
          />
        </Box>
        
        <Divider sx={{ mb: 2 }} />
        
        {isStreaming && events.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <LinearProgress />
            <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
              Waiting for events... Click "Simulate Activity" to generate events from real cloud data
            </Typography>
          </Box>
        )}

        <List sx={{ maxHeight: 600, overflow: 'auto' }}>
          {events.map((event, index) => (
            <ListItem 
              key={event.id || index}
              className="event-item"
              sx={{
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                mb: 1,
                '&:hover': { bgcolor: 'action.hover' }
              }}
            >
              <ListItemIcon>
                {getEventIcon(event.type)}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip 
                      label={event.type} 
                      size="small" 
                      color={getEventColor(event.type)}
                    />
                    <Typography variant="body2">
                      {event.data?.file_name || event.data?.migration_id || 'Event'}
                    </Typography>
                  </Box>
                }
                secondary={
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" display="block">
                      {event.data?.operation && `Operation: ${event.data.operation}`}
                      {event.data?.provider && ` | Provider: ${event.data.provider.toUpperCase()}`}
                      {event.data?.size_mb && ` | Size: ${event.data.size_mb} MB`}
                      {event.data?.amount && ` | $${event.data.amount.toFixed(2)}`}
                      {event.data?.access_count && ` | Access: ${event.data.access_count} times`}
                      {event.data?.data_temperature && ` | Tier: ${event.data.data_temperature}`}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {formatTime(event.timestamp)} | ID: {event.id}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default RealTimeStream;
