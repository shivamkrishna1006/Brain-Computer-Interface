"""
Production-ready examples for CNN-LSTM EEG classification model.

Demonstrates:
1. Model creation and configuration
2. Training with full pipeline
3. Inference and evaluation
4. Model saving and loading
5. Multi-class classification
"""

import numpy as np
import logging
from pathlib import Path
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam

from src.model import (
    CNNLSTMModel, 
    create_model, 
    load_pretrained_model,
    get_class_labels,
    get_label_index
)

from src.utils import setup_logging, load_config
from src.data_preparation import prepare_eeg_data

# Setup logging
logger = setup_logging('cnn_lstm_examples')


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 1: Basic Model Creation and Summary
# ─────────────────────────────────────────────────────────────────────────────

def example_1_create_model():
    """
    Example 1: Create and inspect CNN-LSTM model architecture.
    
    Demonstrates:
    - Basic model creation from config
    - Model summary with parameter counts
    - Class label information
    """
    logger.info("\n" + "="*80)
    logger.info("EXAMPLE 1: Model Creation")
    logger.info("="*80)
    
    # Configuration for 5-class motor imagery
    config = {
        'model': {
            'input_shape': [320, 64],  # 320 time steps, 64 EEG channels
            'cnn_filters': [32, 64, 128],
            'cnn_kernel_size': 5,
            'cnn_pool_size': 2,
            'cnn_dropout': 0.3,
            'lstm_units': [128, 64],  # Bidirectional LSTM
            'lstm_dropout': 0.4,
            'lstm_recurrent_dropout': 0.2,
            'dense_units': [64, 32],
            'dense_dropout': 0.3,
            'l2_regularization': 0.001
        },
        'training': {
            'optimizer': {'name': 'adam'},
            'learning_rate': 0.001
        },
        'output': {
            'model_path': 'models/cnn_lstm_5class.h5',
            'log_dir': 'outputs/logs'
        }
    }
    
    # Create model
    logger.info("Creating CNN-LSTM model for 5-class classification...")
    model = create_model(config, n_classes=5)
    
    # Display architecture
    logger.info("\nModel Architecture:")
    model.summary()
    
    # Display class information
    logger.info("\nClass Labels:")
    labels = get_class_labels()
    for idx, label in labels.items():
        logger.info(f"  {idx}: {label}")
    
    logger.info("✓ Example 1 complete\n")
    
    return model, config


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 2: Training with Data Preparation
# ─────────────────────────────────────────────────────────────────────────────

