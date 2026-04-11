"""
Complete EEG Data Preparation Pipeline Example.

This script demonstrates the full workflow:
1. Load EEG data (synthetic or PhysioNet)
2. Prepare data (normalize, reshape, split)
3. Train model
4. Evaluate results
"""

import sys
import logging
sys.path.insert(0, 'src')

import numpy as np
from data_preparation import prepare_eeg_data, EEGDataPreparation
from utils import load_config, setup_logging, create_directories, normalize_data as utils_normalize
from model import create_model
from train import ModelTrainer
from evaluate import ModelEvaluator


def example_synthetic_data():
    """
    Example 1: Generate and prepare synthetic EEG data.
    """
    print("\n" + "=" * 80)
    print("Example 1: Synthetic EEG Data Preparation")
    print("=" * 80)
    
    # Configuration
    n_samples = 1000
    n_channels = 64
    time_steps = 250
    n_classes = 2
    
    print(f"\nGenerating synthetic EEG data:")
    print(f"  Samples: {n_samples}")
    print(f"  Channels: {n_channels}")
    print(f"  Time steps: {time_steps}")
    print(f"  Classes: {n_classes}")
    
    # Generate synthetic data
    X = np.random.randn(n_samples, n_channels, time_steps)
    y = np.random.randint(0, n_classes, n_samples)
    
    print(f"\nRaw data shape: {X.shape}")
    print(f"Raw labels shape: {y.shape}")
    print(f"Class distribution: {np.bincount(y)}")
    
    # Prepare data using main function
    print(f"\nPreparing data...")
    (X_train, y_train), (X_test, y_test), prep = prepare_eeg_data(
        X, y,
        n_channels=n_channels,
        time_steps=time_steps,
        test_size=0.2,
        random_state=42
    )
    
    print(f"\nPreparation completed:")
    print(f"  Train shape: {X_train.shape}")
    print(f"  Test shape: {X_test.shape}")
    print(f"  Train labels: {np.bincount(y_train)}")
    print(f"  Test labels: {np.bincount(y_test)}")
    
    return (X_train, y_train), (X_test, y_test), prep, n_channels, time_steps


def example_custom_preparation():
    """
    Example 2: Use EEGDataPreparation class directly for fine-grained control.
    """
    print("\n" + "=" * 80)
    print("Example 2: Custom Data Preparation Pipeline")
    print("=" * 80)
    
    # Generate synthetic data
    n_samples = 500
    n_channels = 8
    time_steps = 250
    
    X = np.random.randn(n_samples, time_steps, n_channels) * 50  # μV scale
    y = np.random.randint(0, 2, n_samples)
    
    print(f"\nRaw data:")
    print(f"  Shape: {X.shape}")
    print(f"  Range: [{X.min():.2f}, {X.max():.2f}] μV")
    print(f"  Mean: {X.mean():.2f}, Std: {X.std():.2f}")
    
    # Initialize preparation
    prep = EEGDataPreparation(n_channels=n_channels, time_steps=time_steps)
    
    # Step 1: Validate input shape
    print(f"\nStep 1: Validating input shape...")
    prep.validate_shape(X, "Input data")
    print(f"  ✓ Valid shape: (samples, time, channels)")
    
    # Step 2: Get statistics before normalization
    print(f"\nStep 2: Data statistics before normalization:")
    stats_before = prep.get_statistics(X)
    
    # Step 3: Normalize
    print(f"\nStep 3: Normalizing with StandardScaler...")
    X_normalized = prep.normalize(X, fit=True)
    print(f"  ✓ Normalized")
    print(f"    Range: [{X_normalized.min():.4f}, {X_normalized.max():.4f}]")
    print(f"    Mean: {X_normalized.mean():.4f}, Std: {X_normalized.std():.4f}")
    
    # Step 4: Split with stratification
    print(f"\nStep 4: Splitting with stratification (80-20)...")
    (X_train, y_train), (X_test, y_test) = prep.split_data(
        X_normalized, y,
        test_size=0.2,
        stratify=True
    )
    print(f"  ✓ Split completed")
    print(f"    Train: {len(X_train)} samples, Classes: {np.bincount(y_train)}")
    print(f"    Test:  {len(X_test)} samples, Classes: {np.bincount(y_test)}")
    
    # Step 5: Get normalization parameters
    print(f"\nStep 5: Normalization parameters:")
    norm_params = prep.get_normalization_params()
    print(f"  Mean shape: {norm_params['mean'].shape}")
    print(f"  Scale shape: {norm_params['scale'].shape}")
    
    # Step 6: Verify denormalization
    print(f"\nStep 6: Verifying denormalization...")
    X_denorm = prep.denormalize(X_normalized)
    reconstruction_error = np.mean((X - X_denorm) ** 2)
    print(f"  Reconstruction MSE: {reconstruction_error:.6f}")
    print(f"  ✓ Denormalization verified")
    
    return (X_train, y_train), (X_test, y_test), prep


def example_with_physionet():
    """
    Example 3: Prepare PhysioNet data using data_preparation.
    """
    print("\n" + "=" * 80)
    print("Example 3: PhysioNet Data Preparation")
    print("=" * 80)
    
    try:
        from physionet_loader import load_physionet_data
        
        print(f"\nLoading PhysioNet data...")
        X, y = load_physionet_data(
            subject_ids=[1],
            tasks=['left_hand', 'right_hand'],
            sessions=1
        )
        
        print(f"Loaded data shape: {X.shape}")
        print(f"Class distribution: {np.bincount(y)}")
        
        n_channels = X.shape[1]
        time_steps = X.shape[2]
        
        print(f"\nPreparing data...")
        (X_train, y_train), (X_test, y_test), prep = prepare_eeg_data(
            X, y,
            n_channels=n_channels,
            time_steps=time_steps,
            test_size=0.2
        )
        
        print(f"Preparation completed:")
        print(f"  Train: {X_train.shape}")
        print(f"  Test:  {X_test.shape}")
        
        return (X_train, y_train), (X_test, y_test), prep, n_channels, time_steps
    
    except Exception as e:
        print(f"⚠ PhysioNet loading skipped: {e}")
        print(f"  (Requires internet connection)")
        return None


