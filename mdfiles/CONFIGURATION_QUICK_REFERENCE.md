# Configuration Quick Reference

Fast lookup for common configuration tasks.

## Loading Configuration

### Automatic (Recommended)
```python
from src.config import load_config

# Automatically finds and loads config.yaml
config = load_config()
```

### From Custom File
```python
config = load_config('my_config.yaml')
```

### With Defaults
```python
defaults = {'timeout': 30, 'debug': False}
config = load_config(defaults=defaults)
```

## Accessing Values

### Dot Notation (Safe)
```python
from src.config import get_config_value

lr = get_config_value(config, 'training.learning_rate', 0.001)
```

### Direct Dictionary (Fast)
```python
lr = config['training']['learning_rate']
```

### Convenience Functions
```python
from src.config import (
    get_learning_rate,
    get_batch_size,
    get_epochs,
    get_eeg_channels,
    get_n_classes
)

lr = get_learning_rate(config)
batch = get_batch_size(config)
epochs = get_epochs(config)
```

## Setting Values

### Nested Dictionary
```python
config['training']['learning_rate'] = 0.0005
```

### Dot Notation
```python
from src.config import set_config_value

set_config_value(config, 'training.learning_rate', 0.0005)
```

## Validation

```python
from src.config import validate_config

required_keys = {
    'training.epochs': int,
    'data.eeg_channels': int
}

is_valid, msg = validate_config(config, required_keys)
if not is_valid:
    print(f"Error: {msg}")
```

## Printing Configuration

```python
from src.config import print_config

print_config(config, title="My Configuration")
```

## Command-Line Usage

### Using Default Config
```bash
python train_eeg_model_production.py
```

### Using Custom Config
```bash
python train_eeg_model_production.py --config custom.yaml
```

### Overriding with CLI Arguments
```bash
python train_eeg_model_production.py --epochs 100 --batch-size 16
```

## Common Parameters

| Parameter | Path | Type | Default | Notes |
|-----------|------|------|---------|-------|
| Learning Rate | `training.learning_rate` | float | 0.001 | Typical: 0.0001-0.01 |
| Batch Size | `training.batch_size` | int | 32 | Powers of 2 typical |
| Epochs | `training.epochs` | int | 50 | Typical: 50-200 |
| N Classes | `data.n_classes` | int | 5 | Motor imagery classes |
| EEG Channels | `data.eeg_channels` | int | 8 | Electrodes count |
| Sampling Rate | `data.sampling_rate` | int | 250 | Hz |
| Buffer Size | `realtime.buffer_size` | int | 250 | Samples (1 sec @ 250Hz) |
| Confidence Threshold | `realtime.confidence_threshold` | float | 0.7 | 0-1 range |
| Debounce Count | `realtime.debounce_count` | int | 3 | Predictions before action |
| Move Distance | `realtime.mouse.move_distance` | int | 50 | Pixels |

## Example: Training with Custom Config

```python
from src.config import load_config
from src.train import ModelTrainer

# Load config
config = load_config('experiment_config.yaml')

# Extract parameters
lr = config['training']['learning_rate']
epochs = config['training']['epochs']
batch_size = config['training']['batch_size']

# Use in training
trainer = ModelTrainer(config)
history = trainer.train(model, x_train, y_train, ...)
```

## Example: Real-Time Inference with Config

```python
from src.config import load_config
from src.realtime_inference import RealtimeInferenceEngine

# Load config
config = load_config()

# Create engine with config
engine = RealtimeInferenceEngine(
    model_path='models/best_eeg_model.h5',
    config=config,
    move_distance=config['realtime']['mouse']['move_distance'],
    confidence_threshold=config['realtime']['confidence_threshold']
)

# Use engine
engine.start()
engine.add_sample(eeg_sample)
if engine.is_ready():
    action = engine.process_signal()
```

## Config File Structure

```
config.yaml
├─ paths                  # File locations
├─ model                  # Neural network architecture
├─ training               # Training hyperparameters
├─ data                   # EEG signal parameters
├─ realtime               # Real-time inference settings
├─ data_generation        # Synthetic data (testing)
├─ physionet              # PhysioNet dataset settings
├─ logging                # Logging configuration
├─ validation             # Validation settings
└─ output                 # Export options
```

## Debugging Config Issues

### Check Which Config Loaded
```python
from src.config import load_config

# This will log which config file was loaded
config = load_config()
```

### Print Current Values
```python
from src.config import print_config

print_config(config)
```

### Find Missing Keys
```python
from src.config import get_config_value

val = get_config_value(config, 'some.deep.key', default='NOT_FOUND')
if val == 'NOT_FOUND':
    print(f"Key not found!")
```

### Validate Before Use
```python
from src.config import validate_config

required = {
    'training.epochs': int,
    'training.batch_size': int,
    'data.eeg_channels': int,
}

is_valid, msg = validate_config(config, required)
assert is_valid, f"Config error: {msg}"
```
