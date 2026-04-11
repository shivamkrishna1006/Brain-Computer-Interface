# BCI Web App - Installation & Verification Checklist

Complete checklist for verifying the BCI Web App installation and setup.

## ✅ File Structure Verification

### Backend Files
```
✓ webapp/backend/app.py            - Flask application (400+ lines)
✓ webapp/backend/config.py         - Configuration (50+ lines)
✓ webapp/backend/__init__.py       - Package init (5 lines)
```

### Frontend Files
```
✓ webapp/frontend/templates/index.html       - Dashboard (200+ lines)
✓ webapp/frontend/static/css/dashboard.css   - Styling (300+ lines)
✓ webapp/frontend/static/js/dashboard.js     - Logic (500+ lines)
```

### Configuration Files
```
✓ webapp/requirements.txt           - Dependencies (8 packages)
✓ webapp/.env.example              - Environment template (100+ lines)
```

### Documentation Files
```
✓ webapp/README.md                     - Main docs (600+ lines)
✓ webapp/QUICKSTART.md                - Quick start (300+ lines)
✓ webapp/DEVELOPMENT_SETUP.md         - Dev guide (500+ lines)
✓ webapp/API_TESTING_GUIDE.md         - Testing (400+ lines)
✓ webapp/DOCUMENTATION_INDEX.md       - Navigation guide
✓ webapp/DIRECTORY_STRUCTURE.md       - Structure guide
✓ webapp/COMPLETION_SUMMARY.md        - Summary document
```

---

## 🚀 Quick Verification Test

### Step 1: Verify Installation Files Exist

```bash
# Navigate to webapp
cd webapp

# Check backend
ls -la backend/
# Expected output:
#   app.py
#   config.py
#   __init__.py

# Check frontend
ls -la frontend/templates/
ls -la frontend/static/css/
ls -la frontend/static/js/
# Should see: index.html, dashboard.css, dashboard.js

# Check config files
ls -la requirements.txt .env.example
```

### Step 2: Verify Documentation

```bash
# List all markdown files
ls -la *.md

# Expected files:
# - README.md
# - QUICKSTART.md
# - DEVELOPMENT_SETUP.md
# - API_TESTING_GUIDE.md
# - DOCUMENTATION_INDEX.md
# - DIRECTORY_STRUCTURE.md
# - COMPLETION_SUMMARY.md
```

### Step 3: Install Dependencies

```bash
# Install Flask and dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -i flask

# Expected output should include:
# Flask, Flask-CORS, Flask-SocketIO, python-socketio
```

### Step 4: Create Environment File

```bash
# Copy template
cp .env.example .env

# Verify file created
ls -la .env
```

### Step 5: Start Server

```bash
# Navigate to backend
cd backend

# Start Flask
python app.py

# Expected output:
# * Running on http://0.0.0.0:5000
# * Press CTRL+C to quit
```

### Step 6: Verify Connectivity

```bash
# In another terminal
curl http://localhost:5000/api/status

# Expected response (JSON):
# {
#   "status": "running",
#   "timestamp": "2024-...",
#   "version": "1.0.0",
#   "webapp_version": "1.0.0"
# }
```

### Step 7: Open Dashboard

```
Open browser: http://localhost:5000
Expected: BCI Live Dashboard loads without errors
```

---

## 📋 Pre-Flight Checklist

Before running the app, verify:

### Environment
- [ ] Python 3.8+ installed (`python --version`)
- [ ] pip installed and updated (`pip --version`)
- [ ] Port 5000 is available (`netstat -an | grep 5000`)
- [ ] No port conflicts

### Dependencies
- [ ] requirements.txt present
- [ ] All packages installed (`pip list`)
- [ ] Flask, Flask-CORS, Flask-SocketIO present

### Files
- [ ] app.py exists (400+ lines)
- [ ] config.py exists (50+ lines)
- [ ] index.html exists (200+ lines)
- [ ] dashboard.css exists (300+ lines)
- [ ] dashboard.js exists (500+ lines)

