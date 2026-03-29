# MoltPal Deployment Guide

Quick guide to deploying MoltPal to production.

## Quick Deploy Options

### Option 1: Fly.io (Recommended for MVP)

**Pros:** Easy, fast, free tier, built-in PostgreSQL  
**Cons:** Regional limitations

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch (interactive)
fly launch
# Answer prompts:
# - App name: moltpal (or your choice)
# - Region: Choose closest
# - PostgreSQL: Yes (choose development tier for free)
# - Deploy now: No (we need to set secrets first)

# Set secrets
fly secrets set DATABASE_URL=<from-fly-postgres>
fly secrets set NODE_ENV=production

# Deploy
fly deploy

# Check status
fly status

# View logs
fly logs

# Your API is now live at: https://moltpal.fly.dev
```

### Option 2: Railway

**Pros:** GitHub auto-deploy, easy PostgreSQL  
**Cons:** Pricing can scale up

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Select `moltpal` repository
5. Add PostgreSQL plugin
6. Set environment variables:
   - `DATABASE_URL` (auto-populated from PostgreSQL plugin)
   - `NODE_ENV=production`
   - `PORT=3000`
7. Deploy happens automatically

Your API will be at: `https://moltpal-production.up.railway.app`

### Option 3: Heroku

**Pros:** Simple, mature platform  
**Cons:** Paid plans only (no more free tier)

```bash
# Install Heroku CLI
brew install heroku/brew/heroku  # macOS
# or: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create moltpal

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment
heroku config:set NODE_ENV=production

# Deploy
git push heroku main

# Run migrations
heroku run npm run db:migrate

# Check logs
heroku logs --tail

# Your API: https://moltpal.herokuapp.com
```

### Option 4: VPS (Digital Ocean, Linode, etc.)

**Pros:** Full control, predictable pricing  
**Cons:** More setup required

```bash
# SSH into your VPS
ssh root@your-server-ip

# Install dependencies
apt update
apt install -y nodejs npm postgresql nginx

# Clone repo
git clone https://github.com/alallos/moltpal.git
cd moltpal

# Install dependencies
npm ci --production

# Set up PostgreSQL
sudo -u postgres createdb moltpal
sudo -u postgres createuser moltpal --pwprompt

# Configure environment
cp .env.example .env
# Edit .env with your database URL

# Run migrations
npm run db:migrate

# Install PM2 for process management
npm install -g pm2

# Start app
pm2 start src/index.js --name moltpal
pm2 save
pm2 startup  # Follow instructions

# Configure nginx as reverse proxy
# (see nginx config below)

# Set up SSL with Let's Encrypt
apt install -y certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com
```

**Nginx Config** (`/etc/nginx/sites-available/moltpal`):
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/moltpal /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## Environment Variables

Required for all deployments:

```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
NODE_ENV=production
PORT=3000  # or whatever your platform uses
```

Optional (for future features):
```bash
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
SENTRY_DSN=https://xxx@sentry.io/xxx
```

## Database Setup

All platforms need database migrations run:

```bash
npm run db:migrate
```

### Automated Migrations

For auto-migrations on deploy, add to `package.json`:

```json
{
  "scripts": {
    "start": "npm run db:migrate && node src/index.js"
  }
}
```

**Warning:** Only safe for small teams. Production apps should use migration tools like `db-migrate` or `knex`.

## Health Checks

Most platforms support health checks. Use:

```
GET /health
```

Returns:
```json
{
  "status": "ok",
  "service": "moltpal",
  "version": "0.1.0"
}
```

## Monitoring

### Basic Monitoring

```bash
# Check if app is running
curl https://your-domain.com/health

# Check logs (platform-specific)
fly logs           # Fly.io
railway logs       # Railway
heroku logs --tail # Heroku
pm2 logs moltpal   # VPS
```

### Advanced Monitoring

Recommended tools:
- **Uptime:** UptimeRobot, Pingdom
- **Errors:** Sentry
- **Performance:** New Relic, Datadog
- **Logs:** Papertrail, Loggly

## Backups

### Database Backups

**Fly.io:**
```bash
fly postgres backup list
fly postgres backup create
```

**Railway:**
- Auto-backups enabled by default
- Manual: Project Settings → Backups

**Heroku:**
```bash
heroku pg:backups:capture
heroku pg:backups:download
```

**VPS:**
```bash
# Daily cron job
0 2 * * * pg_dump moltpal | gzip > /backups/moltpal-$(date +\%Y\%m\%d).sql.gz
```

## Security Checklist

Before going live:

- [ ] HTTPS enabled (SSL certificate)
- [ ] Environment variables set (not in code)
- [ ] Database password is strong
- [ ] Rate limiting enabled
- [ ] Error messages don't leak sensitive info
- [ ] CORS configured properly
- [ ] API keys not committed to git
- [ ] Dependencies updated (`npm audit`)
- [ ] Monitoring and alerts configured

## Scaling

### Vertical Scaling (Bigger Server)

**Fly.io:**
```bash
fly scale vm shared-cpu-2x  # More CPU/RAM
```

**Railway:**
- Project → Settings → Resources → Adjust limits

**Heroku:**
```bash
heroku ps:resize web=standard-2x
```

### Horizontal Scaling (More Servers)

```bash
fly scale count 3  # 3 instances
```

**Requirements for horizontal scaling:**
- Stateless API (already is)
- Shared database (already using PostgreSQL)
- Session management (add Redis if needed)

## Performance Tips

1. **Add connection pooling** (already using `pg` Pool)
2. **Add Redis for caching** (for session data, rate limiting)
3. **Enable gzip compression**
4. **Add CDN for static assets** (Cloudflare)
5. **Database indexes** (already configured)

## Troubleshooting

### App won't start

```bash
# Check logs
<platform> logs

# Common issues:
# - Missing DATABASE_URL
# - Database connection failed
# - Port already in use
# - Dependencies not installed
```

### Database connection failed

```bash
# Test connection
psql $DATABASE_URL

# Check:
# - DATABASE_URL is correct
# - Database server is running
# - Firewall allows connection
# - SSL mode (add ?ssl=true if needed)
```

### High response times

```bash
# Check database
# - Add indexes
# - Optimize queries
# - Check connection pool size

# Check API
# - Enable compression
# - Add caching layer
# - Profile slow endpoints
```

## Cost Estimates

### Free Tier Options

- **Fly.io:** Free for hobby (3 shared VMs, 256MB RAM, 3GB storage)
- **Railway:** $5 credit/month (covers small usage)
- **Supabase:** Free PostgreSQL (500MB, 2GB bandwidth)

### Paid Tiers (Estimated)

**Low Traffic (< 1k req/day):**
- Fly.io: ~$5-10/month
- Railway: ~$10-15/month
- Heroku: ~$25/month
- VPS: ~$5-12/month (DigitalOcean, Linode)

**Medium Traffic (10k-100k req/day):**
- ~$30-80/month depending on platform and resources

**High Traffic (> 100k req/day):**
- ~$100-500/month
- Need dedicated database, load balancer, CDN

## Recommended Stack for MVP

**Platform:** Fly.io  
**Database:** Fly PostgreSQL  
**Monitoring:** Sentry (free tier)  
**Uptime Check:** UptimeRobot (free)  
**Cost:** ~$0-10/month

## Next Steps After Deployment

1. Test the API endpoints
2. Create your first user
3. Generate an API key
4. Make a test payment
5. Monitor logs for errors
6. Set up automated backups
7. Configure alerts
8. Share the API URL!

---

Need help? Open an issue on GitHub or email drew@iteradynamics.com
