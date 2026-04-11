# CNN-LSTM Training Guide

Production-ready training infrastructure for EEG classification with advanced callbacks, class weight handling, and comprehensive monitoring.

**Status**: Complete and Production-Ready  
**Version**: 2.0  
**Last Updated**: 2024

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Core Components](#core-components)
5. [Usage Patterns](#usage-patterns)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Performance Tips](#performance-tips)

---

## Overview

### Key Features

The training module (`src/train.py`) provides a complete production-ready training pipeline with:

| Feature | Description |
|---------|-------------|
| **Early Stopping** | Monitor validation loss and stop when plateau detected |
| **Learning Rate Reduction** | Dynamically reduce LR when performance plateaus |
| **Class Weight Computation** | Automatic balanced weights for imbalanced datasets |
| **Model Checkpointing** | Save best model based on validation accuracy |
| **Progress Tracking** | Custom callback with ETA and epoch-wise logging |
| **History Storage** | JSON export of complete training history with metadata |
| **Multi-class Support** | Built for 5-class motor imagery (Left, Right, Hands, Feet, Click) |
| **Comprehensive Logging** | Detailed logging at every training stage |

### Architecture

```
ModelTrainer (Main class)
├── __init__() - Initialize with config
├── compute_class_weights() - Balance imbalanced data
├── build_callbacks() - Create 5 callback types
├── train() - Main training pipeline (5 stages)
├── save_history() - Export history to JSON
└── training_summary() - Generate statistics report

TrainingProgressCallback (Custom callback)
├── on_train_begin() - Log start time
├── on_epoch_end() - Log metrics every N epochs with ETA
└── on_train_end() - Log total duration
```

---

## Quick Start

### Minimal Example

```python
from src.train import ModelTrainer
from src.model import create_model
import numpy as np

# Configure
config = {
    'model': {'input_shape': (320, 64), 'conv1d_filters': [32, 64, 128]},
    'training': {'epochs': 50, 'batch_size': 32},
    'output': {'model_path': 'models/best_model.h5'}
}

# Create data (shape: samples, time_steps, channels)
X_train = np.random.randn(800, 320, 64)
y_train = np.random.randint(0, 5, 800)
X_val = np.random.randn(200, 320, 64)
y_val = np.random.randint(0, 5, 200)

# Train
trainer = ModelTrainer(config, n_classes=5)
results = trainer.train(X_train, y_train, X_val, y_val)

# Summary
summary = trainer.training_summary()
print(f"Best validation accuracy: {summary['best_val_accuracy']:.4f}")
```

### Complete Pipeline Example

See [train_eeg_model.py](train_eeg_model.py) for:
- Data generation and splitting
- Model creation
- Full training with evaluation
- Results saving
- Summary reporting

Run with:
```bash
python train_eeg_model.py
```

---

## Configuration

### Config Dictionary Structure

```python
config = {
    # Model architecture
    'model': {
        'input_shape': (320, 64),  # (time_steps, channels)
        'conv1d_filters': [32, 64, 128],  # Conv filter progression
        'lstm_units': [128, 64],  # BiLSTM layer units
        'dropout_rate': 0.3,  # Dropout after conv/dense
        'l2_regularization': 0.001  # L2 kernel regularizer
    },
    
    # Training parameters
    'training': {
        'epochs': 50,  # Total training epochs
        'batch_size': 32,  # Batch size
        'learning_rate': 0.001,  # Initial learning rate
        'early_stopping_patience': 15,  # Epochs to wait for improvement
        'reduce_lr_patience': 5,  # Epochs before reducing LR
        'reduce_lr_factor': 0.5,  # Multiply LR by this factor
        'log_interval': 5  # Log metrics every N epochs
    },
    
    # Output configuration
    'output': {
        'model_path': 'models/best_model.h5',  # Where to save model
        'log_dir': 'outputs/logs'  # TensorBoard log directory
    }
}
```

### Configuration Parameters Explained

| Parameter | Default | Description |
|-----------|---------|-------------|
| `epochs` | 50 | Total training epochs |
| `batch_size` | 32 | Samples per batch |
| `early_stopping_patience` | 15 | Epochs to wait before stopping |
| `reduce_lr_patience` | 5 | Epochs to wait before reducing LR |
| `reduce_lr_factor` | 0.5 | LR *= this value on plateau |
| `log_interval` | 5 | Update log every N epochs |

---

## Core Components

### 1. ModelTrainer Class

#### Initialization

```python
trainer = ModelTrainer(config, n_classes=5)
```

**Parameters**:
- `config` (Dict): Configuration dictionary with model, training, output keys
- `n_classes` (int): Number of classification classes (default: 5)

**Attributes**:
- `model`: Keras model instance
- `training_history`: Dict of epoch-wise metrics
- `class_weights`: Dict mapping class index to weight
- `timestamp`: Training session timestamp

#### compute_class_weights(labels)

Automatically compute balanced class weights for imbalanced data.

```python
class_weights = trainer.compute_class_weights(y_train)
# Output: {0: 1.2, 1: 0.9, 2: 1.1, 3: 0.8, 4: 1.0}
```

**How it works**:
- Uses sklearn's balanced strategy
- Higher weights for minority classes
- Automatically applied in `train()` method

**Example use case**: If training data is imbalanced (900 "Left", 100 "Click"):
```
Original distribution: {0: 900, 1: 100}
Computed weights: {0: 0.53, 1: 4.5}
Result: "Click" samples weighted 4.5x more
```

#### build_callbacks(model_save_path, **kwargs)

Create comprehensive training callbacks.

```python
callbacks = trainer.build_callbacks(
    model_save_path='models/best_model.h5',
    early_stopping_patience=15,
    reduce_lr_patience=5,
    reduce_lr_factor=0.5,
    log_interval=5
)
```

**Callbacks created**:

1. **EarlyStopping**
   - Monitors: `val_loss`
   - Patience: 15 epochs
   - Restores best weights: Yes

2. **ReduceLROnPlateau**
   - Monitors: `val_loss`
   - Factor: 0.5 (reduces LR by half)
   - Patience: 5 epochs
   - Min LR: 1e-7
   - Cooldown: 2 epochs

3. **ModelCheckpoint**
   - Monitors: `val_accuracy`
   - Saves: Best model only
   - Format: HDF5 (.h5)

4. **TensorBoard**
   - Logs: All metrics
   - Histograms: Enabled
   - Update frequency: Every epoch
   - Graph visualization: Enabled

5. **TrainingProgressCallback**
   - Custom callback
   - Logs: Loss, accuracy, LR, ETA
   - Interval: Every N epochs

#### train(X_train, y_train, X_val, y_val, **kwargs)

Main training function with comprehensive pipeline.

```python
results = trainer.train(
    X_train, y_train,          # Training data and labels
    X_val, y_val,              # Validation data and labels
    X_test=X_test,             # Optional test data
    y_test=y_test,             # Optional test labels
    epochs=50,                 # Override config epochs
    batch_size=32,             # Override config batch size
    verbose=1                  # 0=silent, 1=progress bar, 2=one line per epoch
)
```

**Parameters**:
- Input data must be NumPy arrays
- Labels can be 1D (class indices) or 2D (one-hot encoded)
- Automatically converts 1D labels to categorical

**Returns**:
```python
{
    'history': history_object,           # TensorFlow history
    'metrics': {
        'final_loss': 0.234,
        'final_val_loss': 0.456,
        'final_accuracy': 0.92,
        'final_val_accuracy': 0.88,
        'epochs_trained': 45
    },
    'class_weights': {0: 1.2, 1: 0.9, ...},
    'model_path': 'models/best_model.h5',
    'training_time': 1234.5  # seconds
}
```

**5-Stage Training Pipeline**:

1. **Input Validation** - Check shape compatibility
2. **Model Building** - Create/verify model
3. **Data Preparation** - Convert labels to categorical
4. **Parameter Setup** - Load/override config
5. **Training** - Run model.fit() with callbacks

#### save_history(output_path)

Export training history to JSON with metadata.

```python
path = trainer.save_history('outputs/training_history.json')
```

**JSON Structure**:
```json
{
  "loss": [0.5, 0.4, 0.3, ...],
  "accuracy": [0.7, 0.8, 0.85, ...],
  "val_loss": [0.6, 0.5, 0.4, ...],
  "val_accuracy": [0.68, 0.78, 0.83, ...],
  "metadata": {
    "timestamp": "20240115_143022",
    "n_classes": 5,
    "n_epochs": 45,
    "class_weights": {"0": 1.2, "1": 0.9, ...}
  }
}
```

#### training_summary()

Generate comprehensive statistics report.

```python
summary = trainer.training_summary()
```

**Returns**:
```python
{
    'best_epoch': 32,                          # Best epoch number (1-indexed)
    'best_val_accuracy': 0.8923,               # Best validation accuracy
    'best_val_loss': 0.3456,                   # Lowest validation loss
    'final_metrics': {
        'loss': 0.234,                         # Final training loss
        'accuracy': 0.92,                      # Final training accuracy
        'val_loss': 0.456,                     # Final validation loss
        'val_accuracy': 0.88                   # Final validation accuracy
    },
    'n_epochs_trained': 45,                    # Total epochs completed
    'class_weights': {0: 1.2, 1: 0.9, ...},    # Class weights used
    'n_classes': 5                             # Number of classes
}
```

### 2. TrainingProgressCallback Class

Custom callback for detailed epoch-wise logging with ETA calculation.

**Features**:
- Logs every N epochs (configurable)
- Shows loss, accuracy, validation metrics
- Estimates time to completion
- Shows learning rate changes
- Formatted ASCII output

**Log Output Example**:
```
Epoch 5/50 (10%) - Loss: 0.3456 - Acc: 0.8234 - Val Loss: 0.4567 - Val Acc: 0.8123 - LR: 0.001 - ETA: 12m 34s
Epoch 10/50 (20%) - Loss: 0.2345 - Acc: 0.8765 - Val Loss: 0.3456 - Val Acc: 0.8654 - LR: 0.001 - ETA: 11m 23s
```

---

## Usage Patterns

### Pattern 1: Basic Training with Defaults

```python
from src.train import ModelTrainer
from src.model import create_model

config = {
    'model': {'input_shape': (320, 64)},
    'training': {'epochs': 50},
    'output': {'model_path': 'models/model.h5'}
}

trainer = ModelTrainer(config, n_classes=5)
results = trainer.train(X_train, y_train, X_val, y_val)
```

### Pattern 2: Custom Callbacks Configuration

```python
trainer = ModelTrainer(config, n_classes=5)

callbacks = trainer.build_callbacks(
    model_save_path='models/custom_model.h5',
    early_stopping_patience=20,    # More patient
    reduce_lr_patience=10,          # More patient
    reduce_lr_factor=0.8,           # Smaller reduction
    log_interval=1                  # Log every epoch
)

results = trainer.train(
    X_train, y_train, X_val, y_val,
    epochs=100,
    verbose=2
)
```

### Pattern 3: Training with Test Set Evaluation

```python
results = trainer.train(
    X_train, y_train,
    X_val, y_val,
    X_test=X_test,
    y_test=y_test
)

# Get both validation and test metrics
summary = trainer.training_summary()
print(f"Val Acc: {summary['final_metrics']['val_accuracy']:.4f}")
```

### Pattern 4: Complete Pipeline with History Export

```python
# Train
results = trainer.train(X_train, y_train, X_val, y_val)

# Save history
trainer.save_history('outputs/history.json')

# Generate report
summary = trainer.training_summary()

# Access best model
print(f"Best model at epoch {summary['best_epoch']}")
print(f"Val accuracy: {summary['best_val_accuracy']:.4f}")
```

### Pattern 5: Hyperparameter Tuning

```python
best_score = 0
best_config = None

for batch_size in [16, 32, 64]:
    for lr_patience in [3, 5, 10]:
        config['training']['batch_size'] = batch_size
        config['training']['reduce_lr_patience'] = lr_patience
        
        trainer = ModelTrainer(config)
        results = trainer.train(X_train, y_train, X_val, y_val)
        
        summary = trainer.training_summary()
        if summary['best_val_accuracy'] > best_score:
            best_score = summary['best_val_accuracy']
            best_config = {
                'batch_size': batch_size,
                'lr_patience': lr_patience,
                'score': best_score
            }

print(f"Best config: {best_config}")
```

---

## Advanced Features

### 1. Class Weight Computation

Handles imbalanced classification automatically:

```python
# Automatic computation in train()
trainer = ModelTrainer(config)
results = trainer.train(X_train, y_train, X_val, y_val)
# Class weights applied automatically

# Or manual computation and inspection
weights = trainer.compute_class_weights(y_train)
print(f"Class weights: {weights}")
# {0: 1.2, 1: 0.9, 2: 1.1, 3: 0.8, 4: 1.0}
```

**Algorithm**: sklearn's balanced strategy
- Weight = (n_samples / (n_classes * n_samples_per_class))
- Minority classes get higher weights
- Perfect for imbalanced EEG datasets

### 2. Learning Rate Scheduling

Two mechanisms:

**a) Early Stopping on Validation Loss**:
```python
# If val_loss doesn't improve for 15 epochs → stop
early_stopping_patience = 15
```

**b) Reduce LR on Plateau**:
```python
# If val_loss plateaus for 5 epochs → reduce LR by factor of 0.5
reduce_lr_patience = 5
reduce_lr_factor = 0.5
# Min LR: 1e-7 (won't go below)
# Cooldown: 2 epochs before next reduction
```