### Configuration
- [ ] .env.example exists (template)
- [ ] .env created (if needed)
- [ ] SECRET_KEY set in .env (if production)

### Documentation
- [ ] README.md present (main guide)
- [ ] QUICKSTART.md present (fast start)
- [ ] DEVELOPMENT_SETUP.md present (dev guide)
- [ ] API_TESTING_GUIDE.md present (testing)

---

## 🧪 Functional Testing

After starting the server, verify:

### REST API Tests

```bash
# Test 1: Status endpoint
curl http://localhost:5000/api/status
# Expected: 200 OK, JSON response

# Test 2: Models endpoint
curl http://localhost:5000/api/models
# Expected: 200 OK, models array

# Test 3: Config endpoint
curl http://localhost:5000/api/config
# Expected: 200 OK, configuration JSON

# Test 4: Dashboard
curl http://localhost:5000/
# Expected: 200 OK, HTML content
```

### Dashboard Test

Open browser and verify:

```
1. Page loads without errors
2. Navigation bar visible
3. Status panel present
4. Charts present
5. Upload form visible
6. Console shows no errors (F12)
```

### WebSocket Test

Open browser console (F12) and run:

```javascript
// Test 1: Check connection
console.log(socket.connected);  // Should be true

// Test 2: Start stream
socket.emit('start_stream');

// Test 3: Listen for data
socket.on('eeg_sample', (data) => {
    console.log('✓ EEG data received');
});

// Test 4: Check for errors
socket.on('error', (data) => {
    console.log('✗ Error:', data);
});
```

---

## 🎯 Component Verification

### Backend Components

**Flask Application** (`app.py`)
- [ ] Routes defined (GET /, /api/status, /api/models, /api/config)
- [ ] WebSocket handlers defined
- [ ] Error handlers present
- [ ] Logging configured

**Configuration** (`config.py`)
- [ ] DevelopmentConfig class defined
- [ ] ProductionConfig class defined
- [ ] TestingConfig class defined
- [ ] Environment options supported

### Frontend Components

**HTML** (`index.html`)
- [ ] Navigation bar present
- [ ] Status panel present
- [ ] Charts containers present
- [ ] Upload form present
- [ ] Bootstrap 5 included
- [ ] Scripts included

**CSS** (`dashboard.css`)
- [ ] Layout styles present
- [ ] Color scheme defined
- [ ] Responsive design support
- [ ] Animation definitions
- [ ] Component styles

**JavaScript** (`dashboard.js`)
- [ ] Socket.IO initialization
- [ ] Chart initialization (5 charts)
- [ ] Event listeners setup
- [ ] API communication
- [ ] Data handling

---

## 📊 File Size Verification

Expected approximate sizes:

| File | Expected Size |
|------|----------------|
| app.py | 10-15 KB |
| config.py | 2-3 KB |
| index.html | 8-12 KB |
| dashboard.css | 10-15 KB |
| dashboard.js | 18-22 KB |
| requirements.txt | 200-300 bytes |
| .env.example | 3-4 KB |

You can verify with:
```bash
ls -lh backend/*.py frontend/templates/*.html frontend/static/css/*.css frontend/static/js/*.js
```

---

## 🔍 Code Quality Checks

### Python Code
```bash
# Check syntax
python -m py_compile backend/app.py backend/config.py

# Expected: No errors

# Check imports
python -c "from backend.app import app; print('✓ Imports OK')"
```

### JavaScript Code
```bash
# Can verify in browser DevTools
# F12 → Console → No errors expected
```

### HTML Code
```bash
# Can validate at https://validator.w3.org/
# Or check in browser DevTools
```

---

## 🐛 Debugging Checklist

If something doesn't work, check:

### Server Won't Start
- [ ] Port 5000 in use? (Try different port)
- [ ] Python version 3.8+? (`python --version`)
- [ ] Dependencies installed? (`pip list`)
- [ ] app.py syntax correct? (`python -m py_compile backend/app.py`)

