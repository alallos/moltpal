# MoltPal

**PayPal for AI Agents**

Give your AI agents the ability to spend money autonomously within controlled budgets.

## What It Does

MoltPal lets you:
- Fund an account with your money
- Create API keys for AI agents with spending limits
- Let agents make payments autonomously (within rules)
- Monitor all transactions in real-time
- Emergency kill switch for rogue agents

## How It Works

1. **Human adds funds** → Your balance (via Stripe)
2. **Create agent API key** → Set daily/monthly/per-transaction limits
3. **Agent calls API** → `POST /api/pay` with amount, merchant, description
4. **MoltPal approves/denies** → Checks limits, logs everything
5. **Payment processes** → Via Stripe, webhooks notify you
6. **Dashboard shows all** → Every transaction, agent spending patterns

## Tech Stack

- **Backend**: Node.js + Express + PostgreSQL
- **Frontend**: Next.js + Tailwind
- **Payments**: Stripe Connect
- **Auth**: API keys (agents) + OAuth/Magic Links (humans)

## Status

🚧 **In Active Development** 🚧

Building the MVP now.

## License

MIT
