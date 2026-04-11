# Production-Ready CNN-LSTM EEG Training System

Complete production-ready training implementation with all enterprise-grade features.

## Features Overview

### ✅ Machine Learning Features
- **Early Stopping**: Prevents overfitting by monitoring validation loss
- **Reduce Learning Rate on Plateau**: Adaptively reduces learning rate when validation loss stops improving
- **Class Weight Computation**: Automatically handles imbalanced datasets by weighting classes inversely to their frequency
- **Model Checkpointing**: Saves the best model based on validation accuracy
- **Training Progress Logging**: Detailed epoch-by-epoch metrics with ETA calculation
- **History Storage**: Complete training history saved as JSON for analysis and visualization
- **Comprehensive Metrics**: Loss, accuracy, precision, recall, AUC

### ✅ Production Features
- **Configuration Management**: YAML-based configuration with command-line overrides
- **Error Handling**: Comprehensive validation and graceful error recovery
- **Logging System**: Detailed logging at all stages with customizable verbosity
- **TensorBoard Integration**: Real-time monitoring and visualization
- **Artifact Persistence**: Saves model, history, config, and logs
- **Data Validation**: Input validation and class distribution checking
- **Reproducibility**: Seed control and stratified data splitting

## Project Structure

```
BCI_INTERFACE/
├── src/
│   ├── train.py              # Main training module (production-ready)
│   │   ├── TrainingProgressCallback    # Custom progress logging
│   │   ├── ModelTrainer                # Main trainer class
│   │   ├── compute_class_weights_auto() # Imbalance handling
│   │   ├── validate_training_config()  # Config validation
│   │   └── train_cnn_lstm_model()      # Main pipeline function
│   ├── model.py              # CNN-LSTM model architecture
│   ├── data_loader.py        # Data loading utilities
│   └── ...
├── train_eeg_model_production.py  # Standalone training script (recommended)
├── train_eeg_model.py        # Legacy training script
├── configs/
│   └── config.yaml           # Configuration file
├── models/                   # Saved model directory
├── outputs/                  # Training outputs (history, logs, etc.)
└── data/                     # Data directory
```

## Quick Start

### 1. Basic Training (Synthetic Data)

```bash
# Train with default settings
python train_eeg_model_production.py

# Expected output:
# - Model saved to: models/best_eeg_model_*.h5
# - History saved to: outputs/training_history_*.json
# - Config saved to: outputs/training_config_*.json
# - Logs available at: outputs/logs/
```

### 2. Custom Training Parameters

```bash
# Train with custom epochs and batch size
python train_eeg_model_production.py --epochs 150 --batch-size 16

# Generate more samples for training
python train_eeg_model_production.py --n-samples 5000

# Train with different number of classes
python train_eeg_model_production.py --n-classes 3
```

### 3. Load Custom Configuration

```bash
# Create custom config file (custom_config.yaml)
python train_eeg_model_production.py --config custom_config.yaml
```

## Configuration System

### Default Configuration

```yaml
model:
  input_shape: [250, 8]      # [time_steps, channels]
  cnn_filters: [32, 64, 128]
  lstm_units: [128, 64]
  dense_units: [64, 32]
  l2_regularization: 0.001

training:
  epochs: 100
  batch_size: 32
  learning_rate: 0.001
  
  # Early stopping
  early_stopping_patience: 15
  
  # Learning rate scheduling
  reduce_lr_patience: 5
  reduce_lr_factor: 0.5
  
  # Class weights for imbalance
  use_class_weights: true
```

### Creating Custom Config

```yaml
# custom_config.yaml
model:
  input_shape: [320, 64]
  cnn_filters: [64, 128, 256]
  lstm_units: [256, 128]

training:
  epochs: 200
  batch_size: 64
  learning_rate: 0.0005
  early_stopping_patience: 20
  reduce_lr_patience: 8
```

Usage:
```bash
python train_eeg_model_production.py --config custom_config.yaml
```

## Core Components

### 1. TrainingProgressCallback
Custom Keras callback for detailed progress logging.

**Features:**
- Per-epoch progress with metrics
- ETA calculation using running average
- Learning rate monitoring
- Training time tracking

**Output Example:**
```
Epoch [  1/100] | Loss: 1.2345 | Val Loss: 1.1234 | 
Acc: 0.6543 | Val Acc: 0.7123 | LR: 1.00e-03 | ETA: 45m 32s
```

