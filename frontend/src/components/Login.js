import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { authAPI } from '../services/api';
import './Login.css';

function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isRegister) {
        const response = await authAPI.register(formData);
        toast.success('Registration successful! Please log in.');
        setIsRegister(false);
        setFormData({ username: '', password: '', email: '' });
      } else {
        const response = await authAPI.login({
          username: formData.username,
          password: formData.password,
        });
        const token = response.data.access_token;
        onLogin({ username: formData.username }, token);
        toast.success('Welcome to CloudFlux AI!');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = () => {
    setFormData({ username: 'testuser', password: 'testpass123', email: '' });
    toast.success('Demo credentials filled!');
  };

  return (
    <div className="login-container">
      <div className="login-left">
        <div className="login-brand">
          <div className="brand-icon">☁️</div>
          <h1>CloudFlux AI</h1>
          <p>Intelligent Multi-Cloud Data Orchestration</p>
        </div>
        <div className="login-features">
          <div className="feature-item">
            <span className="feature-icon">🎯</span>
            <div>
              <h3>Smart Placement</h3>
              <p>AI-powered data placement optimization</p>
            </div>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🧠</span>
            <div>
              <h3>ML Predictions</h3>
              <p>Advanced machine learning insights</p>
            </div>
          </div>
          <div className="feature-item">
            <span className="feature-icon">⚡</span>
            <div>
              <h3>Real-Time Streaming</h3>
              <p>Live event monitoring and alerts</p>
            </div>
          </div>
        </div>
      </div>

      <div className="login-right">
        <div className="login-form-container">
          <h2>{isRegister ? 'Create Account' : 'Welcome Back'}</h2>
          <p className="login-subtitle">
            {isRegister ? 'Sign up to get started' : 'Sign in to your account'}
          </p>

          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                required
                className="form-input"
              />
            </div>

            {isRegister && (
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  className="form-input"
                />
              </div>
            )}

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
                className="form-input"
              />
            </div>

            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
              {loading ? 'Processing...' : (isRegister ? 'Sign Up' : 'Sign In')}
            </button>

            {!isRegister && (
              <button type="button" onClick={fillDemo} className="btn btn-outline btn-full">
                Fill Demo Credentials
              </button>
            )}
          </form>

          <p className="login-toggle">
            {isRegister ? 'Already have an account? ' : "Don't have an account? "}
            <span onClick={() => setIsRegister(!isRegister)}>
              {isRegister ? 'Sign In' : 'Sign Up'}
            </span>
          </p>

          <div className="demo-info">
            <p>🔑 <strong>Demo:</strong> testuser / testpass123</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
