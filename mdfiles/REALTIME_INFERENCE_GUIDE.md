# Real-Time BCI Mouse Control System - Complete Guide

## Overview

A production-ready real-time EEG-based mouse control system that:
1. Loads trained CNN-LSTM models
2. Processes EEG signals in real-time
3. Predicts motor imagery classes
4. Executes mouse actions based on predictions
5. Includes smoothing for natural cursor movement

## Features

### ✅ Core Features
- **Model Loading**: Supports TensorFlow .h5 and SavedModel formats
- **Real-Time Inference**: Online predictions from streaming EEG data
- **Motor Imagery Mapping**: 5-class classification to mouse actions
- **Cursor Smoothing**: Exponential smoothing for natural movements
- **Safety Features**: Edge detection, pause mode, debouncing

### ✅ Action Mapping
| Motor Imagery | Action | Result |
|---------------|--------|--------|
| **Left** | `move_left` | Cursor moves left 50px |
| **Right** | `move_right` | Cursor moves right 50px |
| **Hands** | `move_up` | Cursor moves up 50px |
| **Feet** | `move_down` | Cursor moves down 50px |
| **Click** | `click` | Mouse click at current position |

### ✅ Safety Features
- **Confidence Thresholding**: Ignore low-confidence predictions
- **Debouncing**: Require consistent predictions before action
- **Edge Detection**: Prevent cursor from leaving screen
- **Pause Mode**: Easily pause/resume controller
- **Action Cooldown**: Prevent rapid-fire actions

## Quick Start

### 1. Demo with Simulation

```bash
# Run demo with synthetic EEG input
python realtime_inference_demo.py \
  --model models/best_eeg_model.h5 \
  --simulate

# Expected output:
# - 20 iterations of prediction and mouse action
# - Synthesis of class-specific EEG patterns
# - Real-time statistics
```

### 2. Interactive Mode

```bash
# Manual control - test each prediction
python realtime_inference_demo.py \
  --model models/best_eeg_model.h5 \
  --interactive

# Then type:
# 0-4: Generate signal for class 0-4
# p: Pause/Resume
# s: Show status
# q: Quit
```

### 3. Batch Testing

```bash
# Test each class multiple times
python realtime_inference_demo.py \
  --model models/best_eeg_model.h5 \
  --batch

# Tests each of 5 classes 3 times
# Displays accuracy per class
```

## Components

### RealtimeInferenceEngine
Main inference system that coordinates model loading, buffering, and predictions.

```python
from src.realtime_inference import RealtimeInferenceEngine

# Initialize
engine = RealtimeInferenceEngine(
    model_path='models/best_eeg_model.h5',
    config={
        'data': {'eeg_channels': 8, 'sampling_rate': 250},
        'realtime': {'buffer_size': 250}
    },
    move_distance=50,
    confidence_threshold=0.7
)

# Add EEG samples
eeg_sample = np.random.randn(8)  # Single sample
engine.add_sample(eeg_sample)

# Or batch
eeg_batch = np.random.randn(250, 8)  # 250 samples, 8 channels
engine.add_samples(eeg_batch)

# Check readiness
if engine.is_ready():
    # Make prediction
    result = engine.predict()
    
    # Execute action if confident
    if result['confidence'] > 0.7:
        action = engine.controller.predict_and_act(
            result['predicted_class'],
            result['confidence']
        )
```

### CursorSmoother
Exponential smoothing for natural cursor movement.

```python
from src.realtime_inference import CursorSmoother

# Create smoother
smoother = CursorSmoother(alpha=0.3, enabled=True)

# Smooth positions
x, y = 100, 200
smoothed_x, smoothed_y = smoother.smooth((x, y))

# Get velocity
velocity = smoother.get_velocity()
```

### BCIMouseController
Maps predictions to mouse actions with safety features.

```python
from src.realtime_inference import BCIMouseController

# Create controller
controller = BCIMouseController(
    move_distance=50,           # 50px per action
    confidence_threshold=0.7,   # Need 70%+ confidence
    smoothing_alpha=0.3,        # Smoothing factor
    debounce_count=3            # Need 3 consistent predictions
)

# Execute action
action = controller.predict_and_act(
    predicted_class=1,    # Right
    confidence=0.85
)

# Pause/Resume
controller.set_pause(True)  # Pause
controller.set_pause(False) # Resume

# Get statistics
stats = controller.get_statistics()
```

## Configuration

### Default Configuration

```python
{
    'data': {
        'eeg_channels': 8,           # Number of EEG channels
        'sampling_rate': 250,        # Sampling rate in Hz
        'segment_duration': 1.0      # Segment duration in seconds
    },
    'realtime': {
        'buffer_size': 250,          # Samples to collect (1 second at 250Hz)
        'update_interval': 0.1,      # Update interval in seconds
        'confidence_threshold': 0.7  # Min confidence for action
    }
}
```

