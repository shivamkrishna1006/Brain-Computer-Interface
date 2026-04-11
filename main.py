"""
Main entry point for BCI Interface.

This module provides the production-ready CLI for training, evaluating, and running
the BCI system in real-time with comprehensive error handling and logging.
"""

import logging
import argparse
import sys
import traceback
from pathlib import Path
from typing import Optional

import numpy as np
import tensorflow as tf

# Import modules
from src.utils import load_config, setup_logging, create_directories, print_config
from src.data_loader import create_data_loaders
from src.preprocessing import preprocess_eeg_batch
from src.model import create_model
from src.train import ModelTrainer
from src.evaluate import ModelEvaluator
from src.realtime import create_realtime_processor
from src.click_detection import create_click_detector
from src.model_manager import ModelManager, ModelValidator


def setup_environment() -> None:
    """
    Configure TensorFlow and other settings.
    
    Raises:
        RuntimeError: If TensorFlow setup fails
    """
    try:
        # Set random seeds for reproducibility
        np.random.seed(42)
        tf.random.set_seed(42)
        
        # Configure TensorFlow
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                print(f"✓ GPU detected: {len(gpus)} GPU(s) available")
            except RuntimeError as e:
                print(f"⚠ GPU configuration warning: {e}")
        else:
            print("ℹ No GPU detected, using CPU")
            
    except Exception as e:
        raise RuntimeError(f"Failed to setup TensorFlow environment: {e}")


def main_train(config_path: str = 'config.yaml', output_model: Optional[str] = None) -> str:
    """
    Train the BCI model with comprehensive error handling.
    
    Args:
        config_path: Path to configuration file
        output_model: Optional name for output model (without .h5)
        
    Returns:
        Path to saved model
        
    Raises:
        FileNotFoundError: If config file not found
        ValueError: If configuration is invalid
        RuntimeError: If training fails
    """
    try:
        # Load configuration
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        config = load_config(config_path)
        
        # Setup logging
        logger = setup_logging(config)
        
        # Create directories
        create_directories(config)
        
        # Print configuration
        print_config(config, logger)
        
        logger.info("=" * 80)
        logger.info("TRAINING PIPELINE - STARTING")
        logger.info("=" * 80)
        
        # Validate configuration
        logger.info("Step 1/6: Validating configuration...")
        if not all(key in config for key in ['training', 'data']):
            raise ValueError("Configuration missing required sections: training, data")
        logger.info("✓ Configuration validated")
        
        # Create trainer
        logger.info("Step 2/6: Initializing model trainer...")
        trainer = ModelTrainer(config)
        logger.info("✓ Model trainer initialized")
        
        # Prepare data
        logger.info("Step 3/6: Preparing training data...")
        train_set, val_set, test_set = trainer.prepare_data()
        train_data, train_labels = train_set
        val_data, val_labels = val_set
        test_data, test_labels = test_set
        logger.info(f"✓ Data prepared: train={len(train_data)}, val={len(val_data)}, test={len(test_data)}")
        
        # Train model
        logger.info("Step 4/6: Training CNN-LSTM model...")
        history = trainer.train(train_data, train_labels, val_data, val_labels)
        logger.info("✓ Training completed")
        
        # Evaluate model
        logger.info("Step 5/6: Evaluating model...")
        evaluator = ModelEvaluator(trainer.model, config)
        metrics = evaluator.evaluate(test_data, test_labels)
        logger.info(f"✓ Test Accuracy: {metrics.get('accuracy', 'N/A'):.4f}")
        
        # Generate plots
        logger.info("Generating evaluation plots...")
        try:
            evaluator.plot_confusion_matrix()
            evaluator.plot_roc_curve()
            evaluator.plot_prediction_distribution()
            evaluator.save_evaluation_report()
            logger.info("✓ Evaluation plots generated")
        except Exception as e:
            logger.warning(f"Failed to generate plots: {e}")
        
        # Save results
        logger.info("Step 6/6: Saving model and results...")
        
        # Save model using ModelManager
        model_manager = ModelManager(logger=logger)
        model_name = output_model or f"bci_model_{Path(config_path).stem}"
        model_path = model_manager.save_model(
            trainer.model,
            model_name,
            config,
            metrics=metrics,
            overwrite=True
        )
        
        # Validate saved model
        validator = ModelValidator(logger=logger)
        validation_report = validator.validate_model(trainer.model)
        if not validation_report['valid']:
            logger.warning(f"Model validation warnings: {validation_report}")
        
        logger.info("✓ Model saved successfully")
        
        logger.info("=" * 80)
        logger.info("TRAINING COMPLETED SUCCESSFULLY")
        logger.info(f"Model saved to: {model_path}")
        logger.info("=" * 80)
        
        return str(model_path)
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"✗ Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Training failed: {e}")
        logger.error(f"Detailed error: {traceback.format_exc()}")
        sys.exit(1)


