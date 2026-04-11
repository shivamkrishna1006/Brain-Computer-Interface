# BCI Configuration Guide

## Overview

The BCI system is fully configurable through the `config.yaml` file in the project root. All parameters can be modified without changing code, making it easy to experiment with different settings.

## Quick Start

### 1. Default Usage
Simply run training with the default configuration:
```bash
python train_eeg_model_production.py
```

The system will automatically load `config.yaml` from the project root.

### 2. Override Individual Parameters via CLI
```bash
# Override learning rate
python train_eeg_model_production.py --learning-rate 0.0005

# Override multiple parameters
python train_eeg_model_production.py --epochs 150 --batch-size 16 --learning-rate 0.0005

# Use a custom config file
python train_eeg_model_production.py --config my_custom_config.yaml
```

### 3. Use Custom Configuration File
```bash
# Create your own config
cp config.yaml config_experiment.yaml

# Edit config_experiment.yaml with your settings

# Train with custom config
python train_eeg_model_production.py --config config_experiment.yaml
```

## Configuration Sections

### 1. PATHS - File System Locations

Controls where models, data, and outputs are stored.

```yaml
paths:
  # Model storage
  models_dir: "models"                      # Root directory for models
  best_model_path: "models/best_eeg_model.h5"  # Where best model is saved
  checkpoint_dir: "models/checkpoints"      # Checkpoint storage
  
  # Data directories
  data_dir: "data"                          # Root data directory
  raw_data_dir: "data/raw"                  # Raw EEG files
  processed_data_dir: "data/processed"      # Processed/cleaned data
  
  # Output and logs
  output_dir: "outputs"                     # Main output directory
  logs_dir: "outputs/logs"                  # Training logs
  history_path: "outputs/training_history.json"
  metadata_path: "outputs/training_metadata.json"
```

### 2. MODEL - Neural Network Architecture

Defines the CNN-LSTM model structure.

```yaml
model:
  type: "CNN_LSTM"                # Model type
  name: "EEG_Motor_Imagery_Classifier"
  
  cnn:
    filters: [32, 64, 128]       # Number of filters per CNN layer
    kernel_size: 3               # Convolution kernel size
    pool_size: 2                 # Max pooling size
    activation: "relu"           # CNN activation function
  
  lstm:
    units: 128                   # LSTM hidden units
    dropout: 0.5                 # LSTM dropout
    recurrent_dropout: 0.2       # Recurrent layer dropout
    return_sequences: false      # Return full sequence or final output
  
  dense:
    units: [64, 32]             # Dense layer units
    dropout: 0.5                 # Dense layer dropout
    activation: "relu"           # Hidden activation
  
  output:
    activation: "softmax"        # Output activation for classification
    loss: "categorical_crossentropy"
```

**Tips**:
- More filters/units = more complex model, longer training
- Higher dropout = more regularization, less overfitting
- Typical range for filters: 16-128
- Typical range for LSTM units: 64-256

### 3. TRAINING - Training Hyperparameters

Controls model training behavior.

```yaml
training:
  # Core hyperparameters
  learning_rate: 0.001          # Initial learning rate
  optimizer: "adam"             # Optimizer type
  batch_size: 32                # Training batch size
  epochs: 50                    # Maximum number of epochs
  
  # Early stopping
  early_stopping:
    enabled: true
    monitor: "val_loss"         # Metric to monitor
    patience: 15                # Epochs without improvement before stopping
    restore_best_weights: true  # Restore best epoch's weights
    min_delta: 0.0001          # Minimum improvement threshold
  
  # Learning rate reduction
  reduce_lr_on_plateau:
    enabled: true
    monitor: "val_loss"
    factor: 0.5                # Multiply LR by this factor
    patience: 5                # Epochs to wait before reducing
    min_lr: 1e-7              # Minimum learning rate floor
  
  # Model checkpointing
  checkpoint:
    enabled: true
    monitor: "val_accuracy"    # Metric to monitor for best model
    save_best_only: true       # Only save if better than previous
  
  # Regularization
  class_weights:
    enabled: true              # Auto-compute weights for imbalanced data
  
  # Data management
  validation_split: 0.2        # Fraction of training data for validation
  test_split: 0.1              # Fraction of data for testing
  shuffle_data: true           # Shuffle training data
  random_seed: 42              # Reproducibility seed
```

**Tips for hyperparameters**:
- **Learning rate**: Start at 0.001, reduce if loss oscillates
- **Batch size**: Small (8-16) = slower but potentially better; Large (64+) = faster but may overfit
- **Epochs**: Start at 50, increase if validation loss still improving
- **Early stopping patience**: 10-20 typically good, prevents overfitting
- **Reduce LR patience**: Usually 5-10, triggers when loss plateaus

