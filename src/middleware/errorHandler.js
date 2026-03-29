function errorHandler(err, req, res, next) {
  console.error('Error:', err);
  
  // Stripe errors
  if (err.type && err.type.startsWith('Stripe')) {
    return res.status(400).json({
      error: 'Payment processing error',
      message: err.message
    });
  }
  
  // Validation errors
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      error: 'Validation error',
      message: err.message
    });
  }
  
  // Database errors
  if (err.code && err.code.startsWith('23')) {
    return res.status(400).json({
      error: 'Database constraint violation',
      message: 'Invalid data provided'
    });
  }
  
  // Default
  res.status(err.status || 500).json({
    error: err.message || 'Internal server error'
  });
}

module.exports = { errorHandler };
