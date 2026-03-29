const express = require('express');
const router = express.Router();
const db = require('../db');

// POST /api/user/create - Create new user account
router.post('/create', async (req, res) => {
  try {
    const { email } = req.body;
    
    if (!email || !email.includes('@')) {
      return res.status(400).json({ error: 'Valid email required' });
    }
    
    const result = await db.query(
      `INSERT INTO users (email) VALUES ($1) 
       ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email
       RETURNING id, email, balance_cents, created_at`,
      [email.toLowerCase()]
    );
    
    res.json({
      success: true,
      user: result.rows[0]
    });
  } catch (error) {
    console.error('User creation error:', error);
    res.status(500).json({ error: 'Failed to create user' });
  }
});

// GET /api/user/:user_id - Get user details
router.get('/:user_id', async (req, res) => {
  try {
    const { user_id } = req.params;
    
    const result = await db.query(
      `SELECT id, email, balance_cents, created_at, is_active
       FROM users WHERE id = $1`,
      [user_id]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    res.json({ user: result.rows[0] });
  } catch (error) {
    console.error('User fetch error:', error);
    res.status(500).json({ error: 'Failed to fetch user' });
  }
});

// POST /api/user/:user_id/balance - Add funds to user balance
router.post('/:user_id/balance', async (req, res) => {
  try {
    const { user_id } = req.params;
    const { amount } = req.body;
    
    if (!amount || amount <= 0) {
      return res.status(400).json({ error: 'Valid amount required (in cents)' });
    }
    
    const result = await db.query(
      `UPDATE users SET balance_cents = balance_cents + $1 
       WHERE id = $2 
       RETURNING balance_cents`,
      [Math.round(amount), user_id]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    // Log audit
    await db.query(
      `INSERT INTO audit_log (user_id, action, details)
       VALUES ($1, 'balance.added', $2)`,
      [user_id, JSON.stringify({ amount: Math.round(amount) })]
    );
    
    res.json({
      success: true,
      balance: result.rows[0].balance_cents
    });
  } catch (error) {
    console.error('Balance update error:', error);
    res.status(500).json({ error: 'Failed to update balance' });
  }
});

// GET /api/user/:user_id/transactions - Get all user transactions
router.get('/:user_id/transactions', async (req, res) => {
  try {
    const { user_id } = req.params;
    const limit = Math.min(parseInt(req.query.limit) || 100, 500);
    const offset = parseInt(req.query.offset) || 0;
    
    const result = await db.query(
      `SELECT t.*, ak.name as agent_name
       FROM transactions t
       LEFT JOIN agent_keys ak ON t.agent_key_id = ak.id
       WHERE t.user_id = $1
       ORDER BY t.created_at DESC
       LIMIT $2 OFFSET $3`,
      [user_id, limit, offset]
    );
    
    res.json({
      transactions: result.rows,
      count: result.rows.length,
      offset,
      limit
    });
  } catch (error) {
    console.error('Transaction fetch error:', error);
    res.status(500).json({ error: 'Failed to fetch transactions' });
  }
});

// GET /api/user/:user_id/stats - Get spending statistics
router.get('/:user_id/stats', async (req, res) => {
  try {
    const { user_id } = req.params;
    
    const stats = await db.query(
      `SELECT 
        COUNT(*) as total_transactions,
        COALESCE(SUM(amount_cents), 0) as total_spent,
        COALESCE(AVG(amount_cents), 0) as avg_transaction,
        COUNT(DISTINCT agent_key_id) as active_agents
       FROM transactions
       WHERE user_id = $1 AND status = 'completed'`,
      [user_id]
    );
    
    const todayStats = await db.query(
      `SELECT 
        COUNT(*) as transactions_today,
        COALESCE(SUM(amount_cents), 0) as spent_today
       FROM transactions
       WHERE user_id = $1 AND created_at >= CURRENT_DATE`,
      [user_id]
    );
    
    res.json({
      all_time: {
        transactions: parseInt(stats.rows[0].total_transactions),
        spent: parseInt(stats.rows[0].total_spent),
        avg_transaction: Math.round(parseFloat(stats.rows[0].avg_transaction)),
        active_agents: parseInt(stats.rows[0].active_agents)
      },
      today: {
        transactions: parseInt(todayStats.rows[0].transactions_today),
        spent: parseInt(todayStats.rows[0].spent_today)
      }
    });
  } catch (error) {
    console.error('Stats fetch error:', error);
    res.status(500).json({ error: 'Failed to fetch statistics' });
  }
});

module.exports = router;
