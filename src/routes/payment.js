const express = require('express');
const router = express.Router();
const { authenticateAgent } = require('../middleware/auth');
const db = require('../db');
const { v4: uuidv4 } = require('uuid');

// POST /api/payment/pay - Main endpoint for agents to make payments
router.post('/pay', authenticateAgent, async (req, res) => {
  try {
    const { amount, description, merchant, metadata } = req.body;
    
    // Validation
    if (!amount || amount <= 0) {
      return res.status(400).json({ error: 'Valid amount required (in cents)' });
    }
    
    if (!description) {
      return res.status(400).json({ error: 'Description required' });
    }
    
    const amountCents = Math.round(amount);
    
    // Check balance
    if (req.agent.balance_cents < amountCents) {
      return res.status(402).json({ 
        error: 'Insufficient balance',
        balance: req.agent.balance_cents,
        requested: amountCents
      });
    }
    
    // Check limits
    const limitChecks = await checkSpendingLimits(req.agent, amountCents);
    if (!limitChecks.allowed) {
      return res.status(403).json({ 
        error: 'Spending limit exceeded',
        reason: limitChecks.reason,
        limit: limitChecks.limit,
        current: limitChecks.current
      });
    }
    
    // Create transaction
    const txId = uuidv4();
    const result = await db.query(
      `INSERT INTO transactions 
       (id, user_id, agent_key_id, amount_cents, description, merchant, status, metadata)
       VALUES ($1, $2, $3, $4, $5, $6, 'completed', $7)
       RETURNING *`,
      [txId, req.userId, req.agent.id, amountCents, description, merchant || null, JSON.stringify(metadata || {})]
    );
    
    // Update balance and spending
    await db.query(
      `UPDATE users SET balance_cents = balance_cents - $1 WHERE id = $2`,
      [amountCents, req.userId]
    );
    
    await updateSpending(req.agent.id, amountCents);
    
    // Log audit
    await db.query(
      `INSERT INTO audit_log (user_id, agent_key_id, action, details, ip_address)
       VALUES ($1, $2, 'payment.created', $3, $4)`,
      [req.userId, req.agent.id, JSON.stringify({ txId, amount: amountCents, merchant }), req.ip]
    );
    
    res.json({
      success: true,
      transaction: {
        id: result.rows[0].id,
        amount: amountCents,
        description,
        merchant,
        status: 'completed',
        created_at: result.rows[0].created_at
      },
      balance: req.agent.balance_cents - amountCents
    });
    
  } catch (error) {
    console.error('Payment error:', error);
    res.status(500).json({ error: 'Payment processing failed' });
  }
});

// GET /api/payment/transactions - Get transaction history
router.get('/transactions', authenticateAgent, async (req, res) => {
  try {
    const limit = Math.min(parseInt(req.query.limit) || 50, 500);
    const offset = parseInt(req.query.offset) || 0;
    
    const result = await db.query(
      `SELECT id, amount_cents, description, merchant, status, created_at, metadata
       FROM transactions
       WHERE agent_key_id = $1
       ORDER BY created_at DESC
       LIMIT $2 OFFSET $3`,
      [req.agent.id, limit, offset]
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

// GET /api/payment/balance - Get current balance and limits
router.get('/balance', authenticateAgent, async (req, res) => {
  try {
    const result = await db.query(
      `SELECT balance_cents FROM users WHERE id = $1`,
      [req.userId]
    );
    
    res.json({
      balance: result.rows[0].balance_cents,
      limits: {
        per_transaction: req.agent.limit_per_transaction_cents,
        daily: req.agent.limit_daily_cents,
        monthly: req.agent.limit_monthly_cents
      },
      spent: {
        today: req.agent.spent_today_cents,
        this_month: req.agent.spent_this_month_cents
      }
    });
  } catch (error) {
    console.error('Balance fetch error:', error);
    res.status(500).json({ error: 'Failed to fetch balance' });
  }
});

// Helper: Check spending limits
async function checkSpendingLimits(agent, amountCents) {
  // Per-transaction limit
  if (agent.limit_per_transaction_cents && amountCents > agent.limit_per_transaction_cents) {
    return {
      allowed: false,
      reason: 'per_transaction_limit',
      limit: agent.limit_per_transaction_cents,
      current: amountCents
    };
  }
  
  // Daily limit
  if (agent.limit_daily_cents) {
    const newDailyTotal = agent.spent_today_cents + amountCents;
    if (newDailyTotal > agent.limit_daily_cents) {
      return {
        allowed: false,
        reason: 'daily_limit',
        limit: agent.limit_daily_cents,
        current: agent.spent_today_cents
      };
    }
  }
  
  // Monthly limit
  if (agent.limit_monthly_cents) {
    const newMonthlyTotal = agent.spent_this_month_cents + amountCents;
    if (newMonthlyTotal > agent.limit_monthly_cents) {
      return {
        allowed: false,
        reason: 'monthly_limit',
        limit: agent.limit_monthly_cents,
        current: agent.spent_this_month_cents
      };
    }
  }
  
  return { allowed: true };
}

// Helper: Update spending counters
async function updateSpending(agentKeyId, amountCents) {
  await db.query(
    `UPDATE agent_keys 
     SET spent_today_cents = spent_today_cents + $1,
         spent_this_month_cents = spent_this_month_cents + $1
     WHERE id = $2`,
    [amountCents, agentKeyId]
  );
}

module.exports = router;
