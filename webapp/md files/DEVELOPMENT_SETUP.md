# BCI Web App - Development Setup Guide

Complete development environment setup for the BCI Web Application.

## Prerequisites

- **Python 3.8+**: Programming language runtime
- **pip**: Python package manager (comes with Python)
- **Node.js 14+** (optional): For frontend development tools
- **Git**: Version control (for cloning repository)
- **Modern Browser**: Chrome, Firefox, Safari, or Edge

### Verify Installation

```bash
# Check Python
python --version
# Expected: Python 3.8+

# Check pip
pip --version
# Expected: pip 20.0+

# Check Node (optional)
node --version
npm --version
```

---

## Installation Steps

### Step 1: Clone/Download Project

```bash
# Clone the repository
git clone <repository-url>
cd BCI_INTERFACE

# Or navigate to existing project
cd /path/to/BCI_INTERFACE
```

### Step 2: Create Virtual Environment (Recommended)

A virtual environment isolates project dependencies.

**Windows**:
```bash
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# You should see (venv) at the start of your command line
```

**Linux/Mac**:
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# You should see (venv) at the start of your command line
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Navigate to webapp directory
cd webapp

# Install webapp requirements
pip install -r requirements.txt

# Install main project requirements (from parent)
pip install -r ../requirements.txt
```

### Step 4: Create Required Directories

```bash
# From project root
mkdir -p logs
mkdir -p models
mkdir -p data
mkdir -p outputs
mkdir -p webapp/uploads

# Verify directories
ls -la logs models data outputs
```

### Step 5: Configure Environment

```bash
# Navigate to webapp backend
cd webapp/backend

# Copy environment template
cp ../.env.example .env

# Edit .env with your settings (use text editor)
# nano .env              # Linux/Mac
# code .env              # VS Code
```

### Step 6: Run Flask Application

```bash
# From webapp/backend directory
python app.py

# Expected output:
# * Running on http://0.0.0.0:5000
# * Press CTRL+C to quit
```

### Step 7: Access Dashboard

Open your web browser to:
```
http://localhost:5000
```

You should see the BCI Live Dashboard!

---

## Docker Setup (Alternative)

If you prefer containerized development:

```bash
# Build Docker image
docker build -t bci-webapp:latest .

# Run container
docker run -p 5000:5000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  -e FLASK_ENV=development \
  bci-webapp:latest

# Access dashboard
# http://localhost:5000
```

---

## IDE Setup

### Visual Studio Code

1. **Install Extensions**:
   - Python (Microsoft)
   - Flask Snippet (cnjimbo)
   - Thunder Client (optional, for API testing)

2. **Create Launch Configuration** (`.vscode/launch.json`):
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask App",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "app.py",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1"
            },
            "args": ["run"],
            "cwd": "${workspaceFolder}/webapp/backend"
        }
    ]
}
```

3. **Start Debugging**:
   - Press `F5` or click "Run and Debug"

### PyCharm

1. **Create Run Configuration**:
   - Run → Edit Configurations
   - Click `+` → Python
   - Script: `app.py`
   - Working directory: `webapp/backend`
   - Environment: `FLASK_ENV=development`

2. **Start Debugging**:
   - Press `Shift+F9`

### Vim/Neovim

```bash
# Install Python LSP server
pip install python-lsp-server

# Install plugins (e.g., vim-plug)
# Then configure in your vim config
```

---

## Development Workflow

### File Structure Overview

```
BCI_INTERFACE/
├── webapp/                    # Web application
│   ├── backend/              # Flask app (Python)
│   │   ├── app.py            # Main application
│   │   ├── config.py         # Configuration
│   │   └── __init__.py       # Package init
│   ├── frontend/             # Static assets
│   │   ├── templates/        # HTML templates
│   │   │   └── index.html    # Main dashboard
│   │   └── static/           # Static files
│   │       ├── css/
│   │       │   └── dashboard.css
│   │       └── js/
│   │           └── dashboard.js
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example         # Environment template
│   └── README.md            # Documentation
├── src/                      # BCI core modules
│   ├── train.py             # Model training
│   ├── evaluate.py          # Model evaluation
│   └── realtime.py          # Real-time inference
├── models/                   # Trained models
├── data/                     # Input data
├── logs/                     # Application logs
└── config.yaml              # Main configuration
```

### Typical Development Session

1. **Activate Virtual Environment**:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. **Navigate to Backend**:
```bash
cd webapp/backend
```

3. **Start Flask Development Server**:
```bash
python app.py
```

4. **Open Dashboard in Browser**:
```
http://localhost:5000
```

5. **Make Code Changes**:
   - Edit Python files in `app.py`
   - Edit frontend in `../frontend/`
   - Flask auto-reloads on save (if `FLASK_DEBUG=1`)

6. **Stop Server**:
```bash
Ctrl+C  # or Cmd+C on Mac
```

---

## Common Development Tasks

### Adding a New Route

In `app.py`:
```python
@app.route('/api/new-endpoint', methods=['GET', 'POST'])
def new_endpoint():
    """Documentation for endpoint"""
    try:
        data = request.json if request.method == 'POST' else {}
        # Your logic here
        return jsonify({'result': 'success'})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
```

Test with:
```bash
curl http://localhost:5000/api/new-endpoint
```

### Adding a WebSocket Event

