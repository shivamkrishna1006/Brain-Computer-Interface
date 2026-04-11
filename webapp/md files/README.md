# BCI Web Application

Real-time EEG visualization and motor imagery classification dashboard built with Flask and Socket.IO.

## Overview

The BCI Web App provides an interactive interface to monitor, train, and evaluate brain-computer interface (BCI) models in real-time. It features:

- **Live EEG Signal Visualization** - Real-time 8-channel EEG display
- **Confidence Score Charts** - 5-class motor imagery predictions
- **System Monitoring** - Model status, streaming state, prediction metrics
- **Model Management** - Upload, select, and manage trained models
- **Data Upload** - Import EEG recordings for batch prediction
- **Training Interface** - Monitor live training progress
- **Responsive Dashboard** - Mobile-friendly Bootstrap 5 UI

## Architecture

```
webapp/
├── backend/                 # Flask application
│   ├── app.py              # Main Flask app with routes & WebSocket handlers
│   ├── config.py           # Configuration classes
│   └── __init__.py         # Package initialization
└── frontend/               # Static assets & templates
    ├── templates/
    │   └── index.html      # Main dashboard
    ├── static/
    │   ├── css/
    │   │   └── dashboard.css  # Professional styling
    │   └── js/
    │       └── dashboard.js   # Frontend logic & Socket.IO client
```

## Installation

### Prerequisites

- Python 3.8+
- TensorFlow 2.13+
- Node.js 14+ (optional, for frontend development)

### Setup

1. **Install dependencies**:

```bash
cd webapp
pip install -r requirements.txt

# Or install from main project
pip install -r requirements.txt  # Main project dependencies
pip install -r requirements.txt  # Webapp dependencies
```

2. **Create necessary directories**:

```bash
mkdir -p logs uploads models data outputs
```

3. **Configure environment**:

```bash
# Copy example environment file
cp ../.env.example .env

# Edit .env with your settings
nano .env
```

## Configuration

The Flask app uses configuration classes in `backend/config.py`:

```python
# Development (default)
export FLASK_ENV=development
export FLASK_DEBUG=1

# Production
export FLASK_ENV=production
export FLASK_DEBUG=0
```

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `FLASK_ENV` | str | development | Flask environment |
| `FLASK_DEBUG` | bool | True (dev) | Debug mode |
| `SECRET_KEY` | str | dev-key | Session encryption key |
| `LOG_LEVEL` | str | INFO | Logging level |
| `MAX_CONTENT_LENGTH` | int | 50MB | Max upload size |
| `SOCKETIO_CORS_ALLOWED_ORIGINS` | str | * | CORS origins |

## Running the Application

### Development Server

```bash
cd webapp/backend
python app.py
```

The dashboard will be available at `http://localhost:5000`

### Production Server

```bash
# Using gunicorn with Socket.IO support
pip install gunicorn
gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:5000
```

### Docker

```bash
# Build image
docker build -t bci-webapp .

# Run container
docker run -p 5000:5000 bci-webapp
```

## API Reference

### REST Endpoints

#### GET `/`
Main dashboard page

**Response**: HTML page

---

#### GET `/api/status`
Get system status

**Response**:
```json
{
  "status": "running",
  "timestamp": "2024-01-15T10:30:00",
  "version": "1.0.0",
  "webapp_version": "1.0.0"
}
```

---

#### GET `/api/models`
List available trained models

**Response**:
```json
{
  "models": [
    {
      "name": "bci_model_best",
      "path": "/models/bci_model_best.h5",
      "size": "45.23MB",
      "created": "2024-01-10T14:30:00"
    }
  ],
  "count": 1
}
```

---

#### GET `/api/config`
Get webapp configuration

**Response**:
```json
{
  "sampling_rate": 250,
  "channels": 8,
  "classes": ["Left Hand", "Right Hand", "Both Hands", "Both Feet", "Tongue/Click"],
  "buffer_size": 250
}
```

---

### WebSocket Events

#### Client → Server Events

**`connect`** - Client connects to server
```javascript
socket.emit('connect')
```

---

**`start_stream`** - Start EEG data streaming
```javascript
socket.emit('start_stream', {})
```

---

**`stop_stream`** - Stop EEG data streaming
```javascript
socket.emit('stop_stream', {})
```

---

**`request_eeg_sample`** - Request single EEG sample
```javascript
socket.emit('request_eeg_sample')
```

---

**`train_model`** - Train new model
```javascript
socket.emit('train_model', {
  config: {
    epochs: 50,
    batch_size: 32,
    learning_rate: 0.001
  }
})
```

---

**`evaluate_model`** - Evaluate existing model
```javascript
socket.emit('evaluate_model', {
  model: 'bci_model_best'
})
```

---

#### Server → Client Events

**`eeg_sample`** - EEG data sample
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "sample": [0.5, -0.3, 0.2, ...],
  "channels": ["CH1", "CH2", "CH3", ...]
}
```

---

**`prediction`** - Model prediction result
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "class": "Right Hand",
  "class_idx": 1,
  "confidence": 0.87,
  "probabilities": {
    "Left Hand": 0.05,
    "Right Hand": 0.87,
    "Both Hands": 0.03,
    "Both Feet": 0.02,
    "Tongue/Click": 0.03
  }
}
```

---

**`training_progress`** - Training progress update
```json
{
  "epoch": 10,
  "progress": 20.0,
  "loss": 0.34,
  "val_loss": 0.38,
  "accuracy": 72.5
}
```

