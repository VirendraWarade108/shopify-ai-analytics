# Shopify Analytics AI Service

Python FastAPI service that powers the 5-stage AI agent pipeline for natural language analytics queries.

## 🎯 Overview

This service receives natural language questions about e-commerce analytics and processes them through a sophisticated 5-stage pipeline using Claude Sonnet 4 to generate actionable business insights.

## 🏗️ Architecture

### 5-Stage Agent Pipeline

```
Question → [1] Intent       → [2] Query      → [3] ShopifyQL   → [4] Query      → [5] Insight    → Response
           Classification      Planning         Generation        Execution        Synthesis
           
           ↓ Claude API    ↓ Claude API    ↓ Claude API     ↓ NumPy         ↓ Claude API
           
           Domain & confidence → Data sources → Analytics query → Forecasting → Business language
```

### Stage Details

1. **Intent Classification** (`agent/intent_classifier.py`)
   - Classifies question into domains (inventory, sales, customers)
   - Extracts entities (product names, time periods)
   - Returns confidence score

2. **Query Planning** (`agent/query_planner.py`)
   - Determines required data sources
   - Plans aggregations and filters
   - Decides if forecasting is needed

3. **ShopifyQL Generation** (`agent/shopifyql_generator.py`)
   - Generates Shopify Analytics queries
   - Validates query syntax
   - Optimizes for performance

4. **Query Execution** (`agent/query_executor.py`)
   - Executes queries (demo mode: synthetic data)
   - Applies linear regression forecasting
   - Calculates safety stock

5. **Insight Synthesis** (`agent/insight_synthesizer.py`)
   - Transforms data into business language
   - Generates actionable recommendations
   - Creates summary insights

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Anthropic API key
- Virtual environment (recommended)

### Installation

```bash
# 1. Navigate to service directory
cd ai_service

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
nano .env
```

### Configuration

Edit `.env` file:

```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Server
HOST=0.0.0.0
PORT=8000

# Demo Mode (uses synthetic data)
DEMO_MODE=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Forecasting
FORECAST_DAYS=30
HISTORICAL_DAYS=90
SAFETY_STOCK_MULTIPLIER=1.2
```

### Start Service

```bash
# Development mode with auto-reload
uvicorn main:app --reload --port 8000

# Production mode
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📡 API Endpoints

### Health Check
```bash
GET /health

# Response
{
  "status": "healthy",
  "timestamp": "2024-12-27T10:00:00Z",
  "version": "1.0.0",
  "checks": {
    "anthropic_api_key_configured": true
  }
}
```

### Service Info
```bash
GET /

# Response
{
  "service": "Shopify Analytics AI Service",
  "version": "1.0.0",
  "status": "running",
  "llm_model": "claude-sonnet-4-20250514",
  "agent_pipeline": [
    "1. Intent Classification",
    "2. Query Planning",
    "3. ShopifyQL Generation",
    "4. Query Execution",
    "5. Insight Synthesis"
  ]
}
```

### Process Query
```bash
POST /api/v1/query
Content-Type: application/json

{
  "question": "How many units of Blue T-Shirt will I need next month?",
  "shop_domain": "demo.myshopify.com",
  "access_token": "demo_token"
}

# Response
{
  "status": "completed",
  "intent": {
    "domain": "inventory_forecasting",
    "confidence": 0.92,
    "entities": {
      "product_name": "Blue T-Shirt",
      "time_period": "next month"
    }
  },
  "query": "FROM orders SHOW product_name, SUM(quantity)...",
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
```

## 🔬 Forecasting Algorithm

### Linear Regression Implementation

The service uses NumPy for linear regression forecasting:

```python
# 1. Collect historical sales data (90 days)
# 2. Calculate linear trend
slope, intercept = calculate_linear_regression(X, y)

# 3. Project future values (30 days)
future_values = slope * future_X + intercept

# 4. Add safety stock (20%)
safety_stock = forecast * 0.2
total_needed = forecast + safety_stock
```

### Forecasting Features

- **Historical Analysis:** 90 days of sales data
- **Trend Detection:** Linear regression
- **Future Projection:** 30-day forecast
- **Safety Stock:** 20% buffer for uncertainty
- **Confidence Score:** R-squared calculation
- **Daily Velocity:** Average units per day

## 📊 Demo Mode

Demo mode generates synthetic data for testing without real Shopify API:

### Synthetic Data Features

- Multiple product types (5 products)
- 90 days of historical sales
- Realistic inventory levels
- Customer purchase patterns
- Seasonal variations

### Enable Demo Mode

```bash
# In .env file
DEMO_MODE=true
```

## 🧪 Testing

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test query processing
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Top 5 selling products last week",
    "shop_domain": "demo.myshopify.com",
    "access_token": "demo_token"
  }'
```

### Automated Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=agent --cov-report=html
```

## 📁 Project Structure

```
ai_service/
├── agent/                      # 5-stage agent pipeline
│   ├── __init__.py
│   ├── orchestrator.py        # Coordinates all stages
│   ├── intent_classifier.py   # Stage 1: Intent classification
│   ├── query_planner.py       # Stage 2: Query planning
│   ├── shopifyql_generator.py # Stage 3: Query generation
│   ├── query_executor.py      # Stage 4: Query execution
│   └── insight_synthesizer.py # Stage 5: Insight synthesis
├── models/                     # Pydantic models
│   ├── __init__.py
│   ├── requests.py            # Request validation
│   └── responses.py           # Response schemas
├── utils/                      # Utility functions
│   ├── __init__.py
│   └── logger.py              # Structured logging
├── main.py                     # FastAPI application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | Required. Your Anthropic API key |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Claude model to use |
| `DEMO_MODE` | `true` | Use synthetic data |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FORMAT` | `json` | Log format (json/console) |
| `FORECAST_DAYS` | `30` | Days to forecast |
| `HISTORICAL_DAYS` | `90` | Historical data period |
| `SAFETY_STOCK_MULTIPLIER` | `1.2` | Safety stock percentage |

### Logging Configuration

```python
# JSON format (production)
LOG_FORMAT=json

# Console format (development)
LOG_FORMAT=console
```

Example JSON log:
```json
{
  "timestamp": "2024-12-27T10:00:00Z",
  "level": "INFO",
  "event": "query_completed",
  "question": "Top 5 products",
  "confidence": 0.88,
  "processing_time_ms": 2341
}
```

## 🔒 Security

### Best Practices

1. **API Keys:** Never commit `.env` files
2. **HTTPS:** Use HTTPS in production
3. **Rate Limiting:** Implement rate limiting for production
4. **Input Validation:** All inputs validated with Pydantic
5. **Error Handling:** Comprehensive error handling at each stage

### CORS Configuration

```python
# In config.py
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001"
]
```

## 📈 Performance

### Optimization Tips

1. **Caching:** Implement Redis for query caching
2. **Workers:** Increase Gunicorn workers for scale
3. **Async:** All operations are async-ready
4. **Batching:** Batch similar queries when possible
5. **Timeout:** Adjust `AGENT_TIMEOUT` based on needs

### Typical Response Times

- Intent Classification: ~500ms
- Query Planning: ~600ms
- ShopifyQL Generation: ~700ms
- Query Execution: ~200ms (demo) / ~2s (real)
- Insight Synthesis: ~800ms
- **Total:** ~3-4 seconds

## 🐛 Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check Python version
python3 --version  # Need 3.10+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port availability
lsof -i :8000
```

