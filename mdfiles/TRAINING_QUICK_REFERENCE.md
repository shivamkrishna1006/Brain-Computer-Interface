# Training Script Quick Reference

## 🚀 Quick Start (30 seconds)

```bash
# Navigate to project directory
cd e:\BCI_INTERFACE

# Run training with defaults
python train_eeg_model_production.py

# Done! Model saved to: models/best_eeg_model_*.h5
```

## 📋 Common Commands

```bash
# Basic training
python train_eeg_model_production.py

# Custom epochs and batch size
python train_eeg_model_production.py --epochs 150 --batch-size 16

# More training samples
python train_eeg_model_production.py --n-samples 5000

# Custom number of classes
python train_eeg_model_production.py --n-classes 3

# Load custom config
python train_eeg_model_production.py --config custom_config.yaml

# Verbose output
python train_eeg_model_production.py --verbose

# Combine multiple options
python train_eeg_model_production.py \
  --epochs 200 \
  --batch-size 32 \
  --n-samples 10000 \
  --config my_config.yaml
```

## 📊 Monitor Training

```bash
# Real-time visualization with TensorBoard
tensorboard --logdir outputs/logs

# Then open browser: http://localhost:6006
```

## 📁 Output Files

After training, you'll find:
```
outputs/
├── training_history_TIMESTAMP.json    # Metrics per epoch
├── training_config_TIMESTAMP.json     # Configuration used
└── logs/TIMESTAMP/                    # TensorBoard logs

models/
└── best_eeg_model_TIMESTAMP.h5       # Trained model
```

## ⚙️ Key Features (All Built-In)

| Feature | Details |
|---------|---------|
| **Early Stopping** | Stops when validation loss plateaus (15 epochs patience) |
| **Learning Rate Scheduling** | Reduces LR when plateau detected (factor: 0.5) |
| **Class Weights** | Automatically handles imbalanced data |
| **Model Saving** | Saves best model automatically |
| **Progress Logging** | Shows loss, accuracy, ETA per epoch |
| **History Storage** | Complete metrics saved as JSON |
| **Configuration** | YAML-based, fully customizable |
| **TensorBoard** | Real-time monitoring & visualization |

## 🔧 Minimal YAML Config

Create `custom_config.yaml`:
```yaml
model:
  input_shape: [250, 8]
  cnn_filters: [32, 64, 128]
  lstm_units: [128, 64]

training:
  epochs: 100
  batch_size: 32
  learning_rate: 0.001
  early_stopping_patience: 15
  reduce_lr_patience: 5
  reduce_lr_factor: 0.5
```

Then use it:
```bash
python train_eeg_model_production.py --config custom_config.yaml
```

## 📈 Interpreting Output

### Training Log Example
```
Epoch [  1/100] | Loss: 1.2345 | Val Loss: 1.1234 | 
Acc: 0.6543 | Val Acc: 0.7123 | LR: 1.00e-03 | ETA: 45m 32s
```

- **Loss**: Training loss (should decrease)
- **Val Loss**: Validation loss (monitored for early stopping)
- **Acc**: Training accuracy
- **Val Acc**: Validation accuracy (monitored for checkpointing)
- **LR**: Current learning rate
- **ETA**: Estimated time to completion

### Final Metrics
```
Best Epoch: 45
Best Validation Accuracy: 0.9234
Best Validation Loss: 0.2345
Final Validation Accuracy: 0.9123
Total Epochs Trained: 60
```

- **Best Epoch**: Epoch with highest validation accuracy
- **Best Validation Accuracy**: Maximum accuracy achieved
- **Final Validation Accuracy**: Accuracy at end of training
- **Total Epochs Trained**: May be less than requested due to early stopping

## 💡 Tips & Tricks

### Memory Issues?
```bash
# Reduce batch size
python train_eeg_model_production.py --batch-size 8
```

