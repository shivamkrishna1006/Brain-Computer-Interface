# WebApp Startup Guide

Quick start guide for running the BCI Web Application dashboard.

## 5-Minute Quick Start

### Step 1: Navigate to webapp directory
```bash
cd webapp/backend
```

### Step 2: Install dependencies
```bash
pip install -r ../requirements.txt
```

### Step 3: Run the Flask server
```bash
python app.py
```

### Step 4: Open dashboard
Open your browser to: **http://localhost:5000**

You should see the BCI Live Dashboard with:
- Real-time EEG signal chart
- Prediction confidence display
- System status panel
- Model information

---

## Configuration

### Environment Variables

Create a `.env` file in `webapp/backend/`:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO

# Models
MODELS_DIR=../../models

# Server
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### Configuration Objects

The app uses configuration classes in `config.py`:

| Environment | Use Case | Settings |
|------------|----------|----------|
| **development** | Local development | DEBUG=True, LOG_LEVEL=DEBUG |
| **production** | Live deployment | DEBUG=False, SESSION_COOKIE_SECURE=True |
| **testing** | Unit tests | TESTING=True, In-memory DB |

---

## Installation Methods

### Method 1: Standard (Recommended)

```bash
# 1. Navigate to webapp
cd webapp/backend

# 2. Install requirements
pip install -r ../requirements.txt

# 3. Run server
python app.py

# 4. Access dashboard
# http://localhost:5000
```

### Method 2: Virtual Environment (Isolated)

```bash
# 1. Create isolated environment
python -m venv venv

# 2. Activate environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r ../requirements.txt

# 4. Run server
cd backend
python app.py
```

### Method 3: Docker (Containerized)

```bash
# 1. Build Docker image
docker build -t bci-webapp .

# 2. Run container
docker run -p 5000:5000 bci-webapp

# 3. Access dashboard
# http://localhost:5000
```

### Method 4: Production Deployment (Gunicorn)

```bash
# 1. Install gunicorn
pip install gunicorn

# 2. Run with gunicorn
gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:5000

# 3. Access dashboard
# http://localhost:5000
```

---

## First Run Checklist

- [ ] Python 3.8+ installed
- [ ] dependencies installed: `pip install -r ../requirements.txt`
- [ ] `models/` directory exists in project root
- [ ] `logs/` directory exists
- [ ] Port 5000 is available
- [ ] Browser can access `http://localhost:5000`

---

## Dashboard Overview

### Main Components

**1. Navigation Bar**
- Brand logo and title
- Links to documentation
- System status indicator

**2. Status Panel** (Top Left)
- Model loaded status
- Streaming active indicator
- Total predictions made
- Model accuracy

**3. EEG Chart** (Left Side)
- Real-time 8-channel display
- Scrolling signal visualization
- Channel colors

**4. Confidence Chart** (Right Side)
- 5-class prediction scores
- High-confidence indicator
- Class names

**5. Model Info** (Bottom Left)
- Selected model details
- Creation timestamp
- Model size

**6. Upload Form** (Bottom Right)
- Upload EEG data files
- Supported formats: `.csv`, `.npy`
- Batch processing results

**7. Action History** (Bottom)
- Event log
- Timestamps
- Status updates

---

## Common Tasks

### Start Streaming

1. Click "Start Streaming" button
2. EEG chart begins updating in real-time
3. Predictions display in confidence chart
4. Status changes to "STREAMING: ON"

### Stop Streaming

1. Click "Stop Streaming" button
2. EEG chart freezes
3. Status changes to "STREAMING: OFF"

### Upload Data File

1. Click "Choose File" in upload section
2. Select `.csv` or `.npy` file with EEG data
3. Click "Upload & Process"
4. View results in history log

### Change Model

1. Open Model Selector dropdown
2. Choose from available models
3. Confirm selection
4. Status updates with new model info

### View Predictions

- **Real-time**: Watch confidence chart during streaming
- **Batch**: Upload file to process multiple samples
- **History**: Check action log for past predictions

---

## Troubleshooting

### Dashboard doesn't load

**Problem**: Page shows "Cannot GET /"

**Solution**:
1. Check Flask server is running
2. Verify URL is `http://localhost:5000` (not 5001, etc.)
3. Check terminal for error messages
4. Restart Flask: `python app.py`

---

### WebSocket connection fails

**Problem**: Charts don't update when streaming

**Solution**:
1. Check browser console (F12 → Console tab)
2. Look for Socket.IO connection errors
3. Verify Flask server is running: `http://localhost:5000/api/status`
4. Check firewall allows port 5000

---

### Models not found

**Problem**: Model dropdown is empty

**Solution**:
1. Ensure `models/` directory exists
2. Copy trained models: `cp path/to/model.h5 models/`
3. Refresh page: `Ctrl+R` or `Cmd+R`
4. Check Flask logs for load errors

---

### Port 5000 already in use

**Problem**: "Address already in use" error

**Solution**:
```bash
# Find process using port
# Windows:
netstat -ano | findstr :5000

# Linux/Mac:
lsof -i :5000

# Kill process (Windows):
taskkill /PID <PID> /F

# Kill process (Linux/Mac):
kill -9 <PID>

# Or use different port:
python app.py --port 5001
```

---

### High latency / Slow updates

**Problem**: Charts update slowly or lag

**Solution**:
1. Reduce browser tabs (less CPU)
2. Lower EEG sample rate (config.py)
3. Disable verbose logging: `LOG_LEVEL=WARNING`
4. Close unused applications
5. Check system resources (Task Manager)

---

## Next Steps

1. **Explore Dashboard**
   - Test start/stop streaming
   - Upload a test data file
   - Change models

2. **Training** (if trained models available)
   - Click "Train New Model" button
   - Monitor training progress in real-time
   - Evaluate when complete

3. **Integration**
   - Connect to real EEG device (in `app.py`)
   - Modify `EEGSimulator` class
   - Update WebSocket handlers

4. **Customization**
   - Edit CSS in `static/css/dashboard.css`
   - Add routes in `app.py`
   - Extend frontend in `static/js/dashboard.js`

---

## System Requirements

### Minimum
- Python 3.8+
- 512 MB RAM
- 2 MB disk space
- Any modern browser

### Recommended
- Python 3.9+
- 2 GB RAM
- 100 MB disk space
- Chrome/Firefox/Safari latest

---

## Port Configuration

Default port: **5000**

To use different port:

```bash
# In app.py, change:
socketio.run(app, port=5001)

# Or command line:
python app.py --port 5001
```

---

## Logs

Check logs for debugging:

```bash
# View logs while running
tail -f ../../../logs/webapp.log

# On Windows:
Get-Content ../../../logs/webapp.log -Wait
```

---

## Security Notes

⚠️ **Development Mode** (default):
- Debug mode enabled
- HTTPS disabled
- Debug toolbar exposed
- Use only for testing

✅ **Production Mode**:
- Set `FLASK_ENV=production`
- Use HTTPS only
- Change SECRET_KEY
- Disable debug mode

---

## Additional Resources

- **Full Documentation**: [README.md](README.md)
- **API Reference**: [README.md#api-reference](README.md#api-reference)
- **Deployment Guide**: [../DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
- **Project Documentation**: [../DOCUMENTATION_INDEX.md](../DOCUMENTATION_INDEX.md)

---

**Ready to start?** Run:
```bash
cd webapp/backend
python app.py
```

Then open: http://localhost:5000

**Need help?** Check [README.md](README.md) for detailed documentation.
