# Troubleshooting Guide

Common issues and solutions for Shopify Analytics AI system.

## 🔍 Quick Diagnostics

### Check System Status

```bash
# Check if Rails is running
curl http://localhost:3000/health

# Check if Python service is running
curl http://localhost:8000/health

# Check processes
ps aux | grep rails
ps aux | grep uvicorn

# Check ports
lsof -i :3000
lsof -i :8000
```

---

## 🚨 Common Issues

### Issue 1: Rails Server Won't Start

#### Error: `ruby version mismatch`
```
Your Ruby version is 3.1.0, but your Gemfile specified 3.2.0
```

**Solution:**
```bash
# Install correct Ruby version using rbenv
rbenv install 3.2.0
rbenv local 3.2.0

# Or using rvm
rvm install 3.2.0
rvm use 3.2.0
```

---

#### Error: `Could not find gem`
```
Could not find gem 'rails (~> 7.1.0)' in locally installed gems
```

**Solution:**
```bash
cd rails_api
bundle install

# If bundle install fails
gem install bundler
bundle update
bundle install
```

---

#### Error: `Lockbox master key not configured`
```
Lockbox::Error: LOCKBOX_MASTER_KEY not set
```

**Solution:**
```bash
# Generate a new key
bundle exec rails runner "puts Lockbox.generate_key"

# Add to .env file
echo "LOCKBOX_MASTER_KEY=<generated_key>" >> .env

# Restart Rails
rails s
```

---

#### Error: `Database does not exist`
```
ActiveRecord::NoDatabaseError: database "development" does not exist
```

**Solution:**
```bash
cd rails_api
rails db:create
rails db:migrate

# If still failing, drop and recreate
rails db:drop db:create db:migrate
```

---

#### Error: `Port 3000 already in use`
```
Address already in use - bind(2) for "127.0.0.1" port 3000
```

**Solution:**
```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use different port
rails s -p 3001
```

---

### Issue 2: Python AI Service Won't Start

#### Error: `python version too old`
```
Python 3.8 detected, but 3.10+ required
```

**Solution:**
```bash
# Install Python 3.10+
# On Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv

# On macOS with Homebrew
brew install python@3.10

# Verify
python3.10 --version
```

---

#### Error: `No module named 'fastapi'`
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
cd ai_service

# Make sure virtual environment is activated
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt

# If still failing, reinstall everything
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

#### Error: `Anthropic API key not configured`
```
ValueError: ANTHROPIC_API_KEY not set
```

**Solution:**
```bash
# Add to .env file
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env

# Verify it's set
grep ANTHROPIC_API_KEY .env

# Restart service
uvicorn main:app --reload --port 8000
```

---

#### Error: `Port 8000 already in use`
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --reload --port 8001

# Update Rails .env to point to new port
# AI_SERVICE_URL=http://localhost:8001
```

---

### Issue 3: API Request Failures

#### Error: `AI service timeout`
```
Faraday::TimeoutError: AI service request timed out after 120 seconds
```

**Solution:**
```bash
# Increase timeout in Rails .env
echo "AI_SERVICE_TIMEOUT=180" >> rails_api/.env

# Check if Python service is actually running
curl http://localhost:8000/health

# Check Python service logs for errors
# (look at terminal where uvicorn is running)

# Test Python service directly
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "shop_domain": "demo.myshopify.com", "access_token": "demo"}'
```

---

#### Error: `Connection refused`
```
Failed to open TCP connection to localhost:8000
```

**Solution:**
```bash
# Verify Python service is running
curl http://localhost:8000/health

# If not running, start it
cd ai_service
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Check if firewall is blocking
sudo ufw status
sudo ufw allow 8000
```

---

#### Error: `Invalid Anthropic API key`
```
anthropic.AuthenticationError: Invalid API Key
```

**Solution:**
```bash
# Verify your API key
# 1. Go to https://console.anthropic.com/
# 2. Check API Keys section
# 3. Generate new key if needed

