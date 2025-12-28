# 🚀 Welcome to Shopify Analytics AI!

This is an AI-powered analytics system that transforms natural language questions into actionable business insights using a 5-stage Claude AI pipeline.

## ⚡ Quick Start (5 Minutes)

### 1. Install Prerequisites

**Windows:**
- Ruby 3.3.10: https://rubyinstaller.org/downloads/ → Get "Ruby+Devkit 3.3.10-1 (x64)"
- Python 3.11: https://www.python.org/downloads/ → Get "Python 3.11.9"

**Important:** When installing Ruby, run `ridk install` and choose option `3`

### 2. Setup & Run

```powershell
# Navigate to project
cd shopify-ai-analytics

# Setup Rails API
cd rails_api
gem install bundler -v 2.5.23
bundle install
bundle exec rails db:create db:migrate

# Setup Python (in new terminal)
cd ai_service
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Start Rails (Terminal 1)
cd rails_api
bundle exec rails s

# Start Python (Terminal 2)
cd ai_service
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```

### 3. Test It Works

```powershell
# In a new terminal
curl http://localhost:3000/health
curl http://localhost:8000/health

# Try a query!
curl -X POST http://localhost:3000/api/v1/questions `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Top 5 selling products last week\"}'
```

---

## 📖 What This Does

Ask questions in plain English:
- "How many units of Blue T-Shirt will I need next month?"
- "Which products will go out of stock in 7 days?"
- "Top 5 selling products last week"
- "Which customers placed repeat orders?"

Get AI-powered insights:
- Inventory forecasts with linear regression
- Smart recommendations
- Business-friendly explanations
- Confidence scores

---

## 🎯 Features

✅ **5-Stage AI Pipeline**
1. Intent Classification
2. Query Planning
3. Analytics Query Generation
4. Forecasting & Execution
5. Insight Synthesis

✅ **Demo Mode** - Works without real data  
✅ **Inventory Forecasting** - Predicts future needs  
✅ **Sales Analysis** - Identifies trends  
✅ **Customer Insights** - Analyzes behavior  

---

## 📁 Project Structure

```
shopify-ai-analytics/
├── rails_api/           # Ruby on Rails API (Port 3000)
│   ├── app/            # Controllers, models, services
│   ├── config/         # Configuration files
│   ├── db/             # Database & migrations
│   └── .env            # Environment config (create this!)
│
├── ai_service/         # Python AI Service (Port 8000)
│   ├── agent/          # 5-stage AI pipeline
│   ├── models/         # Request/response models
│   ├── config.py       # Service configuration
│   └── .env            # Environment config (create this!)
│
└── docs/               # Documentation
    ├── COMPLETE_SETUP_GUIDE.md  ← **START HERE!**
    ├── API_EXAMPLES.md
    ├── ARCHITECTURE.md
    └── TROUBLESHOOTING.md
```

---

## ⚙️ Configuration Files Needed

### `rails_api/.env`
```bash
DEMO_MODE=true
AI_SERVICE_URL=http://localhost:8000
LOCKBOX_MASTER_KEY=2408364e2c2459b6a9adf829e6594e78b7b1d51a0bf075d40397498cfde67a91
SECRET_KEY_BASE=your_secret_key_here
```

### `ai_service/.env`
```bash
ANTHROPIC_API_KEY=your_api_key_here
DEMO_MODE=true
ENVIRONMENT=development
DEBUG=true
```

**Note:** Get Anthropic API key from https://console.anthropic.com/ ($5 minimum)

---

## 🧪 Example Queries

```powershell
# Inventory Forecasting
curl -X POST http://localhost:3000/api/v1/questions `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"How many units of Blue T-Shirt will I need next month?\"}'

# Low Stock Alert
curl -X POST http://localhost:3000/api/v1/questions `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Which products will go out of stock in 7 days?\"}'

# Top Products
curl -X POST http://localhost:3000/api/v1/questions `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Top 5 selling products last week\"}'
```

---

## 🐛 Troubleshooting

**Ruby gems won't install?**
```powershell
ridk install
# Choose option: 3
```

**Python packages fail?**
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Port already in use?**
```powershell
# Kill process on port 3000 or 8000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**More help?** See `docs/COMPLETE_SETUP_GUIDE.md`

---

## 📊 Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| API | Ruby on Rails | 8.0.4 |
| AI Service | Python + FastAPI | 3.11 + 0.115.5 |
| LLM | Claude Sonnet 4 | Latest |
| Forecasting | NumPy | 2.2.1 |
| Database | SQLite3 | 2.9.0 |

---

## 📈 System Architecture

```
User Question
     ↓
Rails API (3000)
     ↓
Python AI Service (8000)
     ↓
5-Stage Pipeline:
  1. Intent Classification
  2. Query Planning
  3. Query Generation
  4. Execution + Forecasting
  5. Insight Synthesis
     ↓
Claude Sonnet 4 API
     ↓
Business Insights
```

---

## 🎓 Learning Path

1. **Start Here:** `docs/COMPLETE_SETUP_GUIDE.md`
2. **Try Examples:** `docs/API_EXAMPLES.md`
3. **Understand Design:** `docs/ARCHITECTURE.md`
4. **Fix Issues:** `docs/TROUBLESHOOTING.md`

---

## 💰 Costs

**Development/Testing:**
- Demo Mode: **FREE** (no API key needed)
- With Claude API: ~$0.01 per query
- $5 credit = ~500 queries

**Production:**
- Depends on usage volume
- Can optimize with caching
- API costs scale linearly

---

## ✅ Setup Checklist

- [ ] Ruby 3.3.10 installed
- [ ] Python 3.11+ installed
- [ ] DevKit installed (ridk option 3)
- [ ] Both `.env` files created
- [ ] `bundle install` completed
- [ ] `pip install` completed
- [ ] Database migrated
- [ ] Both servers running
- [ ] Health checks pass
- [ ] Test query works

**All checked?** You're ready to go! 🎉

---

## 🔗 Important Links

- **Get Ruby:** https://rubyinstaller.org/downloads/
- **Get Python:** https://www.python.org/downloads/
- **Get API Key:** https://console.anthropic.com/
- **Rails Docs:** https://rubyonrails.org/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Claude Docs:** https://docs.anthropic.com/

---

## 🎯 What's Next?

After setup:
1. ✅ Try all example queries
2. ✅ Read the architecture docs
3. ✅ Get an Anthropic API key ($5)
4. ✅ Customize for your needs
5. ✅ Build something amazing!

---

## 📞 Need Help?

1. Check `docs/TROUBLESHOOTING.md`
2. Review error messages
3. Check logs: `rails_api/log/development.log`
4. Verify both services are running

---

## 🏆 Success Criteria

Your system is working when:
- ✅ http://localhost:3000/health returns "OK"
- ✅ http://localhost:8000/health returns healthy status
- ✅ Test queries return JSON insights
- ✅ No error messages in terminals

**Got all checks?** Congratulations! 🚀

---

## 📄 License

MIT License - Free to use, modify, and distribute

---

**Happy Building!** 🎉

Made with ❤️ using Ruby on Rails, Python, and Claude AI