def main_evaluate(model_path: str, config_path: str = 'config.yaml') -> None:
    """
    Evaluate a trained model with comprehensive error handling.
    
    Args:
        model_path: Path to trained model file or model name
        config_path: Path to configuration file
        
    Raises:
        FileNotFoundError: If model or config not found
    """
    try:
        # Load configuration
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        config = load_config(config_path)
        
        # Setup logging
        logger = setup_logging(config)
        
        logger.info("=" * 80)
        logger.info("EVALUATION PIPELINE - STARTING")
        logger.info("=" * 80)
        
        # Load model using ModelManager
        logger.info("Step 1/4: Loading trained model...")
        model_manager = ModelManager(logger=logger)
        
        # Try to load by name first, then by path
        try:
            model_name = Path(model_path).stem
            model, metadata = model_manager.load_model(model_name)
            logger.info(f"✓ Model loaded from manager: {model_name}")
        except FileNotFoundError:
            if Path(model_path).exists():
                model = tf.keras.models.load_model(str(model_path))
                metadata = {}
                logger.info(f"✓ Model loaded from path: {model_path}")
            else:
                raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Validate model
        logger.info("Step 2/4: Validating model...")
        validator = ModelValidator(logger=logger)
        validation_report = validator.validate_model(model)
        if not validation_report['valid']:
            logger.error(f"Model validation failed: {validation_report['errors']}")
            sys.exit(1)
        logger.info("✓ Model validation passed")
        
        # Load test data
        logger.info("Step 3/4: Preparing evaluation data...")
        data, labels = create_data_loaders(config)
        data, _ = preprocess_eeg_batch(data, config)
        
        from src.utils import split_data
        _, _, test_set = split_data(data, labels, 
                                    train_ratio=0.6, val_ratio=0.2, test_ratio=0.2)
        test_data, test_labels = test_set
        logger.info(f"✓ Test data prepared: {len(test_data)} samples")
        
        # Evaluate
        logger.info("Step 4/4: Evaluating model...")
        evaluator = ModelEvaluator(model, config)
        metrics = evaluator.evaluate(test_data, test_labels)
        logger.info(f"✓ Test Accuracy: {metrics.get('accuracy', 'N/A'):.4f}")
        
        # Generate plots
        logger.info("Generating evaluation plots...")
        try:
            evaluator.plot_confusion_matrix()
            evaluator.plot_roc_curve()
            evaluator.plot_prediction_distribution()
            evaluator.save_evaluation_report()
            logger.info("✓ Evaluation plots generated")
        except Exception as e:
            logger.warning(f"Failed to generate plots: {e}")
        
        logger.info("=" * 80)
        logger.info("EVALUATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Evaluation failed: {e}")
        if hasattr(locals().get('logger', None), 'error'):
            logger.error(f"Detailed error: {traceback.format_exc()}")
        sys.exit(1)


def main_realtime(model_path: str, config_path: str = 'config.yaml') -> None:
    """
    Run BCI in real-time mode with comprehensive error handling.
    
    Args:
        model_path: Path to trained model file or model name
        config_path: Path to configuration file
        
    Raises:
        FileNotFoundError: If model or config not found
    """
    try:
        # Load configuration
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        config = load_config(config_path)
        
        # Setup logging
        logger = setup_logging(config)
        
        logger.info("=" * 80)
        logger.info("REAL-TIME BCI SYSTEM - STARTING")
        logger.info("=" * 80)
        
        # Load model
        logger.info("Step 1/3: Loading trained model...")
        model_manager = ModelManager(logger=logger)
        
        try:
            model_name = Path(model_path).stem
            model, metadata = model_manager.load_model(model_name)
            logger.info(f"✓ Model loaded from manager: {model_name}")
        except FileNotFoundError:
            if Path(model_path).exists():
                model = tf.keras.models.load_model(str(model_path))
                logger.info(f"✓ Model loaded from path: {model_path}")
            else:
                raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Validate model
        logger.info("Validating model...")
        validator = ModelValidator(logger=logger)
        validation_report = validator.validate_model(model)
        if not validation_report['valid']:
            logger.error(f"Model validation failed: {validation_report['errors']}")
            sys.exit(1)
        logger.info("✓ Model validated")
        
        # Create real-time processor
        logger.info("Step 2/3: Initializing real-time processor...")
        processor = create_realtime_processor(config, model)
        logger.info("✓ Processor initialized")
        
        # Create click detector
        logger.info("Step 3/3: Initializing click detector...")
        click_detector = create_click_detector(config)
        logger.info("✓ Click detector initialized")
        
        # Register callbacks
        def on_click(timestamp, confidence):
            logger.info(f"Click detected at {timestamp:.3f} with confidence {confidence:.2f}")
        
        def on_release(click_event):
            logger.info(f"Click released: duration={click_event.duration:.3f}s, "
                       f"confidence={click_event.confidence:.2f}")
        
        click_detector.on_click_callback = on_click
        click_detector.on_release_callback = on_release
        
        # Set prediction callback
        def on_prediction(prediction):
            click_event = click_detector.process_prediction(prediction)
            if click_event:
                logger.info(f"Valid click event: {click_event}")
        
        processor.on_prediction_callback = on_prediction
        
        logger.info("=" * 80)
        logger.info("REAL-TIME BCI SYSTEM READY")
        logger.info("=" * 80)
        logger.info("Waiting for EEG data...")
        logger.info("Press Ctrl+C to stop")
        
        # Keep system running
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            processor.stop()
            logger.info("Real-time BCI system stopped")
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Real-time system failed: {e}")
        if hasattr(locals().get('logger', None), 'error'):
            logger.error(f"Detailed error: {traceback.format_exc()}")
        sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments with comprehensive options.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Brain-Computer Interface (BCI) - EEG Motor Imagery Control',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py train
  python main.py train --config config.yaml --output my_model
  python main.py evaluate --model bci_model
  python main.py realtime --model bci_model --config config.yaml
  python main.py list-models

