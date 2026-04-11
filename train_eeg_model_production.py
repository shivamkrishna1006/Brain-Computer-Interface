"""
Production-Ready CNN-LSTM EEG Classification Training Script

Complete implementation with all production-ready features:
1. Configuration management and validation
2. Synthetic/real data generation
3. Data preprocessing and splitting (with stratification)
4. Model creation
5. Training with comprehensive callbacks:
   - Early stopping (prevents overfitting)
   - Learning rate scheduling via ReduceLROnPlateau
   - Class weight computation for imbalanced data
   - Model checkpointing (saves best model)
   - TensorBoard monitoring (real-time visualization)
   - Custom progress logging (detailed metrics per epoch)
6. Detailed evaluation and reporting
7. History and configuration persistence (JSON)
8. Error handling and validation

Key Features:
- Production-ready with comprehensive logging
- Configuration system with YAML support
- Automatic class weight calculation for data imbalance
- Multiple callback types for robust training
- JSON-based history and config storage
- Detailed console progress with ETA calculation
- TensorBoard integration for visualization
- Model and training artifacts persistence
- Stratified data splitting

Usage:
    python train_eeg_model_production.py
    python train_eeg_model_production.py --epochs 150 --batch-size 16
    python train_eeg_model_production.py --config custom_config.yaml --n-samples 2000

Requirements:
    - tensorflow >= 2.10
    - numpy
    - scikit-learn
    - pyyaml (for config loading)

Author: BCI Interface Team
Version: 2.0
Status: Production-Ready
"""

import logging
import numpy as np
import argparse
import yaml
from pathlib import Path
from typing import Tuple, Dict, Optional
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.train import ModelTrainer, validate_training_config
from src.model import create_model

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING SETUP
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EEG_Training')


