"""
Example evaluation script for CNN-LSTM EEG classification model.

This script demonstrates:
- Loading a trained model
- Making predictions on test data
- Calculating accuracy, precision, recall, F1-score
- Generating classification reports
- Plotting confusion matrix (heatmap)
- Plotting per-class metrics comparison
- Plotting prediction distributions
- Saving all results (text report, JSON, visualizations)

Usage:
    python evaluate_eeg_model.py
"""

import json
import logging
import os
import sys
from typing import Dict, Tuple

import numpy as np
from tensorflow import keras

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from evaluate import ModelEvaluator
from model import create_model


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BCI')


# Configuration
CONFIG = {
    'model': {
        'input_shape': (320, 64),
        'num_classes': 5,
        'bidirectional': True
    },
    'evaluation': {
        'batch_size': 32,
        'output_dir': 'outputs'
    }
}

# Motor imagery class names
CLASS_NAMES = ['Left', 'Right', 'Hands', 'Feet', 'Click']

# Test data parameters
TEST_DATA_PARAMS = {
    'n_samples': 200,
    'n_channels': 320,
    'n_timesteps': 64,
    'n_classes': 5,
    'class_distribution': [0.2, 0.2, 0.2, 0.2, 0.2]  # Balanced classes
}


def generate_synthetic_test_data(random_seed: int = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic EEG test data for demonstration.
    
    Args:
        random_seed: Random seed for reproducibility
        
    Returns:
        Tuple of (test_data, test_labels)
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    logger.info("Generating synthetic test data...")
    
    n_samples = TEST_DATA_PARAMS['n_samples']
    n_channels = TEST_DATA_PARAMS['n_channels']
    n_timesteps = TEST_DATA_PARAMS['n_timesteps']
    n_classes = TEST_DATA_PARAMS['n_classes']
    
    # Generate random EEG data (simulated)
    test_data = np.random.randn(n_samples, n_channels, n_timesteps).astype(np.float32)
    
    # Add class-specific patterns (for more realistic data)
    for i in range(n_samples):
        class_idx = np.random.randint(0, n_classes)
        # Add some structure to the data
        test_data[i] += class_idx * 0.1
        test_data[i] += np.sin(np.linspace(0, 2 * np.pi, n_timesteps)) * 0.2
    
    # Generate corresponding labels
    test_labels = np.random.choice(
        n_classes,
        size=n_samples,
        p=TEST_DATA_PARAMS['class_distribution']
    )
    
    logger.info(f"Generated test data shape: {test_data.shape}")
    logger.info(f"Generated test labels shape: {test_labels.shape}")
    logger.info(f"Class distribution: {np.bincount(test_labels)}")
    
    return test_data, test_labels


def generate_predictions(model: keras.Model, test_data: np.ndarray) -> np.ndarray:
    """
    Generate predictions using the model.
    
    Args:
        model: Trained Keras model
        test_data: Test data
        
    Returns:
        Model predictions (probabilities)
    """
    logger.info("Generating model predictions...")
    
    predictions = model.predict(
        test_data,
        batch_size=CONFIG['evaluation']['batch_size'],
        verbose=1
    )
    
    logger.info(f"Predictions shape: {predictions.shape}")
    logger.info(f"Predictions min/max: {predictions.min():.4f} / {predictions.max():.4f}")
    
    return predictions


def evaluate_and_visualize(model: keras.Model, test_data: np.ndarray,
                          test_labels: np.ndarray) -> Dict:
    """
    Complete evaluation pipeline.
    
    Produces:
    - Accuracy, precision, recall, F1-score (macro and weighted)
    - Confusion matrix heatmap
    - Per-class metrics comparison chart
    - Prediction distribution histogram
    - Comprehensive text report
    - JSON results file
    
    Args:
        model: Trained Keras model
        test_data: Test data
        test_labels: Test labels
        
    Returns:
        Dictionary of evaluation metrics
    """
    logger.info("=" * 80)
    logger.info("STARTING EVALUATION PIPELINE")
    logger.info("=" * 80)
    
    # Create evaluator
    evaluator = ModelEvaluator(
        model=model,
        config=CONFIG,
        n_classes=CONFIG['model']['num_classes']
    )
    
    # Set class names for better visualization
    evaluator.set_class_names(CLASS_NAMES)
    
    # Evaluate on test data
    logger.info("\n[1/5] Evaluating on test data...")
    metrics = evaluator.evaluate(test_data, test_labels)
    
    # Plot confusion matrix
    logger.info("[2/5] Plotting confusion matrix...")
    evaluator.plot_confusion_matrix()
    
    # Plot metrics comparison
    logger.info("[3/5] Plotting metrics comparison...")
    evaluator.plot_metrics_comparison()
    
    # Plot prediction distribution
    logger.info("[4/5] Plotting prediction distribution...")
    evaluator.plot_prediction_distribution()
    
    # Save results
    logger.info("[5/5] Saving results...")
    evaluator.save_evaluation_report()
    evaluator.save_results_json()
    
    logger.info("=" * 80)
    logger.info("EVALUATION COMPLETE")
    logger.info("=" * 80)
    
    return metrics


def print_evaluation_summary(metrics: Dict) -> None:
    """
    Print a formatted summary of evaluation metrics.
    
    Args:
        metrics: Dictionary of evaluation metrics
    """
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    
    print("\nOVERALL METRICS:")
    print("-" * 80)
    print(f"  Accuracy:        {metrics['accuracy']:.4f}")
    print(f"  Precision (macro):   {metrics['precision_macro']:.4f}")
    print(f"  Precision (weighted): {metrics['precision_weighted']:.4f}")
    print(f"  Recall (macro):      {metrics['recall_macro']:.4f}")
    print(f"  Recall (weighted):   {metrics['recall_weighted']:.4f}")
    print(f"  F1-Score (macro):    {metrics['f1_macro']:.4f}")
    print(f"  F1-Score (weighted): {metrics['f1_weighted']:.4f}")
    
    print("\nPER-CLASS METRICS:")
    print("-" * 80)
    for i, class_name in enumerate(CLASS_NAMES):
        print(f"\n{class_name}:")
        print(f"  Precision: {metrics['precision_per_class'][i]:.4f}")
        print(f"  Recall:    {metrics['recall_per_class'][i]:.4f}")
        print(f"  F1-Score:  {metrics['f1_per_class'][i]:.4f}")
    
    print("\nCONFUSION MATRIX:")
    print("-" * 80)
    cm = np.array(metrics['confusion_matrix'])
    print("             " + "  ".join(f"{name:>8}" for name in CLASS_NAMES))
    for i, row in enumerate(cm):
        print(f"{CLASS_NAMES[i]:>12}" + "  ".join(f"{val:>8d}" for val in row))
    
    print("\n" + "=" * 80)


def main():
    """Main evaluation pipeline."""
    
    logger.info("Starting evaluation script...")
    logger.info(f"Configuration: {CONFIG}")
    
    # Step 1: Create and display model information
    logger.info("\n" + "=" * 80)
    logger.info("STEP 1: MODEL CREATION")
    logger.info("=" * 80)
    
    model = create_model(
        input_shape=CONFIG['model']['input_shape'],
        num_classes=CONFIG['model']['num_classes'],
        bidirectional=CONFIG['model']['bidirectional']
    )
    
    model.summary()
    
    # Step 2: Generate test data
    logger.info("\n" + "=" * 80)
    logger.info("STEP 2: TEST DATA GENERATION")
    logger.info("=" * 80)
    
    test_data, test_labels = generate_synthetic_test_data(random_seed=42)
    
    logger.info(f"Test data shape: {test_data.shape}")
    logger.info(f"Test labels shape: {test_labels.shape}")
    logger.info(f"Class distribution:")
    for i, class_name in enumerate(CLASS_NAMES):
        count = np.sum(test_labels == i)
        percentage = 100 * count / len(test_labels)
        logger.info(f"  {class_name}: {count} ({percentage:.1f}%)")
    
    # Step 3: Generate predictions
    logger.info("\n" + "=" * 80)
    logger.info("STEP 3: PREDICTION GENERATION")
    logger.info("=" * 80)
    
    predictions = generate_predictions(model, test_data)
    
    # Step 4: Evaluate and visualize
    logger.info("\n" + "=" * 80)
    logger.info("STEP 4: EVALUATION & VISUALIZATION")
    logger.info("=" * 80)
    
    metrics = evaluate_and_visualize(model, predictions, test_labels)
    
    # Step 5: Print summary
    print_evaluation_summary(metrics)
    
    # Step 6: Save execution summary
    logger.info("\n" + "=" * 80)
    logger.info("STEP 5: EXECUTION SUMMARY")
    logger.info("=" * 80)
    
    summary = {
        'script': 'evaluate_eeg_model.py',
        'timestamp': logging.Formatter().formatTime(logging.LogRecord(
            name='', level=0, pathname='', lineno=0, msg='',
            args=(), exc_info=None
        )),
        'test_samples': int(len(test_labels)),
        'n_classes': CONFIG['model']['num_classes'],
        'class_names': CLASS_NAMES,
        'metrics': metrics,
        'output_directory': CONFIG['evaluation']['output_dir'],
        'output_files': [
            'confusion_matrix_*.png',
            'metrics_comparison_*.png',
            'prediction_distribution_*.png',
            'evaluation_report_*.txt',
            'evaluation_results_*.json'
        ]
    }
    
    logger.info(f"\nEvaluation complete!")
    logger.info(f"Test samples: {summary['test_samples']}")
    logger.info(f"Overall accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"F1-Score (weighted): {metrics['f1_weighted']:.4f}")
    logger.info(f"\nResults saved to {CONFIG['evaluation']['output_dir']}/")
    
    # Save summary to JSON
    os.makedirs(CONFIG['evaluation']['output_dir'], exist_ok=True)
    summary_path = os.path.join(
        CONFIG['evaluation']['output_dir'],
        'evaluation_summary.json'
    )
    with open(summary_path, 'w') as f:
        # Convert numpy types
        summary_serializable = {
            k: v.tolist() if isinstance(v, np.ndarray) else v
            for k, v in summary.items() if k != 'metrics'
        }
        summary_serializable['metrics'] = {
            k: v.tolist() if isinstance(v, np.ndarray) else v
            for k, v in metrics.items()
        }
        json.dump(summary_serializable, f, indent=2)
    
    logger.info(f"Summary saved to {summary_path}")
    
    logger.info("\n" + "=" * 80)
    logger.info("EVALUATION SCRIPT COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