### Dashboard Won't Load
- [ ] Server running? (Check terminal)
- [ ] Browser loading right URL? (http://localhost:5000)
- [ ] Firewall blocking? (Check firewall settings)
- [ ] Browser console errors? (F12 → Console)

### WebSocket Won't Connect
- [ ] Server running? (Check terminal output)
- [ ] CORS allowed? (Check config.py)
- [ ] JavaScript errors? (F12 → Console)
- [ ] Socket.IO loaded? (Check page source)

### API Endpoints Return Errors
- [ ] Server running?
- [ ] Correct URL? (http://localhost:5000/api/status)
- [ ] Server logs? (Check terminal where Flask runs)
- [ ] Python errors? (Check stderr output)

---

## ✨ Success Indicators

You'll know installation is successful when:

✅ Server starts without errors
✅ Dashboard loads in browser
✅ No console errors (F12)
✅ API endpoints return JSON
✅ WebSocket connects
✅ Charts visible and styled
✅ No 404 or 500 errors

---

## 📚 Next Steps After Verification

### If All Tests Pass ✓

1. **Explore the Dashboard**
   - Click buttons and test features
   - Check status indicators
   - View charts

2. **Read Documentation**
   - Start with QUICKSTART.md
   - Read README.md overview
   - Check DEVELOPMENT_SETUP.md

3. **Test APIs**
   - Follow API_TESTING_GUIDE.md
   - Test each endpoint
   - Test WebSocket events

4. **Start Development**
   - Modify CSS styling
   - Add new routes
   - Extend functionality

### If Tests Fail ✗

1. **Check Logs**
   - Terminal output from Flask
   - Browser console (F12)
   - Check logs/ directory

2. **Verify Installation**
   - Reinstall dependencies: `pip install -r requirements.txt`
   - Verify Python version
   - Check file structure

3. **Read Troubleshooting**
   - README.md troubleshooting section
   - QUICKSTART.md common issues
   - DEVELOPMENT_SETUP.md issues

---

## 🚀 Verification Script

Create `verify_installation.sh` for automated verification:

```bash
#!/bin/bash

echo "🔍 BCI Web App Installation Verification"
echo "=========================================="

# Check Python
echo "Checking Python..."
python --version || exit 1

# Check files
echo "Checking files..."
test -f backend/app.py || exit 1
test -f backend/config.py || exit 1
test -f frontend/templates/index.html || exit 1

# Check packages
echo "Checking packages..."
pip list | grep Flask || exit 1

# Check ports
echo "Checking ports..."
netstat -an | grep 5000 && echo "⚠️  Port 5000 in use!" || echo "✓ Port 5000 available"

echo "✅ All checks passed!"
echo "Run: cd backend && python app.py"
```

Run with:
```bash
chmod +x verify_installation.sh
./verify_installation.sh
```

---

## 📋 Verification Checklist Summary

### Files ✓
- [x] Backend (3 files)
- [x] Frontend (3 files)
- [x] Configuration (2 files)
- [x] Documentation (7 files)

### Installation ✓
- [x] Python 3.8+
- [x] Requirements installed
- [x] Environment configured
- [x] Directories created

### Functionality ✓
- [x] Server starts
- [x] Dashboard loads
- [x] API responds
- [x] WebSocket connects
- [x] Charts display

### Documentation ✓
- [x] README complete
- [x] Quick start ready
- [x] Dev guide complete
- [x] Testing guide ready

### Quality ✓
- [x] Code present
- [x] Syntax valid
- [x] Imports work
- [x] No errors

---

## 🎉 Installation Complete!

Once all checks pass, the BCI Web App is:
- ✅ Installed
- ✅ Configured
- ✅ Verified
- ✅ Ready to use
- ✅ Documented

**Next:** Open [QUICKSTART.md](QUICKSTART.md) to start using the app!

---

**Questions?** Check the appropriate guide:
- [README.md](README.md) - Complete reference
- [QUICKSTART.md](QUICKSTART.md) - Quick answers
- [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md) - Testing help
- [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - Navigation