### Custom Configuration (YAML)

Create `realtime_config.yaml`:
```yaml
data:
  eeg_channels: 8
  sampling_rate': 250

realtime:
  buffer_size: 250
  update_interval: 0.05
  confidence_threshold: 0.8
```

Use it:
```bash
python realtime_inference_demo.py \
  --model models/best_eeg_model.h5 \
  --config realtime_config.yaml \
  --simulate
```

## Usage Examples

### Example 1: Basic Inference

```python
from src.realtime_inference import RealtimeInferenceEngine
import numpy as np

# Load config
config = {
    'data': {'eeg_channels': 8, 'sampling_rate': 250},
    'realtime': {'buffer_size': 250}
}

# Create engine
engine = RealtimeInferenceEngine(
    model_path='models/best_eeg_model.h5',
    config=config
)

# Simulate EEG input
for i in range(100):
    # Get EEG sample (real or simulated)
    eeg_sample = np.random.randn(8)
    
    # Add to buffer
    engine.add_sample(eeg_sample)
    
    # Process if ready
    action = engine.process_signal()
    
    if action:
        print(f"Action: {action}")
```

### Example 2: Batch Prediction

```python
# Load multiple signals
eeg_signals = np.random.randn(1000, 8)  # 1000 samples, 8 channels

# Split into buffers
buffer_size = 250
for i in range(0, len(eeg_signals), buffer_size):
    batch = eeg_signals[i:i+buffer_size]
    
    if len(batch) == buffer_size:
        engine.eeg_buffer.clear()
        engine.add_samples(batch)
        
        result = engine.predict()
        if result:
            print(f"Predicted: {result['class_label']} "
                  f"({result['confidence']:.2%})")
```

### Example 3: Simulation with Different Confidence

```python
# Test with different thresholds
for threshold in [0.5, 0.7, 0.9]:
    controller = BCIMouseController(
        confidence_threshold=threshold
    )
    
    # Test predictions
    for conf in [0.4, 0.6, 0.8, 0.95]:
        action = controller.predict_and_act(
            predicted_class=1,
            confidence=conf
        )
        
        print(f"Threshold: {threshold}, Confidence: {conf}, "
              f"Action: {action or 'None'}")
```

## Class Mapping

```python
CLASS_LABELS = {
    0: 'Left',      # Motor imagery: left hand
    1: 'Right',     # Motor imagery: right hand
    2: 'Hands',     # Motor imagery: both hands
    3: 'Feet',      # Motor imagery: both feet
    4: 'Click'      # Motor imagery: rest/click
}

ACTION_MAPPING = {
    'Left': 'move_left',
    'Right': 'move_right',
    'Hands': 'move_up',
    'Feet': 'move_down',
    'Click': 'click'
}
```

## Performance Monitoring

### Get Status
```python
status = engine.get_status()
print(status)
# {
#     'running': True,
#     'uptime_seconds': 45.2,
#     'buffer_usage': '250/250',
#     'predictions_made': 12,
#     'controller_paused': False,
#     'controller_stats': {...}
# }
```

### Get Statistics
```python
stats = controller.get_statistics()
print(stats)
# {
#     'total_predictions': 100,
#     'action_counts': {
#         'move_left': 15,
#         'move_right': 18,
#         'move_up': 22,
#         'move_down': 20,
#         'click': 5
#     },
#     'paused': False,
#     'screen_size': (1920, 1080),
#     'cursor_smoother_velocity': 5.2
# }
```

## Command-Line Options

```
usage: realtime_inference_demo.py [-h] --model MODEL [--config CONFIG]
                                  [--simulate] [--interactive] [--batch]
                                  [--iterations ITERATIONS]
                                  [--move-distance MOVE_DISTANCE]
                                  [--confidence-threshold CONFIDENCE_THRESHOLD]

Options:
  -h, --help                Show this help message
  --model MODEL             Path to trained model (REQUIRED)
  --config CONFIG           Path to custom YAML config
  --simulate                Run simulation mode
  --interactive             Run interactive mode
  --batch                   Run batch testing mode
  --iterations N            Number of iterations (default: 20)
  --move-distance N         Pixels per action (default: 50)
  --confidence-threshold T  Min confidence (default: 0.7)
```

## Common Scenarios

### Scenario 1: Real-Time Mouse Control

```bash
# Test with synthetic data at realistic speed
python realtime_inference_demo.py \
  --model models/best_eeg_model.h5 \
  --simulate \
  --iterations 100
```

### Scenario 2: Accuracy Testing

```bash
# Test accuracy of each class
python realtime_inference_demo.py \
  --model models/best_eeg_model.h5 \
  --batch
```

### Scenario 3: Sensitivity Tuning

