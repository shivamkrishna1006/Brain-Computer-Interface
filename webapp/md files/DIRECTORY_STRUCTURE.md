# BCI Web App - Directory Structure Guide

Complete guide to the webapp directory organization and file purposes.

## Directory Tree

```
webapp/
├── backend/                          # Flask backend application
│   ├── app.py                        # Main Flask app (400+ lines)
│   ├── config.py                     # Configuration classes (50+ lines)
│   └── __init__.py                   # Package initialization (5 lines)
│
├── frontend/                         # Static assets and templates
│   ├── templates/                    # HTML templates
│   │   └── index.html               # Main dashboard (200+ lines)
│   │
│   └── static/                       # Static assets
│       ├── css/                      # Stylesheets
│       │   └── dashboard.css         # Dashboard styling (300+ lines)
│       │
│       └── js/                       # JavaScript files
│           └── dashboard.js          # Frontend application (500+ lines)
│
├── uploads/                          # User uploaded files (auto-created)
│
├── Documentation Files
│   ├── README.md                     # Main documentation (600+ lines)
│   ├── QUICKSTART.md                 # Quick start guide (300+ lines)
│   ├── DEVELOPMENT_SETUP.md          # Dev setup guide (500+ lines)
│   ├── API_TESTING_GUIDE.md          # Testing guide (400+ lines)
│   ├── DOCUMENTATION_INDEX.md        # This directory guide
│   └── DIRECTORY_STRUCTURE.md        # This file
│
├── Configuration Files
│   ├── requirements.txt              # Python dependencies (10+ lines)
│   ├── .env.example                  # Environment template (100+ lines)
│   └── .env                          # Environment file (created by user)
│
└── Miscellaneous
    ├── .gitignore                    # Git ignore rules
    ├── Dockerfile                    # Docker configuration (if at root)
    └── docker-compose.yml            # Docker compose (if at root)
```

---

## Detailed File Descriptions

### Backend Directory (`backend/`)

Purpose: Flask application server and business logic

#### `app.py` (400+ lines) ⭐ MAIN FILE
**Purpose**: Flask application and WebSocket handlers

**Contains**:
- Flask application initialization
- Route definitions (5 endpoints)
- WebSocket event handlers (8+ events)
- EEG simulator class
- Model predictor class
- Error handlers
- Logger setup

**Key Functions**:
```python
# Routes
index()           # GET /
get_models()      # GET /api/models
get_status()      # GET /api/status
get_config()      # GET /api/config

# WebSocket Events
handle_connect()
handle_disconnect()
handle_start_stream()
handle_stop_stream()
handle_eeg_request()
handle_train_model()
handle_evaluate_model()
```

**When to Edit**:
- Adding new routes
- Changing WebSocket events
- Modifying error handling
- Updating business logic

---

#### `config.py` (50+ lines)
**Purpose**: Configuration management

**Contains**:
- Config base class
- DevelopmentConfig
- ProductionConfig
- TestingConfig

**Configuration Options**:
- SECRET_KEY
- LOG_LEVEL
- Model paths
- WebSocket settings
- Session configuration

**When to Edit**:
- Adding new config options
- Changing defaults
- Adjusting for different environments

---

#### `__init__.py` (5 lines)
**Purpose**: Package initialization

**Contains**:
- Package metadata
- Version information
- Import initialization

**When to Edit**:
- Never (unless adding main imports)

---

### Frontend Directory (`frontend/`)

Purpose: User interface and static assets

#### Templates (`templates/`)

##### `index.html` (200+ lines) ⭐ DASHBOARD
**Purpose**: Main dashboard interface

**Structure**:
1. DOCTYPE and head
2. Navigation bar
3. Container sections
4. Status panel (top-left)
5. EEG chart (left)
6. Confidence chart (right)
7. Model info (bottom-left)
8. Upload form (bottom-right)
9. Action history (bottom)
10. Script includes

**When to Edit**:
- Changing layout
- Adding new elements
- Modifying dashboard sections
- Updating navigation

---

#### Stylesheets (`static/css/`)

##### `dashboard.css` (300+ lines)
**Purpose**: Professional styling and theming

**Contains**:
- CSS custom properties (variables)
- Layout styles
- Component styles
- Animation definitions
- Responsive design rules
- Dark mode support
- Color schemes

**When to Edit**:
- Changing colors
- Modifying layout
- Adding animations
- Adjusting responsiveness
- Creating new components

---

#### Scripts (`static/js/`)

##### `dashboard.js` (500+ lines) ⭐ FRONTEND LOGIC
**Purpose**: Dashboard interactivity and real-time updates

**Sections**:
1. Initialization (Socket.IO setup)
2. Socket.IO handlers
3. Chart initialization (5 charts)
4. Chart update functions
5. UI interaction handlers
6. API communication
7. Utility functions
8. Event listeners

