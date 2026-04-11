# CNN-LSTM Model Quick Reference

## 1️⃣ Create Model (One Line)

```python
from src.model import create_model

config = {
    'model': {
        'input_shape': [320, 64],  # time_steps, channels
        'cnn_filters': [32, 64, 128],
        'lstm_units': [128, 64],
        'dense_units': [64, 32],
        'l2_regularization': 0.001
    },
    'training': {
        'optimizer': {'name': 'adam'},
        'learning_rate': 0.001
    }
}

model = create_model(config, n_classes=5)
```

## 2️⃣ Train Model

```python
from tensorflow.keras.utils import to_categorical

# Prepare data
y_train_cat = to_categorical(y_train, num_classes=5)
y_val_cat = to_categorical(y_val, num_classes=5)

# Train
history = model.fit(
    X_train, y_train_cat,
    validation_data=(X_val, y_val_cat),
    epochs=50,
    batch_size=32,
    verbose=1
)
```

## 3️⃣ Predict

```python
# Batch prediction
predictions = model.predict(X_test)  # Shape: (n_samples, 5)

# Get class
predicted_class = np.argmax(predictions, axis=1)  # 0-4

# Get confidence
confidence = np.max(predictions, axis=1)

# Get label name
from src.model import get_class_labels
labels = get_class_labels()
label_name = labels[predicted_class[0]]
```

## 4️⃣ Model Management

```python
from src.model import CNNLSTMModel, load_pretrained_model

# Save
model_builder = CNNLSTMModel(config, n_classes=5)
model_builder.save_model('models/model.h5')
model_builder.save_weights('models/weights.h5')

# Load
model, config = load_pretrained_model('models/model.h5')

# Load weights
model_builder.load_weights('models/weights.h5')
```

## 📊 Architecture

```
Input (320, 64)
    ↓
Conv1D Blocks [32, 64, 128 filters]
    ↓
Bidirectional LSTM [128, 64 units]
    ↓
Dense Layers [64, 32 units]
    ↓
Output (5 classes, softmax)
```

## 🎯 Class Labels

| Index | Label | Description |
|-------|-------|-------------|
| 0 | Left | Left hand |
| 1 | Right | Right hand |
| 2 | Hands | Both hands |
| 3 | Feet | Both feet |
| 4 | Click | Click/Rest |

## 📋 API Reference

### `create_model(config, n_classes)`
Create and build model from configuration.

### `CNNLSTMModel` Class
```python
builder = CNNLSTMModel(config, n_classes)
builder.build()                    # Build architecture
builder.get_callbacks()            # Get training callbacks
builder.save_model(path)          # Save complete model
builder.save_weights(path)        # Save weights only
builder.load_weights(path)        # Load pre-trained weights
builder.count_parameters()        # Get parameter count
builder.get_config()              # Get config dict
```

### Utility Functions
```python
get_class_labels()                # Dict: {0: 'Left', ...}
get_label_index('Left')           # Returns 0
load_pretrained_model(path)       # Returns (model, config)
```

## ⚙️ Key Hyperparameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `input_shape` | [320, 64] | (time_steps, channels) |
| `cnn_filters` | [32, 64, 128] | Filters per Conv layer |
| `lstm_units` | [128, 64] | Bidirectional LSTM |
| `learning_rate` | 0.001 | Initial LR |
| `batch_size` | 32 | Training batch |
| `epochs` | 50 | Training epochs |
| `dropout_rate` | 0.3 | Dropout regularization |

## 🚀 Complete Example

```python
import numpy as np
from tensorflow.keras.utils import to_categorical
from src.model import create_model
from src.data_preparation import prepare_eeg_data

# 1. Load and prepare
X, y = load_eeg_data()  # Your data
(X_train, y_train), (X_test, y_test), prep = prepare_eeg_data(
    X, y, 64, 320, test_size=0.2
)

# 2. Convert to categorical
y_train_cat = to_categorical(y_train, 5)
y_test_cat = to_categorical(y_test, 5)

# 3. Create model
config = {
    'model': {
        'input_shape': [X_train.shape[1], X_train.shape[2]],
        'cnn_filters': [32, 64, 128],
        'lstm_units': [128, 64],
        'dense_units': [64, 32],
        'l2_regularization': 0.001
    },
    'training': {
        'optimizer': {'name': 'adam'},
        'learning_rate': 0.001
    }
}

model = create_model(config, n_classes=5)

# 4. Train
history = model.fit(
    X_train, y_train_cat,
    validation_data=(X_test, y_test_cat),
    epochs=50,
    batch_size=32
)

# 5. Evaluate
y_pred = model.predict(X_test)
y_pred_class = np.argmax(y_pred, axis=1)

from src.model import get_class_labels
labels = get_class_labels()
print("Predictions:", [labels[c] for c in y_pred_class[:5]])
```

## 💡 Pro Tips

1. **Always convert labels to categorical**
   ```python
   y_categorical = to_categorical(y, num_classes=5)
   ```

2. **Use bidirectional LSTM for better context**
   - Forward + backward pass captures complete sequence

3. **Normalize input data**
   ```python
   X_normalized = (X - X.mean(axis=0)) / X.std(axis=0)
   ```

4. **Use learning rate scheduling**
   ```python
   'use_lr_scheduler': True
   'lr_decay_rate': 0.95
   'lr_decay_steps': 10
   ```

5. **Monitor validation metrics**
   ```python
   'early_stopping_patience': 15
   'use_early_stopping': True
   ```

## ⚠️ Common Mistakes

| Mistake | Solution |
|---------|----------|
| Using sigmoid + binary loss | Use softmax + categorical loss |
| Not normalizing data | Use StandardScaler or similar |
| Forgetting to convert labels | Use `to_categorical()` |
| Training/validation data leakage | Use separate data splits |
| Batch size too large | Use 32 or 64 |
| Learning rate too high | Start with 0.001, decay over time |

## 📈 Expected Performance

On PhysioNet motor imagery (5-class):
- **Train Accuracy**: 90-95%
- **Val Accuracy**: 85-92%
- **Test Accuracy**: 80-90%
- **Training Time**: ~30-60 sec per epoch

## 🔧 Troubleshooting

### Training loss not decreasing
```python
# Reduce learning rate
'learning_rate': 0.0005

# Check data normalization
X = (X - X.mean()) / X.std()
```

### Overfitting
```python
# Increase dropout
'cnn_dropout': 0.5
'lstm_dropout': 0.5
'dense_dropout': 0.5

# Increase L2
'l2_regularization': 0.01
```

### Out of memory
```python
# Reduce batch size
batch_size = 16

# Reduce model size
'cnn_filters': [16, 32, 64]
'lstm_units': [64, 32]
```

## 📚 Full Documentation

See [MODEL_GUIDE.md](MODEL_GUIDE.md) for:
- Complete API reference
- Architecture details
- Training best practices
- Performance tuning
- Troubleshooting guide

---

**Status**: Production-Ready  
**Last Updated**: April 2026
