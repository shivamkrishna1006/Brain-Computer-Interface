# PhysioNet EEG Motor Imagery Dataset Module

## Overview

The `physionet_loader.py` module provides a clean, reusable interface for loading and preprocessing the **PhysioNet EEG Motor Imagery Database** using MNE-Python.

**Dataset Reference**: https://physionet.org/content/eegmmidb/1.0.0/

## Features

✅ **Multiple Subject Loading**: Load data from multiple subjects (1-109) simultaneously  
✅ **Task-based Loading**: Support for all 4 motor imagery tasks flexibly  
✅ **Automatic Filtering**: Applies 8-30 Hz bandpass filter (motor imagery frequency band)  
✅ **Epoch Extraction**: Configurable time window (default: 0.5-3.5s after stimulus)  
✅ **Data Validation**: Automatic handling of missing/corrupt data  
✅ **Class Balancing**: Stratified splitting to maintain class distribution  
✅ **Comprehensive Logging**: Detailed debug information  

## Dataset Information

### Structure
- **Subjects**: 1-109 (approximately 109 participants)
- **Sessions**: 1-2 per subject
- **EEG Channels**: 64 channels
- **Sampling Rate**: 160 Hz
- **Recording**: Multiple runs per session

### Motor Imagery Tasks (4-class)

| Task | Event ID | Runs |
|------|----------|------|
| Left Hand | 1 | 3, 7, 11 |
| Right Hand | 2 | 4, 8, 12 |
| Both Hands | 3 | 5, 9, 13 |
| Both Feet | 4 | 6, 10, 14 |

### Existing Runs
- **Runs 1-2**: Baseline, eyes open/closed
- **Runs 3-14**: Motor imagery tasks (listed above)

## Usage

### Basic Usage

```python
from physionet_loader import load_physionet_data

# Load data for first 3 subjects, left and right hand tasks
X, y = load_physionet_data(
    subject_ids=[1, 2, 3],
    tasks=['left_hand', 'right_hand'],
    sessions=1,
    filter_freqs=(8, 30),
    epoch_window=(0.5, 3.5)
)

print(f"Data shape: {X.shape}")  # (n_epochs, 64, time_points)
print(f"Labels: {y.shape}")       # (n_epochs,)
```

### Advanced Usage: Multi-class Classification

```python
# Load all 4 motor imagery tasks
X, y = load_physionet_data(
    subject_ids=[1, 2, 3, 4, 5],
    tasks=['left_hand', 'right_hand', 'both_hands', 'both_feet'],
    sessions=2,  # Load both sessions
    filter_freqs=(8, 30),
    epoch_window=(0.5, 3.5)
)

from physionet_loader import get_label_mapping
label_map = get_label_mapping()
print(label_map)
# {0: 'Rest', 1: 'Left Hand', 2: 'Right Hand', 3: 'Both Hands', 4: 'Both Feet'}
```

### Data Splitting

```python
from physionet_loader import prepare_data_splits

# Split with stratification to maintain class balance
(X_train, y_train), (X_val, y_val), (X_test, y_test) = prepare_data_splits(
    X, y,
    train_ratio=0.7,
    val_ratio=0.15,
    test_ratio=0.15,
    random_seed=42
)
```

### Using PhysioNetEEGDataset Class

For more control, use the class directly:

```python
from physionet_loader import PhysioNetEEGDataset

# Initialize loader
dataset = PhysioNetEEGDataset(data_dir='data/physionet', verbose=False)

# Load single subject
X, y = dataset.load_subject(
    subject_id=1,
    tasks=['left_hand', 'right_hand'],
    sessions=1,
    filter_freqs=(8, 30),
    epoch_window=(0.5, 3.5)
)

# Load multiple subjects
X_all, y_all = dataset.load_subjects(
    subject_ids=[1, 2, 3, 4, 5],
    tasks=['left_hand', 'right_hand'],
    sessions=1
)

# Get dataset information
info = dataset.get_data_info(X, y)
print(info)
# {
#     'n_epochs': 400,
#     'n_channels': 64,
#     'n_timepoints': 321,
#     'n_classes': 2,
#     'class_distribution': {'Left Hand': 200, 'Right Hand': 200},
#     ...
# }
```

## API Reference

### Main Function: `load_physionet_data()`