# ─────────────────────────────────────────────────────────────────────────────
# DEFAULT CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    'model': {
        'name': 'CNN_LSTM_EEG',
        'input_shape': (250, 8),  # (time_steps, channels)
        'cnn_filters': [32, 64, 128],
        'cnn_kernel_size': 5,
        'cnn_pool_size': 2,
        'cnn_dropout': 0.3,
        'lstm_units': [128, 64],
        'lstm_dropout': 0.4,
        'lstm_recurrent_dropout': 0.2,
        'dense_units': [64, 32],
        'dense_dropout': 0.3,
        'l2_regularization': 0.001
    },
    'training': {
        'epochs': 100,
        'batch_size': 32,
        'learning_rate': 0.001,
        'optimizer': 'adam',
        'loss_function': 'categorical_crossentropy',
        
        # Early stopping
        'early_stopping_patience': 15,
        'early_stopping_monitor': 'val_loss',
        'early_stopping_restore_best': True,
        
        # Learning rate scheduling
        'use_lr_scheduler': True,
        'lr_scheduler_type': 'plateau',  # 'plateau', 'exponential', 'step'
        'reduce_lr_patience': 5,
        'reduce_lr_factor': 0.5,
        'lr_decay_rate': 0.95,
        'lr_decay_steps': 10,
        
        # Class weights for imbalance
        'use_class_weights': True,
        
        # Logging
        'log_interval': 5,
        'validation_split': 0.0  # 0 = use separate validation set
    },
    'data': {
        'train_split': 0.6,
        'val_split': 0.2,
        'test_split': 0.2,
        'random_state': 42,
        'normalize': True,
        'normalize_method': 'zscore'  # 'zscore', 'minmax', 'robust'
    },
    'output': {
        'base_dir': 'outputs',
        'model_dir': 'models',
        'log_dir': 'outputs/logs',
        'output_dir': 'outputs'
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# DATA GENERATION & PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def generate_synthetic_eeg_data(
    n_samples: int = 1000,
    time_steps: int = 250,
    n_channels: int = 8,
    n_classes: int = 5,
    noise_level: float = 0.1,
    random_state: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate realistic synthetic EEG data with class-specific patterns.
    
    Creates EEG-like data with:
    - Realistic frequency components (alpha, beta bands)
    - Class-specific patterns
    - Gaussian noise
    - Proper normalization
    
    Args:
        n_samples: Number of samples (default: 1000)
        time_steps: Length of time series per sample (default: 250)
        n_channels: Number of EEG channels (default: 8)
        n_classes: Number of classification classes (default: 5)
        noise_level: Standard deviation of Gaussian noise (default: 0.1)
        random_state: Random seed for reproducibility (default: 42)
        
    Returns:
        Tuple of (X, y):
        - X: Shape (n_samples, time_steps, n_channels), float32, normalized
        - y: Shape (n_samples,), integer class indices
    """
    np.random.seed(random_state)
    
    logger.info(f"Generating {n_samples} synthetic EEG samples...")
    logger.info(f"  Shape: ({n_samples}, {time_steps}, {n_channels})")
    logger.info(f"  Classes: {n_classes}, Noise level: {noise_level}")
    
    # Initialize data
    X = np.random.randn(n_samples, time_steps, n_channels).astype(np.float32)
    y = np.random.randint(0, n_classes, n_samples)
    
    # Add class-specific patterns
    for class_idx in range(n_classes):
        mask = y == class_idx
        n_class_samples = np.sum(mask)
        
        # Class-specific frequency (alpha band: 8-13 Hz normalized)
        base_freq = 0.01 + class_idx * 0.01
        
        # Add temporal patterns for each sample
        for t in range(time_steps):
            # Primary signal: class-specific frequency
            pattern = 0.8 * np.sin(2 * np.pi * base_freq * t / 10)
            # Secondary signal: alpha activity around 10 Hz
            pattern += 0.5 * np.sin(2 * np.pi * 10 * t / time_steps)
            # Tertiary signal: low-frequency drift
            pattern += 0.3 * np.sin(2 * np.pi * 0.02 * t)
            
            X[mask, t, :] += pattern
        
        # Add realistic Gaussian noise
        X[mask] += noise_level * np.random.randn(*X[mask].shape)
    
    # Normalize: zscore normalization per channel
    mean = X.mean(axis=(0, 1), keepdims=True)
    std = X.std(axis=(0, 1), keepdims=True) + 1e-8
    X = (X - mean) / std
    
    # Verify statistics
    logger.info(f"✓ Generated data statistics:")
    logger.info(f"  Mean: {X.mean():.4f}, Std: {X.std():.4f}")
    logger.info(f"  Min: {X.min():.4f}, Max: {X.max():.4f}")
    logger.info(f"  Class distribution: {np.bincount(y)}")
    
    return X, y


def split_data(
    X: np.ndarray, 
    y: np.ndarray,
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    test_ratio: float = 0.2,
    random_state: int = 42,
    stratify: bool = True
) -> Tuple[Tuple[np.ndarray, np.ndarray], 
          Tuple[np.ndarray, np.ndarray], 
          Tuple[np.ndarray, np.ndarray]]:
    """
    Split data into train/validation/test sets with optional stratification.
    
    Ensures class distribution is maintained across all splits.
    
    Args:
        X: Data array (n_samples, ...)
        y: Labels array (n_samples,)
        train_ratio: Proportion for training (default: 0.6)
        val_ratio: Proportion for validation (default: 0.2)
        test_ratio: Proportion for testing (default: 0.2)
        random_state: Random seed (default: 42)
        stratify: Whether to stratify by class (default: True)
        
    Returns:
        Three tuples of (X_split, y_split):
        - (X_train, y_train)
        - (X_val, y_val)
        - (X_test, y_test)
    """
    np.random.seed(random_state)
    
    n_samples = len(X)
    n_train = int(n_samples * train_ratio)
    n_val = int(n_samples * val_ratio)
    
    logger.info(f"Splitting {n_samples} samples (train: {train_ratio*100:.0f}%, "
               f"val: {val_ratio*100:.0f}%, test: {test_ratio*100:.0f}%)...")
    
    if stratify:
        from sklearn.model_selection import train_test_split
        
        # First split: train and temp (val+test)
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y,
            test_size=(1 - train_ratio),
            random_state=random_state,
            stratify=y
        )
        
        # Second split: val and test
        val_size = val_ratio / (val_ratio + test_ratio)
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp,
            test_size=(1 - val_size),
            random_state=random_state,
            stratify=y_temp
        )
        
        logger.info(f"✓ Stratified split completed")
    else:
        # Simple random split
        indices = np.random.permutation(n_samples)
        train_idx = indices[:n_train]
        val_idx = indices[n_train:n_train + n_val]
        test_idx = indices[n_train + n_val:]
        
        X_train, y_train = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx], y[val_idx]
        X_test, y_test = X[test_idx], y[test_idx]
        
        logger.info(f"✓ Random split completed")
    
    # Log split statistics
    logger.info(f"  Train: {X_train.shape[0]} samples - classes: {np.bincount(y_train)}")
    logger.info(f"  Val:   {X_val.shape[0]} samples - classes: {np.bincount(y_val)}")
    logger.info(f"  Test:  {X_test.shape[0]} samples - classes: {np.bincount(y_test)}")
    
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN TRAINING PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def main(config: Dict, args) -> Dict:
    """
    Complete production-ready training pipeline.
    
    Orchestrates:
    1. Configuration validation
    2. Data preparation and splitting
    3. Model creation
    4. Training with comprehensive callbacks
    5. Evaluation and metrics calculation
    6. Result persistence and reporting
    
    Args:
        config: Complete configuration dictionary
        args: Parsed command-line arguments
        
    Returns:
        Dictionary with training results and trainer instance
    """
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("CNN-LSTM EEG CLASSIFICATION TRAINING PIPELINE")
    logger.info("=" * 80)
    logger.info("")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 1: VALIDATE CONFIGURATION
    # ─────────────────────────────────────────────────────────────────
    logger.info("[STEP 1/5] Validating configuration...")
    
    is_valid, msg = validate_training_config(config)
    if not is_valid:
        logger.error(f"Configuration validation failed:\n{msg}")
        sys.exit(1)
    
    logger.info(f"✓ Configuration: {msg}")
    
    # Override config with command-line arguments if provided
    if args.epochs:
        config['training']['epochs'] = args.epochs
        logger.info(f"✓ Epochs overridden: {args.epochs}")
    
    if args.batch_size:
        config['training']['batch_size'] = args.batch_size
        logger.info(f"✓ Batch size overridden: {args.batch_size}")
    
    logger.info("")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 2: PREPARE DATA
    # ─────────────────────────────────────────────────────────────────
    logger.info("[STEP 2/5] Preparing training data...")
    
    X, y = generate_synthetic_eeg_data(
        n_samples=args.n_samples,
        time_steps=config['model']['input_shape'][0],
        n_channels=config['model']['input_shape'][1],
        n_classes=args.n_classes,
        random_state=config['data'].get('random_state', 42)
    )
    
    data_cfg = config.get('data', {})
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = split_data(
        X, y,
        train_ratio=data_cfg.get('train_split', 0.6),
        val_ratio=data_cfg.get('val_split', 0.2),
        test_ratio=data_cfg.get('test_split', 0.2),
        random_state=data_cfg.get('random_state', 42),
        stratify=True
    )
    
    logger.info("")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 3: CREATE MODEL
    # ─────────────────────────────────────────────────────────────────
    logger.info("[STEP 3/5] Creating CNN-LSTM model...")
    
    model = create_model(config, n_classes=args.n_classes)
    total_params = model.count_params() if hasattr(model, 'count_params') else \
                   sum([int(np.prod(w.shape)) for w in model.weights])
    logger.info(f"✓ Model created with {total_params:,} total parameters")
    logger.info(f"✓ Input shape: {config['model']['input_shape']}")
    logger.info(f"✓ Output classes: {args.n_classes}")
    
    logger.info("")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 4: TRAIN MODEL
    # ─────────────────────────────────────────────────────────────────
    logger.info("[STEP 4/5] Starting model training...")
    logger.info(f"Configuration:")
    logger.info(f"  Epochs: {config['training']['epochs']}")
    logger.info(f"  Batch size: {config['training']['batch_size']}")
    logger.info(f"  Learning rate: {config['training']['learning_rate']}")
    logger.info(f"  Early stopping patience: {config['training']['early_stopping_patience']}")
    logger.info(f"  Reduce LR patience: {config['training']['reduce_lr_patience']}")
    logger.info("")
    
    # Create trainer
    trainer = ModelTrainer(config, n_classes=args.n_classes, verbose=True)
    trainer.model = model
    
    # Train model
    training_results = trainer.train(
        X_train, y_train,
        X_val, y_val,
        X_test=X_test,
        y_test=y_test,
        epochs=config['training']['epochs'],
        batch_size=config['training']['batch_size'],
        verbose=1
    )
    
    logger.info(f"\n✓ Training completed in {training_results['training_time']:.1f} seconds")
    logger.info("")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 5: EVALUATE & SAVE RESULTS
    # ─────────────────────────────────────────────────────────────────
    logger.info("[STEP 5/5] Saving training artifacts...")
    
    # Get training summary
    summary = trainer.training_summary()
    
    # Create output directories
    output_cfg = config.get('output', {})
    Path(output_cfg.get('model_dir', 'models')).mkdir(parents=True, exist_ok=True)
    Path(output_cfg.get('output_dir', 'outputs')).mkdir(parents=True, exist_ok=True)
    
    # Save training artifacts
    history_path = f"{output_cfg.get('output_dir', 'outputs')}/training_history_{trainer.timestamp}.json"
    config_path = f"{output_cfg.get('output_dir', 'outputs')}/training_config_{trainer.timestamp}.json"
    
    trainer.save_history(history_path)
    trainer.save_config(config_path)
    
    logger.info("")
    
    # ─────────────────────────────────────────────────────────────────
    # FINAL REPORT
    # ─────────────────────────────────────────────────────────────────
    logger.info("=" * 80)
    logger.info("TRAINING COMPLETION REPORT")
    logger.info("=" * 80)
    
    logger.info("\nKey Metrics:")
    logger.info(f"  Best Epoch: {summary['best_epoch']}")
    logger.info(f"  Best Validation Accuracy: {summary['best_val_accuracy']:.4f}")
    logger.info(f"  Best Validation Loss: {summary['best_val_loss']:.4f}")
    logger.info(f"  Final Validation Accuracy: {summary['final_metrics']['val_accuracy']:.4f}")
    logger.info(f"  Total Epochs Trained: {summary['n_epochs_trained']}")
    
    # Class weights used
    if summary.get('class_weights'):
        logger.info(f"\nClass Weights (for imbalance correction):")
        for cls_idx in sorted(summary['class_weights'].keys()):
            weight = summary['class_weights'][cls_idx]
            logger.info(f"  Class {cls_idx}: {weight:.4f}")
    
    logger.info("\nOutput Files:")
    logger.info(f"  Model: {training_results['model_path']}")
    logger.info(f"  History: {history_path}")
    logger.info(f"  Config: {config_path}")
    logger.info(f"  Logs: {output_cfg.get('log_dir', 'outputs/logs')}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✓ TRAINING SUCCESSFULLY COMPLETED")
    logger.info("=" * 80)
    logger.info("")
    
    return {
        'trainer': trainer,
        'summary': summary,
        'training_results': training_results,
        'model': model
    }


# ─────────────────────────────────────────────────────────────────────────────
# COMMAND-LINE INTERFACE
# ─────────────────────────────────────────────────────────────────────────────

def parse_arguments() -> argparse.Namespace:
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Production-ready CNN-LSTM EEG classification training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Train with default settings
  python train_eeg_model_production.py
  
  # Custom training parameters
  python train_eeg_model_production.py --epochs 150 --batch-size 16 --n-samples 2000
  
  # Load custom YAML config
  python train_eeg_model_production.py --config custom_config.yaml
  
  # Verbose output
  python train_eeg_model_production.py --verbose

DEFAULT SETTINGS:
  - Epochs: 100
  - Batch size: 32
  - Sample count: 1000
  - Classes: 5
  - Early stopping patience: 15 epochs
  - Learning rate reduction patience: 5 epochs
        """
    )
    
    parser.add_argument(
        '--epochs',
        type=int,
        default=None,
        help='Number of training epochs (default: from config)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help='Batch size for training (default: from config)'
    )
    
    parser.add_argument(
        '--n-samples',
        type=int,
        default=1000,
        help='Number of synthetic samples to generate (default: 1000)'
    )
    
    parser.add_argument(
        '--n-classes',
        type=int,
        default=5,
        help='Number of classification classes (default: 5 for motor imagery)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to custom configuration YAML file'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        default=False,
        help='Enable verbose console output'
    )
    
    return parser.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def load_config(config_path: Optional[str] = None) -> Dict:
    """
    Load configuration from YAML file or use defaults.
    
    Priority order:
    1. Provided config_path argument
    2. config.yaml in current directory (project root)
    3. DEFAULT_CONFIG
    
    Args:
        config_path: Optional path to custom config file
        
    Returns:
        Merged configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    
    # Determine which config file to load
    config_file = None
    if config_path and Path(config_path).exists():
        config_file = Path(config_path)
        logger.info(f"Loading custom config from: {config_file}")
    elif Path('config.yaml').exists():
        config_file = Path('config.yaml')
        logger.info(f"Loading project config from: {config_file}")
    else:
        logger.info("Using default configuration (config.yaml not found)")
        return config
    
    # Load and merge config
    try:
        with open(config_file, 'r') as f:
            file_config = yaml.safe_load(f)
        
        if file_config:
            # Deep merge loaded config with defaults
            def deep_merge(base_dict, update_dict):
                """Recursively merge update_dict into base_dict"""
                for key, value in update_dict.items():
                    if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                        deep_merge(base_dict[key], value)
                    else:
                        base_dict[key] = value
            
            deep_merge(config, file_config)
            logger.info(f"✓ Config loaded and merged with defaults\n")
        else:
            logger.warning(f"Config file {config_file} is empty, using defaults\n")
    
    except Exception as e:
        logger.warning(f"Failed to load config from {config_file}: {e}")
        logger.warning(f"Using default configuration\n")
    
    return config


if __name__ == '__main__':
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Load configuration (auto-detect config.yaml or use custom)
        config = load_config(args.config)
        
        # Override config with command-line arguments if provided
        if args.epochs:
            config['training']['epochs'] = args.epochs
        if args.batch_size:
            config['training']['batch_size'] = args.batch_size
        
        # Run training pipeline
        results = main(config, args)
        
    except KeyboardInterrupt:
        logger.info("\n\nTraining interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n\nTraining failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
