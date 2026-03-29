# MoltPal Setup Guide

## Quick Start (Docker)

**Easiest way to get started:**

```bash
# Clone the repo
git clone https://github.com/alallos/moltpal.git
cd moltpal

# Start with Docker Compose
docker-compose up -d

# API will be available at http://localhost:3000
```

That's it! PostgreSQL and the API will be running.

---

## Manual Setup

### Prerequisites
- Node.js 18+
- PostgreSQL 14+

### Steps

1. **Install dependencies:**
```bash
npm install
```

2. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. **Create database:**
```bash
createdb moltpal
```

4. **Run migrations:**
```bash
npm run db:migrate
```

5. **Start server:**
```bash
npm run dev  # Development (auto-reload)
# or
npm start    # Production
```

---

## Testing the API

### 1. Create a user
```bash
curl -X POST http://localhost:3000/api/user/create \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

Response:
```json
{
  "success": true,
  "user": {
    "id": "uuid-here",
    "email": "test@example.com",
    "balance_cents": 0,
    "created_at": "..."
  }
}
```

### 2. Add funds
```bash
curl -X POST http://localhost:3000/api/user/<USER_ID>/balance \
  -H "Content-Type: application/json" \
  -d '{"amount": 100000}'
```

### 3. Create agent API key
```bash
curl -X POST http://localhost:3000/api/agent/keys \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<USER_ID>",
    "name": "Test Agent",
    "limit_per_transaction": 10000,
    "limit_daily": 50000,
    "limit_monthly": 200000
  }'
```

**Save the `api_key` from the response!**

### 4. Make a payment (as agent)
```bash
curl -X POST http://localhost:3000/api/payment/pay \
  -H "Content-Type: application/json" \
  -H "X-API-Key: molt_your_key_here" \
  -d '{
    "amount": 5000,
    "description": "OpenAI API usage",
    "merchant": "OpenAI"
  }'
```

### 5. Check balance
```bash
curl http://localhost:3000/api/payment/balance \
  -H "X-API-Key: molt_your_key_here"
```

---

## Automated Test Script

We provide a test script that does all the above automatically:

```bash
npm run test:demo
```

---

## Production Deployment

### Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - API port (default: 3000)
- `NODE_ENV` - Set to `production`

Optional (for Stripe integration):
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

### Deploying to Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
fly launch

# Set secrets
fly secrets set DATABASE_URL=postgresql://...

# Deploy
fly deploy
```

### Deploying to Railway

1. Connect your GitHub repo
2. Add PostgreSQL plugin
3. Deploy automatically on push

---

## Database Maintenance

### Reset spending counters (daily cron)
```sql
UPDATE agent_keys 
SET spent_today_cents = 0 
WHERE spending_reset_date < CURRENT_DATE;

UPDATE agent_keys 
SET spending_reset_date = CURRENT_DATE;
```

### Reset monthly counters (monthly cron)
```sql
UPDATE agent_keys 
SET spent_this_month_cents = 0 
WHERE EXTRACT(DAY FROM spending_reset_date) = 1;
```

---

## Security Notes

- API keys are hashed with bcrypt (never stored in plaintext)
- Rate limiting: 100 requests/minute per key
- All transactions are logged in audit_log
- Set appropriate spending limits for production agents
- Use HTTPS in production (required for real payments)

---

## Next Steps

- Set up Stripe integration for real payments
- Add webhook notifications
- Build dashboard frontend
- Add email alerts for suspicious activity
- Implement 2FA for account access