def example_2_training(config, num_samples=1000):
    """
    Example 2: Complete training pipeline with data preparation.
    
    Demonstrates:
    - Synthetic data generation
    - Data preparation and normalization
    - Model training with callbacks
    - Monitoring training progress
    """
    logger.info("\n" + "="*80)
    logger.info("EXAMPLE 2: Training Pipeline")
    logger.info("="*80)
    
    # ─────────────────────────────────────────────────────────────
    # 1. Generate synthetic data (replace with your data loading)
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[1/5] Generating synthetic data...")
    np.random.seed(42)
    
    n_samples = num_samples
    n_channels = 64
    time_steps = 320
    n_classes = 5
    
    X = np.random.randn(n_samples, n_channels, time_steps).astype(np.float32)
    y = np.random.randint(0, n_classes, n_samples)
    
    logger.info(f"Data shape: {X.shape}")
    logger.info(f"Labels shape: {y.shape}")
    logger.info(f"Class distribution: {np.bincount(y)}")
    
    # ─────────────────────────────────────────────────────────────
    # 2. Prepare data (normalize, reshape, split)
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[2/5] Preparing data...")
    (X_train, y_train), (X_test, y_test), prep = prepare_eeg_data(
        X, y,
        n_channels=n_channels,
        time_steps=time_steps,
        test_size=0.2,
        random_state=42
    )
    
    logger.info(f"Train data: {X_train.shape}, {y_train.shape}")
    logger.info(f"Test data: {X_test.shape}, {y_test.shape}")
    logger.info(f"Train class distribution: {np.bincount(y_train)}")
    
    # Convert to categorical
    y_train_cat = to_categorical(y_train, n_classes)
    y_test_cat = to_categorical(y_test, n_classes)
    logger.info(f"Categorical shapes: {y_train_cat.shape}, {y_test_cat.shape}")
    
    # ─────────────────────────────────────────────────────────────
    # 3. Create and build model
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[3/5] Building model...")
    model_builder = CNNLSTMModel(config, n_classes=5)
    model_builder.build()
    
    logger.info(f"Total parameters: {model_builder.count_parameters():,}")
    logger.info(f"Trainable parameters: {model_builder.trainable_params:,}")
    
    # ─────────────────────────────────────────────────────────────
    # 4. Get callbacks and train
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[4/5] Training model...")
    callbacks = model_builder.get_callbacks()
    
    history = model_builder.model.fit(
        X_train, y_train_cat,
        validation_data=(X_test, y_test_cat),
        epochs=20,  # Short for demo
        batch_size=32,
        callbacks=callbacks,
        verbose=1
    )
    
    # ─────────────────────────────────────────────────────────────
    # 5. Evaluate
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[5/5] Evaluating model...")
    results = model_builder.model.evaluate(X_test, y_test_cat, verbose=0)
    
    logger.info("\nTest Results:")
    logger.info(f"  Loss: {results[0]:.4f}")
    logger.info(f"  Accuracy: {results[1]:.4f}")
    logger.info(f"  Precision: {results[2]:.4f}")
    logger.info(f"  Recall: {results[3]:.4f}")
    logger.info(f"  AUC: {results[4]:.4f}")
    
    logger.info("✓ Example 2 complete\n")
    
    return model_builder, history


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 3: Inference and Predictions
# ─────────────────────────────────────────────────────────────────────────────

def example_3_inference(model_builder, config):
    """
    Example 3: Making predictions and interpreting results.
    
    Demonstrates:
    - Batch and single predictions
    - Getting class probabilities
    - Confidence scores
    - Class label mapping
    """
    logger.info("\n" + "="*80)
    logger.info("EXAMPLE 3: Inference and Predictions")
    logger.info("="*80)
    
    # Generate test data
    logger.info("\nGenerating test data...")
    n_samples = 10
    X_test_demo = np.random.randn(n_samples, 320, 64).astype(np.float32)
    
    # ─────────────────────────────────────────────────────────────
    # Batch predictions
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[1] Batch Predictions:")
    predictions = model_builder.model.predict(X_test_demo, verbose=0)
    
    logger.info(f"Predictions shape: {predictions.shape}")
    logger.info(f"Output type: probabilities (softmax)")
    logger.info(f"Sum of probabilities per sample: {predictions[0].sum():.4f}")
    
    # ─────────────────────────────────────────────────────────────
    # Get predicted classes
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[2] Predicted Classes:")
    predicted_classes = np.argmax(predictions, axis=1)
    
    labels = get_class_labels()
    predicted_labels = [labels[c] for c in predicted_classes]
    
    for i, (class_idx, label) in enumerate(zip(predicted_classes, predicted_labels)):
        confidence = predictions[i, class_idx]
        logger.info(f"  Sample {i}: {label:10s} (class {class_idx}, "
                   f"confidence: {confidence:.4f})")
    
    # ─────────────────────────────────────────────────────────────
    # Confidence threshold
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[3] Confidence Analysis:")
    max_probs = np.max(predictions, axis=1)
    confidence_threshold = 0.7
    confident = max_probs > confidence_threshold
    
    logger.info(f"Threshold: {confidence_threshold}")
    logger.info(f"Confident predictions: {confident.sum()}/{n_samples}")
    logger.info(f"Mean confidence: {max_probs.mean():.4f}")
    logger.info(f"Min confidence: {max_probs.min():.4f}")
    logger.info(f"Max confidence: {max_probs.max():.4f}")
    
    # ─────────────────────────────────────────────────────────────
    # Per-class probabilities
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[4] Per-Class Probabilities (Sample 0):")
    for class_idx, label in labels.items():
        prob = predictions[0, class_idx]
        bar = "█" * int(prob * 50)
        logger.info(f"  {label:10s}: {prob:.4f} {bar}")
    
    logger.info("✓ Example 3 complete\n")
    
    return predictions


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 4: Model Saving and Loading
# ─────────────────────────────────────────────────────────────────────────────

