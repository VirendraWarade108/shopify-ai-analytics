# Shopify Analytics AI

AI-powered analytics query processing system with a 5-stage LLM agent pipeline using Claude Sonnet 4.

## 🎯 Project Overview

This system transforms natural language questions into actionable business insights by:
1. **Intent Classification** - Understanding what users are asking
2. **Query Planning** - Determining data sources and aggregations
3. **ShopifyQL Generation** - Creating analytics queries
4. **Query Execution** - Running queries with forecasting (linear regression)
5. **Insight Synthesis** - Converting data into business-friendly language

## 🏗️ Architecture
```
┌─────────────────┐         ┌──────────────────┐
│   Rails API     │────────▶│  Python AI       │
│   (Port 3000)   │         │  Service         │
│                 │         │  (Port 8000)     │
│ - OAuth Gateway │         │                  │
│ - Validation    │         │ - 5-Stage Agent  │
│ - History       │         │ - Claude API     │
│ - Token Store   │         │ - Forecasting    │
└─────────────────┘         └──────────────────┘
        │                            │
        │                            │
        ▼                            ▼
   SQLite DB                  Anthropic API
```

## 📋 Tech Stack

### Rails API
- **Framework**: Rails 7.1.0, Ruby 3.2.0
- **Database**: SQLite3
- **Auth**: Shopify OAuth via `shopify_app` gem
- **Security**: Lockbox encryption for tokens
- **HTTP Client**: Faraday

### Python AI Service
- **Framework**: FastAPI 0.104.1
- **LLM**: Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- **Forecasting**: NumPy (linear regression)
- **Logging**: Structlog (JSON format)
- **Validation**: Pydantic

## 🚀 Quick Start

### Prerequisites
- Ruby 3.2.0
- Python 3.10+
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

**1. Clone and setup Rails API:**
```bash
cd rails_api
bundle install
cp .env.example .env

# Edit .env and set your Shopify credentials (or use demo mode)
# Generate encryption key:
bundle exec rails runner "puts Lockbox.generate_key"
# Add it to .env as LOCKBOX_MASTER_KEY

# Setup database
rails db:migrate

# Start Rails server
rails s
```

**2. Setup Python AI Service:**
```bash
cd ai_service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Edit .env and set:
# ANTHROPIC_API_KEY=your_key_here

# Start AI service
uvicorn main:app --reload --port 8000
```

**3. Test the setup:**
```bash
# Health checks
curl http://localhost:3000/health
curl http://localhost:8000/health

# Test query (demo mode)
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many units of Blue T-Shirt will I need next month?"
  }'
```

## 📝 Supported Questions

The system handles 5 types of analytics questions:

1. **Inventory Forecasting**
   - "How many units of Product X will I need next month?"
   - "How much inventory should I reorder?"

2. **Inventory Status**
   - "Which products will go out of stock in 7 days?"
   - "What's my current stock level for Product X?"

3. **Sales Analysis**
   - "Top 5 selling products last week"
   - "What were my best sellers in November?"

4. **Customer Analysis**
   - "Which customers placed repeat orders in last 90 days?"
   - "Who are my top customers by order count?"

5. **Product Ranking**
   - "Show me products ranked by revenue"
   - "What are my worst performing products?"

## 🔑 API Endpoints

### Rails API (Port 3000)

**POST /api/v1/questions**
```json
{
  "question": "How many Blue T-Shirts will I need next month?"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "question": "...",
    "status": "completed",
    "intent": { "domain": "inventory_forecasting", "confidence": 0.92 },
    "insights": {
      "summary": "You'll need approximately 300 Blue T-Shirts next month",
      "key_findings": [
        "You sell about 8 Blue T-Shirts per day",
        "Based on 90 days of sales history",
        "Includes 50 units of safety stock"
      ],
      "recommendations": [
        "Order 300 units to cover next month's demand"
      ]
    },
    "confidence": 0.88
  }
}
```

**GET /api/v1/questions** - List query history

**GET /api/v1/questions/:id** - Get specific query details

**GET /auth/shopify** - Initiate Shopify OAuth

### Python AI Service (Port 8000)

**POST /api/v1/query** - Process analytics question

**GET /health** - Health check

**GET /** - Service information

## 🎯 Demo Mode

Demo mode allows testing without real Shopify API credentials:

**Rails (.env):**
```bash
DEMO_MODE=true
```

**Python (.env):**
```bash
DEMO_MODE=true
```

In demo mode:
- Synthetic data is generated for all queries
- No Shopify OAuth required
- Uses simulated sales/inventory data

## 🔮 Forecasting

The system uses **linear regression** for inventory forecasting:

1. **Historical Data**: Analyzes last 90 days of sales
2. **Trend Calculation**: NumPy linear regression
3. **Projection**: Forecasts next 30 days
4. **Safety Stock**: Adds 20% buffer
5. **Output**: Business-friendly recommendations

Example:
```
Historical: 8 units/day average
Forecast: 240 units (30 days × 8)
Safety Stock: 48 units (20% buffer)
Recommendation: Order 288 units
```

## 🛡️ Security

- **Token Encryption**: Lockbox gem encrypts Shopify access tokens
- **CSRF Protection**: Rails CSRF tokens for session-based requests
- **CORS**: Configured for specified origins only
- **Input Validation**: Pydantic models validate all inputs
- **SQL Injection**: ActiveRecord prevents SQL injection
- **Rate Limiting**: Can be added via Rack::Attack (optional)

## 📊 Database Schema

**shops**
- `shopify_domain` (unique)
- `shopify_token_ciphertext` (encrypted)
- `active` (boolean)
- Timestamps

**analytics_queries**
- `shop_id` (foreign key)
- `question` (text)
- `status` (pending/completed/failed)
- `intent` (JSON)
- `shopifyql_query` (text)
- `insights` (JSON)
- `confidence_score` (decimal)
- Timestamps

## 🧪 Testing

### Manual Testing
```bash
# Test Rails API
cd rails_api
curl http://localhost:3000/health

# Test Python service
cd ai_service
curl http://localhost:8000/health

# Test full flow
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 5 products last week"}'
```

### Automated Testing
```bash
# Rails
cd rails_api
bundle exec rspec

# Python
cd ai_service
pytest
```

## 🐛 Troubleshooting

**Rails won't start:**
- Check Ruby version: `ruby -v` (need 3.2.0)
- Run `bundle install`
- Check database: `rails db:migrate`

**Python service fails:**
- Check Python version: `python --version` (need 3.10+)
- Activate venv: `source venv/bin/activate`
- Install deps: `pip install -r requirements.txt`
- Check ANTHROPIC_API_KEY in .env

**"AI service timeout":**
- Increase timeout in Rails: `AI_SERVICE_TIMEOUT=180`
- Check Python service is running: `curl http://localhost:8000/health`

**"Invalid API key":**
- Verify ANTHROPIC_API_KEY is set correctly
- Test key: `curl https://api.anthropic.com/v1/messages -H "x-api-key: YOUR_KEY"`

## 📚 Documentation

- [Setup Guide](SETUP.md) - Detailed installation
- [API Examples](API_EXAMPLES.md) - Request/response examples
- [Architecture](ARCHITECTURE.md) - System design details
- [Project Summary](PROJECT_SUMMARY.md) - Interview presentation

## 🤝 Contributing

This is an interview assignment project. For questions, contact the candidate.

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- Built with Claude Sonnet 4 by Anthropic
- Shopify OAuth via shopify_app gem
- FastAPI for Python API framework