### Training Too Slow?
```bash
# Increase batch size (if memory allows)
python train_eeg_model_production.py --batch-size 128

# Reduce number of samples
python train_eeg_model_production.py --n-samples 500
```

### Want Longer Training?
```bash
# Increase early stopping patience in config
# Or simply use more epochs
python train_eeg_model_production.py --epochs 500
```

### Class Imbalance Issues?
✓ Already handled automatically!
Class weights are computed and applied during training.

## 🔍 Using Trained Model

```python
from tensorflow.keras.models import load_model
import numpy as np

# Load model
model = load_model('models/best_eeg_model_TIMESTAMP.h5')

# Make predictions
predictions = model.predict(X_new_data)

# Get class predictions
predicted_classes = np.argmax(predictions, axis=1)
```

## 📊 Analyzing Results

```python
import json
import matplotlib.pyplot as plt

# Load history
with open('outputs/training_history_TIMESTAMP.json') as f:
    history = json.load(f)

# Plot training history
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history['loss'], label='Train Loss')
plt.plot(history['val_loss'], label='Val Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history['accuracy'], label='Train Acc')
plt.plot(history['val_accuracy'], label='Val Acc')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.tight_layout()
plt.savefig('training_history.png')
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Out of memory | Reduce `--batch-size` |
| Training too slow | Increase `--batch-size` or reduce `--n-samples` |
| Not improving | Reduce learning rate in config or check data |
| High overfitting | Increase L2 regularization in config |
| Early stopping too aggressive | Increase `early_stopping_patience` in config |

## 📚 Configuration Parameters

### Model Parameters
- `input_shape`: (time_steps, channels) - EEG data shape
- `cnn_filters`: List of filter counts for CNN layers
- `lstm_units`: LSTM layer units
- `dense_units`: Dense layer units
- `l2_regularization`: L2 penalty strength

### Training Parameters
- `epochs`: Number of training epochs
- `batch_size`: Samples per batch
- `learning_rate`: Optimizer learning rate
- `early_stopping_patience`: Epochs before stopping
- `reduce_lr_patience`: Epochs before reducing LR
- `reduce_lr_factor`: LR multiplication factor (e.g., 0.5 = halve LR)

### Data Parameters
- `train_split`: Proportion for training (default: 0.6)
- `val_split`: Proportion for validation (default: 0.2)
- `test_split`: Proportion for testing (default: 0.2)

## 🎯 Default Settings

```
Input Shape:       250 samples × 8 channels
Epochs:            100
Batch Size:        32
Learning Rate:     0.001
Early Stop Wait:   15 epochs
LR Reduction Wait: 5 epochs
Classes:           5 (motor imagery: Left, Right, Hands, Feet, Click)
Training Samples:  1000 (synthetic)
```

## ✨ Key Features

✅ **Early Stopping** - Prevents overfitting
✅ **Learning Rate Scheduling** - Adapts learning dynamically
✅ **Class Weights** - Handles imbalanced data
✅ **Model Checkpointing** - Saves best model
✅ **Progress Logging** - Live training updates
✅ **History Export** - JSON metrics for analysis
✅ **TensorBoard** - Visual monitoring
✅ **Configuration** - Fully customizable YAML

## 📖 Documentation Files

- `TRAINING_IMPLEMENTATION_GUIDE.md` - Complete reference
- `TRAINING_IMPLEMENTATION_COMPLETE.md` - Implementation details
- `TRAINING_GUIDE.md` - Detailed training guide
- `MODEL_GUIDE.md` - Model architecture guide

## 🆘 Need Help?

1. Check output during training for error messages
2. Review `TRAINING_IMPLEMENTATION_GUIDE.md` for detailed docs
3. Check TensorBoard for visual debugging
4. Verify configuration file syntax with YAML validator
5. Ensure data shapes match input_shape in config

---

**Version:** 2.0 | **Status:** Production-Ready | **Date:** 2024
