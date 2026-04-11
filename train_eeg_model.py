"""
Production-Ready CNN-LSTM EEG Classification Training Script

This complete example demonstrates:
1. Configuration management and validation
2. Synthetic data generation (or loading real data)
3. Data preprocessing and splitting
4. Model creation
5. Training with comprehensive callbacks:
   - Early stopping
   - Learning rate scheduling (ReduceLROnPlateau)
   - Class weight computation for imbalance
   - Model checkpointing (best model saving)
   - TensorBoard monitoring
   - Custom progress logging
6. Evaluation and detailed reporting
7. History and configuration persistence
8. Error handling and validation

Features:
- Production-ready with logging and error handling
- Comprehensive configuration system
- Class weight calculation for imbalanced data
- Multiple callback types for robust training
- JSON-based history and config storage
- Detailed console progress reporting
- TensorBoard integration
- Model and training artifacts persistence

Usage:
    python train_eeg_model.py
    python train_eeg_model.py --epochs 100 --batch-size 16
    python train_eeg_model.py --config custom_config.yaml

Requirements:
    - numpy, tensorflow, scikit-learn, pyyaml
    - Configured data in data/ directory or synthetic data generation

Author: BCI Interface Team
Version: 2.0
Status: Production-Ready
"""

import logging
import numpy as np
import argparse
import yaml
from pathlib import Path
from typing import Tuple, Dict
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.train import ModelTrainer, train_cnn_lstm_model, validate_training_config
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
    noise_level: float = 0.1
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate realistic synthetic EEG data for testing.
    
    Creates data with class-specific frequency patterns and realistic noise.
    
    Args:
        n_samples: Number of samples to generate
        time_steps: Length of time series per sample
        n_channels: Number of EEG channels
        n_classes: Number of classification classes
        noise_level: Standard deviation of Gaussian noise
        
    Returns:
        Tuple of (X, y):
        - X: Shape (n_samples, time_steps, n_channels), float32
        - y: Shape (n_samples,), integer class indices
    """
    logger.info(f"Generating {n_samples} synthetic EEG samples...")
    logger.info(f"  Shape: ({n_samples}, {time_steps}, {n_channels})")
    logger.info(f"  Classes: {n_classes}")
    
    # Initialize data
    X = np.random.randn(n_samples, time_steps, n_channels).astype(np.float32)
    y = np.random.randint(0, n_classes, n_samples)
    
    # Add class-specific patterns
    for class_idx in range(n_classes):
        mask = y == class_idx
        n_class_samples = np.sum(mask)
        
        # Add frequency-based patterns for each class
        base_freq = 0.01 + class_idx * 0.01  # Different frequency per class
        
        for t in range(time_steps):
            # Sine wave with class-specific frequency
            pattern = 0.8 * np.sin(2 * np.pi * base_freq * t / 10)
            # Alpha activity around 10 Hz
            pattern += 0.5 * np.sin(2 * np.pi * 10 * t / time_steps)
            X[mask, t, :] += pattern
        
        # Add Gaussian noise
        X[mask] += noise_level * np.random.randn(*X[mask].shape)
    
    # Normalize data
    X = (X - X.mean(axis=(0, 1), keepdims=True)) / (X.std(axis=(0, 1), keepdims=True) + 1e-8)
    
    logger.info(f"✓ Data generated - X: {X.shape}, y: {y.shape}")
    logger.info(f"✓ Class distribution: {np.bincount(y)}")
    logger.info(f"✓ Data range: [{X.min():.4f}, {X.max():.4f}]")
    
    return X, y


def split_data(
    X: np.ndarray, 
    y: np.ndarray,
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    test_ratio: float = 0.2,
    random_state: int = 42,
    stratify: bool = True
) -> Tuple[Tuple, Tuple, Tuple]:
    """
    Split data into train/validation/test sets.
    
    Performs optional stratification to maintain class distribution.
    
    Args:
        X: Data array (n_samples, ...)
        y: Labels array (n_samples,)
        train_ratio: Fraction for training
        val_ratio: Fraction for validation
        test_ratio: Fraction for testing
        random_state: Random seed
        stratify: Whether to stratify by class
        
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
    else:
        # Simple random split
        indices = np.random.permutation(n_samples)
        train_idx = indices[:n_train]
        val_idx = indices[n_train:n_train + n_val]
        test_idx = indices[n_train + n_val:]
        
        X_train, y_train = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx], y[val_idx]
        X_test, y_test = X[test_idx], y[test_idx]
    
    logger.info(f"✓ Data split:")
    logger.info(f"  Train: {X_train.shape[0]} samples ({train_ratio*100:.0f}%)")
    logger.info(f"  Val:   {X_val.shape[0]} samples ({val_ratio*100:.0f}%)")
    logger.info(f"  Test:  {X_test.shape[0]} samples ({test_ratio*100:.0f}%)")
    
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN TRAINING PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def main(config: Dict, args):
    """
    Complete production-ready training pipeline.
    
    Orchestrates:
    1. Data preparation
    2. Model creation
    3. Training with callbacks
    4. Evaluation
    5. Result persistence
    """
    
    logger.info("=" * 80)
    logger.info("CNN-LSTM EEG CLASSIFICATION TRAINING")
    logger.info("=" * 80)
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 1: VALIDATE CONFIGURATION
    # ─────────────────────────────────────────────────────────────────
    logger.info("\n[STEP 1/5] Validating configuration...")
    
    is_valid, msg = validate_training_config(config)
    if not is_valid:
        logger.error(f"Configuration validation failed:\n{msg}")
        sys.exit(1)
    
    logger.info(f"✓ {msg}")
    
    # Override config with command-line args if provided
    if args.epochs:
        config['training']['epochs'] = args.epochs
        logger.info(f"✓ Epochs overridden: {args.epochs}")
    
    if args.batch_size:
        config['training']['batch_size'] = args.batch_size
        logger.info(f"✓ Batch size overridden: {args.batch_size}")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 2: PREPARE DATA
    # ─────────────────────────────────────────────────────────────────
    logger.info("\n[STEP 2/5] Preparing training data...")
    
    X, y = generate_synthetic_eeg_data(
        n_samples=args.n_samples,
        time_steps=config['model']['input_shape'][0],
        n_channels=config['model']['input_shape'][1],
        n_classes=args.n_classes
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
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 3: CREATE MODEL
    # ─────────────────────────────────────────────────────────────────
    logger.info("\n[STEP 3/5] Creating model...")
    
    model = create_model(config, n_classes=args.n_classes)
    total_params = model.count_params() if hasattr(model, 'count_params') else \
                   sum([int(np.prod(w.shape)) for w in model.weights])
    logger.info(f"✓ Model created with {total_params:,} parameters")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 4: TRAIN MODEL
    # ─────────────────────────────────────────────────────────────────
    logger.info("\n[STEP 4/5] Training model...")
    logger.info(f"  Epochs: {config['training']['epochs']}")
    logger.info(f"  Batch size: {config['training']['batch_size']}")
    logger.info(f"  Early stopping patience: {config['training']['early_stopping_patience']}")
    logger.info(f"  Learning rate: {config['training']['learning_rate']}")
    logger.info("")
    
    # Create trainer
    trainer = ModelTrainer(config, n_classes=args.n_classes, verbose=True)
    trainer.model = model
    
    # Train
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
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 5: EVALUATE & SAVE RESULTS
    # ─────────────────────────────────────────────────────────────────
    logger.info("\n[STEP 5/5] Saving results...")
    
    # Get summary
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
    
    # ─────────────────────────────────────────────────────────────────
    # FINAL REPORT
    # ─────────────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 80)
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
        logger.info(f"\nClass Weights (imbalance correction):")
        for cls_idx in sorted(summary['class_weights'].keys()):
            weight = summary['class_weights'][cls_idx]
            logger.info(f"  Class {cls_idx}: {weight:.4f}")
    
    logger.info("\nOutput Files:")
    logger.info(f"  Model: {training_results['model_path']}")
    logger.info(f"  History: {history_path}")
    logger.info(f"  Config: {config_path}")
    logger.info(f"  Logs: {output_cfg.get('log_dir', 'outputs/logs')}")
    
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING SUCCESSFULLY COMPLETED")
    logger.info("=" * 80)
    
    return {
        'trainer': trainer,
        'summary': summary,
        'training_results': training_results
    }


# ─────────────────────────────────────────────────────────────────────────────
# COMMAND-LINE INTERFACE
# ─────────────────────────────────────────────────────────────────────────────

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Production-ready CNN-LSTM EEG classification training script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train with defaults
  python train_eeg_model.py
  
  # Train with custom parameters
  python train_eeg_model.py --epochs 150 --batch-size 16 --n-samples 2000
  
  # Load custom config
  python train_eeg_model.py --config custom_config.yaml
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
        help='Number of classification classes (default: 5)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to custom config YAML file'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        default=False,
        help='Verbose output'
    )
    
    return parser.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args = parse_arguments()
    
    # Load configuration
    config = DEFAULT_CONFIG.copy()
    
    if args.config and Path(args.config).exists():
        logger.info(f"Loading custom config from {args.config}...")
        with open(args.config, 'r') as f:
            custom_config = yaml.safe_load(f)
            # Deep merge with defaults
            for key in custom_config:
                if isinstance(custom_config[key], dict) and key in config:
                    config[key].update(custom_config[key])
                else:
                    config[key] = custom_config[key]
        logger.info(f"✓ Custom config loaded")
    
    # Run training
    try:
        results = main(config, args)
    except KeyboardInterrupt:
        logger.info("\n\nTraining interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n\nTraining failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    
    # Normalize
    X = (X - X.mean(axis=(0, 1))) / X.std(axis=(0, 1))
    
    logger.info(f"✓ Generated X shape: {X.shape}, y shape: {y.shape}")
    logger.info(f"✓ Class distribution: {np.bincount(y)}")
    
    return X, y


def split_data(X: np.ndarray, y: np.ndarray,
               train_ratio: float = 0.6,
               val_ratio: float = 0.2,
               test_ratio: float = 0.2,
               random_state: int = 42) -> Tuple:
    """
    Split data into train/val/test sets with stratification.
    
    Args:
        X: Data array
        y: Labels array
        train_ratio: Proportion for training
        val_ratio: Proportion for validation
        test_ratio: Proportion for testing
        random_state: Random seed
        
    Returns:
        Tuple of (X_train, y_train), (X_val, y_val), (X_test, y_test)
    """
    np.random.seed(random_state)
    
    n_samples = len(X)
    n_train = int(n_samples * train_ratio)
    n_val = int(n_samples * val_ratio)
    
    indices = np.random.permutation(n_samples)
    
    train_idx = indices[:n_train]
    val_idx = indices[n_train:n_train + n_val]
    test_idx = indices[n_train + n_val:]
    
    return (X[train_idx], y[train_idx]), \
           (X[val_idx], y[val_idx]), \
           (X[test_idx], y[test_idx])


# ─────────────────────────────────────────────────────────────────────────────
# MAIN TRAINING FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def main():
    """
    Complete training pipeline for CNN-LSTM EEG classification.
    """
    
    logger.info("=" * 80)
    logger.info("CNN-LSTM EEG CLASSIFICATION TRAINING EXAMPLE")
    logger.info("=" * 80)
    
    # ─────────────────────────────────────────────────────────────────
    # 1. DATA PREPARATION
    # ─────────────────────────────────────────────────────────────────
    logger.info("\n[STEP 1] Preparing data...")
    
    # Generate synthetic EEG data
    X, y = generate_synthetic_eeg_data(
        n_samples=1000,
        time_steps=320,
        n_channels=64,
        n_classes=5
    )
    
    # Split into train/val/test
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = split_data(X, y)
    
    logger.info(f"Training set: {X_train.shape}, {len(y_train)} samples")
    logger.info(f"Validation set: {X_val.shape}, {len(y_val)} samples")
    logger.info(f"Test set: {X_test.shape}, {len(y_test)} samples")
    
    # ─────────────────────────────────────────────────────────────────
    # 2. MODEL CREATION
    # ─────────────────────────────────────────────────────────────────
    logger.info("\n[STEP 2] Creating model...")
    
    model = create_model(CONFIG, n_classes=5)
    logger.info(f"✓ Model created with {model.count_params():,.0f} parameters")
    
    # ─────────────────────────────────────────────────────────────────
    # 3. TRAINING
    # ─────────────────────────────────────────────────────────────────
    logger.info("\n[STEP 3] Training model...")
    
    # Create trainer
    trainer = ModelTrainer(CONFIG, n_classes=5)
    trainer.model = model
    
    # Train
    results = trainer.train(
        X_train, y_train,
        X_val, y_val,
        X_test=X_test,
        y_test=y_test,
        epochs=CONFIG['training']['epochs'],
        batch_size=CONFIG['training']['batch_size'],
        verbose=1
    )
    
    logger.info(f"\n✓ Training completed in {results['training_time']:.1f} seconds")
    
    # ─────────────────────────────────────────────────────────────────
    # 4. EVALUATION & REPORTING
    # ─────────────────────────────────────────────────────────────────
    logger.info("\n[STEP 4] Evaluating results...")
    
    # Get training summary
    summary = trainer.training_summary()
    
    logger.info(f"\nBest validation accuracy: {summary['best_val_accuracy']:.4f}")
    logger.info(f"Best epoch: {summary['best_epoch']}")
    
    # ─────────────────────────────────────────────────────────────────
    # 5. SAVE RESULTS
    # ─────────────────────────────────────────────────────────────────
    logger.info("\n[STEP 5] Saving results...")
    
    # Ensure output directories exist
    Path('models').mkdir(exist_ok=True)
    Path('outputs').mkdir(exist_ok=True)
    
    # Save history
    history_path = 'outputs/training_history.json'
    trainer.save_history(history_path)
    
    # Save model (already saved by checkpoint callback)
    model_path = CONFIG['output']['model_path']
    logger.info(f"✓ Best model saved to: {model_path}")
    
    # ─────────────────────────────────────────────────────────────────
    # 6. SUMMARY REPORT
    # ─────────────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING PIPELINE COMPLETED")
    logger.info("=" * 80)
    
    logger.info("\nFiles Generated:")
    logger.info(f"  - Model: {model_path}")
    logger.info(f"  - History: {history_path}")
    logger.info(f"  - Logs: {CONFIG['output']['log_dir']}")
    
    logger.info("\nTraining Metrics:")
    logger.info(f"  - Best Epoch: {summary['best_epoch']}")
    logger.info(f"  - Best Val Accuracy: {summary['best_val_accuracy']:.4f}")
    logger.info(f"  - Best Val Loss: {summary['best_val_loss']:.4f}")
    logger.info(f"  - Final Val Accuracy: {summary['final_metrics']['val_accuracy']:.4f}")
    logger.info(f"  - Total Epochs: {summary['n_epochs_trained']}")
    
    logger.info("\nClass Weights Used:")
    for class_idx, weight in summary['class_weights'].items():
        logger.info(f"  - Class {class_idx}: {weight:.4f}")
    
    logger.info("\n✓ Training pipeline completed successfully!")
    logger.info("=" * 80)
    
    return trainer, results, summary


if __name__ == '__main__':
    trainer, results, summary = main()