**Key Objects**:
```javascript
socket              // Socket.IO connection
charts              // Chart.js instances
eegBuffer          // Real-time data buffer
predictionHistory  // Historical predictions
trainingMetrics    // Training progress data
```

**When to Edit**:
- Adding new charts
- Changing animations
- Adding UI features
- Modifying real-time updates
- Updating interactions

---

### Documentation Files

#### `README.md` (600+ lines) 📖 PRIMARY DOCS
**Purpose**: Complete application documentation

**Sections**:
1. Overview
2. Architecture
3. Installation
4. Configuration
5. API Reference
6. WebSocket Events
7. Frontend Usage
8. Development Guide
9. Testing
10. Troubleshooting
11. Optimization
12. Security
13. Deployment
14. Contributing
15. License

---

#### `QUICKSTART.md` (300+ lines) 🚀 FAST START
**Purpose**: Get running in 5 minutes

**Sections**:
1. 5-minute quick start
2. Configuration
3. Installation methods (4 ways)
4. Dashboard overview
5. Common tasks
6. Troubleshooting
7. Next steps

---

#### `DEVELOPMENT_SETUP.md` (500+ lines) 🔧 DEV GUIDE
**Purpose**: Complete development environment setup

**Sections**:
1. Prerequisites
2. Installation steps
3. Docker setup
4. IDE setup (VS Code, PyCharm, Vim)
5. Development workflow
6. Common tasks (20+ examples)
7. Testing & debugging
8. Performance
9. Issues & solutions
10. Resources
11. Next steps

---

#### `API_TESTING_GUIDE.md` (400+ lines) ✅ TEST GUIDE
**Purpose**: Test and validate the system

**Sections**:
1. Quick start test
2. REST API testing
3. WebSocket testing
4. Tools & setup (6 tools)
5. Test scenarios (7 scenarios)
6. Testing checklist (30+ items)
7. Troubleshooting
8. Performance testing
9. Continuous testing

---

#### `DOCUMENTATION_INDEX.md`
**Purpose**: Documentation navigation guide

**Contains**:
- Documentation structure
- File descriptions
- Quick reference tables
- Use case navigation
- Learning paths
- Status information

---

### Configuration Files

#### `requirements.txt` (10+ lines)
**Purpose**: Python package dependencies

**Packages**:
- Flask 2.3.0
- Flask-CORS 4.0.0
- Flask-SocketIO 5.3.0
- python-socketio 5.9.0
- python-engineio 4.5.0
- python-dotenv 1.0.0
- Werkzeug 2.3.0
- flask-debug 0.4.3

**When to Update**:
- Adding new Python packages
- Updating package versions
- Removing unused packages

---

#### `.env.example` (100+ lines)
**Purpose**: Environment variable template

**Contains**:
- Flask settings
- Security keys
- Server configuration
- Logging options
- Model paths
- EEG settings
- WebSocket config
- Upload settings
- Feature flags
- Deployment options

**How to Use**:
1. Copy: `cp .env.example .env`
2. Edit: `nano .env`
3. Set your values
4. App loads from `.env`

**Never commit** `.env` with real secrets!

---

### Directories to Create (Auto-created)

#### `uploads/` (user uploaded files)
**Purpose**: Store user-uploaded EEG data files

**Contents**:
- CSV files
- NumPy files (.npy)
- Model files (.h5)

**Cleanup**: Remove old files periodically

---

## File Organization Best Practices

### Backend Organization

```
backend/
├── app.py              # Routes and WebSocket
├── config.py           # Configuration
├── models/             # Database models (if added)
├── routes/             # Route blueprints (if splitting)
├── services/           # Business logic (if added)
├── utils/              # Helper functions (if added)
└── __init__.py         # Package init
```

**When to split**:
- More than 500 lines in app.py
- Multiple route groups
- Complex business logic
- Shared utilities

---

### Frontend Organization

```
frontend/
├── templates/
│   ├── index.html      # Main page
│   ├── base.html       # Base template (if added)
│   └── components/     # Component templates (if added)
└── static/
    ├── css/
    │   ├── dashboard.css
    │   ├── base.css    # Base styles (if added)
    │   └── components/ # Component styles (if added)
    ├── js/
    │   ├── dashboard.js
    │   ├── api.js      # API client (if split)
    │   └── utils.js    # Utilities (if added)
    └── img/            # Images (if added)
```

**When to split**:
- CSS exceeds 500 lines
- JavaScript exceeds 1000 lines
- Multiple pages needed
- Component reuse needed

---

## Development Workflow File Access

### When Adding a Feature

**Backend Route**:
1. Edit → `backend/app.py`
2. Add route function
3. Test via `API_TESTING_GUIDE.md`

**WebSocket Event**:
1. Edit → `backend/app.py`
2. Add @socketio.on() handler
3. Emit response

**Frontend Button/UI**:
1. Edit → `frontend/templates/index.html`
2. Add HTML element
3. Edit → `frontend/static/css/dashboard.css` for styling
4. Edit → `frontend/static/js/dashboard.js` for interactivity