def example_training_pipeline():
    """
    Example 4: Complete training pipeline with data preparation.
    """
    print("\n" + "=" * 80)
    print("Example 4: Complete Training Pipeline")
    print("=" * 80)
    
    # Load configuration
    config = load_config('configs/config.yaml')
    logger = setup_logging(config)
    create_directories(config)
    
    # Generate synthetic data
    print(f"\nGenerating synthetic data for training...")
    n_samples = 500
    n_channels = 64
    time_steps = 250
    
    X = np.random.randn(n_samples, n_channels, time_steps)
    y = np.random.randint(0, 2, n_samples)
    
    # Prepare data
    print(f"\nPreparing data...")
    (X_train, y_train), (X_test, y_test), prep = prepare_eeg_data(
        X, y,
        n_channels=n_channels,
        time_steps=time_steps,
        test_size=0.2
    )
    
    # Update config for our data
    config['data']['eeg_channels'] = n_channels
    config['data']['segment_samples'] = time_steps
    config['model']['input_shape'] = [time_steps, n_channels]
    config['training']['epochs'] = 10  # Quick training for example
    config['training']['batch_size'] = 32
    
    print(f"\nBuilding model...")
    model = create_model(config)
    
    print(f"Training model...")
    trainer = ModelTrainer(config)
    trainer.model = model
    history = trainer.train(X_train, y_train, X_test, y_test)
    
    print(f"\nEvaluating model...")
    evaluator = ModelEvaluator(model, config)
    metrics = evaluator.evaluate(X_test, y_test)
    
    print(f"\nResults:")
    print(f"  Accuracy: {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall: {metrics['recall']:.4f}")
    print(f"  F1-score: {metrics['f1']:.4f}")
    
    return metrics


def example_comparison_strategies():
    """
    Example 5: Compare different data preparation strategies.
    """
    print("\n" + "=" * 80)
    print("Example 5: Comparison of Preparation Strategies")
    print("=" * 80)
    
    # Generate synthetic data
    n_samples = 1000
    n_channels = 8
    time_steps = 250
    
    X = np.random.randn(n_samples, n_channels, time_steps) * 100
    y = np.random.randint(0, 3, n_samples)
    
    print(f"\nRaw data statistics:")
    print(f"  Shape: {X.shape}")
    print(f"  Range: [{X.min():.2f}, {X.max():.2f}]")
    print(f"  Mean: {X.mean():.2f}, Std: {X.std():.2f}")
    
    # Strategy 1: Direct preparation (recommended)
    print(f"\n{'='*40}")
    print(f"Strategy 1: Using prepare_eeg_data()")
    print(f"{'='*40}")
    (X_train1, y_train1), (X_test1, y_test1), prep1 = prepare_eeg_data(X, y, n_channels, time_steps)
    print(f"Train shape: {X_train1.shape}")
    print(f"Data range: [{X_train1.min():.4f}, {X_train1.max():.4f}]")
    
    # Strategy 2: Manual step-by-step
    print(f"\n{'='*40}")
    print(f"Strategy 2: Manual step-by-step")
    print(f"{'='*40}")
    prep2 = EEGDataPreparation(n_channels, time_steps)
    X_norm = prep2.normalize(X, fit=True)
    (X_train2, y_train2), (X_test2, y_test2) = prep2.split_data(X_norm, y)
    print(f"Train shape: {X_train2.shape}")
    print(f"Data range: [{X_train2.min():.4f}, {X_train2.max():.4f}]")
    
    # Strategy 3: With custom test size
    print(f"\n{'='*40}")
    print(f"Strategy 3: Custom test size (70-30)")
    print(f"{'='*40}")
    from data_preparation import prepare_eeg_data_with_validation
    (X_train3, y_train3), (X_test3, y_test3), prep3 = prepare_eeg_data_with_validation(
        X, y, n_channels, time_steps, train_size=0.7
    )
    print(f"Train shape: {X_train3.shape} ({len(X_train3)/len(X)*100:.1f}%)")
    print(f"Test shape:  {X_test3.shape} ({len(X_test3)/len(X)*100:.1f}%)")
    
    print(f"\n{'='*40}")
    print(f"All strategies completed successfully!")
    print(f"{'='*40}")


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("EEG Data Preparation - Complete Tutorial")
    print("=" * 80)
    
    # Run examples
    try:
        # Example 1: Synthetic data with main function
        train1, test1, prep1, ch1, ts1 = example_synthetic_data()
        
        # Example 2: Custom pipeline
        train2, test2, prep2 = example_custom_preparation()
        
        # Example 3: PhysioNet data (optional, requires internet)
        physionet_result = example_with_physionet()
        
        # Example 4: Complete training (commented out to avoid long runtime)
        print("\n" + "=" * 80)
        print("Example 4: Complete Training Pipeline")
        print("=" * 80)
        print("(Skipped - uncomment to run. Takes ~5 minutes)")
        # metrics = example_training_pipeline()
        
        # Example 5: Comparison of strategies
        example_comparison_strategies()
        
        print("\n" + "=" * 80)
        print("✓ All examples completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
