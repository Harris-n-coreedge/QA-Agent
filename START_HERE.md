# 🚀 START HERE - QA Agent Frontend Setup

## ✅ Current Status

- ✅ Frontend is running on http://localhost:3000
- ❌ Backend needs to be started (causing the 500 errors you see)

## 🎯 Quick Start (2 Commands)

### Step 1: Install Backend Dependencies

```bash
pip install fastapi uvicorn python-dotenv
```

### Step 2: Start Backend

Open a **NEW terminal window** and run:

```bash
cd C:\Users\Admin\Desktop\QA_Agent-qa_agentV1
python standalone_backend.py
```

Or use the simple starter:

```bash
python start_backend_simple.py
```

### Step 3: Verify

- Backend: http://localhost:8000/docs (Should show API documentation)
- Frontend: http://localhost:3000 (Should stop showing errors)

**That's it!** The frontend errors will disappear and you can start using the app.

---

## 🎨 What You Can Do

### 1. Dashboard (http://localhost:3000)
- View active sessions
- Monitor test results
- System health

### 2. Sessions Page
- Click "New Session"
- Choose:
  - Website URL (e.g., https://www.w3schools.com)
  - AI Provider (OpenAI, Anthropic, or Google)
  - Auto-check enabled
- Browser opens automatically
- Execute commands like:
  - "click the login button"
  - "scroll down"
  - "search for python"

### 3. Browser Use Page
- Quick one-off automation
- Enter task: "Go to google.com and search for react"
- Executes immediately

### 4. Test Results
- View all execution history
- Filter by session
- See timing and status

---

## 🔧 Requirements

### Must Have

```bash
pip install fastapi uvicorn python-dotenv
```

### For Full Functionality

```bash
pip install playwright openai anthropic google-genai
playwright install  # Install browser binaries
```

### For Browser Use Feature (Optional)

```bash
pip install browser-use
```

---

## 🔑 Environment Setup

Create/edit `.env` file in project root:

```env
# Add at least ONE of these:
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here

ENV=local
```

---

## 📝 Files Created

### Backend Options (Choose One)

1. **standalone_backend.py** ⭐ RECOMMENDED
   - Completely independent
   - No dependencies on existing routes
   - Full functionality
   - Run with: `python standalone_backend.py`

2. **minimal_backend.py**
   - Ultra-light (just for testing connection)
   - No session creation
   - Run with: `python minimal_backend.py`

3. **start_backend_simple.py**
   - Wrapper that starts standalone_backend
   - Run with: `python start_backend_simple.py`

### Frontend

Located in `frontend/` directory:
- Modern React UI
- TailwindCSS styling
- Real-time updates
- Already running on port 3000

### Documentation

- **START_HERE.md** ← You are here
- **QUICK_START.md** - Alternative quick guide
- **FRONTEND_GUIDE.md** - Complete feature documentation
- **TROUBLESHOOTING.md** - Common issues and fixes
- **SETUP_INSTRUCTIONS.md** - Detailed setup

---

## 🐛 Troubleshooting

### Error: "Request failed with status code 500"

**Cause:** Backend not running or has errors

**Fix:**
```bash
python standalone_backend.py
```

Check terminal for specific error messages.

### Error: "ECONNREFUSED"

**Cause:** Backend not running at all

**Fix:**
```bash
python standalone_backend.py
```

### Error: "Module not found"

**Fix:**
```bash
pip install fastapi uvicorn python-dotenv
```

### Error: "API key not found"

**Fix:** Add API key to `.env` file:
```env
OPENAI_API_KEY=your-key-here
```

### Port 8000 already in use

**Fix:**
```bash
# Find and kill process
netstat -ano | findstr :8000

# Or use different port
python standalone_backend.py --port 8001
```

Then update `frontend/vite.config.js` proxy settings.

---

## 📊 Architecture

```
┌─────────────────┐
│ React Frontend  │  http://localhost:3000
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│ FastAPI Backend │  http://localhost:8000
│  (Port 8000)    │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌──────────────────┐  ┌──────────────┐
│ multi_ai_qa_agent│  │ broswer_use  │
│      .py         │  │    .py       │
└──────────────────┘  └──────────────┘
```

---

## 🎓 Tutorial: Create Your First Session

1. **Start Backend** (if not running):
   ```bash
   python standalone_backend.py
   ```

2. **Open Frontend**: http://localhost:3000

3. **Click "Sessions"** in navigation

4. **Click "New Session"** button

5. **Fill the form:**
   - Session Name: "My First Test"
   - Website URL: https://www.w3schools.com
   - AI Provider: OpenAI (or whatever you have API key for)
   - Auto Check: ✓ (leave checked)

6. **Click "Create Session"**
   - Browser window opens automatically
   - Navigates to website
   - Status changes to "active"

7. **Execute a command:**
   - Type: "click the login button"
   - Press Send
   - Watch it work!

8. **Try more commands:**
   - "scroll down"
   - "find all buttons on the page"
   - "search for python"

9. **View Results:**
   - Click "Test Results" in navigation
   - See execution history

---

## ⚡ Quick Commands Reference

### Start Everything

```bash
# Terminal 1 - Frontend (already running)
cd frontend
npm run dev

# Terminal 2 - Backend
cd C:\Users\Admin\Desktop\QA_Agent-qa_agentV1
python standalone_backend.py
```

### Test Backend

```bash
# Check if running
curl http://localhost:8000/api/v1/qa-tests/health

# View API docs
# Open: http://localhost:8000/docs
```

### Install Everything

```bash
# Minimal (gets it working)
pip install fastapi uvicorn python-dotenv

# Full (all features)
pip install fastapi uvicorn python-dotenv playwright openai anthropic google-genai browser-use
playwright install
```

---

## 🎉 Success Checklist

- [ ] Backend running (see "Application startup complete")
- [ ] Frontend running (http://localhost:3000 loads)
- [ ] No errors in frontend terminal
- [ ] Can open http://localhost:8000/docs
- [ ] Dashboard shows stats (even if zeros)
- [ ] Can click "Sessions" page
- [ ] "New Session" button works

Once all checked, you're ready to test!

---

## 🆘 Still Having Issues?

1. **Run diagnostic:**
   ```bash
   python test_backend.py
   ```

2. **Check backend terminal** for red error messages

3. **Check frontend console** (F12 in browser)

4. **See TROUBLESHOOTING.md** for detailed help

5. **Try minimal backend first:**
   ```bash
   python minimal_backend.py
   ```

---

## 📞 Next Steps

Once you have it running:

1. ✅ Create a session
2. ✅ Execute commands
3. ✅ View results
4. ✅ Try Browser Use feature
5. ✅ Explore the API docs

**Enjoy your QA automation platform!** 🎉
