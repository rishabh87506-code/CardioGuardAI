const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const { createProxyMiddleware } = require('http-proxy-middleware');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Routes
const authRoutes = require('./routes/auth');
const metricsRoutes = require('./routes/metrics');
const authMiddleware = require('./middleware/auth');


// Public Root
app.get('/', (req, res) => {
  res.json({
    message: 'CardioGuard AI API Gateway is operational',
    version: '1.0.0',
    disclaimer: 'General Wellness & Lifestyle Monitoring Platform - Non-Medical Service',
    endpoints: {
      auth: '/api/v1/auth',
      metrics: '/api/v1/metrics',
      brain: '/api/v1/brain (protected)'
    }
  });
});

app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'api-gateway',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/metrics', metricsRoutes);


// Protected Proxy Routes - Directs to Python Wellness Engine
app.use('/api/v1/brain', authMiddleware, createProxyMiddleware({
  target: PYTHON_BACKEND_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/api/v1/brain': '/api/v1',
  },
  onProxyReq: (proxyReq, req, res) => {
    // Inject user context into headers for the Python backend
    // This allows the Python services to be stateless regarding authentication
    if (req.user) {
      proxyReq.setHeader('x-user-id', req.user.user.id);
      proxyReq.setHeader('x-user-email', req.user.user.email);
    }
  },
  onError: (err, req, res) => {
    console.error('Proxy Error:', err);
    res.status(502).json({
      error: 'Wellness Engine (Python) is currently unavailable',
      message: 'We are working to restore the connection to our analysis agents.',
      disclaimer: 'In case of urgent wellness concerns, please consult a healthcare provider directly.'
    });
  }
}));

// Start Server
app.listen(PORT, () => {
  console.log(`🚀 Gateway running on port ${PORT}`);
  console.log(`🔗 Proxying /api/v1/brain to ${PYTHON_BACKEND_URL}`);
});


