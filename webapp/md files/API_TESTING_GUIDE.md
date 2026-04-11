# BCI Web App - API Testing Guide

Complete guide for testing the BCI Web App REST API and WebSocket endpoints.

## Table of Contents

1. [Quick Start](#quick-start)
2. [REST API Testing](#rest-api-testing)
3. [WebSocket Testing](#websocket-testing)
4. [Tools & Setup](#tools--setup)
5. [Test Scenarios](#test-scenarios)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Minimal Test

```bash
# Start Flask server
cd webapp/backend
python app.py

# In another terminal, test endpoint
curl http://localhost:5000/api/status
```

Expected response:
```json
{
  "status": "running",
  "timestamp": "2024-01-15T10:30:00",
  "version": "1.0.0",
  "webapp_version": "1.0.0"
}
```

---

## REST API Testing

### Endpoint List

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Main dashboard |
| GET | `/api/status` | System status |
| GET | `/api/models` | List models |
| GET | `/api/config` | App configuration |

### Test with cURL

#### 1. Get System Status

```bash
curl -X GET http://localhost:5000/api/status
```

**Expected**: 200 OK with status information

```json
{
  "status": "running",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "webapp_version": "1.0.0"
}
```

#### 2. List Models

```bash
curl -X GET http://localhost:5000/api/models
```

**Expected**: 200 OK with model list

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

#### 3. Get Configuration

```bash
curl -X GET http://localhost:5000/api/config
```

**Expected**: 200 OK with configuration

```json
{
  "sampling_rate": 250,
  "channels": 8,
  "classes": [
    "Left Hand",
    "Right Hand",
    "Both Hands",
    "Both Feet",
    "Tongue/Click"
  ],
  "buffer_size": 250
}
```

#### 4. Load Dashboard

```bash
curl -X GET http://localhost:5000/
```

**Expected**: 200 OK with HTML page

### Test with Python

```python
import requests
import json

BASE_URL = 'http://localhost:5000'

# Test status endpoint
response = requests.get(f'{BASE_URL}/api/status')
print(f"Status: {response.status_code}")
print(f"Data: {json.dumps(response.json(), indent=2)}")

# Test models endpoint
response = requests.get(f'{BASE_URL}/api/models')
print(f"Models: {response.json()}")

# Test config endpoint
response = requests.get(f'{BASE_URL}/api/config')
print(f"Config: {response.json()}")
```

### Test with Postman

1. **Import Collection**:
   - Click Import → Paste raw JSON below

2. **Postman Collection JSON**:
```json
{
  "info": {
    "name": "BCI Web App API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Status",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:5000/api/status",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "status"]
        }
      }
    },
    {
      "name": "Get Models",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:5000/api/models",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "models"]
        }
      }
    },
    {
      "name": "Get Config",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:5000/api/config",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "config"]
        }
      }
    }
  ]
}
```

3. **Run Tests**:
   - Click blue "Send" button for each request
   - Verify responses

---

## WebSocket Testing

### Browser Console Testing

Open dashboard at `http://localhost:5000` and use browser console (F12 → Console):

#### 1. Test Connection

```javascript
// Check connection status
console.log(socket.connected);  // true/false

// Manually connect (if disconnected)
socket.connect();

// Disconnect
socket.disconnect();
```

#### 2. Start Streaming

```javascript
// Start EEG stream
socket.emit('start_stream');

// Listen for EEG samples
socket.on('eeg_sample', (data) => {
    console.log('EEG Sample:', data);
});

// Listen for predictions
socket.on('prediction', (data) => {
    console.log('Prediction:', data);
});
```

#### 3. Stop Streaming

```javascript
socket.emit('stop_stream');
```

#### 4. Request Single Sample

```javascript
socket.emit('request_eeg_sample');

// Listen for response
socket.on('eeg_sample', (data) => {
    console.log('Sample received:', data);
});
```

#### 5. Train Model

```javascript
socket.emit('train_model', {
    config: {
        epochs: 50,
        batch_size: 32,
        learning_rate: 0.001
    }
});

// Listen for training progress
socket.on('training_progress', (data) => {
    console.log('Training progress:', data);
});

// Listen for completion
socket.on('training_complete', (data) => {
    console.log('Training complete:', data);
});
```

#### 6. Evaluate Model

```javascript
socket.emit('evaluate_model', {
    model: 'bci_model_best'
});

// Listen for results
socket.on('evaluation_result', (data) => {
    console.log('Evaluation result:', data);
});
```

### Python Socket.IO Client Testing

```python
import socketio
import time

# Create client
sio = socketio.Client()

@sio.event
def connect():
    print('Connection established')
    # Start streaming
    sio.emit('start_stream')

@sio.event
def eeg_sample(data):
    print(f'EEG Sample: {data}')

@sio.event
def prediction(data):
    print(f'Prediction: {data}')

@sio.event
def error(data):
    print(f'Error: {data}')

# Connect to server
sio.connect('http://localhost:5000')

# Keep connected for 10 seconds
time.sleep(10)

# Stop streaming
sio.emit('stop_stream')

# Disconnect
sio.disconnect()
```

### Node.js Socket.IO Client Testing

```javascript
const io = require('socket.io-client');

const socket = io('http://localhost:5000');

socket.on('connect', () => {
    console.log('Connected to server');
    socket.emit('start_stream');
});

socket.on('eeg_sample', (data) => {
    console.log('EEG Sample:', data);
});

socket.on('prediction', (data) => {
    console.log('Prediction:', data);
});

socket.on('error', (data) => {
    console.error('Error:', data);
});

// Stop after 10 seconds
setTimeout(() => {
    socket.emit('stop_stream');
    socket.disconnect();
}, 10000);
```

---

## Tools & Setup

### Tool 1: cURL (Command Line)

**Already available on most systems**

```bash
# Test endpoint
curl http://localhost:5000/api/status

# With headers
curl -H "Content-Type: application/json" http://localhost:5000/api/status

# Pretty print JSON
curl http://localhost:5000/api/status | python -m json.tool
```

### Tool 2: Python Requests

```bash
pip install requests
```

Test script:
```python
import requests

url = 'http://localhost:5000/api/status'
response = requests.get(url)
print(response.json())
```

### Tool 3: Postman

Download from: https://www.postman.com/downloads/

**Benefits**:
- GUI for testing
- Environment variables
- Pre-request scripts
- Test automation
- Request history

### Tool 4: Thunder Client (VS Code)

```bash
# Install extension
# VS Code → Extensions → Thunder Client
```

**Quick start**:
1. Click Thunder Client icon
2. Enter URL: `http://localhost:5000/api/status`
3. Click Send

### Tool 5: Browser DevTools

**No installation needed**

1. Open `http://localhost:5000`
2. Press F12 (DevTools)
3. Go to Console tab
4. Run JavaScript commands

### Tool 6: JMeter (Performance Testing)

Download from: https://jmeter.apache.org/

Useful for:
- Load testing
- Stress testing
- Performance profiling

---

## Test Scenarios

### Scenario 1: Basic Connectivity

**Goal**: Verify server is running

1. Start Flask server
2. Run: `curl http://localhost:5000/`
3. **Expected**: Dashboard HTML loads

### Scenario 2: API Endpoints

**Goal**: Verify all REST endpoints work

```bash
# Test status
curl http://localhost:5000/api/status
# Expected: 200 OK, JSON response

# Test models
curl http://localhost:5000/api/models
# Expected: 200 OK, JSON with models array

# Test config
curl http://localhost:5000/api/config
# Expected: 200 OK, JSON with config
```

### Scenario 3: WebSocket Connection

**Goal**: Verify real-time communication

1. Open dashboard
2. Open DevTools console
3. Run:
```javascript
socket.on('connect', () => {
    console.log('✓ WebSocket connected');
});
```
4. **Expected**: "✓ WebSocket connected" logs

### Scenario 4: Data Streaming

**Goal**: Verify EEG data streaming

1. Open dashboard
2. Console:
```javascript
let sampleCount = 0;
socket.on('eeg_sample', () => {
    sampleCount++;
    console.log(`Received ${sampleCount} samples`);
});
socket.emit('start_stream');
```
3. **Expected**: Sample counter increments

### Scenario 5: Predictions

**Goal**: Verify model predictions

1. Open dashboard
2. Console:
```javascript
socket.on('prediction', (data) => {
    console.log(`Prediction: ${data.class} (${(data.confidence * 100).toFixed(1)}%)`);
});
socket.emit('request_eeg_sample');
```
3. **Expected**: Prediction displayed

### Scenario 6: Training Simulation

**Goal**: Verify training progress

1. Open dashboard
2. Console:
```javascript
socket.emit('train_model', {config: {epochs: 5}});
socket.on('training_progress', (data) => {
    console.log(`Epoch ${data.epoch}: Loss=${data.loss.toFixed(3)}, Acc=${data.accuracy.toFixed(1)}%`);
});
socket.on('training_complete', (data) => {
    console.log('✓ Training complete:', data);
});
```
3. **Expected**: Progress updates, then completion

### Scenario 7: Error Handling

**Goal**: Verify error handling

1. Close server
2. Refresh dashboard at `http://localhost:5000`
3. **Expected**: Error message in console
4. Restart server
5. **Expected**: Connection restored automatically

---

## Testing Checklist

### Pre-Testing
- [ ] Flask server running (`python app.py`)
- [ ] No port conflicts
- [ ] Browser is modern (Chrome, Firefox, Safari, Edge)
- [ ] Console open (F12)
- [ ] Network tab available

### REST API Testing
- [ ] `GET /` returns dashboard
- [ ] `GET /api/status` returns status
- [ ] `GET /api/models` returns models list
- [ ] `GET /api/config` returns configuration
- [ ] All endpoints return correct JSON
- [ ] All endpoints return correct status codes (200)

### WebSocket Testing
- [ ] Socket connects successfully
- [ ] `start_stream` starts EEG streaming
- [ ] `stop_stream` stops streaming
- [ ] `request_eeg_sample` returns single sample
- [ ] `train_model` sends progress updates
- [ ] `evaluate_model` returns results
- [ ] Error events are captured
- [ ] Disconnect/reconnect works

### Frontend Testing
- [ ] Dashboard loads without errors
- [ ] Charts display and animate
- [ ] Status indicators update
- [ ] Streaming toggle works
- [ ] Model dropdown populates
- [ ] Charts responsive on mobile

### Performance Testing
- [ ] No console errors
- [ ] Smooth chart animations
- [ ] No memory leaks
- [ ] CPU usage reasonable
- [ ] WebSocket latency < 100ms

---

## Troubleshooting

### Issue: Connection Refused

```
Error: Failed to connect to http://localhost:5000
```

**Solution**:
1. Verify Flask is running
2. Check port 5000 is available
3. Check firewall settings
4. Try different URL: `http://127.0.0.1:5000`

### Issue: WebSocket Won't Connect

```
WebSocket connection failed
```

**Solution**:
1. Check Flask is running with Socket.IO
2. Check CORS settings in config.py
3. Verify no proxy interference
4. Refresh page (Ctrl+R)
5. Check browser console for errors

### Issue: API Returns 404

```
{
  "error": "Not found"
}
```

**Solution**:
1. Verify endpoint URL spelling
2. Check if endpoint exists in app.py
3. Ensure Flask server Running
4. Check port (should be 5000)

### Issue: CORS Error

```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solution**:
In `app.py`:
```python
CORS(app, origins="*")  # Allow all origins
# Or restrict:
CORS(app, origins=["http://localhost:5000"])
```

### Issue: 500 Server Error

```
Internal Server Error
```

**Solution**:
1. Check Flask server logs
2. Check Python syntax errors
3. Verify all imports available
4. Check database connections
5. Restart server

---

## Performance Testing

### Load Testing with Apache Bench

```bash
# Install
# Mac: brew install httpd
# Linux: apt-get install apache2-utils

# Test 1000 requests
ab -n 1000 -c 10 http://localhost:5000/api/status

# Expected: ~100-200 req/sec on dev server
```

### Stress Testing

```bash
# Test with concurrent requests
ab -n 10000 -c 100 http://localhost:5000/api/status

# Monitor with:
# Mac/Linux: top
# Windows: Task Manager
```

---

## Continuous Testing

### Automated Test Script

Create `test_api.py`:

```python
import requests
import json
import time

def test_endpoints():
    """Test all API endpoints"""
    base_url = 'http://localhost:5000'
    
    tests = [
        ('Status', f'{base_url}/api/status'),
        ('Models', f'{base_url}/api/models'),
        ('Config', f'{base_url}/api/config'),
    ]
    
    for name, url in tests:
        try:
            response = requests.get(url)
            status = '✓' if response.status_code == 200 else '✗'
            print(f'{status} {name}: {response.status_code}')
        except Exception as e:
            print(f'✗ {name}: {e}')

if __name__ == '__main__':
    test_endpoints()
```

Run:
```bash
python test_api.py
```

---

## Resources

- **Flask Testing**: https://flask.palletsprojects.com/testing/
- **Pytest**: https://docs.pytest.org/
- **Socket.IO Testing**: https://python-socketio.readthedocs.io/
- **Postman Docs**: https://learning.postman.com/
- **JMeter Tutorial**: https://jmeter.apache.org/usermanual/

---

## Summary

**Quick Test Commands**:
```bash
# 1. Basic connectivity
curl http://localhost:5000/

# 2. API endpoints
curl http://localhost:5000/api/status

# 3. Open dashboard
# http://localhost:5000

# 4. Browser console test
# socket.emit('start_stream')
```

---

**Happy Testing!** 🧪