#### API Key Error

```bash
# Verify API key is set
grep ANTHROPIC_API_KEY .env

# Test API key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

#### Slow Responses

```bash
# Reduce forecast complexity
echo "FORECAST_DAYS=15" >> .env
echo "HISTORICAL_DAYS=45" >> .env

# Increase timeout
echo "AGENT_TIMEOUT=180" >> .env

# Check Claude API rate limits
```

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=DEBUG uvicorn main:app --reload

# View detailed logs
tail -f logs/app.log
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEMO_MODE=false`
- [ ] Use production API keys
- [ ] Set `DEBUG=false`
- [ ] Use `LOG_FORMAT=json`
- [ ] Configure proper `CORS_ORIGINS`
- [ ] Set up monitoring
- [ ] Configure SSL/TLS
- [ ] Implement rate limiting
- [ ] Set up log aggregation
- [ ] Configure health checks

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

```bash
# Build and run
docker build -t shopify-ai-service .
docker run -p 8000:8000 --env-file .env shopify-ai-service
```

## 📚 Dependencies

### Core Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **anthropic** - Claude API client
- **pydantic** - Data validation
- **numpy** - Forecasting calculations
- **structlog** - Structured logging

### Development Dependencies

- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **black** - Code formatting
- **flake8** - Linting
- **mypy** - Type checking

## 🤝 Integration with Rails API

The AI service integrates with the Rails API:

```
Rails API (Port 3000)
    ↓ HTTP POST
Python AI Service (Port 8000)
    ↓ Process through 5 stages
    ↓ Return insights
Rails API
    ↓ Store results
    ↓ Return to client
```

### Communication Flow

1. Rails receives user question
2. Rails calls Python `/api/v1/query` endpoint
3. Python processes through 5-stage pipeline
4. Python returns structured insights
5. Rails stores in database
6. Rails returns to user

## 📖 API Documentation

When running, visit:
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## 🎓 Learning Resources

### Understanding the Pipeline

1. **Intent Classification:** NLP classification with LLMs
2. **Query Planning:** SQL query optimization
3. **ShopifyQL:** Shopify's analytics query language
4. **Linear Regression:** Time series forecasting
5. **Natural Language Generation:** Technical to business language

### Related Technologies

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Claude API Docs: https://docs.anthropic.com/
- NumPy Linear Algebra: https://numpy.org/doc/stable/reference/routines.linalg.html
- Pydantic Validation: https://docs.pydantic.dev/

## 📄 License

MIT License - See LICENSE file in root directory

## 🙋 Support

For issues or questions:
1. Check the logs for errors
2. Review TROUBLESHOOTING.md in root directory
3. Verify environment configuration
4. Test each endpoint individually
5. Check Claude API status

## 🎯 Next Steps

After getting the service running:
1. Explore different question types
2. Experiment with forecasting parameters
3. Try production mode with real Shopify API
4. Implement caching for better performance
5. Add custom domain classifications
6. Extend with additional data sources

---

**Quick Commands:**
```bash
# Start development
uvicorn main:app --reload --port 8000

# Start production
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Run tests
pytest

# Check health
curl http://localhost:8000/health
```

---

**Version:** 1.0.0  
**Last Updated:** December 2024  
**Maintained by:** Virendra Warade