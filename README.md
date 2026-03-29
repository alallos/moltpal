<div align="center">

# 🔥 MoltPal

**PayPal for AI Agents**

Give your AI agents the ability to spend money autonomously within controlled budgets.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Status: Alpha](https://img.shields.io/badge/Status-Alpha-orange.svg)]()
[![Node.js](https://img.shields.io/badge/Node.js-20+-green.svg)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)]()

[Features](#features) • [Quick Start](#quick-start) • [API Docs](docs/API.md) • [Setup Guide](docs/SETUP.md)

</div>

---

## 🎯 Problem

AI agents are getting smarter and more autonomous, but they still can't spend money without constant human approval. This creates bottlenecks and limits what they can do.

## 💡 Solution

**MoltPal** is an API-first payment system designed specifically for AI agents. Set spending limits, fund an account, and let your agents handle payments autonomously.

## ✨ Features

- 🤖 **Agent API Keys** - Each agent gets its own API key with custom spending limits
- 💰 **Budget Controls** - Per-transaction, daily, and monthly limits
- 🔒 **Secure** - API keys hashed with bcrypt, rate-limited (100 req/min)
- 📊 **Real-time Monitoring** - Track every transaction as it happens
- 🚨 **Emergency Controls** - Instantly deactivate rogue agents
- 📝 **Full Audit Trail** - Every action logged with timestamps and metadata
- ⚡ **Fast** - Sub-100ms response times for payment authorization
- 🐳 **Docker Ready** - One command to get started

## 🚀 Quick Start

### With Docker (Recommended)

```bash
git clone https://github.com/alallos/moltpal.git
cd moltpal
docker-compose up -d
```

API available at: `http://localhost:3000`

### Manual Setup

```bash
npm install
npm run db:migrate
npm run dev
```

See [Setup Guide](docs/SETUP.md) for details.

## 📖 Usage Example

### 1. Create a user and fund account
```bash
curl -X POST http://localhost:3000/api/user/create \
  -H "Content-Type: application/json" \
  -d '{"email":"agent@example.com"}'

curl -X POST http://localhost:3000/api/user/<USER_ID>/balance \
  -H "Content-Type: application/json" \
  -d '{"amount": 100000}'
```

### 2. Create agent API key
```bash
curl -X POST http://localhost:3000/api/agent/keys \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<USER_ID>",
    "name": "Production Agent",
    "limit_per_transaction": 10000,
    "limit_daily": 50000,
    "limit_monthly": 200000
  }'
```

**Save the API key!** (Only shown once)

### 3. Agent makes a payment
```bash
curl -X POST http://localhost:3000/api/payment/pay \
  -H "Content-Type: application/json" \
  -H "X-API-Key: molt_your_key_here" \
  -d '{
    "amount": 5000,
    "description": "OpenAI GPT-4 API usage",
    "merchant": "OpenAI"
  }'
```

### 4. Check balance
```bash
curl http://localhost:3000/api/payment/balance \
  -H "X-API-Key: molt_your_key_here"
```

## 🎯 Use Cases

- **Autonomous AI Agents** - Let agents pay for API calls without approval
- **Development Tools** - Coding agents that spin up cloud resources on-demand
- **Data Processing** - Agents that purchase datasets or processing credits
- **Digital Purchases** - Buy templates, assets, or services programmatically
- **Multi-Agent Systems** - Each agent has its own budget and accountability

## 🏗️ Architecture

```
┌─────────────┐
│   AI Agent  │
└──────┬──────┘
       │ API Key
       ▼
┌─────────────┐      ┌──────────────┐
│  MoltPal    │─────▶│  PostgreSQL  │
│     API     │      │   Database   │
└──────┬──────┘      └──────────────┘
       │
       ▼
┌─────────────┐
│   Stripe    │ (Future)
│  Payments   │
└─────────────┘
```

## 📊 Tech Stack

- **Backend**: Node.js + Express
- **Database**: PostgreSQL 14+
- **Auth**: bcrypt-hashed API keys
- **Rate Limiting**: 100 req/min per key
- **Payments**: Stripe (planned)
- **Deployment**: Docker + Docker Compose

## 🔐 Security

- API keys hashed with bcrypt (never stored in plaintext)
- Rate limiting (100 requests/minute per key)
- All transactions logged in audit trail
- IP address tracking for suspicious activity
- Emergency deactivation for compromised keys
- Database constraints prevent overspending

## 📚 Documentation

- [API Reference](docs/API.md) - Complete API documentation
- [Setup Guide](docs/SETUP.md) - Installation and configuration
- [Architecture](docs/ARCHITECTURE.md) - System design and decisions
- [Contributing](CONTRIBUTING.md) - How to contribute

## 🛣️ Roadmap

- [x] Core payment API
- [x] Agent key management
- [x] Spending limits (per-tx, daily, monthly)
- [x] Transaction history
- [x] Audit logging
- [ ] Stripe integration
- [ ] Webhook notifications
- [ ] Web dashboard UI
- [ ] Email alerts
- [ ] 2FA for account access
- [ ] Multi-currency support
- [ ] Team/organization accounts

## 🤝 Contributing

This is an early-stage project. Issues and PRs welcome!

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙋 Support

- GitHub Issues: [Report bugs or request features](https://github.com/alallos/moltpal/issues)
- Email: drew@iteradynamics.com

---

<div align="center">

**Built by [@alallos](https://github.com/alallos)**

Making AI agents financially independent, one API call at a time.

</div>
