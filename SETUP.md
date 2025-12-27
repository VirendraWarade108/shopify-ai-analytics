# Setup Guide

Complete installation and configuration guide for the Shopify Analytics AI system.

## System Requirements

### Hardware
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **CPU**: Any modern processor

### Software
- **Operating System**: macOS, Linux, or Windows
- **Ruby**: 3.2.0
- **Python**: 3.10 or higher
- **Git**: Latest version
- **cURL**: For API testing

## Step-by-Step Installation

### 1. Clone the Repository
```bash
# Clone or extract the project
cd shopify-analytics-ai
```

### 2. Rails API Setup

#### 2.1 Install Ruby Dependencies
```bash
cd rails_api

# Install bundler if not already installed
gem install bundler

# Install gems
bundle install
```

#### 2.2 Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Generate encryption key for Lockbox
bundle exec rails runner "puts Lockbox.generate_key"

# Edit .env and set the following:
nano .env
```

Required `.env` configuration:
```bash
# Copy the generated key here
LOCKBOX_MASTER_KEY=your_generated_key_here

# For demo mode (no real Shopify API)
DEMO_MODE=true

# For production with real Shopify
DEMO_MODE=false
SHOPIFY_API_KEY=your_shopify_api_key
SHOPIFY_API_SECRET=your_shopify_api_secret
SHOPIFY_SCOPES=read_products,read_orders,read_customers,read_analytics
```

#### 2.3 Setup Database
```bash
# Create and migrate database
rails db:create
rails db:migrate

# Verify schema
rails db:schema:dump
```

#### 2.4 Start Rails Server
```bash
# Start on default port 3000
rails s

# Or specify port
rails s -p 3000
```

Verify Rails is running:
```bash
curl http://localhost:3000/health
# Should return: OK
```

### 3. Python AI Service Setup

#### 3.1 Create Virtual Environment
```bash
cd ai_service

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 3.2 Install Python Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

#### 3.3 Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env
nano .env
```

Required `.env` configuration:
```bash
# Get your API key from: https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Demo mode (uses synthetic data)
DEMO_MODE=true

# Service configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

#### 3.4 Start Python Service
```bash
# Start with uvicorn
uvicorn main:app --reload --port 8000

# Or run directly
python main.py
```

Verify Python service is running:
```bash
curl http://localhost:8000/health
# Should return JSON with status: "healthy"
```

## Verification & Testing

### Test Both Services
```bash
# Test Rails API
curl http://localhost:3000/health

# Test Python AI Service
curl http://localhost:8000/health

# Test full integration
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "How many Blue T-Shirts will I need next month?"}'
```

### Expected Response
```json
{
  "success": true,
  "data": {
    "id": 1,
    "question": "How many Blue T-Shirts will I need next month?",
    "status": "completed",
    "intent": {
      "domain": "inventory_forecasting",
      "confidence": 0.92
    },
    "insights": {
      "summary": "You'll need approximately 300 Blue T-Shirts next month",
      "key_findings": [
        "You sell about 8 Blue T-Shirts per day",
        "Based on 90 days of sales history"
      ],
      "recommendations": [
        "Order 300 units to cover next month's demand"
      ]
    },
    "confidence": 0.88
  }
}
```

## Configuration Options

### Rails API Configuration

**Database**: `config/database.yml`
```yaml
development:
  adapter: sqlite3
  database: db/development.sqlite3
```

**Routes**: `config/routes.rb`
- View available routes: `rails routes`

**CORS**: `config/initializers/cors.rb`
- Add allowed origins as needed

### Python AI Service Configuration

**Settings**: `config.py`
```python
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
FORECAST_DAYS = 30
HISTORICAL_DAYS = 90
SAFETY_STOCK_MULTIPLIER = 1.2
```

**Logging**: Set `LOG_FORMAT` in `.env`
- `json` - Structured JSON logs (production)
- `console` - Human-readable logs (development)

## Production Deployment

### Rails API
```bash
# Set production environment
export RAILS_ENV=production
export SECRET_KEY_BASE=$(rails secret)

# Use PostgreSQL instead of SQLite
# Update config/database.yml

# Precompile assets (if needed)
rails assets:precompile

# Run migrations
rails db:migrate

# Start with production server (Puma)
bundle exec puma -C config/puma.rb
```

### Python AI Service
```bash
# Set production environment
export ENVIRONMENT=production
export DEBUG=false

# Use Gunicorn for production
pip install gunicorn

# Start with Gunicorn
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

## Troubleshooting

### Rails Issues

**"Bundle install fails"**
```bash
# Update bundler
gem update --system
gem install bundler

# Clear bundle cache
bundle clean --force
bundle install
```

**"Database migration fails"**
```bash
# Drop and recreate database
rails db:drop db:create db:migrate
```

**"Lockbox encryption error"**
```bash
# Generate new key
bundle exec rails runner "puts Lockbox.generate_key"
# Update LOCKBOX_MASTER_KEY in .env
```

### Python Issues

**"Module not found"**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

**"Anthropic API error"**
```bash
# Test API key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}'
```

**"Port already in use"**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --reload --port 8001
```

## Next Steps

1. Review [API Examples](API_EXAMPLES.md) for usage patterns
2. Read [Architecture](ARCHITECTURE.md) for system design
3. Check [Project Summary](PROJECT_SUMMARY.md) for overview

## Getting Help

- Check logs: `tail -f rails_api/log/development.log`
- Python logs: Stdout when running `uvicorn`
- Health checks: `/health` endpoints