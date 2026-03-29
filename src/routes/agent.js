const express = require('express');
const router = express.Router();
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const db = require('../db');

// Generate random API key
function generateApiKey() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let key = 'molt_';
  for (let i = 0; i < 48; i++) {
    key += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return key;
}

// POST /api/agent/keys - Create new agent API key
router.post('/keys', async (req, res) => {
  try {
    const { 
      user_id, 
      name, 
      limit_per_transaction, 
      limit_daily, 
      limit_monthly 
    } = req.body;
    
    if (!user_id || !name) {
      return res.status(400).json({ error: 'user_id and name required' });
    }
    
    // Generate API key
    const apiKey = generateApiKey();
    const keyHash = await bcrypt.hash(apiKey, 10);
    
    // Create key
    const result = await db.query(
      `INSERT INTO agent_keys 
       (user_id, key_hash, name, limit_per_transaction_cents, limit_daily_cents, limit_monthly_cents)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING id, name, created_at, limit_per_transaction_cents, limit_daily_cents, limit_monthly_cents`,
      [
        user_id, 
        keyHash, 
        name,
        limit_per_transaction || null,
        limit_daily || null,
        limit_monthly || null
      ]
    );
    
    // Log audit
    await db.query(
      `INSERT INTO audit_log (user_id, action, details)
       VALUES ($1, 'agent_key.created', $2)`,
      [user_id, JSON.stringify({ key_id: result.rows[0].id, name })]
    );
    
    res.json({
      success: true,
      key: {
        id: result.rows[0].id,
        api_key: apiKey, // Only shown once!
        name: result.rows[0].name,
        created_at: result.rows[0].created_at,
        limits: {
          per_transaction: result.rows[0].limit_per_transaction_cents,
          daily: result.rows[0].limit_daily_cents,
          monthly: result.rows[0].limit_monthly_cents
        }
      },
      warning: 'Save this API key now. You won\'t be able to see it again.'
    });
    
  } catch (error) {
    console.error('Key creation error:', error);
    res.status(500).json({ error: 'Failed to create API key' });
  }
});

// GET /api/agent/keys/:user_id - List all keys for user
router.get('/keys/:user_id', async (req, res) => {
  try {
    const { user_id } = req.params;
    
    const result = await db.query(
      `SELECT id, name, created_at, last_used_at, is_active,
              limit_per_transaction_cents, limit_daily_cents, limit_monthly_cents,
              spent_today_cents, spent_this_month_cents
       FROM agent_keys
       WHERE user_id = $1
       ORDER BY created_at DESC`,
      [user_id]
    );
    
    res.json({
      keys: result.rows.map(key => ({
        id: key.id,
        name: key.name,
        created_at: key.created_at,
        last_used_at: key.last_used_at,
        is_active: key.is_active,
        limits: {
          per_transaction: key.limit_per_transaction_cents,
          daily: key.limit_daily_cents,
          monthly: key.limit_monthly_cents
        },
        spent: {
          today: key.spent_today_cents,
          this_month: key.spent_this_month_cents
        }
      }))
    });
  } catch (error) {
    console.error('Key listing error:', error);
    res.status(500).json({ error: 'Failed to list keys' });
  }
});

// DELETE /api/agent/keys/:key_id - Deactivate a key
router.delete('/keys/:key_id', async (req, res) => {
  try {
    const { key_id } = req.params;
    
    const result = await db.query(
      `UPDATE agent_keys SET is_active = false WHERE id = $1 RETURNING user_id, name`,
      [key_id]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Key not found' });
    }
    
    // Log audit
    await db.query(
      `INSERT INTO audit_log (user_id, action, details)
       VALUES ($1, 'agent_key.deactivated', $2)`,
      [result.rows[0].user_id, JSON.stringify({ key_id })]
    );
    
    res.json({ success: true, message: 'API key deactivated' });
  } catch (error) {
    console.error('Key deletion error:', error);
    res.status(500).json({ error: 'Failed to deactivate key' });
  }
});

module.exports = router;