```bash
# Test with different confidence thresholds
for threshold in 0.5 0.7 0.9; do
    echo "Testing threshold: $threshold"
    python realtime_inference_demo.py \
      --model models/best_eeg_model.h5 \
      --simulate \
      --confidence-threshold $threshold
done
```

### Scenario 4: Speed vs Accuracy

```bash
# Test with different move distances
for distance in 25 50 100 200; do
    echo "Testing move distance: ${distance}px"
    python realtime_inference_demo.py \
      --model models/best_eeg_model.h5 \
      --simulate \
      --move-distance $distance
done
```

## Advanced Features

### Cursor Smoothing

Exponential smoothing for natural cursor movement:

```
smoothed_x = alpha * new_x + (1 - alpha) * old_x
```

- **alpha = 0.3** (default): Smooth, lag ~200ms
- **alpha = 0.5**: Moderate smoothing, lag ~100ms
- **alpha = 0.9**: Minimal smoothing, lag ~20ms
- **alpha = 1.0**: No smoothing, immediate response

### Debouncing

Requires N consistent predictions before executing action:

```python
debounce_count = 3  # Requires 3 consistent predictions

# Example:
# Prediction 1: Left (0.75) - buffered
# Prediction 2: Left (0.82) - buffered
# Prediction 3: Left (0.78) - ACTION: MOVE_LEFT
```

### Confidence Threshold

Filters out low-confidence predictions:

```python
confidence_threshold = 0.7

# Example:
# Prediction: Right (0.65) - IGNORED (below threshold)
# Prediction: Right (0.85) - CONSIDERED (above threshold)
```

## Troubleshooting

### Issue: Model not found
```
Solution: Ensure model path is correct
python realtime_inference_demo.py --model models/best_eeg_model.h5
```

### Issue: Low accuracy
```
Solution: Increase debounce_count or confidence_threshold
python realtime_inference_demo.py \
  --model models/best_eeg_model.h5 \
  --confidence-threshold 0.9
```

### Issue: Cursor moves too slow
```
Solution: Increase move_distance parameter
python realtime_inference_demo.py \
  --model models/best_eeg_model.h5 \
  --move-distance 100
```

### Issue: Cursor movement is jittery
```
Solution: Smoothing is already applied (alpha=0.3)
Default configuration provides good balance
```

## File Structure

```
BCI_INTERFACE/
├── src/
│   ├── realtime_inference.py     # Main inference module
│   ├── train.py                  # Training module
│   ├── model.py                  # Model architecture
│   └── ...
├── realtime_inference_demo.py    # Demo script
├── models/
│   └── best_eeg_model.h5        # Trained model
└── requirements.txt
```

## Requirements

```
tensorflow >= 2.10
numpy
pyautogui >= 0.9.53
pyyaml
```

Install:
```bash
pip install -r requirements.txt
```

## Performance

### Expected Performance
- Inference latency: ~10-50ms (per prediction)
- Cursor update rate: 10-100 Hz
- Memory usage: ~100MB (model + buffer)
- CPU usage: ~10-20% (per prediction)

### Optimization Tips
- Reduce buffer_size for lower latency
- Increase batch processing for throughput
- Enable GPU acceleration for faster inference

## Safety Considerations

1. **Cursor Out-of-Bounds**: System prevents cursor from leaving screen (20px margin)
2. **Accidental Clicks**: Use high confidence threshold to prevent unintended clicks
3. **Pause Mode**: Easily pause with `controller.set_pause(True)`
4. **Action Cooldown**: 100ms between actions prevents rapid clicking

## Tutorial: Building a Custom Application

```python
from src.realtime_inference import RealtimeInferenceEngine
import threading
import time

class BCIMouseApp:
    def __init__(self, model_path):
        self.engine = RealtimeInferenceEngine(
            model_path=model_path,
            config=config,
            confidence_threshold=0.8
        )
        self.running = False
    
    def process_eeg(self, eeg_buffer):
        """Process EEG buffer and execute action."""
        self.engine.add_samples(eeg_buffer)
        action = self.engine.process_signal()
        return action
    
    def start(self):
        """Start inference engine."""
        self.running = True
        self.engine.start()
    
    def stop(self):
        """Stop inference engine."""
        self.running = False
        self.engine.stop()

# Usage
app = BCIMouseApp('models/best_eeg_model.h5')
app.start()

# Feed data
while app.running:
    eeg_data = get_eeg_data()  # Your data source
    action = app.process_eeg(eeg_data)
    time.sleep(0.01)

app.stop()
```

## References

- CNN-LSTM Model: See `MODEL_GUIDE.md`
- Training System: See `TRAINING_IMPLEMENTATION_GUIDE.md`
- Data Preparation: See `DATA_PREPARATION_GUIDE.md`

---

**Version:** 2.0 | **Status:** Production-Ready | **Date:** 2024