### 3. Multi-class Support

Built for 5-class motor imagery by default:

```python
# Classes: 0=Left, 1=Right, 2=Hands, 3=Feet, 4=Click

y = np.array([0, 1, 2, 3, 4, 0, 1, ...])  # Shape: (n_samples,)
# Automatically converted to one-hot in train()

# y one-hot: [[1,0,0,0,0], [0,1,0,0,0], ...]
```

Extend to N classes:
```python
trainer = ModelTrainer(config, n_classes=10)  # 10-class problem
results = trainer.train(X_train, y_train, X_val, y_val)
```

### 4. Label Format Flexibility

Supports both formats:

```python
# 1D labels (class indices)
y_train = np.array([0, 1, 2, 3, 4, 0, 1, ...])
results = trainer.train(X_train, y_train, X_val, y_val)
# Auto-converted to categorical

# 2D labels (one-hot encoded)
y_train = np.array([[1,0,0,0,0], [0,1,0,0,0], ...])
results = trainer.train(X_train, y_train, X_val, y_val)
# Used directly
```

### 5. Validation Data Flexibility

```python
# Standard approach
trainer.train(X_train, y_train, X_val, y_val)

# Custom validation tuple
trainer.train(
    X_train, y_train,
    X_val, y_val,
    validation_data=(custom_X, custom_y)
)
```