# Update .env
echo "ANTHROPIC_API_KEY=sk-ant-your-new-key" > ai_service/.env

# Restart Python service
```

---

#### Error: `CORS policy blocked`
```
Access to fetch at 'http://localhost:3000' blocked by CORS policy
```

**Solution:**
```bash
# Add origin to Rails CORS config
# Edit rails_api/config/initializers/cors.rb

# Or add to .env
echo "CORS_ORIGINS=http://localhost:3001,http://localhost:3000" >> rails_api/.env

# Restart Rails
```

---

### Issue 4: Database Issues

#### Error: `Table doesn't exist`
```
ActiveRecord::StatementInvalid: SQLite3::SQLException: no such table: shops
```

**Solution:**
```bash
cd rails_api

# Run migrations
rails db:migrate

# If schema is corrupted, reset
rails db:drop db:create db:migrate

# In production, never drop - only migrate!
```

---

#### Error: `Column not found`
```
ActiveRecord::StatementInvalid: no such column: analytics_queries.insights
```

**Solution:**
```bash
# Check if migrations are up to date
rails db:migrate:status

# Run pending migrations
rails db:migrate

# If migration file is missing, regenerate
rails db:schema:load
```

---

#### Error: `Database locked`
```
SQLite3::BusyException: database is locked
```

**Solution:**
```bash
# Stop all Rails processes
pkill -f rails

# Remove lock file
rm db/*.sqlite3-journal

# Restart Rails
rails s

# For production, use PostgreSQL instead of SQLite
```

---

### Issue 5: Demo Mode Issues

#### Error: `Demo data not generating`
```
No data returned in demo mode
```

**Solution:**
```bash
# Verify DEMO_MODE is enabled
# In rails_api/.env
echo "DEMO_MODE=true" >> rails_api/.env

# In ai_service/.env
echo "DEMO_MODE=true" >> ai_service/.env

# Restart both services

# Test directly
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 5 products"}'
```

---

#### Error: `Shopify authentication required`
```
Unauthorized: Shop authentication required
```

**Solution:**
```bash
# Make sure DEMO_MODE=true in rails_api/.env
grep DEMO_MODE rails_api/.env

# If false, change to true
sed -i 's/DEMO_MODE=false/DEMO_MODE=true/' rails_api/.env

# Restart Rails
```

---

### Issue 6: Performance Issues

#### Error: `Slow query responses (>10 seconds)`

**Solution:**
```bash
# Check Python service logs for bottlenecks

# Reduce forecast days
echo "FORECAST_DAYS=15" >> ai_service/.env
echo "HISTORICAL_DAYS=45" >> ai_service/.env

# Increase workers (if you have multiple CPUs)
# Gunicorn: --workers 4
# Puma: workers 4

# Check Claude API rate limits
# May need to wait if rate limited

# Add Redis caching (advanced)
# gem 'redis'
# gem 'redis-rails'
```

---

## 🔧 Development Tools

### Debugging Rails

```bash
# Start Rails in debug mode
rails s --debugger

# Access Rails console
rails console

# Check logs
tail -f log/development.log

# Test specific route
rails routes | grep questions
```

### Debugging Python

```bash
# Run with debug logging
LOG_LEVEL=DEBUG uvicorn main:app --reload

# Python interactive debugging
python -m pdb main.py

# Check logs
# Logs print to stdout by default
```

---

## 📊 Monitoring & Logging

### Check Rails Logs
```bash
# Development log
tail -f rails_api/log/development.log

# Production log
tail -f rails_api/log/production.log

# Search for errors
grep -i error rails_api/log/development.log

# Search for specific query
grep "query_id.*123" rails_api/log/development.log
```

### Check Python Logs
```bash
# Python logs to stdout
# Redirect to file when running:
uvicorn main:app --reload 2>&1 | tee ai_service.log

# Search logs
grep -i error ai_service.log
grep "stage_.*completed" ai_service.log
```

