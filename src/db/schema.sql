-- MoltPal Database Schema

-- Users (account owners)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    balance_cents INTEGER DEFAULT 0 CHECK (balance_cents >= 0),
    stripe_customer_id VARCHAR(255),
    is_active BOOLEAN DEFAULT true
);

-- Agent API Keys
CREATE TABLE IF NOT EXISTS agent_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    
    -- Spending limits (in cents)
    limit_per_transaction_cents INTEGER,
    limit_daily_cents INTEGER,
    limit_monthly_cents INTEGER,
    
    -- Current period spending tracking
    spent_today_cents INTEGER DEFAULT 0,
    spent_this_month_cents INTEGER DEFAULT 0,
    spending_reset_date DATE DEFAULT CURRENT_DATE
);

-- Transactions
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    agent_key_id UUID REFERENCES agent_keys(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Transaction details
    amount_cents INTEGER NOT NULL,
    description TEXT NOT NULL,
    merchant VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, failed, reversed
    
    -- Payment processing
    stripe_payment_id VARCHAR(255),
    
    -- Metadata
    metadata JSONB
);

-- Webhooks for notifications
CREATE TABLE IF NOT EXISTS webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    secret VARCHAR(100) NOT NULL,
    events TEXT[] NOT NULL, -- ['transaction.created', 'transaction.completed', etc]
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    agent_key_id UUID REFERENCES agent_keys(id),
    action VARCHAR(100) NOT NULL,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_keys_user_id ON agent_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);
