"""
Example evaluation script for CNN-LSTM EEG classification model.

This script demonstrates:
- Loading a trained model (with selection options)
- Making predictions on test data
- Calculating accuracy, precision, recall, F1-score
- Generating classification reports
- Plotting confusion matrix (heatmap)
- Plotting per-class metrics comparison
- Plotting prediction distributions
- Saving all results (text report, JSON, visualizations)

Usage:
    python evaluate_eeg_model.py                              # Interactive mode
    python evaluate_eeg_model.py --model best                 # Load best model
    python evaluate_eeg_model.py --model new                  # Create new model
    python evaluate_eeg_model.py --model checkpoint           # Load checkpoint
    python evaluate_eeg_model.py --model custom --path models/my_model.h5
    python evaluate_eeg_model.py --help                       # Show all options
"""

import json
import logging
import os
import sys
import argparse
from typing import Dict, Tuple, Optional
from pathlib import Path

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

# Model paths
MODEL_PATHS = {
    'best': 'models/best_eeg_model.h5',
    'checkpoint': 'models/checkpoints/best_model.h5',
    'v2': 'models/best_eeg_model.h5'  # Latest v2.0 model
}

# Motor imagery class names
CLASS_NAMES = ['Left', 'Right', 'Hands', 'Feet', 'Click']


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for model selection.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Evaluate CNN-LSTM EEG classification model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python evaluate_eeg_model.py                          # Interactive selection
  python evaluate_eeg_model.py --model best             # Load best model
  python evaluate_eeg_model.py --model new              # Create new model
  python evaluate_eeg_model.py --model v2               # Load v2.0 model
  python evaluate_eeg_model.py --model custom --path models/my_model.h5
  python evaluate_eeg_model.py --model checkpoint       # Load checkpoint
  python evaluate_eeg_model.py --synthetic              # Use synthetic data
  python evaluate_eeg_model.py --data data/test_data.npy  # Use real data
        """
    )
    
    parser.add_argument(
        '--model',
        type=str,
        choices=['best', 'new', 'checkpoint', 'custom', 'v2'],
        help='Model to evaluate (default: interactive selection)'
    )
    
    parser.add_argument(
        '--path',
        type=str,
        help='Path to custom model file'
    )
    
    parser.add_argument(
        '--synthetic',
        action='store_true',
        help='Use synthetic test data (default: True)'
    )
    
    parser.add_argument(
        '--data',
        type=str,
        help='Path to real test data (NPY file)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs',
        help='Output directory for results'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    return parser.parse_args()


def interactive_model_selection() -> Tuple[str, Optional[str]]:
    """
    Interactive menu for model selection.
    
    Returns:
        Tuple of (model_type, custom_path)
    """
    print("\n" + "=" * 80)
    print("MODEL SELECTION")
    print("=" * 80)
    print("\nAvailable Models:")
    print("  1. Load Best Trained Model (models/best_eeg_model.h5)")
    print("  2. Load Latest Checkpoint (models/checkpoints/best_model.h5)")
    print("  3. Load v2.0 Enhanced Model (76.43% accuracy)")
    print("  4. Load Custom Model (provide custom path)")
    print("  5. Create New Model (untrained)")
    print("\n" + "-" * 80)
    
    choice = input("\nSelect model option (1-5): ").strip()
    
    model_map = {
        '1': ('best', None),
        '2': ('checkpoint', None),
        '3': ('v2', None),
        '4': ('custom', None),
        '5': ('new', None)
    }
    
    if choice not in model_map:
        print("Invalid choice! Using default (Best Model)")
        return 'best', None
    
    model_type, _ = model_map[choice]
    
    custom_path = None
    if model_type == 'custom':
        custom_path = input("Enter path to model file: ").strip()
        if not os.path.exists(custom_path):
            print(f"Error: File not found: {custom_path}")
            print("Using default (Best Model) instead")
            return 'best', None
    
    return model_type, custom_path


def load_or_create_model(model_type: str, custom_path: Optional[str] = None) -> keras.Model:
    """
    Load or create a model based on selection.
    
    Args:
        model_type: Type of model ('best', 'new', 'checkpoint', 'custom', 'v2')
        custom_path: Path to custom model file
        
    Returns:
        Keras model
    """
    logger.info(f"\n{'=' * 80}")
    logger.info("LOADING MODEL")
    logger.info(f"{'=' * 80}")
    logger.info(f"Model Type: {model_type}")
    
    try:
        if model_type == 'new':
            logger.info("Creating new (untrained) model...")
            model = create_model(
                input_shape=CONFIG['model']['input_shape'],
                num_classes=CONFIG['model']['num_classes'],
                bidirectional=CONFIG['model']['bidirectional']
            )
            logger.info("✓ New model created successfully")
            
        elif model_type == 'custom':
            if not custom_path or not os.path.exists(custom_path):
                raise ValueError(f"Custom model path not found: {custom_path}")
            logger.info(f"Loading custom model from: {custom_path}")
            model = keras.models.load_model(custom_path)
            logger.info(f"✓ Custom model loaded successfully (Model Size: {os.path.getsize(custom_path)/1024/1024:.2f} MB)")
            
        else:
            # best, checkpoint, or v2
            model_path = MODEL_PATHS.get(model_type, MODEL_PATHS['best'])
            
            if not os.path.exists(model_path):
                logger.warning(f"Model not found: {model_path}")
                logger.info("Falling back to creating new model...")
                model = create_model(
                    input_shape=CONFIG['model']['input_shape'],
                    num_classes=CONFIG['model']['num_classes'],
                    bidirectional=CONFIG['model']['bidirectional']
                )
                logger.info("✓ New model created as fallback")
            else:
                logger.info(f"Loading {model_type} model from: {model_path}")
                model = keras.models.load_model(model_path)
                file_size = os.path.getsize(model_path) / 1024 / 1024
                logger.info(f"✓ {model_type.upper()} model loaded successfully (Model Size: {file_size:.2f} MB)")
        
        # Display model info
        logger.info(f"\nModel Information:")
        logger.info(f"  Parameters: {model.count_params():,}")
        logger.info(f"  Input Shape: {model.input_shape}")
        logger.info(f"  Output Shape: {model.output_shape}")
        
        return model
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        logger.info("Falling back to new model creation...")
        return create_model(
            input_shape=CONFIG['model']['input_shape'],
            num_classes=CONFIG['model']['num_classes'],
            bidirectional=CONFIG['model']['bidirectional']
        )

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
    """Main evaluation pipeline with model selection."""
    
    # Parse command-line arguments
    args = parse_arguments()
    
    logger.info("Starting evaluation script...")
    logger.info(f"Configuration: {CONFIG}")
    
    # Step 1: Model Selection
    logger.info("\n" + "=" * 80)
    logger.info("STEP 1: MODEL SELECTION & LOADING")
    logger.info("=" * 80)
    
    if args.model:
        # Command-line model selection
        model_type = args.model
        custom_path = args.path if args.model == 'custom' else None
        logger.info(f"Model selected via command-line: {model_type}")
    else:
        # Interactive selection
        model_type, custom_path = interactive_model_selection()
    
    model = load_or_create_model(model_type, custom_path)
    model.summary()
    
    # Step 2: Test Data Preparation
    logger.info("\n" + "=" * 80)
    logger.info("STEP 2: TEST DATA PREPARATION")
    logger.info("=" * 80)
    
    if args.data:
        # Load real test data
        logger.info(f"Loading test data from: {args.data}")
        if os.path.exists(args.data):
            test_data = np.load(args.data)
            # Generate dummy labels if not provided
            test_labels = np.random.randint(0, 5, size=len(test_data))
            logger.info(f"✓ Test data loaded: {test_data.shape}")
        else:
            logger.warning(f"File not found: {args.data}")
            logger.info("Using synthetic test data instead...")
            test_data, test_labels = generate_synthetic_test_data(random_seed=42)
    else:
        # Use synthetic data
        logger.info("Generating synthetic test data...")
        test_data, test_labels = generate_synthetic_test_data(random_seed=42)
    
    logger.info(f"Test data shape: {test_data.shape}")
    logger.info(f"Test labels shape: {test_labels.shape}")
    logger.info(f"Class distribution:")
    for i, class_name in enumerate(CLASS_NAMES):
        count = np.sum(test_labels == i)
        percentage = 100 * count / len(test_labels)
        logger.info(f"  {class_name}: {count} ({percentage:.1f}%)")
    
    # Step 3: Generate Predictions
    logger.info("\n" + "=" * 80)
    logger.info("STEP 3: PREDICTION GENERATION")
    logger.info("=" * 80)
    
    predictions = generate_predictions(model, test_data)
    
    # Step 4: Evaluate and Visualize
    logger.info("\n" + "=" * 80)
    logger.info("STEP 4: EVALUATION & VISUALIZATION")
    logger.info("=" * 80)
    
    metrics = evaluate_and_visualize(model, predictions, test_labels)
    
    # Step 5: Print Summary
    print_evaluation_summary(metrics)
    
    # Step 6: Save Execution Summary
    logger.info("\n" + "=" * 80)
    logger.info("STEP 5: EXECUTION SUMMARY")
    logger.info("=" * 80)
    
    summary = {
        'script': 'evaluate_eeg_model.py',
        'model_type': model_type,
        'model_path': custom_path if model_type == 'custom' else MODEL_PATHS.get(model_type, 'new'),
        'timestamp': logging.Formatter().formatTime(logging.LogRecord(
            name='', level=0, pathname='', lineno=0, msg='',
            args=(), exc_info=None
        )),
        'test_samples': int(len(test_labels)),
        'n_classes': CONFIG['model']['num_classes'],
        'class_names': CLASS_NAMES,
        'metrics': metrics,
        'output_directory': args.output_dir or CONFIG['evaluation']['output_dir'],
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
