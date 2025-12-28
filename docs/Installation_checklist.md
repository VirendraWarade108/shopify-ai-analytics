# Installation Checklist for Shopify Analytics AI

Use this checklist to track your setup progress:

---

## 📋 Pre-Installation (5 minutes)

- [ ] Downloaded project ZIP file
- [ ] Extracted to desired location (e.g., `D:\Projects\shopify-ai-analytics\`)
- [ ] Opened PowerShell as administrator
- [ ] Have stable internet connection

---

## 🔧 Install Prerequisites (15-20 minutes)

### Ruby Installation
- [ ] Downloaded Ruby+Devkit 3.3.10-1 (x64) from https://rubyinstaller.org/
- [ ] Ran installer
- [ ] Checked "Add Ruby executables to your PATH"
- [ ] Ran `ridk install` at the end
- [ ] Chose option `3` (MSYS2 and MINGW development toolchain)
- [ ] Waited for DevKit installation to complete (5-10 min)
- [ ] Opened NEW PowerShell window
- [ ] Verified: `ruby -v` shows `ruby 3.3.10`
- [ ] Verified: `gem -v` shows gem version
- [ ] Verified: `ridk version` shows Ruby installation details

### Python Installation
- [ ] Downloaded Python 3.11.9 from https://www.python.org/
- [ ] Ran installer
- [ ] Checked "Add Python 3.11 to PATH" ⚠️ IMPORTANT!
- [ ] Clicked "Install Now"
- [ ] Opened NEW PowerShell window
- [ ] Verified: `python --version` shows `Python 3.11.9`
- [ ] Verified: `pip --version` shows pip version

---

## 📁 Project Setup (10-15 minutes)

### Rails API Setup
- [ ] Navigated to `rails_api` directory
- [ ] Installed Bundler: `gem install bundler -v 2.5.23`
- [ ] Created `.env` file in `rails_api/` directory
- [ ] Copied content from setup guide to `.env`
- [ ] Ran `bundle install` (wait 5-10 min)
- [ ] Saw "Bundle complete!" message
- [ ] Ran `bundle exec rails db:create`
- [ ] Ran `bundle exec rails db:migrate`
- [ ] (Optional) Ran `bundle exec rails db:seed`

### Python AI Service Setup
- [ ] Opened NEW PowerShell window
- [ ] Navigated to `ai_service` directory
- [ ] Created virtual environment: `python -m venv venv`
- [ ] Activated venv: `.\venv\Scripts\Activate.ps1`
- [ ] If error: Ran `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- [ ] Activated again: `.\venv\Scripts\Activate.ps1`
- [ ] See `(venv)` in prompt
- [ ] Created `.env` file in `ai_service/` directory
- [ ] Copied content from setup guide to `.env`
- [ ] Updated pip: `python -m pip install --upgrade pip`
- [ ] Ran `pip install -r requirements.txt` (wait 5-10 min)
- [ ] Saw "Successfully installed..." message

---

## 🚀 Start Services (2 minutes)

### Terminal 1: Rails API
- [ ] Navigated to `rails_api` directory
- [ ] Ran `bundle exec rails s`
- [ ] See "Listening on http://127.0.0.1:3000"
- [ ] Left terminal window open

### Terminal 2: Python AI
- [ ] Opened NEW PowerShell window
- [ ] Navigated to `ai_service` directory
- [ ] Activated venv: `.\venv\Scripts\Activate.ps1`
- [ ] Ran `uvicorn main:app --reload --port 8000`
- [ ] See "Application startup complete"
- [ ] Left terminal window open

---

## 🧪 Testing (3 minutes)

### Health Checks
- [ ] Opened NEW PowerShell window (Terminal 3)
- [ ] Ran: `curl http://localhost:3000/health`
- [ ] Got response: `OK`
- [ ] Ran: `curl http://localhost:8000/health`
- [ ] Got JSON response with `"status": "healthy"`

### Test Query
- [ ] In Terminal 3, ran test query:
```powershell
curl -X POST http://localhost:3000/api/v1/questions `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"Top 5 selling products last week\"}'
```
- [ ] Got JSON response with insights
- [ ] Response includes: `"success": true`
- [ ] Response includes: `"insights"` object
- [ ] No error messages

---

## ✅ Final Verification

### Services Running
- [ ] Rails API running on http://localhost:3000
- [ ] Python AI running on http://localhost:8000
- [ ] Both terminals show no errors
- [ ] Health checks pass
- [ ] Test query returns valid JSON

### Files Created
- [ ] `rails_api/.env` exists and configured
- [ ] `ai_service/.env` exists and configured
- [ ] `rails_api/db/development.sqlite3` exists
- [ ] `ai_service/venv/` directory exists

### Documentation Read
- [ ] Read `START_HERE.md`
- [ ] Reviewed `COMPLETE_SETUP_GUIDE.md`
- [ ] Bookmarked `API_EXAMPLES.md` for reference
- [ ] Know where to find `TROUBLESHOOTING.md`

---

## 🎉 Success Criteria

Your installation is successful if ALL of these are true:

✅ Ruby 3.3.10 is installed and working  
✅ Python 3.11+ is installed and working  
✅ Both `.env` files are created and configured  
✅ Rails gems installed without errors  
✅ Python packages installed without errors  
✅ Database created and migrated  
✅ Rails server starts and responds on port 3000  
✅ Python service starts and responds on port 8000  
✅ Health checks return success  
✅ Test query returns valid insights JSON  

---

## 📊 Time Tracking

Record your actual times:

- Prerequisites Installation: _____ minutes
- Project Setup: _____ minutes
- Starting Services: _____ minutes
- Testing: _____ minutes
- **Total Time**: _____ minutes

**Expected Total:** 30-45 minutes for first-time installation

---

## 🐛 Common Issues Encountered

Check off if you encountered and resolved:

- [ ] Ruby gems failed to compile → Fixed with `ridk install` option 3
- [ ] Python execution policy error → Fixed with `Set-ExecutionPolicy`
- [ ] Port already in use → Killed process or used different port
- [ ] Virtual environment activation failed → Used `.bat` file instead
- [ ] ANTHROPIC_API_KEY warning → Added placeholder or real key
- [ ] Database locked → Stopped all Rails processes and restarted

---

## 📝 Notes

Write down any issues you faced or solutions you found:

```
Issue 1:
_________________________________________________________________

Solution:
_________________________________________________________________


Issue 2:
_________________________________________________________________

Solution:
_________________________________________________________________


Issue 3:
_________________________________________________________________

Solution:
_________________________________________________________________
```

---

## 🎯 Next Steps After Installation

- [ ] Try all example queries from `API_EXAMPLES.md`
- [ ] Read `ARCHITECTURE.md` to understand the system
- [ ] Get Anthropic API key from https://console.anthropic.com/
- [ ] Add real API key to `ai_service/.env`
- [ ] Customize demo data in `rails_api/db/seeds.rb`
- [ ] Explore the 5-stage AI pipeline code
- [ ] Build your own features!

---

## 🏆 Completion

Installation completed on: __________________

Completed by: __________________

Installation was: ⭐ Easy  ⭐ Moderate  ⭐ Difficult

Notes:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

**Congratulations on completing the installation!** 🎉

You're now ready to use Shopify Analytics AI!