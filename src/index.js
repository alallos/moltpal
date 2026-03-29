require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const paymentRoutes = require('./routes/payment');
const agentRoutes = require('./routes/agent');
const userRoutes = require('./routes/user');
const { errorHandler } = require('./middleware/errorHandler');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'moltpal', version: '0.1.0' });
});

// Routes
app.use('/api/payment', paymentRoutes);
app.use('/api/agent', agentRoutes);
app.use('/api/user', userRoutes);

// Error handling
app.use(errorHandler);

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

app.listen(PORT, () => {
  console.log(`🚀 MoltPal API running on port ${PORT}`);
});

module.exports = app;
