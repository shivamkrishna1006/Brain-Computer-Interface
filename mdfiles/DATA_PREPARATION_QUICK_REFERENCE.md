# Data Preparation Quick Reference

## 1️⃣ One-Line Preparation

```python
from src.data_preparation import prepare_eeg_data

(X_train, y_train), (X_test, y_test), prep = prepare_eeg_data(X, y, 64, 250)
```

## 2️⃣ Class Usage

```python
from src.data_preparation import EEGDataPreparation

prep = EEGDataPreparation(n_channels=64, time_steps=250)

# Reshape
X = prep.reshape_for_model(X)  # → (samples, 250, 64)

# Normalize
X_norm = prep.normalize(X, fit=True)  # Fit on training data

# Split
(X_train, y_train), (X_test, y_test) = prep.split_data(X_norm, y)
```

## 3️⃣ With PhysioNet Data

```python
from src.physionet_loader import load_physionet_data
from src.data_preparation import prepare_eeg_data

# Load
X, y = load_physionet_data([1,2,3,4,5])  # 64 channels, 160 Hz

# Prepare
(X_train, y_train), (X_test, y_test), prep = prepare_eeg_data(
    X, y, X.shape[1], X.shape[2]
)

# Train
model.fit(X_train, y_train, validation_data=(X_test, y_test))
```

## 📊 API Reference

### `prepare_eeg_data()`
```python
prepare_eeg_data(X, y, n_channels, time_steps, test_size=0.2, random_state=42)
→ ((X_train, y_train), (X_test, y_test), prep)
```

### `EEGDataPreparation` Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `reshape_for_model()` | Convert to (samples, time, channels) | `X = prep.reshape_for_model(X)` |
| `normalize()` | StandardScaler normalization | `X = prep.normalize(X, fit=True)` |
| `split_data()` | Stratified 80-20 split | `(tr, te) = prep.split_data(X, y)` |
| `validate_shape()` | Check data format | `prep.validate_shape(X)` |
| `get_statistics()` | Mean, std, min, max | `stats = prep.get_statistics(X)` |
| `get_normalization_params()` | Scaler parameters | `params = prep.get_normalization_params()` |
| `denormalize()` | Reverse normalization | `X_orig = prep.denormalize(X_norm)` |

## 🎯 Common Patterns

### Pattern: Train-Test Normalization
```python
# FIT on training data
X_train_norm = prep.normalize(X_train, fit=True)

# NO FIT on test data (use training parameters)
X_test_norm = prep.normalize(X_test, fit=False)
```

### Pattern: Different Split Ratios
```python
prepare_eeg_data(X, y, 64, 250, test_size=0.1)   # 90-10
prepare_eeg_data(X, y, 64, 250, test_size=0.2)   # 80-20
prepare_eeg_data(X, y, 64, 250, test_size=0.3)   # 70-30
```

### Pattern: Multi-Subject Processing
```python
prep = EEGDataPreparation(64, 250)  # Create once

for subject in range(1, 11):
    X, y = load_subject(subject)
    X_norm = prep.normalize(X, fit=(subject==1))  # Fit only on first
    # Process X_norm
```

## 🔍 Data Shapes

| Stage | Shape | Example |
|-------|-------|---------|
| Input | `(samples, channels, time)` | `(1000, 64, 250)` |
| After reshape | `(samples, time, channels)` | `(1000, 250, 64)` |
| After normalize | Same | `(1000, 250, 64)` |
| After split | Train: `(800, 250, 64)` Test: `(200, 250, 64)` | |

## ⚙️ Normalization Explained

**StandardScaler (Z-score)**:
```
X_norm = (X - mean) / std
```

- Mean ≈ 0
- Std ≈ 1
- Reversible

## ✅ Best Practices

1. **Always stratify splits** (maintains class balance)
   ```python
   (train, test) = prep.split_data(X, y, stratify=True)
   ```

2. **Fit scaler once on training data**
   ```python
   X_train_norm = prep.normalize(X_train, fit=True)    # ✓
   X_test_norm = prep.normalize(X_test, fit=False)     # ✓
   ```

3. **Validate shapes early**
   ```python
   prep.validate_shape(X)  # Catch issues immediately
   ```

4. **Preserve scaler parameters**
   ```python
   params = prep.get_normalization_params()
   np.save('scaler.npy', params)
   ```

## 🚀 Full Example

```python
from src.physionet_loader import load_physionet_data
from src.data_preparation import prepare_eeg_data
from src.model import create_model
from src.train import ModelTrainer

# 1. Load data
X, y = load_physionet_data([1, 2, 3, 4, 5])

# 2. Prepare
(X_train, y_train), (X_test, y_test), prep = prepare_eeg_data(
    X, y, n_channels=64, time_steps=320
)

# 3. Train
config = {'model': {'input_shape': [X_train.shape[1], X_train.shape[2]]}}
model = create_model(config)
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=50)

# 4. Denormalize predictions if needed
y_pred_norm = model.predict(X_test)
# (predictions are already normalized, usually used as-is)
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ValueError: cannot reshape` | Check `X.shape` - should be (samples, features) |
| `UserWarning: least populated class has 1 member` | Reduce `test_size` or collect more data |
| Shape is `(1000, 16000)` not `(1000, 250, 64)` | Use `reshape_for_model()` first |
| Test data has different distribution | Use `stratify=True` in split |

## 📚 Full Documentation

See [DATA_PREPARATION_GUIDE.md](DATA_PREPARATION_GUIDE.md) for:
- Detailed method documentation
- 4+ complete usage examples
- Integration examples with training
- Performance notes
- Advanced topics

---

**Updated**: April 2026  
**Status**: Production-Ready
