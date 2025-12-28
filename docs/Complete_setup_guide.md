# Deployment Guide

Comprehensive guide for deploying Shopify Analytics AI to production environments.

## 🎯 Deployment Options

### Option 1: Traditional VPS (Recommended for MVP)
- AWS EC2, DigitalOcean Droplet, or Linode
- Full control over environment
- Cost-effective for small scale
- Easy to debug

### Option 2: Platform as a Service
- Heroku (Rails + Python)
- Railway.app
- Render.com
- Fly.io

### Option 3: Containerized (Docker)
- Docker Compose for both services
- AWS ECS or Google Cloud Run
- Kubernetes for scale

---

## 📋 Pre-Deployment Checklist

### 1. Environment Preparation
- [ ] Obtain production API keys (Anthropic, Shopify)
- [ ] Setup production database (PostgreSQL recommended)
- [ ] Configure domain and SSL certificates
- [ ] Setup monitoring tools
- [ ] Configure backup strategy

### 2. Security
- [ ] Generate strong SECRET_KEY_BASE
- [ ] Generate new LOCKBOX_MASTER_KEY
- [ ] Enable HTTPS only
- [ ] Configure CORS for production domains
- [ ] Setup rate limiting
- [ ] Enable database encryption at rest

### 3. Performance
- [ ] Setup Redis for caching
- [ ] Configure CDN for assets
- [ ] Enable database query optimization
- [ ] Setup load balancing (if needed)

---

## 🚀 Deployment Steps

### Step 1: Prepare Production Database

**Switch from SQLite to PostgreSQL:**

```ruby
# Gemfile
gem 'pg', '~> 1.5'
# Remove: gem 'sqlite3'
```

```yaml
# config/database.yml
production:
  adapter: postgresql
  encoding: unicode
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  url: <%= ENV['DATABASE_URL'] %>
```

**Run migrations:**
```bash
RAILS_ENV=production rails db:migrate
```

---

### Step 2: Configure Production Environment

**Rails (.env.production):**
```bash
# Application
RAILS_ENV=production
SECRET_KEY_BASE=<generate with: rails secret>

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Shopify
SHOPIFY_API_KEY=your_production_key
SHOPIFY_API_SECRET=your_production_secret
SHOPIFY_SCOPES=read_products,read_orders,read_customers,read_analytics

# Security
LOCKBOX_MASTER_KEY=<generate with: Lockbox.generate_key>

# AI Service
AI_SERVICE_URL=https://ai.yourdomain.com
AI_SERVICE_TIMEOUT=120

# URLs
APP_URL=https://api.yourdomain.com
FRONTEND_URL=https://app.yourdomain.com

# CORS
CORS_ORIGINS=https://app.yourdomain.com

# Demo mode
DEMO_MODE=false
```

**Python (.env.production):**
```bash
# Environment
ENVIRONMENT=production
DEBUG=false

# Anthropic
ANTHROPIC_API_KEY=your_production_key
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Server
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Demo mode
DEMO_MODE=false

# CORS
CORS_ORIGINS=https://api.yourdomain.com,https://app.yourdomain.com
```

---

### Step 3: Deploy Rails API

**Using Ubuntu Server with Nginx + Puma:**

```bash
# 1. Install dependencies
sudo apt update
sudo apt install -y ruby ruby-dev build-essential postgresql-client libpq-dev nginx

# 2. Install bundler
gem install bundler

# 3. Clone and setup
cd /var/www/shopify-analytics
git clone <your-repo>
cd rails_api
bundle install --without development test

# 4. Setup database
RAILS_ENV=production rails db:create db:migrate

# 5. Precompile assets (if any)
RAILS_ENV=production rails assets:precompile

# 6. Configure Puma
# Create config/puma/production.rb
```

**Puma Configuration (config/puma/production.rb):**
```ruby
workers ENV.fetch("WEB_CONCURRENCY") { 2 }
threads_count = ENV.fetch("RAILS_MAX_THREADS") { 5 }
threads threads_count, threads_count

port ENV.fetch("PORT") { 3000 }
environment ENV.fetch("RAILS_ENV") { "production" }

pidfile ENV.fetch("PIDFILE") { "tmp/pids/server.pid" }

preload_app!

on_worker_boot do
  ActiveRecord::Base.establish_connection if defined?(ActiveRecord)
end
```

**Nginx Configuration:**
```nginx
upstream rails_app {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    root /var/www/shopify-analytics/rails_api/public;

    location / {
        proxy_pass http://rails_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Systemd Service (rails-api.service):**
```ini
[Unit]
Description=Shopify Analytics Rails API
After=network.target postgresql.service

[Service]
Type=simple
User=deploy
WorkingDirectory=/var/www/shopify-analytics/rails_api
Environment="RAILS_ENV=production"
EnvironmentFile=/var/www/shopify-analytics/rails_api/.env.production
ExecStart=/usr/local/bin/bundle exec puma -C config/puma/production.rb
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start services:**
```bash
sudo systemctl enable rails-api
sudo systemctl start rails-api
sudo systemctl enable nginx
sudo systemctl restart nginx
```

---

### Step 4: Deploy Python AI Service

**Using Gunicorn:**