---

## Troubleshooting

### Issue 1: Training Loss Not Decreasing

**Symptoms**: Loss stays high or increases throughout training

**Solutions**:
1. **Reduce learning rate**:
   ```python
   config['training']['learning_rate'] = 0.0001
   ```

2. **Increase batch size**:
   ```python
   config['training']['batch_size'] = 64
   ```

3. **Check data normalization**:
   ```python
   print(f"X_train mean: {X_train.mean():.4f}, std: {X_train.std():.4f}")
   # Should be close to 0 and 1
   ```

### Issue 2: Validation Accuracy Lower Than Training

**Symptoms**: Val_acc significantly lower than train_acc (overfitting)

**Solutions**:
1. **Increase dropout**:
   ```python
   config['model']['dropout_rate'] = 0.5
   ```

2. **Increase L2 regularization**:
   ```python
   config['model']['l2_regularization'] = 0.01
   ```

3. **More training data** needed

4. **Early stopping triggered**:
   - Reduce early_stopping_patience
   - Check if model is actually overfitting

### Issue 3: Early Stopping Stopping Too Early

**Symptoms**: Training stops before convergence

**Solutions**:
1. **Increase patience**:
   ```python
   config['training']['early_stopping_patience'] = 30
   ```

2. **Check for learning rate reduction**:
   - ReduceLROnPlateau might be reducing LR too aggressively
   - Increase `reduce_lr_patience`