```python
def load_physionet_data(
    subject_ids: List[int],
    tasks: Optional[List[str]] = None,
    sessions: int = 1,
    filter_freqs: Tuple[float, float] = (8, 30),
    epoch_window: Tuple[float, float] = (0.5, 3.5),
    data_dir: str = 'data/physionet',
    verbose: bool = False
) -> Tuple[np.ndarray, np.ndarray]
```

**Parameters:**
- `subject_ids`: List of subject IDs to load (1-109)
- `tasks`: Motor imagery tasks to load
  - Options: `'left_hand'`, `'right_hand'`, `'both_hands'`, `'both_feet'`
  - Default (None): Load all tasks
- `sessions`: Number of sessions per subject (1 or 2)
- `filter_freqs`: Bandpass filter range (low_freq, high_freq) in Hz
  - Default: (8, 30) - motor imagery frequency band
  - Common values: (0.5, 40) for broadband, (8, 30) for motor, (8, 12) for alpha
- `epoch_window`: Time window (tmin, tmax) in seconds relative to stimulus onset
  - Default: (0.5, 3.5) - 0.5 to 3.5 seconds after stimulus
  - Motor imagery task duration: 4 seconds
- `data_dir`: Directory to download/cache dataset
- `verbose`: Enable verbose MNE logging

**Returns:**
- `X`: EEG data array of shape (n_epochs, n_channels, n_times)
- `y`: Label array of shape (n_epochs,) with values 1-4

### Class: `PhysioNetEEGDataset`

```python
class PhysioNetEEGDataset:
    def __init__(self, data_dir: str = 'data/physionet', verbose: bool = False)
    
    def load_subject(
        self,
        subject_id: int,
        tasks: Optional[List[str]] = None,
        sessions: int = 1,
        filter_freqs: Tuple[float, float] = (8, 30),
        epoch_window: Tuple[float, float] = (0.5, 3.5)
    ) -> Tuple[np.ndarray, np.ndarray]
    
    def load_subjects(
        self,
        subject_ids: List[int],
        tasks: Optional[List[str]] = None,
        sessions: int = 1,
        filter_freqs: Tuple[float, float] = (8, 30),
        epoch_window: Tuple[float, float] = (0.5, 3.5)
    ) -> Tuple[np.ndarray, np.ndarray]
    
    def get_data_info(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Dict
```

### Helper Functions

```python
def prepare_data_splits(
    X: np.ndarray,
    y: np.ndarray,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = 42
) -> Tuple[Tuple, Tuple, Tuple]
# Returns: ((X_train, y_train), (X_val, y_val), (X_test, y_test))

def get_label_mapping() -> Dict[int, str]
# Returns: {0: 'Rest', 1: 'Left Hand', 2: 'Right Hand', 3: 'Both Hands', 4: 'Both Feet'}

def get_task_mapping() -> Dict[str, List[int]]
# Returns: {'left_hand': [3, 7, 11], 'right_hand': [4, 8, 12], ...}
```

## Examples

### Example 1: Binary Classification (Left vs Right Hand)

```python
from physionet_loader import load_physionet_data, prepare_data_splits
import numpy as np

# Load left and right hand data
X, y = load_physionet_data(
    subject_ids=list(range(1, 6)),  # First 5 subjects
    tasks=['left_hand', 'right_hand'],
    sessions=1
)

print(f"Data shape: {X.shape}")  # (n_epochs, 64, ~320)
print(f"Class distribution: {np.bincount(y)}")

# Split data
(X_train, y_train), (X_val, y_val), (X_test, y_test) = prepare_data_splits(X, y)

# Use with your model
from src.model import create_model
from src.utils import load_config

config = load_config('configs/config.yaml')
config['data']['eeg_channels'] = X.shape[1]  # 64
config['model']['input_shape'] = [X.shape[2], X.shape[1]]

model = create_model(config)
```

### Example 2: Motor Imagery Task Comparison

```python
from physionet_loader import load_physionet_data, get_label_mapping
import numpy as np

# Load all 4 motor imagery tasks
X_all, y_all = load_physionet_data(
    subject_ids=[1, 2, 3],
    tasks=['left_hand', 'right_hand', 'both_hands', 'both_feet'],
    sessions=1
)

# Compare tasks
label_map = get_label_mapping()
for label_id in np.unique(y_all):
    count = np.sum(y_all == label_id)
    print(f"{label_map[label_id]}: {count} epochs")
```

### Example 3: Cross-subject Analysis