### 2. ModelTrainer Class
Main training orchestration class.

**Key Methods:**
```python
trainer = ModelTrainer(config, n_classes=5)

# Compute class weights for imbalanced data
class_weights = trainer.compute_class_weights(y_train)

# Build all training callbacks
callbacks = trainer.build_callbacks(
    model_save_path='models/best_model.h5',
    early_stopping_patience=15,
    reduce_lr_patience=5
)

# Train the model
results = trainer.train(
    X_train, y_train,
    X_val, y_val,
    X_test, y_test
)

# Save training history
trainer.save_history('outputs/history.json')

# Save configuration
trainer.save_config('outputs/config.json')

# Get detailed metrics
metrics = trainer.get_training_metrics()

# Print summary
summary = trainer.training_summary()
```

### 3. Training Callbacks Suite

#### Early Stopping
- **Monitors**: Validation loss
- **Patience**: 15 epochs (configurable)
- **Action**: Restores best weights and stops training
- **Min delta**: 1e-4 (minimum improvement)

#### ReduceLROnPlateau
- **Monitors**: Validation loss
- **Patience**: 5 epochs
- **Factor**: 0.5 (multiply LR by 0.5)
- **Min LR**: 1e-7 (prevents collapse)
- **Cooldown**: 2 epochs between reductions

#### ModelCheckpoint
- **Monitors**: Validation accuracy
- **Save best only**: True
- **Format**: Full model (architecture + weights)

#### TensorBoard
- **Update frequency**: Every epoch
- **Histogram frequency**: Every epoch
- **Graph writing**: Enabled
- **Usage**: `tensorboard --logdir outputs/logs`

### 4. Class Weight Computation

Automatically handles imbalanced datasets using `sklearn.utils.class_weight.compute_class_weight`.

**Algorithm**: Balanced strategy (inverse frequency weighting)
- Minority classes get higher weights
- Majority classes get lower weights
- Prevents bias toward dominant class

**Example Output:**
```
Class weights computed:
  Class 0: 1.5000
  Class 1: 1.2500
  Class 2: 2.0000
  Class 3: 2.0000
  Class 4: 2.0000
```

## Training Workflow

1. **Configuration Validation**
   - Checks for required keys
   - Validates parameter ranges
   - Reports any issues before training

2. **Data Preparation**
   - Generates or loads data
   - Computes statistics
   - Performs stratified split (maintains class distribution)

3. **Model Creation**
   - Builds CNN-LSTM architecture
   - Compiles with optimizer and loss
   - Reports parameter count

4. **Class Weight Computation**
   - Analyzes training set class distribution
   - Computes balanced weights
   - Reports weights per class

5. **Callback Setup**
   - Early stopping
   - Learning rate scheduling
   - Model checkpointing
   - TensorBoard logging
   - Progress tracking

6. **Training Loop**
   - Iterates through epochs
   - Applies all callbacks
   - Logs progress
   - Saves best model

7. **Evaluation & Reporting**
   - Computes summary statistics
   - Identifies best epoch
   - Reports final metrics
   - Saves all artifacts

## Output Files

### Training History (`training_history_*.json`)
Complete training metrics per epoch:
```json
{
  "loss": [1.234, 1.123, ...],
  "accuracy": [0.654, 0.712, ...],
  "val_loss": [1.234, 1.123, ...],
  "val_accuracy": [0.654, 0.712, ...],
  "metadata": {
    "timestamp": "20240410_120000",
    "n_classes": 5,
    "n_epochs": 45,
    "class_weights": {"0": 1.5, "1": 1.25, ...}
  }
}
```

### Training Config (`training_config_*.json`)
Configuration used for reproducibility:
```json
{
  "timestamp": "20240410_120000",
  "n_classes": 5,
  "model_config": {...},
  "training_config": {...},
  "class_weights": {...},
  "best_model_path": "models/best_eeg_model.h5"
}
```

### Model File (`best_eeg_model_*.h5`)
Complete trained model (architecture + weights):
- Ready for inference
- Compatible with TensorFlow/Keras
- Contains all layer definitions

### TensorBoard Logs (`outputs/logs/`)
Real-time training visualization:
```bash
tensorboard --logdir outputs/logs
# Open browser to http://localhost:6006
```

## Advanced Usage

### Using in Python Code