---

**`training_complete`** - Training finished
```json
{
  "status": "completed",
  "final_accuracy": 73.21,
  "model_name": "bci_model_1705314600"
}
```

---

**`evaluation_result`** - Evaluation complete
```json
{
  "model": "bci_model_best",
  "accuracy": 71.47,
  "per_class_accuracy": {
    "Left Hand": 72.3,
    "Right Hand": 73.1,
    "Both Hands": 70.5,
    "Both Feet": 68.9,
    "Tongue/Click": 72.1
  },
  "f1_score": 0.70
}
```

---

## Frontend Usage

### Dashboard Sections

#### Prediction Display
- Real-time EEG signal visualization (8 channels)
- Confidence scores for each motor imagery class
- Current prediction and confidence level

#### Model Management
- Select from available trained models
- View model metadata (creation date, size)
- Upload new model files

#### Data Upload
- Upload EEG recordings (.csv, .npy format)
- Auto-process and generate predictions
- View batch results

#### System Monitor
- Active model status
- Streaming status (on/off)
- Total predictions made
- System health metrics

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `S` | Toggle streaming |
| `C` | Clear history |
| `R` | Reset display |
| `M` | Toggle model selector |

## Development

### Project Structure

```
backend/
├── app.py              # Flask application (400+ lines)
├── config.py           # Configuration classes (50+ lines)
└── __init__.py         # Package init (5 lines)

frontend/
├── templates/
│   └── index.html      # Dashboard template (200+ lines)
└── static/
    ├── css/
    │   └── dashboard.css  # Styling (300+ lines)
    └── js/
        └── dashboard.js   # Frontend logic (500+ lines)
```

### Adding New Features

**Backend Route Example**:
```python
@app.route('/api/new-endpoint')
def new_endpoint():
    """New endpoint documentation"""
    try:
        # Your logic here
        return jsonify({'result': 'success'})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
```

**WebSocket Handler Example**:
```python
@socketio.on('new_event')
def handle_new_event(data):
    """New WebSocket event handler"""
    try:
        # Your logic here
        emit('response', {'status': 'processed'})
    except Exception as e:
        logger.error(f"Error: {e}")
        emit('error', {'message': str(e)})
```

**Frontend Event Listener**:
```javascript
socket.on('response', (data) => {
    console.log('Received:', data);
    // Update UI
});
```

## Testing

### Manual Testing

1. **Start server**:
```bash
cd webapp/backend
python app.py
```

2. **Open dashboard**:
```
http://localhost:5000
```

3. **Test WebSocket**:
- Click "Start Streaming"
- Verify EEG chart updates
- Observe confidence scores changing
- Check server logs for events

### Automated Testing

```bash
# Create test file
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=backend
```

## Troubleshooting

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### WebSocket Connection Failed

1. Check CORS settings in `config.py`
2. Verify server is running: `http://localhost:5000`
3. Check browser console for errors
4. Ensure firewall allows port 5000

### Models Not Found

```bash
# Create models directory structure
mkdir -p models data outputs logs

# Copy trained models
cp ../../models/*.h5 models/
```

### High Latency

1. Reduce chart sample history (dashboard.js line ~450)
2. Disable verbose logging (LOG_LEVEL = 'WARNING')
3. Increase WebSocket buffer size (config.py)

## Performance Optimization

### Frontend
- Chart.js max 500 points displayed
- Throttle WebSocket events to 10/second
- Lazy load static assets
- Enable gzip compression

### Backend
- Thread-based Socket.IO async mode
- Database connection pooling
- Cache model metadata
- Batch process predictions

### Deployment
- Use gunicorn with multiple workers
- Enable Redis message queue for scale
- Implement load balancing
- Use CDN for static assets

## Security

### Production Checklist

- [ ] Change SECRET_KEY in config
- [ ] Set FLASK_ENV=production
- [ ] Use HTTPS/TLS
- [ ] Enable CORS restrictions
- [ ] Set secure cookies
- [ ] Add authentication for API
- [ ] Validate file uploads
- [ ] Implement rate limiting
- [ ] Add input sanitization
- [ ] Use environment variables for secrets

### Best Practices

```python
# ✅ Good - Use environment variables
SECRET_KEY = os.environ.get('SECRET_KEY')

# ❌ Bad - Hardcoded secrets
SECRET_KEY = 'my-secret-123'
```

## Deployment

### Local Development
```bash
cd webapp/backend
python app.py
```

### Docker
```bash
docker build -t bci-webapp .
docker run -p 5000:5000 bci-webapp
```

### Production (Ubuntu/Linux)
```bash
# Install dependencies
sudo apt-get install python3-pip python3-venv nginx supervisord

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Run with gunicorn
gunicorn --worker-class eventlet -w 1 app:app
```

### Cloud Deployment

See [../DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) for AWS, GCP, Azure, and Kubernetes instructions.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see [../LICENSE](../LICENSE) file for details.

## Contact

For questions or support:
- Issues: GitHub Issues
- Email: support@example.com
- Documentation: [../DOCUMENTATION_INDEX.md](../DOCUMENTATION_INDEX.md)

## Acknowledgments

- TensorFlow/Keras team for deep learning framework
- Flask and Socket.IO communities
- Chart.js for visualization
- Bootstrap for responsive design

---

**Last Updated**: January 2024
**Version**: 1.0.0
**Status**: Production Ready