```python
from physionet_loader import PhysioNetEEGDataset

dataset = PhysioNetEEGDataset()

# Load multiple subjects separately for cross-validation
subject_data = {}
for subject_id in range(1, 6):
    X, y = dataset.load_subject(subject_id, tasks=['left_hand', 'right_hand'])
    subject_data[subject_id] = (X, y)
    print(f"Subject {subject_id}: {X.shape[0]} epochs")
```

## Frequency Band Recommendations

Different frequency bands are important for different analyses:

| Band | Frequency Range | Use Case |
|------|-----------------|----------|
| Delta | 0.5-4 Hz | Slow oscillations |
| Theta | 4-8 Hz | Attention, meditation |
| Alpha | 8-12 Hz | Idle state, baseline |
| **Mu/Beta** | **8-30 Hz** | **Motor imagery (default)** |
| Gamma | 30-50 Hz | Active processing |
| Broadband | 0.5-50 Hz | All activity |

For motor imagery tasks, **8-30 Hz** is the standard choice as it captures mu and beta activity associated with motor planning.

## Epoch Window Selection

The epoch window determines what portion of the motor imagery task to extract:

```
├─ Rest (2s)  ├─ Stimulus (4s)  └─ Rest (2s)
                  ├─ Preparation (0-0.5s)
                  ├─ Execution (0.5-3.5s) ← Default window
                  └─ Post (3.5-4s)
```

- **Narrow (0.5-2.0s)**: Focus on movement execution
- **Standard (0.5-3.5s)**: Full execution period (default)
- **Wide (0.0-4.0s)**: Include preparation phase

## Common Issues & Solutions

### Issue 1: Memory Usage for Large Datasets

```python
# Load and process in batches instead
for subject_id in range(1, 20):
    X, y = load_physionet_data([subject_id])
    # Process and save immediately
    np.save(f'data/subject_{subject_id}_X.npy', X)
    np.save(f'data/subject_{subject_id}_y.npy', y)
```

### Issue 2: Imbalanced Classes

```python
from physionet_loader import prepare_data_splits

# prepare_data_splits automatically uses stratified splitting
(X_train, y_train), (X_val, y_val), (X_test, y_test) = prepare_data_splits(X, y)

# Verify balance
print(np.bincount(y_train) / len(y_train))  # Proportions should match original
```

### Issue 3: Different Sampling Rates

PhysioNet data is resampled to 160 Hz. If you need a different rate:

```python
import mne

# Resample after loading
X, y = load_physionet_data([1, 2, 3])
new_sfreq = 250  # Desired sampling rate

# Interpolate channels
from scipy import signal
for i in range(X.shape[0]):
    new_length = int(X.shape[2] * new_sfreq / 160)
    X[i, :, :] = signal.resample(X[i, :, :], new_length, axis=1)
```

## Performance Notes

- **Download Time**: First-run data download ~5 minutes per subject
- **Processing Time**: ~1-2 minutes per subject for preprocessing
- **Memory**: ~100-200 MB for 5 subjects, all tasks
- **Disk Space**: ~2 GB for all 109 subjects

## Integration with BCI System

```python
from physionet_loader import load_physionet_data, prepare_data_splits
from utils import normalize_data
from model import create_model
from train import ModelTrainer

# Load data
X, y = load_physionet_data([1, 2, 3, 4, 5])

# Normalize
original_shape = X.shape
X_reshaped = X.reshape(-1, X.shape[-1])
X_reshaped, norm_params = normalize_data(X_reshaped, method='zscore')
X = X_reshaped.reshape(original_shape)

# Split
(X_train, y_train), (X_val, y_val), (X_test, y_test) = prepare_data_splits(X, y)

# Train
config = load_config('configs/config.yaml')
config['data']['eeg_channels'] = X.shape[1]
config['model']['input_shape'] = [X.shape[2], X.shape[1]]

trainer = ModelTrainer(config)
history = trainer.train(X_train, y_train, X_val, y_val)
```

## References

1. **PhysioNet Dataset**: Schalk et al. (2004) - "A brain-computer interface based on motor imagery"
2. **MNE-Python**: Gramfort et al. - https://mne.tools/
3. **Motor Imagery**: Pfurtscheller & Neuper (2001)

## License

This module is provided as-is for research and educational purposes.

---

**Last Updated**: April 2026  
**Version**: 1.0.0  
**Status**: Production-Ready
