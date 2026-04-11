"""
Example: Using PhysioNet EEG Motor Imagery Dataset with BCI System.

This script demonstrates how to:
1. Load PhysioNet EEG Motor Imagery data
2. Preprocess and prepare data splits
3. Train the CNN-LSTM model
4. Evaluate performance
"""

import logging
import sys
import argparse
sys.path.insert(0, 'src')

import numpy as np
from physionet_loader import (
    load_physionet_data, 
    prepare_data_splits, 
    get_label_mapping
)
from utils import setup_logging, load_config, create_directories, normalize_data
from model import create_model
from train import ModelTrainer
from evaluate import ModelEvaluator


def main(subject_ids: list = None, tasks: list = None, epochs: int = 50):
    """
    Main example function.
    
    Args:
        subject_ids: List of subject IDs to load
        tasks: List of motor imagery tasks
        epochs: Number of training epochs
    """
    # Default values
    if subject_ids is None:
        subject_ids = [1, 2, 3]  # Load first 3 subjects
    if tasks is None:
        tasks = ['left_hand', 'right_hand']  # Left vs right hand
    
    # Load configuration
    config = load_config('configs/config.yaml')
    
    # Setup logging
    logger = setup_logging(config)
    create_directories(config)
    
    logger.info("=" * 80)
    logger.info("PhysioNet EEG Motor Imagery Dataset Example")
    logger.info("=" * 80)
    
    # Step 1: Load data from PhysioNet
    logger.info("\nStep 1: Loading PhysioNet EEG data")
    logger.info("-" * 80)
    
    logger.info(f"Loading subjects: {subject_ids}")
    logger.info(f"Tasks: {tasks}")
    
    X, y = load_physionet_data(
        subject_ids=subject_ids,
        tasks=tasks,
        sessions=1,
        filter_freqs=(8, 30),  # Motor imagery frequency band
        epoch_window=(0.5, 3.5),  # 0.5-3.5s after stimulus
        verbose=False
    )
    
    logger.info(f"Data shape: {X.shape}")
    logger.info(f"Labels shape: {y.shape}")
    
    # Display label information
    label_map = get_label_mapping()
    logger.info("\nLabel distribution:")
    for label_id in np.unique(y):
        label_name = label_map.get(label_id, f'Unknown_{label_id}')
        count = np.sum(y == label_id)
        logger.info(f"  {label_name}: {count} epochs")
    
    # Step 2: Data preprocessing and splitting
    logger.info("\nStep 2: Data preprocessing and splitting")
    logger.info("-" * 80)
    
    # Normalize data
    logger.info("Normalizing data...")
    original_shape = X.shape
    X_reshaped = X.reshape(-1, X.shape[-1])
    X_reshaped, norm_params = normalize_data(X_reshaped, method='zscore')
    X = X_reshaped.reshape(original_shape)
    
    # Split data with stratification to maintain class balance
    logger.info("Splitting data into train/val/test sets...")
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = prepare_data_splits(
        X, y,
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15
    )
    
    logger.info(f"Training set: {X_train.shape}")
    logger.info(f"Validation set: {X_val.shape}")
    logger.info(f"Test set: {X_test.shape}")
    
    # Display split label distribution
    logger.info("\nLabel distribution in splits:")
    for split_name, y_split in [('Train', y_train), ('Val', y_val), ('Test', y_test)]:
        logger.info(f"  {split_name}: {np.bincount(y_split)}")
    
    # Step 3: Configure model for PhysioNet data
    logger.info("\nStep 3: Configuring model for PhysioNet data")
    logger.info("-" * 80)
    
    # Update config for PhysioNet data characteristics
    logger.info(f"Original data shape: {X_train.shape}")
    config['data']['eeg_channels'] = X_train.shape[1]  # 64 channels
    config['data']['segment_samples'] = X_train.shape[2]  # Time points
    config['model']['input_shape'] = [X_train.shape[2], X_train.shape[1]]
    config['training']['epochs'] = epochs  # Custom epoch count
    config['training']['batch_size'] = 16  # Smaller batch for smaller dataset
    
    # Update other config values
    config['data']['num_classes'] = 2  # Binary classification (left vs right)
    
    logger.info(f"Model input shape: {config['model']['input_shape']}")
    logger.info(f"Number of channels: {config['data']['eeg_channels']}")
    logger.info(f"Batch size: {config['training']['batch_size']}")
    logger.info(f"Training epochs: {config['training']['epochs']}")
    
    # Step 4: Build and train model
    logger.info("\nStep 4: Building and training model")
    logger.info("-" * 80)
    
    # Create model
    model = create_model(config)
    
    # Train model
    logger.info("Starting training...")
    trainer = ModelTrainer(config)
    trainer.model = model
    
    history = trainer.train(X_train, y_train, X_val, y_val)
    
    # Step 5: Evaluate on test set
    logger.info("\nStep 5: Evaluating on test set")
    logger.info("-" * 80)
    
    evaluator = ModelEvaluator(model, config)
    metrics = evaluator.evaluate(X_test, y_test)
    
    # Display results
    logger.info("\nEvaluation Results:")
    for metric_name, metric_value in metrics.items():
        if metric_name != 'confusion_matrix':
            logger.info(f"  {metric_name.upper()}: {metric_value:.4f}")
    
    # Generate visualizations
    logger.info("\nGenerating evaluation plots...")
    evaluator.plot_confusion_matrix()
    evaluator.plot_roc_curve()
    evaluator.plot_prediction_distribution()
    evaluator.save_evaluation_report()
    
    logger.info("\n" + "=" * 80)
    logger.info("Example completed successfully!")
    logger.info("=" * 80)
    
    return model, metrics, (X_train, y_train, X_val, y_val, X_test, y_test)