### 4. DATA - EEG Signal and Data Parameters

Controls how EEG data is processed and split.

```yaml
data:
  # EEG signal characteristics
  eeg_channels: 8              # Number of electrode channels
  sampling_rate: 250           # Sampling frequency (Hz)
  signal_duration: 1.0         # Signal length (seconds)
  n_samples_per_signal: 250    # Samples per signal
  
  # Classification setup
  n_classes: 5                 # Number of motor imagery classes
  class_labels:                # Name of each class
    0: "Left"
    1: "Right"
    2: "Hands"
    3: "Feet"
    4: "Click"
  
  # Data preprocessing
  preprocessing:
    normalize: true            # Normalize signal
    normalization_type: "z-score"  # z-score or min-max
    
    bandpass_filter:
      enabled: true
      low_cutoff: 0.5         # High-pass cutoff (Hz)
      high_cutoff: 50.0       # Low-pass cutoff (Hz)
      order: 4                # Filter order (higher = steeper)
    
    artifact_removal:
      enabled: false          # Automatic artifact removal
      method: "ICA"
  
  # Data augmentation
  augmentation:
    enabled: true            # Increase training data variety
    noise_std: 0.01         # Standard deviation of added noise
    time_shift: 5           # Max time shift in samples
    scaling_factor: [0.9, 1.1]  # Amplitude scaling range
    stretch_factor: [0.8, 1.2]  # Time stretching range
  
  # Dataset parameters
  n_subjects: 10            # Number of subjects
  n_sessions_per_subject: 2 # Sessions per subject
  n_trials_per_session: 48  # Trials per session
  
  # Frequency bands of interest
  frequency_range:
    low_freq: 8             # Lowest frequency of interest
    high_freq: 30           # Highest frequency of interest
    bands:
      alpha:
        low: 8
        high: 13
      beta:
        low: 13
        high: 30
```

**Tips**:
- Standard EEG sampling: 250Hz or 500Hz
- Motor imagery typically uses alpha (8-13Hz) and beta (13-30Hz) bands
- More channels = more spatial information but longer processing
- Class imbalance? Enable `class_weights`

### 5. REALTIME - Real-Time Inference Parameters

Controls behavior of the real-time inference system.

```yaml
realtime:
  # Buffer management
  buffer_size: 250              # Samples in sliding window (1 sec @ 250Hz)
  buffer_overlap: 0.5           # Fraction of buffer to overlap
  
  # Decision making
  confidence_threshold: 0.7     # Minimum confidence to execute action
  debounce_count: 3             # N predictions needed before acting
  action_cooldown_ms: 100       # Minimum time between actions
  
  # Mouse control
  mouse:
    move_distance: 50           # Pixels per movement
    cursor_smoothing:
      enabled: true             # Smooth cursor movements
      alpha: 0.3               # 0=smooth, 1=responsive
      velocity_factor: 0.8     # Momentum/inertia factor
    
    edge_margin_px: 20          # Keep cursor from screen edges
    
    # Per-action configuration
    left_move_pixels: 50
    right_move_pixels: 50
    up_move_pixels: 50
    down_move_pixels: 50
    click_duration_ms: 100
  
  # Statistics and monitoring
  track_statistics: true        # Log action counts
  print_predictions: false      # Print each prediction
  print_interval_sec: 5.0       # Statistics print interval
  
  # Control options
  allow_pause: true             # Allow pause/resume
  return_status: true           # Return system status
```

**Tips**:
- **Confidence threshold**: Higher (0.8+) = safer but may miss real commands; Lower (0.5) = responsive but more errors
- **Debounce count**: Higher (5+) = stable but slower; Lower (1-2) = faster but jittery
- **Alpha smoothing**: Higher (0.5+) = more responsive; Lower (0.1) = smoother motion

### 6. DATA_GENERATION - Synthetic Data Parameters

For testing without real EEG hardware.

```yaml
data_generation:
  generate_synthetic: false      # Generate synthetic data
  synthetic_data_size: 1000      # Number of samples to generate
  
  # Signal characteristics for synthetic data
  base_frequency: 10.0          # Hz (alpha band)
  noise_level: 0.1              # Relative noise
  drift_frequency: 0.1          # Hz (low-frequency drift)
  
  # Class-specific patterns
  class_patterns:
    left_amplitude: 1.2
    right_amplitude: 1.2
    hands_amplitude: 1.3
    feet_amplitude: 1.4
    click_amplitude: 1.1
```