For more information, visit: https://github.com/yourusername/bci-eeg-interface
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train the BCI model')
    train_parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    train_parser.add_argument(
        '--output', '-o',
        type=str,
        help='Name for output model (optional)'
    )
    train_parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing model'
    )
    
    # Evaluate command
    eval_parser = subparsers.add_parser('evaluate', help='Evaluate a trained model')
    eval_parser.add_argument(
        '--model', '-m',
        type=str,
        required=True,
        help='Model name or path to evaluate'
    )
    eval_parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    # Real-time command
    realtime_parser = subparsers.add_parser('realtime', help='Run in real-time mode')
    realtime_parser.add_argument(
        '--model', '-m',
        type=str,
        required=True,
        help='Model name or path to use for inference'
    )
    realtime_parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    # List models command
    list_parser = subparsers.add_parser('list-models', help='List available models')
    list_parser.add_argument(
        '--details',
        action='store_true',
        help='Show detailed model information'
    )
    
    # Delete model command
    delete_parser = subparsers.add_parser('delete-model', help='Delete a trained model')
    delete_parser.add_argument(
        '--model', '-m',
        type=str,
        required=True,
        help='Model name to delete'
    )
    delete_parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    return parser.parse_args()


if __name__ == '__main__':
    try:
        # Setup environment first
        setup_environment()
        
        # Parse arguments
        args = parse_arguments()
        
        # Check if command is specified
        if not args.command:
            # Show help
            parser = argparse.ArgumentParser(description='Brain-Computer Interface (BCI)')
            print("BCI Interface - EEG Motor Imagery Control System")
            print("=" * 80)
            print("\nUsage: python main.py <command> [options]")
            print("\nAvailable commands:")
            print("  train           - Train the BCI model")
            print("  evaluate        - Evaluate a trained model")
            print("  realtime        - Run in real-time mode")
            print("  list-models     - List available models")
            print("  delete-model    - Delete a trained model")
            print("\nRun 'python main.py <command> --help' for more information")
            sys.exit(0)
        
        # Execute command
        if args.command == 'train':
            main_train(
                config_path=args.config,
                output_model=args.output if hasattr(args, 'output') else None
            )
            
        elif args.command == 'evaluate':
            main_evaluate(
                model_path=args.model,
                config_path=args.config
            )
            
        elif args.command == 'realtime':
            main_realtime(
                model_path=args.model,
                config_path=args.config
            )
            
        elif args.command == 'list-models':
            model_manager = ModelManager()
            models = model_manager.list_models()
            
            if not models:
                print("No models found")
            else:
                print("\nAvailable Models:")
                print("=" * 80)
                for model_name, metadata in models.items():
                    print(f"\n▪ {model_name}")
                    if args.details if hasattr(args, 'details') else False:
                        print(f"  Created: {metadata.get('timestamp', 'N/A')}")
                        if 'metrics' in metadata:
                            acc = metadata['metrics'].get('accuracy', 'N/A')
                            print(f"  Accuracy: {acc}")
                        arch = metadata.get('model_architecture', {})
                        print(f"  Parameters: {arch.get('parameters', 'N/A')}")
                        print(f"  Input Shape: {arch.get('input_shape', 'N/A')}")
                    else:
                        timestamp = metadata.get('timestamp', 'N/A')
                        print(f"  Timestamp: {timestamp}")
                        
        elif args.command == 'delete-model':
            model_manager = ModelManager()
            try:
                model_manager.delete_model(
                    args.model,
                    confirm=args.force if hasattr(args, 'force') else False
                )
                print(f"✓ Model '{args.model}' deleted successfully")
            except FileNotFoundError as e:
                print(f"✗ Error: {e}")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Fatal Error: {e}")
        print(f"\nDebug information:")
        print(traceback.format_exc())
        sys.exit(1)
