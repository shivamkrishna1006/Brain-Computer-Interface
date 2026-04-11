"""
Production-ready CNN-LSTM model architecture for EEG-based Brain Computer Interface.

This module implements a deep learning model combining:
- Conv1D layers for spatial feature extraction from EEG channels
- Batch normalization for training stability
- MaxPooling for dimensionality reduction
- Bidirectional LSTM layers for temporal modeling
- Dense softmax layers for multi-class classification

Features:
- Multi-class classification (configurable number of classes)
- Bidirectional LSTM for complete sequence context
- L2 regularization throughout
- Dropout for overfitting prevention
- Batch normalization after each layer
- Flexible architecture configuration
- Model utilities (save, load, export)

Classes (default):
- 0: Left hand motor imagery
- 1: Right hand motor imagery
- 2: Both hands motor imagery
- 3: Both feet motor imagery
- 4: Click detection / Rest state

Author: BCI Interface Team
Version: 2.0
Status: Production-Ready
"""

import logging
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers, callbacks
from tensorflow.keras.optimizers import Adam, SGD, RMSprop


logger = logging.getLogger('BCI')


# Class mapping for EEG motor imagery classification
CLASS_LABELS = {
    0: 'Left',
    1: 'Right',
    2: 'Hands',
    3: 'Feet',
    4: 'Click'
}

LABEL_TO_INDEX = {v: k for k, v in CLASS_LABELS.items()}