```python
from src.train import train_cnn_lstm_model, ModelTrainer
from src.model import create_model

# Load your data
X_train, y_train = load_train_data()
X_val, y_val = load_val_data()
X_test, y_test = load_test_data()

# Train model
results = train_cnn_lstm_model(
    config=config,
    X_train=X_train,
    y_train=y_train,
    X_val=X_val,
    y_val=y_val,
    X_test=X_test,
    y_test=y_test,
    n_classes=5
)

# Access results
model = results['model']
trainer = results['trainer']
history = results['history']
metrics = results['metrics']
```

### Custom Configuration in Python

```python
config = {
    'model': {
        'input_shape': (320, 64),
        'cnn_filters': [64, 128, 256],
        'lstm_units': [256, 128],
        'l2_regularization': 0.001
    },
    'training': {
        'epochs': 150,
        'batch_size': 64,
        'learning_rate': 0.0005,
        'early_stopping_patience': 20,
        'reduce_lr_patience': 8,
        'reduce_lr_factor': 0.3
    },
    'output': {
        'model_dir': 'models',
        'log_dir': 'outputs/logs'
    }
}

# Train with custom config
trainer = ModelTrainer(config, n_classes=5)
trainer.model = create_model(config)
results = trainer.train(X_train, y_train, X_val, y_val)
```

### Loading and Fine-tuning

```python
from tensorflow.keras.models import load_model

# Load trained model
model = load_model('models/best_eeg_model.h5')

# Fine-tune on new data
trainer = ModelTrainer(config)
trainer.model = model
results = trainer.train(
    X_train_new, y_train_new,
    X_val_new, y_val_new,
    epochs=20,  # Few epochs for fine-tuning
    verbose=1
)
```

## Monitoring with TensorBoard

```bash
# Start TensorBoard
tensorboard --logdir outputs/logs

# View in browser
# http://localhost:6006
```

**Available metrics:**
- Training loss, accuracy, precision, recall, AUC
- Validation loss, accuracy, precision, recall, AUC
- Learning rate changes
- Histogram of weights and biases
- Model graph architecture

## Troubleshooting

### Issue: Out of Memory
**Solution:** Reduce batch size or input shape
```bash
python train_eeg_model_production.py --batch-size 16
```

### Issue: Training not improving
**Solution:** Increase learning rate or reduce regularization
Edit config:
```yaml
training:
  learning_rate: 0.01
model:
  l2_regularization: 0.0001
```

### Issue: Early stopping too aggressive
**Solution:** Increase patience
```bash
python train_eeg_model_production.py
# Then edit config to increase early_stopping_patience
```

### Issue: Class imbalance not handled
**Solution:** Ensure use_class_weights is True (default)
- Training automatically computes class weights
- Check logs for "Class weights computed"

## Requirements

```
tensorflow >= 2.10
numpy >= 1.21
scikit-learn >= 1.0
pyyaml >= 5.4
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Best Practices

1. **Data Preparation**
   - Use stratified data splitting (built-in)
   - Normalize input data (built-in)
   - Balance classes with weights (automatic)
   - Use validation set for early stopping

2. **Hyperparameter Tuning**
   - Start with default config
   - Adjust epochs and batch size for your data size
   - Use ReduceLROnPlateau for learning rate
   - Monitor with TensorBoard

3. **Production Deployment**
   - Save trained model (automatic)
   - Save configuration (automatic)
   - Log all metrics (automatic)
   - Version your models with timestamps

4. **Monitoring**
   - Check TensorBoard for visual monitoring
   - Review training history JSON for analysis
   - Monitor early stopping triggering
   - Check learning rate scheduling

## Performance Tips

### Speed Optimization
- Increase batch size (more memory needed)
- Reduce log interval
- Disable TensorBoard histogram freq if not needed

### Memory Optimization
- Reduce batch size
- Reduce input shape
- Use gradient accumulation for large batches

### Accuracy Optimization
- Increase epochs
- Use smaller learning rate
- Increase model capacity (more filters, units)
- Use data augmentation

## Version History

- **2.0** (Current): Production-ready with all features
  - Early stopping
  - ReduceLROnPlateau
  - Class weights
  - Model checkpointing
  - TensorBoard integration
  - Comprehensive logging
  - Configuration system

- **1.0**: Basic training implementation

## License

BCI Interface Team - Production Ready

## Support

For issues or questions, refer to:
- `TRAINING_GUIDE.md` - Detailed training guide
- `CONFIG_GUIDE.md` - Configuration documentation
- Model docstrings in `src/model.py`
- Trainer docstrings in `src/train.py`