### Issue 4: Learning Rate Not Reducing

**Symptoms**: LR stays constant, ReduceLROnPlateau not triggering

**Solutions**:
1. **Check validation loss**:
   - Reduce LR only if val_loss plateaus
   - May need more patience

2. **Enable debug logging**:
   ```python
   logger.setLevel(logging.DEBUG)  # More detailed logs
   ```

### Issue 5: Memory Error During Training

**Symptoms**: Out of memory error

**Solutions**:
1. **Reduce batch size**:
   ```python
   config['training']['batch_size'] = 16
   ```

2. **Reduce data size**:
   ```python
   X_train = X_train[:1000]
   y_train = y_train[:1000]
   ```

3. **Use data generator** for very large datasets

---

## Performance Tips

### 1. Data Preprocessing

```python
# Normalize data
X = (X - X.mean(axis=(0,1))) / X.std(axis=(0,1))

# Remove artifacts (if applicable)
# Filter to frequency bands of interest
# Resample if needed
```

### 2. Early Hyperparameter Tuning

```python
# Start with 1/10 of data for quick testing
results = trainer.train(
    X_train[:100], y_train[:100],
    X_val[:50], y_val[:50],
    epochs=5
)
```

### 3. Monitor via TensorBoard

```python
# During training
tensorboard --logdir=outputs/logs

# View in browser at http://localhost:6006
# Check: loss curves, learning rate changes, histogram of weights
```

