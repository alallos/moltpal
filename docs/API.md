# MoltPal API Documentation

## Base URL
```
http://localhost:3000/api
```

## Authentication

Agent API keys are passed via header:
```
X-API-Key: molt_your_api_key_here
```
or
```
Authorization: Bearer molt_your_api_key_here
```

---

## Payment Endpoints

### POST /api/payment/pay
Make a payment as an agent.

**Headers:**
- `X-API-Key: molt_xxx`

**Body:**
```json
{
  "amount": 1000,
  "description": "OpenAI API usage",
  "merchant": "OpenAI",
  "metadata": {
    "service": "gpt-4",
    "tokens": 5000
  }
}
```

**Response:**
```json
{
  "success": true,
  "transaction": {
    "id": "uuid",
    "amount": 1000,
    "description": "OpenAI API usage",
    "merchant": "OpenAI",
    "status": "completed",
    "created_at": "2026-03-29T..."
  },
  "balance": 9000
}
```

### GET /api/payment/balance
Get current balance and spending limits.

**Headers:**
- `X-API-Key: molt_xxx`

**Response:**
```json
{
  "balance": 10000,
  "limits": {
    "per_transaction": 5000,
    "daily": 10000,
    "monthly": 50000
  },
  "spent": {
    "today": 1000,
    "this_month": 5000
  }
}
```

### GET /api/payment/transactions
Get transaction history for this agent.

**Headers:**
- `X-API-Key: molt_xxx`

**Query Params:**
- `limit` (default: 50, max: 500)
- `offset` (default: 0)

**Response:**
```json
{
  "transactions": [...],
  "count": 10,
  "offset": 0,
  "limit": 50
}
```

---

## Agent Key Management

### POST /api/agent/keys
Create a new agent API key.

**Body:**
```json
{
  "user_id": "uuid",
  "name": "Production Agent",
  "limit_per_transaction": 5000,
  "limit_daily": 10000,
  "limit_monthly": 50000
}
```

**Response:**
```json
{
  "success": true,
  "key": {
    "id": "uuid",
    "api_key": "molt_xxx",
    "name": "Production Agent",
    "created_at": "2026-03-29T...",
    "limits": {
      "per_transaction": 5000,
      "daily": 10000,
      "monthly": 50000
    }
  },
  "warning": "Save this API key now. You won't be able to see it again."
}
```

### GET /api/agent/keys/:user_id
List all keys for a user.

**Response:**
```json
{
  "keys": [
    {
      "id": "uuid",
      "name": "Production Agent",
      "created_at": "2026-03-29T...",
      "last_used_at": "2026-03-29T...",
      "is_active": true,
      "limits": {...},
      "spent": {...}
    }
  ]
}
```

### DELETE /api/agent/keys/:key_id
Deactivate an API key.

**Response:**
```json
{
  "success": true,
  "message": "API key deactivated"
}
```

---

## User Management

### POST /api/user/create
Create a new user account.

**Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "balance_cents": 0,
    "created_at": "2026-03-29T..."
  }
}
```

### GET /api/user/:user_id
Get user details.

### POST /api/user/:user_id/balance
Add funds to user balance.

**Body:**
```json
{
  "amount": 10000
}
```

### GET /api/user/:user_id/transactions
Get all transactions for a user.

### GET /api/user/:user_id/stats
Get spending statistics.

---

## Error Responses

All errors return appropriate HTTP status codes with JSON body:

```json
{
  "error": "Error message here"
}
```

Common codes:
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid API key)
- `402` - Payment Required (insufficient balance)
- `403` - Forbidden (spending limit exceeded)
- `404` - Not Found
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error
