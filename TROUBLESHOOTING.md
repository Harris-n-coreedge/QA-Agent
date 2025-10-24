# Troubleshooting Guide

## Current Issue: Backend 500 Error / Won't Start

### Quick Diagnostic

Run this command to diagnose the issue:

```bash
python test_backend.py
```

This will tell you exactly what's missing.

---

## Solution 1: Start Minimal Backend (Gets Frontend Working)

If you just want to see the frontend working:

```bash
python minimal_backend.py
```

This starts a simple backend that:
- ✅ Responds to frontend health checks
- ✅ Stops the connection errors
- ❌ Can't create sessions yet (need full setup)

---

## Solution 2: Full Backend Setup

### Step 1: Check Python Environment

```bash
python --version
```

Should be Python 3.9 or higher.

### Step 2: Install Required Packages

```bash
pip install fastapi uvicorn websockets pydantic
```

### Step 3: Verify Installation

```bash
python test_backend.py
```

Look for:
- ✅ FastAPI imported successfully
- ✅ uvicorn imported successfully
- ✅ QA Agent API imported successfully

### Step 4: Start Full Backend

```bash
python start_backend_simple.py
```

Or:

```bash
uvicorn qa_agent.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Common Errors and Fixes

### Error: "No module named 'fastapi'"

**Fix:**
```bash
pip install fastapi uvicorn
```

### Error: "No module named 'pydantic'"

**Fix:**
```bash
pip install pydantic
```

### Error: "No module named 'qa_agent'"

**Cause:** Running from wrong directory

**Fix:**
```bash
cd C:\Users\Admin\Desktop\QA_Agent-qa_agentV1
python start_backend_simple.py
```

### Error: "Failed to import MultiAIQAAgent"

**Cause:** `multi_ai_qa_agent.py` not found or has syntax errors

**Fix:**
1. Verify file exists:
   ```bash
   dir multi_ai_qa_agent.py
   ```

2. If it exists, check for Python errors:
   ```bash
   python -c "import multi_ai_qa_agent"
   ```

3. If errors, check the file for syntax issues

### Error: "browser-use library not installed"

**Cause:** Trying to use Browser Use feature without the library

**Fix:**
```bash
pip install browser-use
```

**Note:** Browser Use is optional. Sessions feature works without it.

### Error: Port 8000 already in use

**Fix:**
1. Find what's using port 8000:
   ```bash
   netstat -ano | findstr :8000
   ```

2. Kill that process or use different port:
   ```bash
   uvicorn qa_agent.api.main:app --reload --port 8001
   ```

3. Update frontend proxy in `frontend/vite.config.js`

---

## Frontend Issues

### Frontend shows "Request failed with status code 500"

**Cause:** Backend is running but has errors

**Fix:**
1. Check backend terminal for error messages
2. Look for red error text
3. Fix the specific error shown
4. Restart backend

### Frontend shows "ECONNREFUSED" errors

**Cause:** Backend not running

**Fix:**
1. Start backend:
   ```bash
   python minimal_backend.py
   ```

2. Or install dependencies and start full backend

### Frontend won't load at all

**Fix:**
```bash
cd frontend
npm install
npm run dev
```

---

## Testing the Setup

### Test 1: Minimal Backend

```bash
# Terminal 1
python minimal_backend.py

# Terminal 2
curl http://localhost:8000/api/v1/qa-tests/health
```

Should return JSON with status "healthy"

### Test 2: Frontend Connection

1. Start minimal backend
2. Open http://localhost:3000
3. Should see Dashboard with zeros (no errors)

### Test 3: Full Backend

```bash
# Terminal 1
python test_backend.py

# Should show all ✅ checks

# Terminal 2
python start_backend_simple.py

# Should start without errors

# Terminal 3
curl http://localhost:8000/docs
```

Should see API documentation page

---

## Recommended Setup Order

1. **Test First:**
   ```bash
   python test_backend.py
   ```

2. **Install Missing Packages:**
   Based on test results, install what's missing

3. **Start Minimal Backend:**
   ```bash
   python minimal_backend.py
   ```
   Frontend should connect (no errors)

4. **Install Full Dependencies:**
   ```bash
   pip install -r requirements-backend.txt
   ```

5. **Start Full Backend:**
   ```bash
   python start_backend_simple.py
   ```

6. **Test Session Creation:**
   - Open http://localhost:3000
   - Click "Sessions"
   - Click "New Session"
   - Should work!

---

## Still Having Issues?

### Check Backend Logs

When you start the backend, look for:
- ✅ "Application startup complete"
- ✅ "Uvicorn running on http://0.0.0.0:8000"
- ❌ Red error messages

### Check Frontend Console

1. Open http://localhost:3000
2. Press F12 (Developer Tools)
3. Look at Console tab for errors

### Check Network Tab

1. F12 Developer Tools
2. Network tab
3. Click on failed requests
4. See exact error message

### API Documentation

Visit http://localhost:8000/docs to:
- See all available endpoints
- Test endpoints directly
- See error responses

---

## Quick Win: See Frontend Working

Want to see the frontend working right now?

```bash
# Terminal 1 (already running - your frontend)
# Keep it running

# Terminal 2 (new terminal)
cd C:\Users\Admin\Desktop\QA_Agent-qa_agentV1
python minimal_backend.py
```

Now refresh http://localhost:3000 - connection errors should be gone!

The frontend will show empty data but prove the connection works.

---

## Next Steps After Minimal Backend Works

1. Run `python test_backend.py`
2. Install any missing packages it identifies
3. Switch to full backend: `python start_backend_simple.py`
4. Create your first session!

---

## Contact / Help

- Backend terminal: Shows detailed error messages
- API Docs: http://localhost:8000/docs (when running)
- Frontend Console: F12 in browser
- Test Script: `python test_backend.py`
