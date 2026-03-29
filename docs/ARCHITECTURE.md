# MoltPal Architecture

## Overview

MoltPal is an API-first payment system designed specifically for AI agents. It provides budget controls, real-time monitoring, and autonomous spending capabilities.

## System Design

```
┌───────────────────────────────────────────────────────────┐
│                        AI Agents                          │
│  (Clawdbot, AutoGPT, custom agents, etc.)                │
└──────────────────────┬────────────────────────────────────┘
                       │ API Key Authentication
                       ▼
┌───────────────────────────────────────────────────────────┐
│                     API Gateway                           │
│  - Rate Limiting (100 req/min per key)                   │
│  - Authentication & Authorization                         │
│  - Request Validation                                     │
└──────────────────────┬────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────────────┐
│                  Business Logic Layer                     │
│                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐    │
│  │  Payment    │  │   Agent Key  │  │    User     │    │
│  │  Service    │  │   Service    │  │   Service   │    │
│  └─────────────┘  └──────────────┘  └─────────────┘    │
│                                                           │
│  - Spending limit checks                                 │
│  - Transaction processing                                │
│  - Audit logging                                         │
└──────────────────────┬────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────────────┐
│                   PostgreSQL Database                     │
│                                                           │
│  users | agent_keys | transactions | audit_log | webhooks│
└───────────────────────────────────────────────────────────┘
```

## Data Model

### Users
- Account owners who fund balances
- Can create multiple agent keys
- Track overall balance and activity

### Agent Keys
- Each key represents one agent
- Hashed with bcrypt (prefix stored for fast lookup)
- Per-transaction, daily, and monthly spending limits
- Spending counters reset automatically

### Transactions
- Immutable record of all payments
- Links to user and agent key
- Status tracking (pending, completed, failed)
- Metadata field for custom data

### Audit Log
- Every action logged with timestamp
- User ID, agent key ID, IP address
- Enables forensics and compliance

## Security Model

### Authentication
1. Agent passes API key via header (`X-API-Key` or `Authorization: Bearer`)
2. System extracts first 8 chars (prefix) for fast DB lookup
3. Retrieves matching keys from database
4. Verifies full key against bcrypt hash
5. Checks if key and user account are active
6. Updates `last_used_at` timestamp

### Authorization
Before processing payment:
1. Check user balance >= amount
2. Check per-transaction limit
3. Check daily spending limit (reset at midnight)
4. Check monthly spending limit (reset on 1st of month)
5. Log attempt to audit trail
6. Process or reject

### Rate Limiting
- 100 requests per minute per API key
- In-memory rate limiter (rate-limiter-flexible)
- Returns 429 Too Many Requests on limit

### Data Protection
- API keys never stored in plaintext
- bcrypt hashing with salt rounds = 10
- Database constraints prevent negative balances
- All transactions are atomic (ACID compliance)

## API Design

### RESTful Principles
- `/api/payment/*` - Payment operations
- `/api/agent/*` - Agent key management
- `/api/user/*` - User account management

### Response Format
Success:
```json
{
  "success": true,
  "data": {...}
}
```

Error:
```json
{
  "error": "Error message",
  "details": {...}
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid API key)
- `402` - Payment Required (insufficient balance)
- `403` - Forbidden (spending limit exceeded)
- `404` - Not Found
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error

## Spending Limits

### Per-Transaction Limit
- Maximum amount for a single transaction
- Checked before processing
- Useful for preventing large accidental charges

### Daily Limit
- Maximum spending in a 24-hour period
- Resets at midnight (server timezone)
- Prevents runaway spending

### Monthly Limit
- Maximum spending in a calendar month
- Resets on the 1st of each month
- Long-term budget control

### Implementation
```sql
UPDATE agent_keys 
SET spent_today_cents = spent_today_cents + $amount
WHERE id = $key_id;
```

Spending resets handled by cron job or at check time.

## Deployment Architecture

### Development
- Docker Compose with PostgreSQL
- Hot-reload with nodemon
- Local testing with curl

### Production
Options:
1. **Fly.io** - Deploy with `fly launch`
2. **Railway** - Connect GitHub, auto-deploy
3. **Heroku** - One-click PostgreSQL addon
4. **VPS** - Docker + reverse proxy (nginx)

Requirements:
- PostgreSQL 14+ database
- Node.js 20+ runtime
- Environment variables configured
- HTTPS for production (required for Stripe)

## Future Enhancements

### Phase 2: Stripe Integration
- Real payment processing
- Webhook handling for async updates
- Refunds and disputes
- Multi-currency support

### Phase 3: Web Dashboard
- Visual transaction history
- Real-time spending charts
- Agent management UI
- Email notifications

### Phase 4: Advanced Features
- Webhook notifications to external systems
- Team/organization accounts
- Role-based access control
- Spending analytics and insights
- Budget recommendations based on ML

### Phase 5: Ecosystem
- Marketplace for agent services
- Agent-to-agent payments
- Escrow for service contracts
- Recurring subscriptions

## Performance Considerations

### Database
- Indexes on foreign keys and timestamps
- Materialized views for analytics (future)
- Connection pooling via pg Pool

### API
- Sub-100ms response times for auth
- Async transaction logging
- Caching for frequently accessed data (future)

### Scaling
- Stateless API (horizontal scaling ready)
- PostgreSQL handles high read/write volume
- Rate limiter can move to Redis for multi-instance

## Monitoring & Observability

### Current
- Console logging of errors
- Audit trail in database

### Planned
- Application performance monitoring (APM)
- Error tracking (Sentry)
- Metrics dashboard (Grafana)
- Alerts for suspicious activity

## Compliance & Legal

### Current State
- MVP/Demo phase
- No real money processing
- MIT License

### Required for Production
- Terms of Service
- Privacy Policy
- KYC/AML compliance (if processing real payments)
- PCI DSS compliance (via Stripe)
- Data protection (GDPR if serving EU)

## Design Decisions

### Why PostgreSQL?
- ACID transactions prevent race conditions
- Strong consistency for financial data
- Excellent JSON support for metadata
- Mature ecosystem and tools

### Why bcrypt for API Keys?
- Industry standard for password hashing
- Resistant to brute force attacks
- Salting built-in
- Adjustable work factor

### Why Express?
- Minimal, flexible framework
- Large ecosystem of middleware
- Easy to understand and maintain
- Fast enough for our use case

### Why API Keys Instead of OAuth?
- Simpler for machine-to-machine auth
- No user interaction required
- Easier to revoke and rotate
- Standard for developer APIs

## Questions & Decisions

**Q: Why not use Stripe Connect immediately?**  
A: MVP first. Prove the concept works before adding payment complexity.

**Q: How do agents discover their spending limits?**  
A: `GET /api/payment/balance` returns limits and current spending.

**Q: What happens if an agent goes rogue?**  
A: Owner can deactivate the key instantly via `DELETE /api/agent/keys/:id`.

**Q: Can multiple agents share one key?**  
A: Technically yes, but not recommended. Each agent should have its own key for accountability.

**Q: How are disputes handled?**  
A: Currently, all transactions are internal (no real money). Future: Stripe handles disputes.

---

For implementation details, see the source code in `src/`.