def example_4_model_persistence(model_builder):
    """
    Example 4: Saving and loading models.
    
    Demonstrates:
    - Saving complete model (architecture + weights)
    - Saving weights only
    - Loading pre-trained models
    - Configuration persistence
    """
    logger.info("\n" + "="*80)
    logger.info("EXAMPLE 4: Model Persistence")
    logger.info("="*80)
    
    save_dir = Path('models')
    save_dir.mkdir(exist_ok=True)
    
    # ─────────────────────────────────────────────────────────────
    # Save complete model
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[1] Saving complete model...")
    model_path = save_dir / 'cnn_lstm_complete.h5'
    model_builder.save_model(str(model_path), include_config=True)
    logger.info(f"✓ Saved to {model_path}")
    
    # ─────────────────────────────────────────────────────────────
    # Save weights only
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[2] Saving weights only...")
    weights_path = save_dir / 'cnn_lstm_weights.h5'
    model_builder.save_weights(str(weights_path))
    logger.info(f"✓ Saved to {weights_path}")
    
    # ─────────────────────────────────────────────────────────────
    # Load pre-trained model
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[3] Loading pre-trained model...")
    loaded_model, loaded_config = load_pretrained_model(
        str(model_path),
        str(save_dir / 'model_config.json')
    )
    
    logger.info("✓ Model loaded successfully")
    logger.info(f"  Classes: {loaded_config.get('n_classes', 'N/A')}")
    logger.info(f"  Input shape: {loaded_config.get('input_shape', 'N/A')}")
    
    # ─────────────────────────────────────────────────────────────
    # Verify loaded model works
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[4] Testing loaded model...")
    X_test = np.random.randn(5, 320, 64).astype(np.float32)
    predictions = loaded_model.predict(X_test, verbose=0)
    logger.info(f"✓ Predictions shape: {predictions.shape}")
    logger.info(f"✓ Output sample: {predictions[0]}")
    
    logger.info("✓ Example 4 complete\n")


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE 5: Advanced Configuration
# ─────────────────────────────────────────────────────────────────────────────