class CNNLSTMModel:
    """
    Production-ready CNN-LSTM model for EEG classification.
    
    Combines convolutional neural networks with bidirectional LSTM layers
    for effective temporal-spatial feature extraction from EEG signals.
    
    Architecture:
    - Input: (time_steps, channels)
    - Conv1D blocks: Feature extraction with batch norm and pooling
    - Bidirectional LSTM: Temporal context from both directions
    - Dense layers: Classification with dropout and batch norm
    - Output: Softmax probabilities for N classes
    
    Attributes:
        config (Dict): Configuration dictionary
        model (keras.Model): Compiled Keras model
        n_classes (int): Number of output classes
        input_shape (Tuple): Expected input shape (time_steps, channels)
    """
    
    def __init__(self, config: Dict, n_classes: int = 5):
        """
        Initialize CNN-LSTM model.
        
        Args:
            config: Configuration dictionary with keys:
                'model': Model architecture config
                'training': Training parameters
                'output': Output paths
            n_classes: Number of output classes (default: 5)
        """
        self.config = config
        self.model = None
        self.n_classes = n_classes
        self.model_config = config.get('model', {})
        self.training_config = config.get('training', {})
        self.input_shape = None
        
        logger.info(f"Initialized CNN-LSTM model for {n_classes} classes")
        
    def build(self) -> keras.Model:
        """
        Build CNN-LSTM model architecture.
        
        Constructs the full neural network with:
        1. Conv1D feature extraction layers
        2. Bidirectional LSTM temporal layers
        3. Dense classification layers
        4. Softmax output for multi-class classification
        
        Returns:
            Compiled Keras model
            
        Raises:
            ValueError: If input_shape not found in config
        """
        if 'input_shape' not in self.model_config:
            raise ValueError("'input_shape' required in model config")
        
        input_shape = tuple(self.model_config['input_shape'])
        self.input_shape = input_shape
        
        logger.info(f"Building CNN-LSTM model with input shape {input_shape}")
        
        # Input layer: (time_steps, channels)
        inputs = layers.Input(shape=input_shape, name='eeg_input')
        
        # CNN feature extraction
        x = self._build_cnn_layers(inputs)
        logger.debug("✓ CNN layers built")
        
        # Bidirectional LSTM temporal modeling
        x = self._build_bilstm_layers(x)
        logger.debug("✓ Bidirectional LSTM layers built")
        
        # Dense classification layers
        x = self._build_dense_layers(x)
        logger.debug("✓ Dense layers built")
        
        # Output layer (softmax for multi-class)
        outputs = layers.Dense(
            units=self.n_classes,
            activation='softmax',
            name='class_output'
        )(x)
        
        # Create model
        self.model = keras.Model(inputs=inputs, outputs=outputs, name='CNN_LSTM_EEG')
        
        # Compile model
        self._compile_model()
        
        logger.info(f"✓ Model built successfully with {self.count_parameters():,} parameters")
        
        return self.model
    
    def _build_cnn_layers(self, inputs: layers.Layer) -> layers.Layer:
        """
        Build CNN feature extraction layers.
        
        Args:
            inputs: Input layer
            
        Returns:
            Output of CNN layers
        """
        cnn_filters = self.model_config.get('cnn_filters', [32, 64, 128])
        kernel_size = self.model_config.get('cnn_kernel_size', 5)
        pool_size = self.model_config.get('cnn_pool_size', 2)
        dropout_rate = self.model_config.get('cnn_dropout', 0.3)
        l2_reg = self.model_config.get('l2_regularization', 0.001)
        
        x = inputs
        
        for i, filters in enumerate(cnn_filters):
            # Conv1D layer
            x = layers.Conv1D(
                filters=filters,
                kernel_size=kernel_size,
                padding='same',
                activation='relu',
                kernel_regularizer=regularizers.l2(l2_reg),
                name=f'conv1d_{i+1}'
            )(x)
            
            # Batch normalization
            x = layers.BatchNormalization(name=f'bn_{i+1}')(x)
            
            # Max pooling
            x = layers.MaxPooling1D(pool_size=pool_size, name=f'maxpool_{i+1}')(x)
            
            # Dropout
            x = layers.Dropout(dropout_rate, name=f'dropout_cnn_{i+1}')(x)
        
        return x
    
    def _build_bilstm_layers(self, inputs: layers.Layer) -> layers.Layer:
        """
        Build Bidirectional LSTM temporal modeling layers.
        
        Bidirectional LSTM processes sequences in both forward and backward
        directions, capturing temporal context from the entire sequence.
        
        Args:
            inputs: Input from CNN layers (time_steps, features)
            
        Returns:
            Output of bidirectional LSTM layers
        """
        lstm_units = self.model_config.get('lstm_units', [128, 64])
        dropout_rate = self.model_config.get('lstm_dropout', 0.4)
        recurrent_dropout = self.model_config.get('lstm_recurrent_dropout', 0.2)
        l2_reg = self.model_config.get('l2_regularization', 0.001)
        
        # Ensure lstm_units is a list
        if isinstance(lstm_units, int):
            lstm_units = [lstm_units, lstm_units // 2]
        
        x = inputs
        
        # First Bidirectional LSTM layer (returns sequences)
        x = layers.Bidirectional(
            layers.LSTM(
                units=lstm_units[0],
                return_sequences=True,
                kernel_regularizer=regularizers.l2(l2_reg),
                recurrent_regularizer=regularizers.l2(l2_reg),
                dropout=dropout_rate,
                recurrent_dropout=recurrent_dropout,
                name='lstm_1'
            ),
            name='bilstm_1'
        )(x)
        
        # Batch normalization
        x = layers.BatchNormalization(name='bn_bilstm_1')(x)
        
        # Second Bidirectional LSTM layer (returns single output)
        x = layers.Bidirectional(
            layers.LSTM(
                units=lstm_units[1] if len(lstm_units) > 1 else lstm_units[0] // 2,
                return_sequences=False,
                kernel_regularizer=regularizers.l2(l2_reg),
                recurrent_regularizer=regularizers.l2(l2_reg),
                dropout=dropout_rate,
                recurrent_dropout=recurrent_dropout,
                name='lstm_2'
            ),
            name='bilstm_2'
        )(x)
        
        # Batch normalization
        x = layers.BatchNormalization(name='bn_bilstm_2')(x)
        
        # Dropout for regularization
        x = layers.Dropout(dropout_rate, name='dropout_bilstm')(x)
        
        return x
    
    def _build_dense_layers(self, inputs: layers.Layer) -> layers.Layer:
        """
        Build dense classification layers.
        
        Processes LSTM output through fully connected layers with
        batch normalization and dropout for multi-class classification.
        
        Args:
            inputs: Input from LSTM layers
            
        Returns:
            Output of dense layers (before softmax)
        """
        dense_units = self.model_config.get('dense_units', [64, 32])
        dropout_rate = self.model_config.get('dense_dropout', 0.3)
        l2_reg = self.model_config.get('l2_regularization', 0.001)
        
        # Ensure dense_units is a list
        if isinstance(dense_units, int):
            dense_units = [dense_units, dense_units // 2]
        
        x = inputs
        
        # First dense layer
        x = layers.Dense(
            units=dense_units[0] if len(dense_units) > 0 else 64,
            activation='relu',
            kernel_regularizer=regularizers.l2(l2_reg),
            name='dense_1'
        )(x)
        
        # Batch normalization
        x = layers.BatchNormalization(name='bn_dense_1')(x)
        
        # Dropout
        x = layers.Dropout(dropout_rate, name='dropout_dense_1')(x)
        
        # Second dense layer
        x = layers.Dense(
            units=dense_units[1] if len(dense_units) > 1 else 32,
            activation='relu',
            kernel_regularizer=regularizers.l2(l2_reg),
            name='dense_2'
        )(x)
        
        # Batch normalization
        x = layers.BatchNormalization(name='bn_dense_2')(x)
        
        # Dropout
        x = layers.Dropout(dropout_rate, name='dropout_dense_2')(x)
        
        return x
    
    def _compile_model(self) -> None:
        """
        Compile the model with optimizer, loss, and metrics.
        
        Uses categorical crossentropy for multi-class classification.
        Includes metrics for multi-class evaluation.
        """
        optimizer_name = self.training_config.get('optimizer', {}).get('name', 'adam')
        learning_rate = self.training_config.get('learning_rate', 0.001)
        
        # Select optimizer
        if isinstance(optimizer_name, str):
            optimizer_name = optimizer_name.lower()
            if optimizer_name == 'adam':
                optimizer = Adam(learning_rate=learning_rate)
            elif optimizer_name == 'sgd':
                optimizer = SGD(learning_rate=learning_rate, momentum=0.9)
            elif optimizer_name == 'rmsprop':
                optimizer = RMSprop(learning_rate=learning_rate)
            else:
                optimizer = Adam(learning_rate=learning_rate)
        else:
            optimizer = Adam(learning_rate=learning_rate)
        
        # Use categorical crossentropy for multi-class
        loss_function = 'categorical_crossentropy'
        
        # Metrics for multi-class classification
        metrics = [
            'accuracy',
            keras.metrics.Precision(),
            keras.metrics.Recall(),
            keras.metrics.AUC()
        ]
        
        self.model.compile(
            optimizer=optimizer,
            loss=loss_function,
            metrics=metrics
        )
        
        logger.info(f"Model compiled with {optimizer_name} optimizer, "
                   f"categorical crossentropy loss, {self.n_classes} classes")
    
    def get_callbacks(self) -> List[callbacks.Callback]:
        """
        Get training callbacks.
        
        Includes:
        - Early stopping on validation loss
        - Learning rate scheduling for adaptive training
        - Model checkpointing for best weights
        - TensorBoard for visualization
        
        Returns:
            List of Keras callbacks
        """
        callback_list = []
        
        training_config = self.training_config
        
        # Early stopping
        early_stopping = callbacks.EarlyStopping(
            monitor=training_config.get('early_stopping_monitor', 'val_loss'),
            patience=training_config.get('early_stopping_patience', 15),
            restore_best_weights=training_config.get('early_stopping_restore_best', True),
            verbose=1
        )
        callback_list.append(early_stopping)
        logger.debug("✓ Early stopping callback added")
        
        # Learning rate scheduler
        if training_config.get('use_lr_scheduler', True):
            def lr_scheduler(epoch, lr):
                """Exponential learning rate decay."""
                decay_rate = training_config.get('lr_decay_rate', 0.95)
                decay_steps = training_config.get('lr_decay_steps', 10)
                
                if epoch % decay_steps == 0 and epoch > 0:
                    return lr * decay_rate
                return lr
            
            scheduler = callbacks.LearningRateScheduler(lr_scheduler, verbose=1)
            callback_list.append(scheduler)
            logger.debug("✓ Learning rate scheduler callback added")
        
        # Model checkpoint
        output_config = self.config.get('output', {})
        model_path = output_config.get('model_path', 'models/bci_model_best.h5')
        
        checkpoint = callbacks.ModelCheckpoint(
            filepath=model_path,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1,
            mode='max'
        )
        callback_list.append(checkpoint)
        logger.debug(f"✓ Model checkpoint callback added (path: {model_path})")
        
        # TensorBoard
        log_dir = output_config.get('log_dir', 'outputs/logs')
        tensorboard = callbacks.TensorBoard(
            log_dir=log_dir,
            histogram_freq=1,
            update_freq='epoch',
            write_graph=True,
            profile_batch=0
        )
        callback_list.append(tensorboard)
        logger.debug(f"✓ TensorBoard callback added (log dir: {log_dir})")
        
        return callback_list
    
    def summary(self) -> None:
        """
        Print model summary with layer details.
        
        Displays architecture, parameters, and layer information
        for debugging and verification.
        """
        if self.model is None:
            logger.error("Model not built yet. Call build() first.")
            return
        
        logger.info("=" * 80)
        logger.info("CNN-LSTM MODEL SUMMARY")
        logger.info("=" * 80)
        self.model.summary()
        logger.info("=" * 80)
    
    def count_parameters(self) -> int:
        """
        Count total trainable and non-trainable parameters.
        
        Returns:
            Total number of parameters
        """
        if self.model is None:
            return 0
        
        trainable = sum([tf.keras.backend.count_params(w) 
                        for w in self.model.trainable_weights])
        non_trainable = sum([tf.keras.backend.count_params(w) 
                            for w in self.model.non_trainable_weights])
        
        return trainable + non_trainable
    
    def load_weights(self, filepath: str) -> None:
        """
        Load pre-trained model weights.
        
        Args:
            filepath: Path to model weights file (.h5 or TensorFlow format)
            
        Raises:
            FileNotFoundError: If weights file not found
        """
        if self.model is None:
            self.build()
        
        if not Path(filepath).exists():
            raise FileNotFoundError(f"Weights file not found: {filepath}")
        
        self.model.load_weights(filepath)
        logger.info(f"✓ Loaded weights from {filepath}")
    
    def save_model(self, filepath: str, include_config: bool = True) -> None:
        """
        Save complete model (architecture + weights).
        
        Supports both .h5 and SavedModel formats.
        
        Args:
            filepath: Path to save model (end with .h5 for h5 format or no extension for SavedModel)
            include_config: Whether to save architecture config as JSON
        """
        if self.model is None:
            logger.error("Model not built yet. Call build() first.")
            return
        
        # Create directory if needed
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Save model
        self.model.save(filepath)
        logger.info(f"✓ Saved model to {filepath}")
        
        # Optionally save architecture config
        if include_config:
            config_path = Path(filepath).parent / 'model_config.json'
            config_dict = {
                'n_classes': self.n_classes,
                'input_shape': list(self.input_shape) if self.input_shape else None,
                'class_labels': CLASS_LABELS,
                'model_config': self.model_config,
                'training_config': self.training_config
            }
            with open(config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            logger.info(f"✓ Saved model config to {config_path}")
    
    def save_weights(self, filepath: str) -> None:
        """
        Save only model weights (not architecture).
        
        Args:
            filepath: Path to save weights (.h5 format)
        """
        if self.model is None:
            logger.error("Model not built yet. Call build() first.")
            return
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        self.model.save_weights(filepath)
        logger.info(f"✓ Saved weights to {filepath}")
    
    def get_model(self) -> keras.Model:
        """
        Get the underlying Keras model.
        
        Useful for direct model access when building training loops.
        
        Returns:
            Compiled Keras model
        """
        if self.model is None:
            self.build()
        return self.model
    
    def get_config(self) -> Dict:
        """
        Get model configuration for saving/loading.
        
        Returns:
            Dictionary with model configuration and class information
        """
        return {
            'n_classes': self.n_classes,
            'input_shape': self.input_shape,
            'class_labels': CLASS_LABELS,
            'model_config': self.model_config,
            'training_config': self.training_config
        }
    
    @property
    def trainable_params(self) -> int:
        """Get number of trainable parameters."""
        if self.model is None:
            return 0
        return sum([tf.keras.backend.count_params(w) for w in self.model.trainable_weights])
    
    @property
    def total_params(self) -> int:
        """Get total number of parameters."""
        return self.count_parameters()


# ─────────────────────────────────────────────────────────────────────────────
# Model Creation Functions
# ─────────────────────────────────────────────────────────────────────────────

def create_model(config: Dict, n_classes: int = 5) -> keras.Model:
    """
    Create and build CNN-LSTM model from configuration.
    
    Convenience function that creates, builds, and returns the Keras model.
    
    Args:
        config: Configuration dictionary with 'model' and 'training' keys
        n_classes: Number of output classes (default: 5)
        
    Returns:
        Compiled Keras model ready for training
        
    Example:
        ```python
        config = {
            'model': {
                'input_shape': [320, 64],  # time_steps, channels
                'cnn_filters': [32, 64, 128],
                'lstm_units': [128, 64],
                'dense_units': [64, 32],
                'dropout_rate': 0.3,
                'l2_regularization': 0.001
            },
            'training': {
                'optimizer': {'name': 'adam'},
                'learning_rate': 0.001
            }
        }
        
        model = create_model(config, n_classes=5)
        model.fit(X_train, y_train, validation_data=(X_valid, y_valid))
        ```
    """
    logger.info(f"Creating CNN-LSTM model with {n_classes} classes...")
    
    model_builder = CNNLSTMModel(config, n_classes=n_classes)
    model_builder.build()
    
    logger.info("=" * 80)
    logger.info("MODEL CREATED SUCCESSFULLY")
    logger.info("=" * 80)
    logger.info(f"Classes: {list(CLASS_LABELS.values())}")
    logger.info(f"Parameters: {model_builder.count_parameters():,}")
    logger.info("=" * 80)
    
    return model_builder.model


def load_pretrained_model(model_path: str, config_path: Optional[str] = None) -> Tuple[keras.Model, Dict]:
    """
    Load a pre-trained CNN-LSTM model.
    
    Args:
        model_path: Path to saved model (.h5 or SavedModel directory)
        config_path: Optional path to model_config.json
        
    Returns:
        Tuple of (Keras model, configuration dictionary)
    """
    logger.info(f"Loading model from {model_path}...")
    
    # Load model
    if Path(model_path).suffix == '.h5':
        model = keras.models.load_model(model_path)
    else:
        model = keras.models.load_model(model_path)
    
    # Load config if available
    config = {}
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"✓ Loaded config from {config_path}")
    
    logger.info(f"✓ Loaded model with {sum([tf.keras.backend.count_params(w) for w in model.weights]):,} parameters")
    
    return model, config


# ─────────────────────────────────────────────────────────────────────────────
# Model Utilities
# ─────────────────────────────────────────────────────────────────────────────

def get_class_labels() -> Dict[int, str]:
    """
    Get EEG classification class labels.
    
    Returns:
        Dictionary mapping class indices to labels
        
    Example:
        ```python
        labels = get_class_labels()
        # {0: 'Left', 1: 'Right', 2: 'Hands', 3: 'Feet', 4: 'Click'}
        ```
    """
    return CLASS_LABELS.copy()


def get_label_index(label: str) -> int:
    """
    Get class index from label name.
    
    Args:
        label: Class label (e.g., 'Left', 'Right', 'Hands', 'Feet', 'Click')
        
    Returns:
        Class index
        
    Raises:
        ValueError: If label not found
    """
    if label not in LABEL_TO_INDEX:
        raise ValueError(f"Unknown label: {label}. Valid labels: {list(LABEL_TO_INDEX.keys())}")
    return LABEL_TO_INDEX[label]