```bash
# 1. Install Python and dependencies
cd /var/www/shopify-analytics/ai_service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 2. Test run
gunicorn main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

**Systemd Service (ai-service.service):**
```ini
[Unit]
Description=Shopify Analytics AI Service
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/var/www/shopify-analytics/ai_service
Environment="PATH=/var/www/shopify-analytics/ai_service/venv/bin"
EnvironmentFile=/var/www/shopify-analytics/ai_service/.env.production
ExecStart=/var/www/shopify-analytics/ai_service/venv/bin/gunicorn main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 180 --access-logfile /var/log/ai-service/access.log --error-logfile /var/log/ai-service/error.log
Restart=always

[Install]
WantedBy=multi-user.target
```

**Nginx Configuration for AI Service:**
```nginx
upstream ai_service {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name ai.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/ai.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ai.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://ai_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 180s;
        proxy_connect_timeout 180s;
    }
}
```

**Start service:**
```bash
sudo systemctl enable ai-service
sudo systemctl start ai-service
```

---

## 🔒 SSL Certificates

**Using Let's Encrypt (Free):**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificates
sudo certbot --nginx -d api.yourdomain.com
sudo certbot --nginx -d ai.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## 📊 Monitoring Setup

### 1. Log Aggregation

**Papertrail Setup:**
```bash
# Install remote_syslog2
wget https://github.com/papertrail/remote_syslog2/releases/download/v0.20/remote_syslog_linux_amd64.tar.gz
tar xzf remote_syslog*.tar.gz
sudo cp remote_syslog/remote_syslog /usr/local/bin/

# Configure
sudo nano /etc/log_files.yml
```

**log_files.yml:**
```yaml
files:
  - /var/www/shopify-analytics/rails_api/log/production.log
  - /var/log/ai-service/*.log
destination:
  host: logs.papertrailapp.com
  port: YOUR_PORT
  protocol: tls
```

### 2. Application Monitoring

**New Relic APM:**
```ruby
# Gemfile
gem 'newrelic_rpm'
```

```python
# requirements.txt
newrelic
```

### 3. Uptime Monitoring
- UptimeRobot (free)
- Pingdom
- StatusCake

Configure health check endpoints:
- https://api.yourdomain.com/health
- https://ai.yourdomain.com/health

---

## 💾 Backup Strategy

### Database Backups

**Automated PostgreSQL Backup:**
```bash
#!/bin/bash
# /usr/local/bin/backup-db.sh

BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DATABASE="shopify_analytics_production"

# Create backup
pg_dump $DATABASE | gzip > "$BACKUP_DIR/backup_$DATE.sql.gz"

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/backup_$DATE.sql.gz" s3://your-bucket/backups/
```

**Cron job:**
```bash
# Run daily at 2 AM
0 2 * * * /usr/local/bin/backup-db.sh
```

---

## 🚨 Monitoring & Alerts

### Setup Email Alerts

**Rails Exception Notification:**
```ruby
# Gemfile
gem 'exception_notification'

# config/environments/production.rb
config.middleware.use ExceptionNotification::Rack,
  email: {
    email_prefix: '[Shopify Analytics Error] ',
    sender_address: %{"notifier" <notifier@yourdomain.com>},
    exception_recipients: %w{admin@yourdomain.com}
  }
```

---

## 🔄 Continuous Deployment

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy Rails API
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PRODUCTION_HOST }}
          username: deploy
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /var/www/shopify-analytics/rails_api
            git pull origin main
            bundle install
            RAILS_ENV=production rails db:migrate
            sudo systemctl restart rails-api
      
      - name: Deploy AI Service
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PRODUCTION_HOST }}
          username: deploy
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /var/www/shopify-analytics/ai_service
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart ai-service
```

---

## 🐛 Post-Deployment Testing

```bash
# Test Rails API
curl https://api.yourdomain.com/health

# Test AI Service
curl https://ai.yourdomain.com/health

# Test full flow
curl -X POST https://api.yourdomain.com/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 5 products last week"}'
```

---

## 📈 Scaling Considerations

### Horizontal Scaling
- Add more Puma workers
- Add more Gunicorn workers
- Use load balancer (Nginx/HAProxy)
- Deploy multiple instances

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Add Redis caching
- Use CDN

### Database Scaling
- Read replicas
- Connection pooling (PgBouncer)
- Query optimization
- Database partitioning

---

## 🎓 Best Practices

1. **Always use HTTPS in production**
2. **Set strong secrets and rotate regularly**
3. **Monitor logs and metrics daily**
4. **Test deployments in staging first**
5. **Keep dependencies updated**
6. **Use environment variables, never hardcode**
7. **Implement rate limiting**
8. **Setup automated backups**
9. **Document all deployment procedures**
10. **Have a rollback plan**

---

## 📞 Support

For deployment issues:
1. Check logs: `/var/log/nginx/`, service logs
2. Verify environment variables
3. Check service status: `systemctl status rails-api`
4. Test connectivity between services
5. Review SSL certificate expiration

---

**Deployment Checklist:**
- [ ] Production database setup
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Services running via systemd
- [ ] Nginx configured and running
- [ ] Monitoring setup
- [ ] Backups automated
- [ ] Health checks passing
- [ ] Documentation updated
- [ ] Team notified

---

**Note:** This is a general deployment guide. Adjust based on your specific infrastructure and requirements.