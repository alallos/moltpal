const bcrypt = require('bcrypt');
const db = require('../db');
const { RateLimiterMemory } = require('rate-limiter-flexible');

// Rate limiter: max 100 requests per minute per key
const rateLimiter = new RateLimiterMemory({
  points: 100,
  duration: 60
});

async function authenticateAgent(req, res, next) {
  try {
    const apiKey = req.headers['x-api-key'] || req.headers['authorization']?.replace('Bearer ', '');
    
    if (!apiKey) {
      return res.status(401).json({ error: 'API key required' });
    }
    
    // Rate limiting
    try {
      await rateLimiter.consume(apiKey);
    } catch (rateLimiterRes) {
      return res.status(429).json({ error: 'Too many requests' });
    }
    
    // Get all active keys (we'll verify hash below)
    // TODO: optimize by storing key prefix separately for faster lookup
    const result = await db.query(
      `SELECT ak.*, u.balance_cents, u.is_active as user_active 
       FROM agent_keys ak 
       JOIN users u ON ak.user_id = u.id 
       WHERE ak.is_active = true`
    );
    
    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid API key' });
    }
    
    // Verify key hash (brute force for now, optimize later)
    let validKey = null;
    for (const row of result.rows) {
      try {
        const match = await bcrypt.compare(apiKey, row.key_hash);
        if (match) {
          validKey = row;
          break;
        }
      } catch (err) {
        // Invalid hash format, skip
        continue;
      }
    }
    
    if (!validKey) {
      return res.status(401).json({ error: 'Invalid API key' });
    }
    
    if (!validKey.user_active) {
      return res.status(403).json({ error: 'Account inactive' });
    }
    
    // Update last used timestamp
    await db.query(
      'UPDATE agent_keys SET last_used_at = CURRENT_TIMESTAMP WHERE id = $1',
      [validKey.id]
    );
    
    // Attach to request
    req.agent = validKey;
    req.userId = validKey.user_id;
    
    next();
  } catch (error) {
    console.error('Auth error:', error);
    res.status(500).json({ error: 'Authentication failed' });
  }
}

module.exports = { authenticateAgent };
