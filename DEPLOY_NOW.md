# Deploy MoltPal to Fly.io - Quick Guide

**Time to deploy:** ~5 minutes

## Option 1: Fly.io (Recommended - Free Tier)

### Steps:

```bash
# 1. Navigate to project
cd /home/clawd/clawd/moltpal

# 2. Login to Fly.io (opens browser)
flyctl auth login

# 3. Create PostgreSQL database (free tier)
flyctl postgres create --name moltpal-db --region iad --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1

# 4. Save the connection string it gives you

# 5. Create the app
flyctl launch --no-deploy

# 6. Set database secret
flyctl secrets set DATABASE_URL="<connection-string-from-step-4>"

# 7. Deploy!
flyctl deploy

# 8. Open it
flyctl open
```

**That's it!** Your API will be live at `https://moltpal.fly.dev`

## Option 2: Railway (Even Easier)

1. Go to [railway.app](https://railway.app)
2. Click "Deploy from GitHub"
3. Select the `alallos/moltpal` repo
4. Add PostgreSQL service
5. Set environment variable: `NODE_ENV=production`
6. Deploy!

**Done** - Railway auto-deploys on every push.

## After Deploy

1. Test health: `curl https://your-app.fly.dev/health`
2. Create first user via API
3. Update README with live URL
4. Tweet about it being live!

---

**Which option do you want?**
- Fly.io = More control, free tier
- Railway = Easier, auto-deploys from GitHub