### 7. LOGGING - Logging and Debugging

Controls log output verbosity and format.

```yaml
logging:
  level: "INFO"                 # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "outputs/logs/training.log"
  
  verbose:
    print_epoch_details: true   # Print detailed epoch metrics
    print_batch_details: false  # Print batch-level details
    print_eta: true             # Print estimated time remaining
    show_progress_bar: true     # Show progress bar during epochs
```

## Common Configuration Scenarios

### Scenario 1: Quick Prototyping
```yaml
training:
  epochs: 20                    # Reduced epochs for faster iteration
  batch_size: 64               # Larger batches (faster training)
  learning_rate: 0.01          # Higher LR (faster convergence)

model:
  cnn:
    filters: [16, 32]          # Fewer filters (smaller model)
  lstm:
    units: 64                  # Smaller LSTM (faster)
```

### Scenario 2: High Accuracy (Large Dataset)
```yaml
training:
  epochs: 150                  # More epochs for convergence
  batch_size: 16              # Smaller batches (better updates)
  learning_rate: 0.0005       # Lower LR (stable learning)
  early_stopping:
    patience: 25              # More patience for slow convergence

model:
  cnn:
    filters: [64, 128, 256]   # More filters (more capacity)
  lstm:
    units: 256                # Larger LSTM
  dense:
    units: [128, 64]          # More dense layers
```

### Scenario 3: Real-Time Motor Control (Low Latency)
```yaml
realtime:
  buffer_size: 250            # 1 second of data
  debounce_count: 2           # Faster response (less stable)
  confidence_threshold: 0.6   # Lower threshold
  action_cooldown_ms: 50      # Faster action rate
  mouse:
    cursor_smoothing:
      alpha: 0.8              # More responsive
```

### Scenario 4: Robust Motor Control (High Stability)
```yaml
realtime:
  debounce_count: 5           # More predictions required
  confidence_threshold: 0.8   # Stricter threshold
  action_cooldown_ms: 200     # Slower action rate
  mouse:
    cursor_smoothing:
      alpha: 0.2              # Smoother movement
    edge_margin_px: 50        # More margin from edges
```

## Using Configuration in Code

### Load Config in Your Script

```python
from src.config import load_config

# Auto-load config.yaml
config = load_config()

# Or with custom path
config = load_config('my_config.yaml')
```

### Access Config Values

```python
from src.config import (
    load_config, 
    get_config_value,
    get_learning_rate,
    get_epochs
)

config = load_config()

# Direct access (nested dictionary)
batch_size = config['training']['batch_size']

# Dot-notation access (safer)
batch_size = get_config_value(config, 'training.batch_size', default=32)

# Convenience functions
lr = get_learning_rate(config)
epochs = get_epochs(config)
channels = get_eeg_channels(config)
```

### Validate Config

```python
from src.config import validate_config

config = load_config()

required = {
    'training.epochs': int,
    'data.eeg_channels': int,
    'data.sampling_rate': int,
}

is_valid, message = validate_config(config, required)
if not is_valid:
    print(f"Config error: {message}")
```

### Print Config

```python
from src.config import print_config

config = load_config()
print_config(config, "Training Configuration")
```

## Best Practices

1. **Start with defaults**: Use the default `config.yaml` as a starting point
2. **Version your configs**: Keep configs for different experiments (e.g., `config_v1.yaml`, `config_exp_large.yaml`)
3. **Document changes**: Add comments explaining why you modified specific parameters
4. **Use appropriate units**: Learning rate in scientific notation (e.g., 1e-3 not 0.001)
5. **Keep consistent**: Don't mix approaches (use either YAML or CLI args, not both)
6. **Validate early**: Check config validity before starting expensive computations

## Troubleshooting

### Config not loading?
```bash
# Check if config.yaml exists
ls config.yaml

# Use explicit path
python train_eeg_model_production.py --config config.yaml
```

### Override not working?
- CLI arguments only work for: `--epochs`, `--batch-size`
- For other parameters, edit `config.yaml` directly

### "Key not found" error?
- Check spelling of configuration keys
- Use `print_config()` to see available keys
- Ensure YAML syntax is correct (colons, indentation)

## Default Configuration Values

See `config.yaml` in the project root for the complete list of default values. This is the authoritative reference.

## Further Reading

- [YAML Documentation](https://yaml.org/)
- [Python argparse](https://docs.python.org/3/library/argparse.html)
- TensorFlow/Keras documentation for model-specific parameters
