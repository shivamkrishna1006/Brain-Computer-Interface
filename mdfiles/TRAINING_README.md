# CNN-LSTM Training Script

Complete production-ready training implementation for EEG-based brain-computer interface with CNN-LSTM architecture.

## Features

✅ **Early Stopping** - Monitors validation loss and stops training when plateau detected  
✅ **Learning Rate Reduction** - ReduceLROnPlateau reduces learning rate when performance plateaus  
✅ **Class Weight Computation** - Automatic balanced weights for imbalanced datasets  
✅ **Best Model Checkpointing** - Saves best model based on validation accuracy  
✅ **Training Progress Logging** - Custom callback with loss, accuracy, and ETA  
✅ **History Storage** - Complete training history exported to JSON  

## Quick Start

### Basic Usage

```python
from src.train import ModelTrainer
import numpy as np

# Prepare your data
X_train = np.random.randn(800, 320, 64)  # (n_samples, time_steps, channels)
y_train = np.random.randint(0, 5, 800)    # Class labels
X_val = np.random.randn(200, 320, 64)
y_val = np.random.randint(0, 5, 200)

# Configure training
config = {
    'model': {'input_shape': (320, 64)},
    'training': {
        'epochs': 50,
        'batch_size': 32,
        'early_stopping_patience': 15,
        'reduce_lr_patience': 5,
        'reduce_lr_factor': 0.5
    },
    'output': {'model_path': 'models/best_model.h5'}
}

# Train
trainer = ModelTrainer(config, n_classes=5)
results = trainer.train(X_train, y_train, X_val, y_val)

# Save history and get summary
trainer.save_history('outputs/history.json')
summary = trainer.training_summary()
```

### Running the Complete Example

```bash
python train_eeg_model.py
```

This generates synthetic EEG data, trains a model, and saves results.

## File Structure

```
├── src/
│   └── train.py                      # Core training implementation
├── train_eeg_model.py                # Complete working example
├── TRAINING_GUIDE.md                 # Comprehensive documentation
├── TRAINING_IMPLEMENTATION_SUMMARY.md # Technical overview
├── REQUIREMENTS_CHECKLIST.md         # Requirements verification
└── test_training_module.py           # Unit tests for verification
```

## Core Classes

### ModelTrainer

Main class for training CNN-LSTM models.

```python
trainer = ModelTrainer(config, n_classes=5)
```

**Methods:**
- `compute_class_weights(labels)` - Calculate balanced class weights
- `build_callbacks(model_save_path, **kwargs)` - Create training callbacks
- `train(X_train, y_train, X_val, y_val, **kwargs)` - Train the model
- `save_history(output_path)` - Export history to JSON
- `training_summary()` - Get training statistics

### TrainingProgressCallback

Custom callback for detailed progress logging.

Logs every N epochs with:
- Training loss and accuracy
- Validation loss and accuracy
- Current learning rate
- Time estimation

## Configuration

### Required Config Keys

```python
config = {
    'model': {
        'input_shape': (320, 64),      # EEG shape: (time_steps, channels)
        'conv1d_filters': [32, 64, 128],
        'lstm_units': [128, 64],
        'dropout_rate': 0.3,
        'l2_regularization': 0.001
    },
    'training': {
        'epochs': 50,
        'batch_size': 32,
        'learning_rate': 0.001,
        'early_stopping_patience': 15,    # Req 1
        'reduce_lr_patience': 5,          # Req 2
        'reduce_lr_factor': 0.5,          # Req 2
        'log_interval': 5
    },
    'output': {
        'model_path': 'models/best_model.h5',
        'log_dir': 'outputs/logs'
    }
}
```

## Training Output

### Console Output
```
[TRAINING PIPELINE STARTED]
[1/5] Validating inputs...
✓ Training data: (800, 320, 64) → (800,)
✓ Validation data: (200, 320, 64) → (200,)

[2/5] Building model...
✓ Model created for 5 classes

[3/5] Preparing training data...
Converting labels to categorical format...
Class weights computed:
  Class 0: 1.2000
  Class 1: 0.9000
  Class 2: 1.1000
  Class 3: 0.8000
  Class 4: 1.0000

[4/5] Setting up training parameters...
✓ Epochs: 50
✓ Batch size: 32

[5/5] Starting training...
[Epoch   1/50] Loss: 0.3456 | Val Loss: 0.4567 | Acc: 0.8234 | Val Acc: 0.8123 | LR: 0.001000 | ETA: 12:34
[Epoch   5/50] Loss: 0.2345 | Val Loss: 0.3456 | Acc: 0.8765 | Val Acc: 0.8654 | LR: 0.001000 | ETA: 11:23
...
[TRAINING METRICS]
Final Training - Loss: 0.1234, Acc: 0.9234
Final Validation - Loss: 0.2345, Acc: 0.9123
Test - Loss: 0.2456, Acc: 0.9089
```

### Saved History (JSON)
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

## Training Summary Output

```python
summary = trainer.training_summary()
# Returns:
{
    'best_epoch': 32,
    'best_val_accuracy': 0.8923,
    'best_val_loss': 0.3456,
    'final_metrics': {
        'loss': 0.234,
        'accuracy': 0.92,
        'val_loss': 0.456,
        'val_accuracy': 0.88
    },
    'n_epochs_trained': 45,
    'class_weights': {0: 1.2, 1: 0.9, ...},
    'n_classes': 5
}
```

## Testing

Run the verification test to confirm all features work:

```bash
python test_training_module.py
```

This validates:
- Module imports
- Class instantiation
- Class weight computation
- Callback creation
- History saving capability
- Summary reporting capability

## Documentation

- **TRAINING_GUIDE.md** - Comprehensive API reference with examples
- **TRAINING_IMPLEMENTATION_SUMMARY.md** - Technical implementation details
- **REQUIREMENTS_CHECKLIST.md** - Verification of all 6 requirements
- **train_eeg_model.py** - Complete working example

## Integration with BCI System

The training module integrates seamlessly with the existing BCI system:

```python
from src.model import create_model
from src.train import ModelTrainer
from src.data_preparation import prepare_eeg_data

# Load and prepare data
X, y = load_eeg_data()
(X_train, y_train), (X_test, y_test), _ = prepare_eeg_data(X, y, n_channels=64, time_steps=320)

# Create and train model
config = load_config('configs/config.yaml')
trainer = ModelTrainer(config, n_classes=5)
results = trainer.train(X_train, y_train, X_test, y_test)

# Evaluate
summary = trainer.training_summary()
print(f"Validation accuracy: {summary['best_val_accuracy']:.4f}")
```

## Troubleshooting

### Issue: Model not training
- Check data shapes match (n_samples, 320, 64)
- Verify labels are integers 0-4 (or configure different n_classes)
- Check learning rate is appropriate

### Issue: Training stops too early
- Increase `early_stopping_patience` (default: 15)
- Reduce `reduce_lr_patience` (default: 5)

### Issue: Memory errors
- Reduce `batch_size` (default: 32)
- Reduce number of training samples
- Use data generators for large datasets

## Requirements

- TensorFlow >= 2.10
- NumPy
- scikit-learn
- Python 3.8+

## Version

- Training Script: 2.0
- Status: Production-Ready
- All 6 requirements implemented and tested