def main_compare_tasks(subject_ids: list = None):
    """
    Compare different motor imagery tasks.
    
    Args:
        subject_ids: List of subject IDs to load
    """
    if subject_ids is None:
        subject_ids = [1]
    
    config = load_config('configs/config.yaml')
    logger = setup_logging(config)
    
    logger.info("Comparing motor imagery tasks...")
    
    # Define task combinations
    task_combinations = [
        (['left_hand', 'right_hand'], 'Left vs Right Hand'),
        (['both_hands', 'both_feet'], 'Hands vs Feet'),
        (['left_hand', 'right_hand', 'both_hands', 'both_feet'], 'All Tasks (4-class)'),
    ]
    
    results = {}
    
    for tasks, task_name in task_combinations:
        logger.info(f"\nLoading {task_name}...")
        
        X, y = load_physionet_data(
            subject_ids=subject_ids,
            tasks=tasks,
            sessions=1,
            filter_freqs=(8, 30),
            epoch_window=(0.5, 3.5),
            verbose=False
        )
        
        if len(X) == 0:
            logger.warning(f"No data for {task_name}")
            continue
        
        logger.info(f"Data shape: {X.shape}")
        logger.info(f"Classes: {np.unique(y)}")
        logger.info(f"Class distribution: {np.bincount(y)}")
        
        results[task_name] = {
            'X_shape': X.shape,
            'n_classes': len(np.unique(y)),
            'class_dist': dict(zip(np.unique(y), np.bincount(y)))
        }
    
    # Display comparison
    logger.info("\n" + "=" * 80)
    logger.info("Task Comparison Summary")
    logger.info("=" * 80)
    
    for task_name, info in results.items():
        logger.info(f"\n{task_name}:")
        logger.info(f"  Data shape: {info['X_shape']}")
        logger.info(f"  Number of classes: {info['n_classes']}")
        logger.info(f"  Class distribution: {info['class_dist']}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='PhysioNet EEG Motor Imagery Dataset Example'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        default='train',
        choices=['train', 'compare'],
        help='Mode: train model or compare tasks'
    )
    
    parser.add_argument(
        '--subjects',
        type=int,
        nargs='+',
        default=[1, 2, 3],
        help='Subject IDs to load (default: 1 2 3)'
    )
    
    parser.add_argument(
        '--tasks',
        type=str,
        nargs='+',
        default=['left_hand', 'right_hand'],
        help='Motor imagery tasks (default: left_hand right_hand)'
    )
    
    parser.add_argument(
        '--epochs',
        type=int,
        default=50,
        help='Number of training epochs (default: 50)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        model, metrics, data = main(
            subject_ids=args.subjects,
            tasks=args.tasks,
            epochs=args.epochs
        )
    elif args.mode == 'compare':
        main_compare_tasks(subject_ids=args.subjects)