**Configuration Option**:
1. Edit → `backend/config.py` (class definition)
2. Edit → `.env.example` (template)
3. Document in `README.md`

### When Debugging

1. **Check logs**: `logs/webapp.log`
2. **Check browser console**: `F12 → Console`
3. **Check Flask output**: Terminal where Flask runs
4. **Check config**: `backend/config.py`
5. **Read docs**: Relevant `.md` file

### When Deploying

1. Update → `requirements.txt`
2. Update → `.env` with production settings
3. Read → `README.md - Deployment`
4. Read → `DEPLOYMENT_GUIDE.md`
5. Test in staging first

---

## File Size Statistics

| File | Lines | Purpose |
|------|-------|---------|
| app.py | 400+ | Main Flask app |
| dashboard.js | 500+ | Frontend logic |
| README.md | 600+ | Complete docs |
| dashboard.css | 300+ | Styling |
| index.html | 200+ | Dashboard |
| DEVELOPMENT_SETUP.md | 500+ | Dev guide |
| API_TESTING_GUIDE.md | 400+ | Testing |
| QUICKSTART.md | 300+ | Quick start |
| config.py | 50+ | Configuration |
| requirements.txt | 10+ | Dependencies |
| .env.example | 100+ | Env template |
| __init__.py | 5 | Package init |

**Total Documentation**: 1900+ lines
**Total Code**: 1450+ lines

---

## File Dependencies

### app.py depends on:
- `config.py` (configuration)
- `backend/__init__.py` (package)
- Flask libraries (requirements.txt)
- Socket.io libraries

### dashboard.js depends on:
- `index.html` (HTML structure)
- `dashboard.css` (styling)
- Chart.js library
- Socket.io client library

### index.html depends on:
- `dashboard.css` (styling)
- `dashboard.js` (logic)
- Bootstrap 5 CDN
- Chart.js CDN
- Socket.io CDN

### Documentation depends on:
- Code files (for examples)
- Configuration files (for references)
-. 
---

## Common File Locations

### To change styling: 
`frontend/static/css/dashboard.css`

### To add API endpoint: 
`backend/app.py` (search for @app.route)

### To add WebSocket event: 
`backend/app.py` (search for @socketio.on)

### To modify dashboard layout: 
`frontend/templates/index.html`

### To change config: 
`backend/config.py`

### To set environment variables: 
`.env`

### To add dependency: 
`requirements.txt`

### To understand system: 
`README.md`

### To get started: 
`QUICKSTART.md`

### To develop: 
`DEVELOPMENT_SETUP.md`

### To test: 
`API_TESTING_GUIDE.md`

---

## File Naming Conventions

### Python Files
- `lowercase_with_underscores.py`
- `app.py` - main application
- `config.py` - configuration
- `__init__.py` - package marker

### HTML Files
- `lowercase_with_underscores.html`
- `index.html` - main page
- `base.html` - template base
- `components.html` - reusable parts

### CSS Files
- `lowercase_with_underscores.css`
- `dashboard.css` - dashboard styling
- `base.css` - base styles
- `components.css` - component styles

### JavaScript Files
- `camelCase.js`
- `dashboard.js` - dashboard logic
- `api.js` - API communication
- `utils.js` - utility functions

### Documentation
- `UPPERCASE.md` - Major docs
- `README.md` - Main documentation
- `QUICKSTART.md` - Quick start
- `.env` - Environment variables
- `requirements.txt` - Dependencies

---

## Version Control (.gitignore)

**Should commit**:
- `*.py` (code)
- `*.html`, `*.css`, `*.js` (frontend)
- `requirements.txt`
- `.env.example`
- `*.md` (documentation)

**Should NOT commit**:
- `.env` (secrets)
- `venv/` or `env/` (virtual environment)
- `__pycache__/` (Python cache)
- `*.log` (logs)
- `uploads/` (user files)
- `.DS_Store` (Mac)
- `.idea/` or `.vscode/` (IDE)

---

## Summary

The webapp is organized into:

1. **Backend** (`backend/`): Flask application
   - `app.py` - Routes and WebSocket
   - `config.py` - Configuration
   
2. **Frontend** (`frontend/`): Static assets
   - `templates/index.html` - Dashboard
   - `static/css/dashboard.css` - Styling
   - `static/js/dashboard.js` - Logic

3. **Documentation** (4 guides):
   - README.md - Complete guide
   - QUICKSTART.md - Fast start
   - DEVELOPMENT_SETUP.md - Dev setup
   - API_TESTING_GUIDE.md - Testing

4. **Configuration**:
   - `requirements.txt` - Dependencies
   - `.env.example` - Environment template

This organization keeps code organized, documentation clear, and development easy!

---

**Next**: Choose your starting point:
- [README.md](README.md) - Understand the system
- [QUICKSTART.md](QUICKSTART.md) - Get running fast
- [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md) - Set up for development
- [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md) - Test the system