---

## 🧪 Testing Endpoints

### Test Rails API
```bash
# Health check
curl http://localhost:3000/health

# Create question
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}' | jq .

# Get query history
curl http://localhost:3000/api/v1/questions | jq .
```

### Test Python AI Service
```bash
# Health check
curl http://localhost:8000/health | jq .

# Service info
curl http://localhost:8000/ | jq .

# Direct query (bypass Rails)
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Top 5 products",
    "shop_domain": "demo.myshopify.com",
    "access_token": "demo"
  }' | jq .
```

---

## 🔄 Reset Everything

If all else fails, complete reset:

```bash
# 1. Stop all services
pkill -f rails
pkill -f uvicorn

# 2. Clean Rails
cd rails_api
rm -rf log/*.log tmp/cache/* tmp/pids/*
rails db:drop db:create db:migrate
bundle install

# 3. Clean Python
cd ai_service
rm -rf __pycache__
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Verify .env files exist and have correct values

# 5. Start services fresh
# Terminal 1:
cd rails_api && rails s

# Terminal 2:
cd ai_service && source venv/bin/activate && uvicorn main:app --reload --port 8000

# 6. Test
curl http://localhost:3000/health
curl http://localhost:8000/health
```

---

## 📞 Getting Help

### Information to Gather

When reporting issues:

1. **Environment:**
   - OS version
   - Ruby version: `ruby -v`
   - Python version: `python --version`
   - Rails version: `rails -v`

2. **Error Message:**
   - Full error text
   - Stack trace
   - Relevant logs

3. **Reproduction Steps:**
   - What you were doing
   - Command that failed
   - Expected vs actual behavior

4. **Configuration:**
   - Contents of .env files (hide API keys!)
   - Recent changes made

### Diagnostic Script

```bash
#!/bin/bash
# Save as diagnose.sh

echo "=== Environment ==="
echo "OS: $(uname -a)"
echo "Ruby: $(ruby -v 2>&1)"
echo "Python: $(python3 --version 2>&1)"
echo "Rails: $(rails -v 2>&1)"

echo -e "\n=== Processes ==="
echo "Rails: $(ps aux | grep rails | grep -v grep)"
echo "Python: $(ps aux | grep uvicorn | grep -v grep)"

echo -e "\n=== Ports ==="
echo "Port 3000: $(lsof -i :3000 2>&1)"
echo "Port 8000: $(lsof -i :8000 2>&1)"

echo -e "\n=== Services ==="
echo "Rails health: $(curl -s http://localhost:3000/health)"
echo "Python health: $(curl -s http://localhost:8000/health)"

echo -e "\n=== Database ==="
cd rails_api
echo "Migrations: $(rails db:migrate:status 2>&1 | tail -5)"
```

---

## ✅ Health Checklist

Use this checklist to verify system health:

- [ ] Ruby 3.2.0 installed
- [ ] Python 3.10+ installed
- [ ] Rails dependencies installed (`bundle install`)
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Database migrated (`rails db:migrate`)
- [ ] .env files configured
- [ ] ANTHROPIC_API_KEY set
- [ ] LOCKBOX_MASTER_KEY set
- [ ] Rails server running on port 3000
- [ ] Python service running on port 8000
- [ ] Health checks passing
- [ ] Demo mode working
- [ ] No error logs

---

## 🆘 Last Resort

If nothing works:

1. **Check GitHub Issues** - Someone may have had same problem
2. **Review documentation** - README, SETUP, ARCHITECTURE
3. **Clean install** - Follow SETUP.md from scratch
4. **Ask for help** - Provide diagnostic information above

Remember: Most issues are configuration-related. Double-check your .env files!

---

**Quick Reference:**
- Rails API: http://localhost:3000
- Python AI: http://localhost:8000
- Health checks: `/health` endpoints
- Logs: `rails_api/log/` and stdout
- Config: `.env` files