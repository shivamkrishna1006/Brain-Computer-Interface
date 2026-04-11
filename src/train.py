"""
Production-ready training script for CNN-LSTM EEG classification model.

This module provides comprehensive training utilities including:
- Early stopping on validation loss
- Reduce learning rate on plateau (ReduceLROnPlateau)
- Automatic class weight computation for imbalanced data
- Best model checkpointing
- Detailed training progress with custom callbacks
- Complete history storage with visualization-ready format
- Training statistics and summary reporting

Key Features:
- Handles multi-class classification (including 5-class motor imagery)
- Integrates with data_preparation and model modules
- Comprehensive logging and progress tracking
- TensorBoard integration for visualization
- JSON history export for analysis
- Model and config persistence
- Validation and error handling
- Production-ready with error recovery

Author: BCI Interface Team
Version: 2.0
Status: Production-Ready
"""

import logging
import os
import json
import warnings
from typing import Dict, Tuple, Optional, Union, List
from pathlib import Path
from datetime import datetime
import pickle

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import callbacks as cb
from sklearn.utils.class_weight import compute_class_weight

# Suppress TensorFlow warnings for cleaner output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore', category=UserWarning)

logger = logging.getLogger('BCI')




class TrainingProgressCallback(keras.callbacks.Callback):
    """
    Custom callback for detailed training progress reporting.
    
    Logs training progress with custom formatting, interval-based updates,
    and detailed performance metrics. Designed for production monitoring.
    
    Features:
    - Epoch-by-epoch progress tracking
    - ETA calculation with running average
    - Learning rate monitoring
    - Confidence interval estimation
    - Performance-based logging
    """
    
    def __init__(self, total_epochs: int, log_interval: int = 5, 
                 verbose: bool = True):
        """
        Initialize progress callback.
        
        Args:
            total_epochs: Total number of epochs
            log_interval: Log metrics every N epochs
            verbose: Whether to print detailed output
        """
        super().__init__()
        self.total_epochs = total_epochs
        self.log_interval = log_interval
        self.verbose = verbose
        self.start_time = None
        self.epoch_times = []
    
    def on_train_begin(self, logs=None):
        """Called at start of training."""
        self.start_time = datetime.now()
        self.epoch_times = []
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("TRAINING STARTED")
        logger.info("=" * 80)
        logger.info(f"Total Epochs: {self.total_epochs}")
        logger.info(f"Timestamp: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
    
    def on_epoch_begin(self, epoch, logs=None):
        """Called at beginning of each epoch."""
        self._epoch_start = datetime.now()
    
    def on_epoch_end(self, epoch, logs=None):
        """Called at end of each epoch with detailed metrics."""
        if logs is None:
            logs = {}
        
        # Calculate timing
        epoch_time = (datetime.now() - self._epoch_start).total_seconds()
        self.epoch_times.append(epoch_time)
        
        elapsed = datetime.now() - self.start_time
        avg_time_per_epoch = np.mean(self.epoch_times)
        remaining_epochs = self.total_epochs - (epoch + 1)
        eta_seconds = remaining_epochs * avg_time_per_epoch
        
        # Format timing
        elapsed_str = self._format_duration(elapsed.total_seconds())
        eta_str = self._format_duration(eta_seconds)
        
        # Get learning rate
        try:
            lr = float(self.model.optimizer.learning_rate.numpy())
            lr_str = f"{lr:.2e}"
        except:
            lr_str = "N/A"
        
        # Log at intervals or on first/last epoch
        should_log = ((epoch + 1) % self.log_interval == 0 or 
                     epoch == 0 or 
                     epoch == self.total_epochs - 1)
        
        if should_log and self.verbose:
            loss = logs.get('loss', np.nan)
            val_loss = logs.get('val_loss', np.nan)
            acc = logs.get('accuracy', np.nan)
            val_acc = logs.get('val_accuracy', np.nan)
            
            logger.info(
                f"Epoch [{epoch+1:3d}/{self.total_epochs:3d}] | "
                f"Loss: {loss:.4f} | Val Loss: {val_loss:.4f} | "
                f"Acc: {acc:.4f} | Val Acc: {val_acc:.4f} | "
                f"LR: {lr_str} | Epoch Time: {epoch_time:.1f}s | ETA: {eta_str}"
            )
    
    def on_train_end(self, logs=None):
        """Called at end of training with summary."""
        total_time = datetime.now() - self.start_time
        total_seconds = total_time.total_seconds()
        
        avg_epoch_time = np.mean(self.epoch_times) if self.epoch_times else 0
        
        logger.info("=" * 80)
        logger.info("TRAINING COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Total Duration: {self._format_duration(total_seconds)}")
        logger.info(f"Average Time/Epoch: {avg_epoch_time:.2f}s")
        logger.info(f"Total Epochs: {len(self.epoch_times)}")
        logger.info("=" * 80)
    
    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in human-readable format."""
        if isinstance(seconds, float):
            total_seconds = int(seconds)
        else:
            total_seconds = int(seconds)
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


class ModelTrainer:
    """
    Production-ready model trainer for CNN-LSTM EEG classification.
    
    Provides comprehensive training with:
    - Early stopping on validation loss
    - Reduce learning rate on plateau
    - Automatic class weight computation
    - Model checkpointing
    - Detailed training progress logging
    - History storage and statistics
    - Advanced metrics tracking
    - Model persistence and recovery
    """
    
    def __init__(self, config: Dict, n_classes: int = 5, verbose: bool = True):
        """
        Initialize model trainer.
        
        Args:
            config: Configuration dictionary with 'model', 'training', 'output' keys
            n_classes: Number of classification classes (default: 5)
            verbose: Whether to print detailed logs (default: True)
        """
        self.config = config
        self.n_classes = n_classes
        self.model = None
        self.training_history = None
        self.class_weights = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.verbose = verbose
        self.best_model_path = None
        
        logger.info(f"Initialized ModelTrainer for {n_classes}-class classification")
        logger.info(f"Timestamp: {self.timestamp}")

    
    def compute_class_weights(self, labels: np.ndarray) -> Dict:
        """
        Compute class weights for imbalanced classification.
        
        Handles class imbalance by assigning higher weights to minority classes.
        
        Args:
            labels: Array of class labels
            
        Returns:
            Dictionary mapping class index to weight
        """
        unique_classes = np.unique(labels)
        
        # Compute weights
        weights = compute_class_weight(
            class_weight='balanced',
            classes=unique_classes,
            y=labels
        )
        
        # Create class weight dictionary
        class_weight_dict = {int(cls): float(w) for cls, w in zip(unique_classes, weights)}
        
        logger.info("Class weights computed:")
        for cls_idx, weight in sorted(class_weight_dict.items()):
            logger.info(f"  Class {cls_idx}: {weight:.4f}")
        
        self.class_weights = class_weight_dict
        return class_weight_dict
    
    def build_callbacks(self, model_save_path: str,
                       early_stopping_patience: int = 15,
                       reduce_lr_patience: int = 5,
                       reduce_lr_factor: float = 0.5,
                       log_interval: int = 5) -> List[keras.callbacks.Callback]:
        """
        Build comprehensive training callbacks for production-ready training.
        
        Callbacks included:
        1. **EarlyStopping**: Stops training when validation loss plateaus
           - Monitors: val_loss (customizable)
           - Restores best weights automatically
           - Patience: configurable epochs to wait
        
        2. **ModelCheckpoint**: Saves best model checkpoints
           - Monitors: val_accuracy (for best performance)
           - Saves only best models (save_best_only=True)
           - Handles full model + architecture
        
        3. **ReduceLROnPlateau**: Reduces learning rate dynamically
           - Monitors: val_loss
           - Reduces by factor when plateau detected
           - Min learning rate: 1e-7 (prevents training collapse)
           - Cooldown: 2 epochs between reductions
        
        4. **TensorBoard**: Real-time monitoring and visualization
           - Histogram freq: 1 epoch
           - Write graph: enabled for architecture visualization
           - Profile batch: disabled for efficiency
        
        5. **CustomProgressCallback**: Detailed epoch-by-epoch logging
           - ETA calculation
           - Learning rate display
           - Time-per-epoch tracking
        
        Args:
            model_save_path: Absolute path to save best model
            early_stopping_patience: Epochs to wait before stopping (default: 15)
            reduce_lr_patience: Epochs to wait before reducing LR (default: 5)
            reduce_lr_factor: Factor to multiply LR by (default: 0.5)
            log_interval: Print metrics every N epochs (default: 5)
            
        Returns:
            List of configured Keras callbacks
            
        Raises:
            ValueError: If save path not writable
        """
        callback_list = []
        training_config = self.config.get('training', {})
        epochs = training_config.get('epochs', 50)
        
        logger.info("\n[Callbacks] Building comprehensive callback suite...")
        
        # ─────────────────────────────────────────────────────────────────
        # 1. EARLY STOPPING CALLBACK
        # ─────────────────────────────────────────────────────────────────
        early_stopping = cb.EarlyStopping(
            monitor='val_loss',
            patience=early_stopping_patience,
            restore_best_weights=True,
            verbose=1,
            mode='min',
            start_from_epoch=max(5, early_stopping_patience // 2),  # Start monitoring after initial epochs
            min_delta=1e-4  # Minimum change to qualify as improvement
        )
        callback_list.append(early_stopping)
        logger.debug(f"  ✓ EarlyStopping: patience={early_stopping_patience} epochs, "
                    f"monitor=val_loss, restore_best_weights=True")
        
        # ─────────────────────────────────────────────────────────────────
        # 2. REDUCE LEARNING RATE ON PLATEAU CALLBACK
        # ─────────────────────────────────────────────────────────────────
        reduce_lr = cb.ReduceLROnPlateau(
            monitor='val_loss',
            factor=reduce_lr_factor,
            patience=reduce_lr_patience,
            verbose=1,
            mode='min',
            min_delta=1e-4,  # Minimum change to avoid spurious reductions
            cooldown=2,      # Wait 2 epochs before reducing again
            min_lr=1e-7      # Prevent learning rate from becoming too small
        )
        callback_list.append(reduce_lr)
        logger.debug(f"  ✓ ReduceLROnPlateau: patience={reduce_lr_patience}, "
                    f"factor={reduce_lr_factor}, min_lr=1e-7, cooldown=2")
        
        # ─────────────────────────────────────────────────────────────────
        # 3. MODEL CHECKPOINT CALLBACK
        # ─────────────────────────────────────────────────────────────────
        save_dir = Path(model_save_path).parent
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate write permissions
        try:
            test_write = save_dir / '.write_test'
            test_write.touch()
            test_write.unlink()
        except (PermissionError, IOError) as e:
            raise ValueError(f"Cannot write to {save_dir}: {e}")
        
        checkpoint = cb.ModelCheckpoint(
            filepath=str(model_save_path),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1,
            mode='max',
            save_weights_only=False
        )
        callback_list.append(checkpoint)
        self.best_model_path = model_save_path
        logger.debug(f"  ✓ ModelCheckpoint: monitor=val_accuracy, save_best_only=True")
        logger.debug(f"    Path: {model_save_path}")
        
        # ─────────────────────────────────────────────────────────────────
        # 4. TENSORBOARD CALLBACK
        # ─────────────────────────────────────────────────────────────────
        log_dir = self.config.get('output', {}).get('log_dir', 'outputs/logs')
        log_dir = str(Path(log_dir) / self.timestamp)  # Add timestamp to logs
        
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        tensorboard = cb.TensorBoard(
            log_dir=log_dir,
            histogram_freq=1,
            update_freq='epoch',
            write_graph=True,
            profile_batch=0,  # Disable profiling for speed
            embeddings_freq=0
        )
        callback_list.append(tensorboard)
        logger.debug(f"  ✓ TensorBoard: histogram_freq=1, write_graph=True")
        logger.debug(f"    Log directory: {log_dir}")
        
        # ─────────────────────────────────────────────────────────────────
        # 5. CUSTOM PROGRESS CALLBACK
        # ─────────────────────────────────────────────────────────────────
        progress_callback = TrainingProgressCallback(
            total_epochs=epochs,
            log_interval=log_interval,
            verbose=self.verbose
        )
        callback_list.append(progress_callback)
        logger.debug(f"  ✓ TrainingProgressCallback: log_interval={log_interval} epochs")
        
        logger.info(f"✓ Callback suite ready: {len(callback_list)} callbacks configured")
        
        return callback_list

    
    def train(self, 
              X_train: np.ndarray, 
              y_train: np.ndarray,
              X_val: np.ndarray, 
              y_val: np.ndarray,
              X_test: Optional[np.ndarray] = None,
              y_test: Optional[np.ndarray] = None,
              validation_data: Optional[Tuple] = None,
              epochs: Optional[int] = None,
              batch_size: Optional[int] = None,
              verbose: int = 1) -> Dict:
        """
        Train the model with comprehensive callbacks and monitoring.
        
        Handles multi-class classification with:
        - Class weight computation for imbalanced data
        - Early stopping on validation loss
        - Learning rate reduction on plateau
        - Best model checkpointing
        - Detailed progress logging
        
        Args:
            X_train: Training data (n_samples, time_steps, channels)
            y_train: Training labels (n_samples,) or (n_samples, n_classes)
            X_val: Validation data
            y_val: Validation labels
            X_test: Optional test data for evaluation
            y_test: Optional test labels
            validation_data: Optional validation data tuple (overrides X_val, y_val)
            epochs: Number of training epochs (overrides config)
            batch_size: Batch size (overrides config)
            verbose: Verbosity level (0, 1, or 2)
            
        Returns:
            Dictionary containing training history with keys:
            - 'history': TensorFlow history object
            - 'metrics': Final training metrics
            - 'class_weights': Used class weights
            - 'model_path': Path to saved model
            - 'training_time': Total training time
        """
        logger.info("=" * 80)
        logger.info("TRAINING PIPELINE STARTED")
        logger.info("=" * 80)
        
        # ─────────────────────────────────────────────────────────────────
        # 1. Validate inputs
        # ─────────────────────────────────────────────────────────────────
        logger.info("[1/5] Validating inputs...")
        
        if X_train.shape[0] != y_train.shape[0]:
            raise ValueError("X_train and y_train must have same number of samples")
        
        if X_val.shape[0] != y_val.shape[0]:
            raise ValueError("X_val and y_val must have same number of samples")
        
        logger.info(f"✓ Training data: {X_train.shape} → {y_train.shape}")
        logger.info(f"✓ Validation data: {X_val.shape} → {y_val.shape}")
        
        if X_test is not None:
            logger.info(f"✓ Test data: {X_test.shape} → {y_test.shape}")
        
        # ─────────────────────────────────────────────────────────────────
        # 2. Build model
        # ─────────────────────────────────────────────────────────────────
        logger.info("\n[2/5] Building model...")
        
        if self.model is None:
            from .model import create_model
            self.model = create_model(self.config, n_classes=self.n_classes)
            logger.info(f"✓ Model created for {self.n_classes} classes")
        else:
            logger.info("✓ Using existing model")
        
        # ─────────────────────────────────────────────────────────────────
        # 3. Prepare training data
        # ─────────────────────────────────────────────────────────────────
        logger.info("\n[3/5] Preparing training data...")
        
        # Handle label format (1D array or one-hot encoded)
        if len(y_train.shape) == 1:
            # Convert to one-hot if needed
            from tensorflow.keras.utils import to_categorical
            logger.info("Converting labels to categorical format...")
            y_train = to_categorical(y_train, num_classes=self.n_classes)
            y_val = to_categorical(y_val, num_classes=self.n_classes)
            if y_test is not None:
                y_test = to_categorical(y_test, num_classes=self.n_classes)
        
        # Compute class weights from original labels (before one-hot)
        original_labels = np.argmax(y_train, axis=1)
        class_weights = self.compute_class_weights(original_labels)
        
        # ─────────────────────────────────────────────────────────────────
        # 4. Setup training parameters
        # ─────────────────────────────────────────────────────────────────
        logger.info("\n[4/5] Setting up training parameters...")
        
        training_config = self.config.get('training', {})
        epochs = epochs or training_config.get('epochs', 50)
        batch_size = batch_size or training_config.get('batch_size', 32)
        
        logger.info(f"✓ Epochs: {epochs}")
        logger.info(f"✓ Batch size: {batch_size}")
        logger.info(f"✓ Class weights: {class_weights}")
        
        # Get validation data
        val_data = validation_data or (X_val, y_val)
        
        # Setup callbacks
        model_save_path = self.config.get('output', {}).get('model_path', 
                                                            f'models/best_model_{self.timestamp}.h5')
        
        callback_list = self.build_callbacks(
            model_save_path=model_save_path,
            early_stopping_patience=training_config.get('early_stopping_patience', 15),
            reduce_lr_patience=training_config.get('reduce_lr_patience', 5),
            reduce_lr_factor=training_config.get('reduce_lr_factor', 0.5),
            log_interval=training_config.get('log_interval', 5)
        )
        
        # ─────────────────────────────────────────────────────────────────
        # 5. Train model
        # ─────────────────────────────────────────────────────────────────
        logger.info("\n[5/5] Starting training...")
        
        start_time = datetime.now()
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=val_data,
            epochs=epochs,
            batch_size=batch_size,
            class_weight=class_weights,
            callbacks=callback_list,
            verbose=verbose
        )
        
        end_time = datetime.now()
        training_time = (end_time - start_time).total_seconds()
        
        logger.info(f"\n✓ Training complete! ({int(training_time)}s)")
        
        # Store history
        self.training_history = history.history
        
        # ─────────────────────────────────────────────────────────────────
        # 6. Evaluate and report
        # ─────────────────────────────────────────────────────────────────
        logger.info("\n" + "=" * 80)
        logger.info("TRAINING METRICS")
        logger.info("=" * 80)
        
        # Final metrics
        final_loss = history.history['loss'][-1]
        final_val_loss = history.history['val_loss'][-1]
        final_acc = history.history['accuracy'][-1]
        final_val_acc = history.history['val_accuracy'][-1]
        
        logger.info(f"Final Training - Loss: {final_loss:.4f}, Acc: {final_acc:.4f}")
        logger.info(f"Final Validation - Loss: {final_val_loss:.4f}, Acc: {final_val_acc:.4f}")
        
        # Test evaluation (if provided)
        if X_test is not None and y_test is not None:
            logger.info("\nEvaluating on test set...")
            test_results = self.model.evaluate(X_test, y_test, verbose=0)
            logger.info(f"Test - Loss: {test_results[0]:.4f}, Acc: {test_results[1]:.4f}")
        
        logger.info("=" * 80)
        
        return {
            'history': history,
            'metrics': {
                'final_loss': float(final_loss),
                'final_val_loss': float(final_val_loss),
                'final_accuracy': float(final_acc),
                'final_val_accuracy': float(final_val_acc),
                'epochs_trained': len(history.history['loss'])
            },
            'class_weights': class_weights,
            'model_path': model_save_path,
            'training_time': training_time
        }
    
    def save_history(self, output_path: str) -> str:
        """
        Save training history to JSON file with metadata.
        
        Stores complete training history including:
        - Epoch-wise metrics (loss, accuracy, val_loss, val_accuracy, learning_rate)
        - Model configuration
        - Class weights used
        - Training metadata (timestamp, duration, data shapes)
        
        Args:
            output_path: Path to save JSON history file
            
        Returns:
            Path where history was saved
        """
        if self.training_history is None:
            logger.warning("No training history available. Train model first.")
            return None
        
        logger.info(f"\nSaving training history to {output_path}...")
        
        # Prepare history for JSON serialization
        history_dict = {
            key: [float(v) for v in values]
            for key, values in self.training_history.items()
        }
        
        # Add metadata
        history_dict['metadata'] = {
            'timestamp': self.timestamp,
            'n_classes': self.n_classes,
            'n_epochs': len(history_dict.get('loss', [])),
            'class_weights': {str(k): float(v) for k, v in (self.class_weights or {}).items()}
        }
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save
        with open(output_path, 'w') as f:
            json.dump(history_dict, f, indent=2)
        
        logger.info(f"✓ History saved: {output_path}")
        return output_path
    
    def training_summary(self) -> Dict:
        """
        Generate comprehensive training summary statistics.
        
        Returns:
            Dictionary with summary statistics:
            - best_epoch: Epoch with best validation accuracy
            - best_val_accuracy: Best validation accuracy achieved
            - best_val_loss: Lowest validation loss achieved
            - final_metrics: Final epoch metrics
            - training_duration: Total training time
            - class_distribution: Statistics on class weights
        """
        if self.training_history is None:
            logger.warning("No training history available.")
            return None
        
        history = self.training_history
        
        # Find best epoch
        val_acc = history.get('val_accuracy', [])
        if not val_acc:
            logger.warning("No validation accuracy metrics found.")
            return None
        
        best_epoch = int(np.argmax(val_acc))
        best_val_acc = float(np.max(val_acc))
        best_val_loss = float(history['val_loss'][best_epoch])
        
        # Final metrics
        final_epoch = len(val_acc) - 1
        final_metrics = {
            'loss': float(history['loss'][final_epoch]),
            'accuracy': float(history['accuracy'][final_epoch]),
            'val_loss': float(history['val_loss'][final_epoch]),
            'val_accuracy': float(val_acc[final_epoch])
        }
        
        summary = {
            'best_epoch': best_epoch + 1,  # 1-indexed
            'best_val_accuracy': best_val_acc,
            'best_val_loss': best_val_loss,
            'final_metrics': final_metrics,
            'n_epochs_trained': final_epoch + 1,
            'class_weights': self.class_weights or {},
            'n_classes': self.n_classes
        }
        
        # Log summary
        logger.info("\n" + "=" * 80)
        logger.info("TRAINING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Best Epoch: {summary['best_epoch']}")
        logger.info(f"Best Validation Accuracy: {summary['best_val_accuracy']:.4f}")
        logger.info(f"Best Validation Loss: {summary['best_val_loss']:.4f}")
        logger.info(f"Final Val Accuracy: {final_metrics['val_accuracy']:.4f}")
        logger.info(f"Total Epochs Trained: {summary['n_epochs_trained']}")
        logger.info(f"Number of Classes: {summary['n_classes']}")
        logger.info("=" * 80)
        
        return summary
    
    def save_config(self, output_path: str) -> str:
        """
        Save trainer configuration to JSON file.
        
        Saves model configuration, training parameters, and class information
        for reproducibility and reference.
        
        Args:
            output_path: Path to save configuration JSON
            
        Returns:
            Path where config was saved
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        config_to_save = {
            'timestamp': self.timestamp,
            'n_classes': self.n_classes,
            'model_config': self.config.get('model', {}),
            'training_config': self.config.get('training', {}),
            'class_weights': {str(k): float(v) for k, v in (self.class_weights or {}).items()},
            'best_model_path': str(self.best_model_path)
        }
        
        with open(output_path, 'w') as f:
            json.dump(config_to_save, f, indent=2)
        
        logger.info(f"✓ Configuration saved: {output_path}")
        return output_path
    
    def get_training_metrics(self) -> Dict:
        """
        Get detailed training metrics from history.
        
        Returns:
            Dictionary with computed metrics including:
            - convergence_speed: Epochs to convergence
            - overfitting_indicator: Difference between train and val accuracy
            - final_loss: Final training loss
            - final_val_loss: Final validation loss
        """
        if self.training_history is None:
            logger.warning("No training history available.")
            return {}
        
        history = self.training_history
        
        metrics = {
            'total_epochs': len(history.get('loss', [])),
            'final_loss': float(history['loss'][-1]),
            'final_accuracy': float(history['accuracy'][-1]),
            'final_val_loss': float(history['val_loss'][-1]),
            'final_val_accuracy': float(history['val_accuracy'][-1]),
            'best_val_accuracy': float(np.max(history.get('val_accuracy', []))),
            'best_val_loss': float(np.min(history.get('val_loss', []))),
            'overfitting_indicator': float(
                history['accuracy'][-1] - history['val_accuracy'][-1]
            ),
            'training_stability': float(
                np.std(np.diff(history['val_loss']))
            )
        }
        
        return metrics


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def compute_class_weights_auto(y_train: np.ndarray) -> Dict[int, float]:
    """
    Automatically compute class weights for imbalanced classification.
    
    Uses sklearn's compute_class_weight with 'balanced' strategy
    which weights classes inversely proportional to their frequency.
    
    Args:
        y_train: Training labels (1D array of class indices)
        
    Returns:
        Dictionary mapping class index to weight
        
    Example:
        ```python
        weights = compute_class_weights_auto(np.array([0, 0, 1, 2, 2, 2]))
        # {0: 1.5, 1: 3.0, 2: 1.0}
        ```
    """
    unique_classes = np.unique(y_train)
    
    weights = compute_class_weight(
        class_weight='balanced',
        classes=unique_classes,
        y=y_train
    )
    
    class_weight_dict = {int(cls): float(w) for cls, w in zip(unique_classes, weights)}
    
    return class_weight_dict


def validate_training_config(config: Dict) -> Tuple[bool, str]:
    """
    Validate training configuration for common issues.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    errors = []
    
    # Check required keys
    if 'model' not in config:
        errors.append("Missing 'model' configuration")
    if 'training' not in config:
        errors.append("Missing 'training' configuration")
    
    # Check model config
    if 'model' in config:
        model_cfg = config['model']
        if 'input_shape' not in model_cfg:
            errors.append("Missing 'input_shape' in model config")
    
    # Check training config
    if 'training' in config:
        train_cfg = config['training']
        if train_cfg.get('epochs', 0) < 1:
            errors.append("Invalid epochs value (must be >= 1)")
        if train_cfg.get('batch_size', 0) < 1:
            errors.append("Invalid batch_size value (must be >= 1)")
        if train_cfg.get('learning_rate', 0) <= 0:
            errors.append("Invalid learning_rate value (must be > 0)")
    
    if errors:
        return False, "\n".join(errors)
    
    return True, "Configuration is valid"


# ─────────────────────────────────────────────────────────────────────────────
# MAIN TRAINING FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def train_cnn_lstm_model(
    config: Dict,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    X_test: Optional[np.ndarray] = None,
    y_test: Optional[np.ndarray] = None,
    n_classes: int = 5,
    verbose: int = 1
) -> Dict:
    """
    Complete production-ready training pipeline for CNN-LSTM model.
    
    Orchestrates the entire training process including:
    1. Configuration validation
    2. Model creation
    3. Class weight computation
    4. Training with callbacks
    5. Evaluation and reporting
    6. Result persistence
    
    Args:
        config: Complete configuration dictionary
        X_train: Training data (n_samples, time_steps, channels)
        y_train: Training labels (n_samples,)
        X_val: Validation data
        y_val: Validation labels
        X_test: Optional test data
        y_test: Optional test labels
        n_classes: Number of classes
        verbose: Verbosity level (0, 1, or 2)
        
    Returns:
        Dictionary with training results:
        - 'model': Trained Keras model
        - 'trainer': ModelTrainer instance
        - 'history': Training history
        - 'metrics': Training metrics
        - 'model_path': Path to saved model
        - 'history_path': Path to saved history
        
    Example:
        ```python
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
        ```
    """
    # Validate configuration
    is_valid, msg = validate_training_config(config)
    if not is_valid:
        logger.error(f"Configuration validation failed:\n{msg}")
        raise ValueError(f"Invalid configuration: {msg}")
    
    logger.info(f"Configuration validation: {msg}")
    
    # Create trainer
    trainer = ModelTrainer(config, n_classes=n_classes, verbose=verbose)
    
    # Train model
    training_results = trainer.train(
        X_train, y_train,
        X_val, y_val,
        X_test=X_test,
        y_test=y_test,
        verbose=verbose
    )
    
    # Save results
    output_dir = Path(config.get('output', {}).get('output_dir', 'outputs'))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save history
    history_path = output_dir / f'training_history_{trainer.timestamp}.json'
    trainer.save_history(str(history_path))
    
    # Save config
    config_path = output_dir / f'training_config_{trainer.timestamp}.json'
    trainer.save_config(str(config_path))
    
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)
    logger.info(f"Model saved: {trainer.best_model_path}")
    logger.info(f"History saved: {history_path}")
    logger.info(f"Config saved: {config_path}")
    logger.info("=" * 80)
    
    return {
        'model': trainer.model,
        'trainer': trainer,
        'history': training_results['history'],
        'metrics': trainer.get_training_metrics(),
        'model_path': trainer.best_model_path,
        'history_path': str(history_path),
        'config_path': str(config_path)
    }