In `app.py`:
```python
@socketio.on('new_event')
def handle_new_event(data):
    """Handle new WebSocket event"""
    logger.info(f"Event received: {data}")
    # Your logic here
    emit('response', {'status': 'received'})
```

Test with browser console:
```javascript
socket.emit('new_event', {data: 'test'});
```

### Styling Updates

Edit `frontend/static/css/dashboard.css`:
```css
/* Add new styles */
.custom-class {
    color: #0d6efd;
    padding: 1rem;
    border-radius: 0.5rem;
}
```

Browser will auto-refresh (Ctrl+R if not automatic).

### Adding JavaScript Features

Edit `frontend/static/js/dashboard.js`:
```javascript
// Add new feature
function newFeature() {
    console.log('New feature activated');
    // Your code here
}

// Call on page load
document.addEventListener('DOMContentLoaded', function() {
    newFeature();
});
```

---

## Testing & Debugging

### Manual Testing

1. **Test API Endpoints**:
```bash
# Check status
curl http://localhost:5000/api/status

# Get models
curl http://localhost:5000/api/models

# Get config
curl http://localhost:5000/api/config
```

2. **Test WebSocket**:
   - Open browser DevTools (F12)
   - Go to Console tab
   - Execute:
```javascript
socket.emit('start_stream');
socket.on('eeg_sample', (data) => console.log(data));
```

### Browser DevTools

**Chrome/Edge**:
- F12 to open DevTools
- Console: JavaScript errors/logs
- Network: HTTP requests and WebSocket
- Elements: DOM inspection

**Firefox**:
- F12 to open DevTools
- Console: JavaScript errors/logs
- Network: HTTP requests and WebSocket
- Inspector: DOM inspection

### Python Debugging

With VS Code or PyCharm:
1. Set breakpoint (click line number)
2. Run in debug mode (F5)
3. Step through code (F10/F11)
4. Inspect variables

### Logging

Flask automatically logs:
```python
import logging

logger = logging.getLogger(__name__)

logger.debug('Debug message')      # Detailed info
logger.info('Info message')        # General info
logger.warning('Warning message')  # Important notice
logger.error('Error message')      # Error occurred
```

View logs:
```bash
# Real-time logs (Linux/Mac)
tail -f logs/webapp.log

# Real-time logs (Windows)
Get-Content logs/webapp.log -Wait

# All logs
cat logs/webapp.log
```

---

## Performance Development

### Frontend Performance

1. **Charts Optimization**:
   - Limit displayed points (see `dashboard.js`)
   - Use canvas-based rendering
   - Throttle updates

2. **Network Optimization**:
   - Compress static assets
   - Enable gzip
   - Minimize HTTP requests

3. **Memory Usage**:
   - Monitor browser memory (DevTools → Memory)
   - Clear old chart data
   - Unsubscribe from events when not needed

### Backend Performance

1. **Database Queries**:
   - Add indexes for common searches
   - Use connection pooling
   - Cache frequently accessed data

2. **API Endpoints**:
   - Profile with `cProfile`
   - Cache responses (Redis)
   - Batch operations

3. **WebSocket**:
   - Reduce update frequency
   - Compress messages
   - Implement backpressure

---

## Common Issues & Solutions

### Port 5000 Already in Use

```bash
# Kill the process
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Or use different port
python app.py --port 5001
```

### Module Not Found Error

```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Template Not Found

Ensure paths are correct:
- Templates: `webapp/frontend/templates/`
- Static: `webapp/frontend/static/`

### WebSocket Connection Failed

1. Check Flask is running
2. Check browser console for errors
3. Verify CORS settings in config.py
4. Ensure firewall allows port 5000

---

## Next Steps

1. **Explore the Code**:
   - Read `app.py` for routes
   - Check `config.py` for settings
   - Review `index.html` for templates
   - Study `dashboard.js` for frontend logic

2. **Customize**:
   - Change colors in `dashboard.css`
   - Add new endpoints in `app.py`
   - Extend models in `config.py`

3. **Deploy**:
   - See [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
   - Use Docker for containerization
   - Set up CI/CD pipeline

4. **Test Your Changes**:
   - Write unit tests
   - Test APIs manually
   - Verify frontend in multiple browsers

---

## Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Socket.IO Documentation**: https://python-socketio.readthedocs.io/
- **Chart.js Documentation**: https://www.chartjs.org/
- **Bootstrap Documentation**: https://getbootstrap.com/docs/
- **Python Documentation**: https://docs.python.org/3/

---

## Getting Help

1. **Check Logs**:
```bash
cat logs/webapp.log
```

2. **View Server Output**:
   - Watch terminal where Flask is running
   - Look for error messages

3. **Browser Console**:
   - F12 → Console tab
   - Check for JavaScript errors

4. **Check Documentation**:
   - [README.md](README.md) - Full documentation
   - [QUICKSTART.md](QUICKSTART.md) - Quick reference
   - [../DOCUMENTATION_INDEX.md](../DOCUMENTATION_INDEX.md) - Project docs

---

**Ready to develop?** 

```bash
# One-command setup
python -m venv venv && \
(source venv/bin/activate || venv\Scripts\activate) && \
pip install -r requirements.txt && \
cd webapp/backend && \
python app.py
```

Then open: **http://localhost:5000**
