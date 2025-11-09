import React, { useState } from 'react';
import './LandingPage.css';

const LandingPage = ({ onLogin }) => {
  const [showModal, setShowModal] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ username: '', password: '', email: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const body = isLogin 
        ? { username: formData.username, password: formData.password }
        : formData;

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        onLogin({ username: formData.username });
        setShowModal(false);
      } else {
        setError(data.detail || 'Authentication failed');
      }
    } catch (err) {
      setError('Connection failed. Please check if backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = () => {
    setFormData({ username: 'testuser', password: 'testpass123', email: '' });
  };

  return (
    <div className="landing-container">
      <nav className="landing-nav">
        <div className="nav-content">
          <div className="nav-logo">
            <svg className="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
            </svg>
            <span className="logo-text">CloudFlux AI</span>
          </div>
          <button className="nav-btn" onClick={() => setShowModal(true)}>Sign In</button>
        </div>
      </nav>

      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Intelligent Data Orchestration
            <span className="hero-gradient"> Powered by AI</span>
          </h1>
          <p className="hero-subtitle">
            Optimize data placement, predict workloads, and automate migrations with advanced machine learning
          </p>
          <div className="hero-buttons">
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>Get Started</button>
            <button className="btn btn-secondary">View Demo</button>
          </div>
          <div className="demo-credentials">
            <p>🔑 Demo: testuser / testpass123</p>
          </div>
        </div>
      </section>

      <section className="features-section">
        <h2 className="section-title">Enterprise Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Smart Placement</h3>
            <p>AI-powered data placement optimization with temperature-based tiering and cost analysis</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🧠</div>
            <h3>ML Predictions</h3>
            <p>Advanced machine learning models for workload forecasting and capacity planning</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>Real-Time Streaming</h3>
            <p>Live event monitoring with WebSocket connections and instant notifications</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🚀</div>
            <h3>Auto Migrations</h3>
            <p>Automated data migration jobs with progress tracking and rollback support</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">💰</div>
            <h3>Cost Optimization</h3>
            <p>Real-time cost analysis and recommendations for storage tier optimization</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Analytics Dashboard</h3>
            <p>Comprehensive insights with interactive visualizations and performance metrics</p>
          </div>
        </div>
      </section>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            <h2 className="modal-title">{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
            
            {error && <div className="error-message">{error}</div>}
            
            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label>Username</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                />
              </div>
              
              {!isLogin && (
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                  />
                </div>
              )}
              
              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Sign Up')}
              </button>
              
              {isLogin && (
                <button type="button" className="btn btn-secondary btn-full" onClick={fillDemo}>
                  Fill Demo Credentials
                </button>
              )}
            </form>

            <p className="modal-toggle">
              {isLogin ? "Don't have an account? " : "Already have an account? "}
              <span onClick={() => setIsLogin(!isLogin)}>
                {isLogin ? 'Sign Up' : 'Sign In'}
              </span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LandingPage;