def example_5_advanced_config():
    """
    Example 5: Advanced model configurations for different scenarios.
    
    Demonstrates:
    - Lightweight model (mobile/edge)
    - Standard model (typical use)
    - Large model (maximum accuracy)
    - Configuration templates
    """
    logger.info("\n" + "="*80)
    logger.info("EXAMPLE 5: Advanced Configurations")
    logger.info("="*80)
    
    # ─────────────────────────────────────────────────────────────
    # Lightweight configuration (mobile/edge deployment)
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[1] Lightweight Configuration:")
    logger.info("   Use case: Mobile/edge devices, real-time processing")
    
    lightweight_config = {
        'model': {
            'input_shape': [320, 64],
            'cnn_filters': [16, 32, 64],  # Smaller than default
            'cnn_kernel_size': 3,
            'cnn_pool_size': 2,
            'cnn_dropout': 0.2,
            'lstm_units': [64, 32],  # Smaller LSTM
            'lstm_dropout': 0.3,
            'lstm_recurrent_dropout': 0.1,
            'dense_units': [32, 16],  # Smaller dense
            'dense_dropout': 0.2,
            'l2_regularization': 0.0001  # Less regularization
        },
        'training': {
            'optimizer': {'name': 'adam'},
            'learning_rate': 0.001
        }
    }
    
    model_light = create_model(lightweight_config, n_classes=5)
    logger.info(f"Parameters: {sum([tf.keras.backend.count_params(w) for w in model_light.weights]):,}")
    logger.info("✓ Good for: Limited memory, fast inference")
    
    # ─────────────────────────────────────────────────────────────
    # Standard configuration (recommended)
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[2] Standard Configuration:")
    logger.info("   Use case: Typical training and deployment")
    
    standard_config = {
        'model': {
            'input_shape': [320, 64],
            'cnn_filters': [32, 64, 128],  # Balanced
            'cnn_kernel_size': 5,
            'cnn_pool_size': 2,
            'cnn_dropout': 0.3,
            'lstm_units': [128, 64],  # Balanced LSTM
            'lstm_dropout': 0.4,
            'lstm_recurrent_dropout': 0.2,
            'dense_units': [64, 32],  # Balanced dense
            'dense_dropout': 0.3,
            'l2_regularization': 0.001  # Standard regularization
        },
        'training': {
            'optimizer': {'name': 'adam'},
            'learning_rate': 0.001
        }
    }
    
    model_standard = create_model(standard_config, n_classes=5)
    from tensorflow.keras import backend as K
    logger.info(f"Parameters: {sum([K.count_params(w) for w in model_standard.weights]):,}")
    logger.info("✓ Good for: Balanced accuracy and efficiency")
    
    # ─────────────────────────────────────────────────────────────
    # Large configuration (maximum accuracy)
    # ─────────────────────────────────────────────────────────────
    logger.info("\n[3] Large Configuration:")
    logger.info("   Use case: Research, maximum accuracy, server deployment")
    
    large_config = {
        'model': {
            'input_shape': [320, 64],
            'cnn_filters': [64, 128, 256],  # Large filters
            'cnn_kernel_size': 7,
            'cnn_pool_size': 2,
            'cnn_dropout': 0.4,
            'lstm_units': [256, 128],  # Larger LSTM
            'lstm_dropout': 0.5,
            'lstm_recurrent_dropout': 0.3,
            'dense_units': [128, 64],  # Larger dense
            'dense_dropout': 0.4,
            'l2_regularization': 0.01  # Strong regularization
        },
        'training': {
            'optimizer': {'name': 'adam'},
            'learning_rate': 0.0005  # Lower LR for large model
        }
    }
    
    model_large = create_model(large_config, n_classes=5)
    logger.info(f"Parameters: {sum([K.count_params(w) for w in model_large.weights]):,}")
    logger.info("✓ Good for: Best accuracy, research applications")
    
    logger.info("\n[4] Configuration Selection Guide:")
    logger.info("  Lightweight: <500K params - mobile/edge")
    logger.info("  Standard: 900K-1.2M params - typical use")
    logger.info("  Large: >2M params - maximum accuracy")
    
    logger.info("✓ Example 5 complete\n")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────────────────────

def main():
    """Run all examples."""
    logger.info("\n" + "="*80)
    logger.info("CNN-LSTM EEG Classification - Production Examples")
    logger.info("="*80)
    
    # Example 1: Create model
    model, config = example_1_create_model()
    
    # Example 2: Training
    model_builder, history = example_2_training(config, num_samples=500)
    
    # Example 3: Inference
    predictions = example_3_inference(model_builder, config)
    
    # Example 4: Model persistence
    example_4_model_persistence(model_builder)
    
    # Example 5: Advanced configurations
    example_5_advanced_config()
    
    logger.info("\n" + "="*80)
    logger.info("All examples completed successfully!")
    logger.info("="*80)
    logger.info("\nNext steps:")
    logger.info("1. Load your own EEG data")
    logger.info("2. Prepare using data_preparation module")
    logger.info("3. Configure model parameters")
    logger.info("4. Train with appropriate hyperparameters")
    logger.info("5. Save and deploy model")
    logger.info("\nFor more information, see MODEL_GUIDE.md")


if __name__ == '__main__':
    main()