### 4. Batch Size Selection

| Batch Size | Pros | Cons |
|-----------|------|------|
| 16 | More gradient updates | Noisier training |
| 32 | Balanced | Default |
| 64 | Faster training | Less frequent updates |
| 128+ | Very fast | May converge to poor minima |

### 5. Optimal Configuration for EEG

```python
{
    'training': {
        'epochs': 50-100,            # Depends on data size
        'batch_size': 32,            # Good balance
        'learning_rate': 0.001,      # Standard for Adam
        'early_stopping_patience': 15,
        'reduce_lr_patience': 5,
        'reduce_lr_factor': 0.5
    }
}
```

### 6. Monitoring Metrics

Focus on:
1. **Initial epochs (1-10)**: Should see steady loss decrease
2. **Middle epochs (20-40)**: Watch for learning rate reductions
3. **Late epochs (40+)**: Check if early stopping triggers appropriately

**Good signs**:
- Train loss: ↓ gradually
- Val loss: ↓ initially, then plateau
- Val accuracy: ↑ initially, then plateau
- LR: Reduces 1-2 times during training

---

## Examples

### Complete Example: PhysioNet EEG Training

```python
from src.train import ModelTrainer
from src.physionet_loader import PhysioNetEEGLoader

# Load PhysioNet data
loader = PhysioNetEEGLoader(config)
data, labels = loader.load_data(subject_ids=[1, 2, 3])

# Split
from sklearn.model_selection import train_test_split
X_train, X_temp, y_train, y_temp = train_test_split(data, labels, test_size=0.4)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5)

# Train
config = {...}
trainer = ModelTrainer(config, n_classes=5)
results = trainer.train(X_train, y_train, X_val, y_val, X_test=X_test, y_test=y_test)

# Results
summary = trainer.training_summary()
trainer.save_history('outputs/physionet_history.json')
```

---

## API Reference

### ModelTrainer

```python
class ModelTrainer:
    def __init__(config: Dict, n_classes: int = 5)
    def compute_class_weights(labels: np.ndarray) -> Dict
    def build_callbacks(model_save_path: str, **kwargs) -> list
    def train(X_train, y_train, X_val, y_val, **kwargs) -> Dict
    def save_history(output_path: str) -> str
    def training_summary() -> Dict
```

### Configuration Keys

```
model.input_shape = (time_steps, channels)
model.conv1d_filters = [int, int, int]
model.lstm_units = [int, int]
model.dropout_rate = float (0-1)
model.l2_regularization = float

training.epochs = int
training.batch_size = int
training.learning_rate = float
training.early_stopping_patience = int
training.reduce_lr_patience = int
training.reduce_lr_factor = float
training.log_interval = int

output.model_path = str
output.log_dir = str
```

---

## Summary

The `ModelTrainer` class provides a complete, production-ready training pipeline for EEG classification with:

✅ Early stopping on validation loss  
✅ Learning rate reduction on plateau  
✅ Automatic class weight computation  
✅ Best model checkpointing  
✅ Comprehensive progress tracking  
✅ History storage and statistics  
✅ Multi-class support (5+ classes)  
✅ Flexible label formats  
✅ TensorBoard integration  
✅ Comprehensive logging  

Use `train_eeg_model.py` as a starting point for your own models!
