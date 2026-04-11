"""
Real-Time BCI Mouse Control Demo

This script demonstrates the real-time inference system:
1. Loads a trained CNN-LSTM model
2. Simulates EEG input (or accepts real input)
3. Makes real-time predictions
4. Controls mouse cursor based on motor imagery predictions

Usage:
    python realtime_inference_demo.py --model models/best_eeg_model.h5
    python realtime_inference_demo.py --model models/best_eeg_model.h5 --simulate
    python realtime_inference_demo.py --help

Features:
- Model loading and inference
- Simulated or real EEG input
- Live prediction display
- Mouse action execution
- Safety features (pause, edge detection)
- Real-time statistics

Author: BCI Interface Team
Version: 2.0
Status: Production-Ready
"""

import logging
import argparse
import time
import numpy as np
from pathlib import Path
from datetime import datetime
import yaml
import sys

from src.realtime_inference import (
    RealtimeInferenceEngine,
    CLASS_LABELS,
    ACTION_MAPPING
)
from src.config import load_config, deep_merge, print_config

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING SETUP
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BCI_Demo')


# ─────────────────────────────────────────────────────────────────────────────
# DEFAULT CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    'data': {
        'eeg_channels': 8,
        'sampling_rate': 250,
        'segment_duration': 1.0
    },
    'realtime': {
        'buffer_size': 250,
        'update_interval': 0.1,
        'confidence_threshold': 0.7
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# SYNTHETIC DATA GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_synthetic_eeg_signal(
    class_idx: int,
    n_samples: int = 250,
    n_channels: int = 8,
    sampling_rate: int = 250,
    noise_level: float = 0.1
) -> np.ndarray:
    """
    Generate synthetic EEG signal for a specific class.
    
    Args:
        class_idx: Class index (0-4)
        n_samples: Number of samples
        n_channels: Number of channels
        sampling_rate: Sampling rate in Hz
        noise_level: Noise standard deviation
        
    Returns:
        Synthetic EEG signal (n_samples, n_channels)
    """
    # Create time vector
    t = np.arange(n_samples) / sampling_rate
    
    # Base frequency for this class
    base_freq = 0.5 + class_idx * 0.5
    
    # Initialize signal
    signal = np.zeros((n_samples, n_channels))
    
    # Add class-specific patterns
    for ch in range(n_channels):
        # Primary oscillation (class frequency)
        signal[:, ch] += 0.5 * np.sin(2 * np.pi * base_freq * t)
        
        # Alpha band (8-12 Hz)
        signal[:, ch] += 0.3 * np.sin(2 * np.pi * 10 * t)
        
        # Low frequency drift
        signal[:, ch] += 0.2 * np.sin(2 * np.pi * 0.5 * t)
        
        # Additional frequency for channel variation
        ch_freq = 5 + ch
        signal[:, ch] += 0.2 * np.sin(2 * np.pi * ch_freq * t / 100)
    
    # Add realistic noise
    signal += noise_level * np.random.randn(n_samples, n_channels)
    
    # Normalize
    signal = (signal - signal.mean(axis=0)) / (signal.std(axis=0) + 1e-8)
    
    return signal.astype(np.float32)


# ─────────────────────────────────────────────────────────────────────────────
# DEMO SCENARIOS
# ─────────────────────────────────────────────────────────────────────────────

def demo_simulation(engine: RealtimeInferenceEngine, num_iterations: int = 20):
    """
    Simulation mode: generate synthetic EEG and make predictions.
    
    Args:
        engine: RealtimeInferenceEngine instance
        num_iterations: Number of prediction iterations
    """
    logger.info("=" * 80)
    logger.info("SIMULATION MODE - Synthetic EEG Input")
    logger.info("=" * 80)
    logger.info(f"Running {num_iterations} prediction iterations...\n")
    
    engine.start()
    
    try:
        for iteration in range(num_iterations):
            # Randomly select class for this iteration
            class_idx = np.random.randint(0, 5)
            class_label = CLASS_LABELS[class_idx]
            
            logger.info(f"\n[Iteration {iteration+1}/{num_iterations}] "
                       f"Simulating {class_label} (class {class_idx})")
            
            # Generate synthetic signal
            signal = generate_synthetic_eeg_signal(
                class_idx=class_idx,
                n_samples=engine.buffer_size,
                n_channels=engine.n_channels
            )
            
            # Add signal to buffer
            engine.add_samples(signal)
            
            logger.info(f"  Buffer: {len(engine.eeg_buffer)}/{engine.buffer_size} samples")
            
            # Make prediction
            if engine.is_ready():
                result = engine.predict()
                
                if result:
                    logger.info(f"  Prediction: {result['class_label']} "
                               f"(confidence: {result['confidence']:.4f})")
                    
                    # Print probability distribution
                    logger.info("  Probabilities:")
                    for i, prob in enumerate(result['probability_distribution']):
                        label = CLASS_LABELS[i]
                        logger.info(f"    {label}: {prob:.4f}")
                    
                    # Execute action
                    action = engine.controller.predict_and_act(
                        result['predicted_class'],
                        result['confidence']
                    )
                    
                    if action:
                        logger.info(f"  ✓ Action executed: {action}")
            
            # Simulate delay between samples
            time.sleep(0.1)
        
        # Final statistics
        logger.info("\n" + "=" * 80)
        logger.info("SIMULATION COMPLETE")
        logger.info("=" * 80)
        
        status = engine.get_status()
        logger.info(f"Total predictions: {status['predictions_made']}")
        logger.info(f"Uptime: {status['uptime_seconds']:.1f}s")
        logger.info(f"Mouse actions: {status['controller_stats']['action_counts']}")
        
    except KeyboardInterrupt:
        logger.info("\nSimulation interrupted by user")
    finally:
        engine.stop()


def demo_batch_prediction(engine: RealtimeInferenceEngine, 
                         n_classes: int = 5,
                         n_per_class: int = 3):
    """
    Batch mode: test prediction for each class.
    
    Args:
        engine: RealtimeInferenceEngine instance
        n_classes: Number of classes
        n_per_class: Predictions per class
    """
    logger.info("=" * 80)
    logger.info("BATCH MODE - Testing Each Class")
    logger.info("=" * 80)
    logger.info(f"Testing {n_per_class} predictions per class...\n")
    
    engine.start()
    
    results_summary = {i: [] for i in range(n_classes)}
    
    try:
        for class_idx in range(n_classes):
            class_label = CLASS_LABELS[class_idx]
            logger.info(f"\nTesting class: {class_label}")
            
            for attempt in range(n_per_class):
                # Generate signal for this class
                signal = generate_synthetic_eeg_signal(
                    class_idx=class_idx,
                    n_samples=engine.buffer_size
                )
                
                # Clear buffer and add new signal
                engine.eeg_buffer.clear()
                engine.add_samples(signal)
                
                # Make prediction
                result = engine.predict()
                
                if result:
                    predicted_label = result['class_label']
                    confidence = result['confidence']
                    correct = (result['predicted_class'] == class_idx)
                    
                    results_summary[class_idx].append({
                        'predicted': result['predicted_class'],
                        'confidence': confidence,
                        'correct': correct
                    })
                    
                    status = "✓" if correct else "✗"
                    logger.info(f"  {status} Attempt {attempt+1}: Predicted {predicted_label} "
                               f"({confidence:.4f})")
                
                time.sleep(0.1)
        
        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("BATCH RESULTS SUMMARY")
        logger.info("=" * 80)
        
        for class_idx in range(n_classes):
            results = results_summary[class_idx]
            if results:
                correct = sum(1 for r in results if r['correct'])
                total = len(results)
                accuracy = 100 * correct / total
                avg_confidence = np.mean([r['confidence'] for r in results])
                
                logger.info(f"Class {CLASS_LABELS[class_idx]:8s}: "
                           f"Accuracy {accuracy:5.1f}% ({correct}/{total}), "
                           f"Avg Conf: {avg_confidence:.4f}")
        
    except KeyboardInterrupt:
        logger.info("\nBatch testing interrupted by user")
    finally:
        engine.stop()


def demo_interactive(engine: RealtimeInferenceEngine):
    """
    Interactive mode: user can manually trigger predictions.
    
    Args:
        engine: RealtimeInferenceEngine instance
    """
    logger.info("=" * 80)
    logger.info("INTERACTIVE MODE - Manual Input")
    logger.info("=" * 80)
    logger.info("Commands:")
    logger.info("  0-4: Generate signal for class (Left, Right, Hands, Feet, Click)")
    logger.info("  p: Pause/Resume controller")
    logger.info("  s: Show status")
    logger.info("  q: Quit\n")
    
    engine.start()
    
    try:
        while True:
            command = input("Enter command: ").strip().lower()
            
            if command == 'q':
                break
            
            elif command in '01234':
                class_idx = int(command)
                class_label = CLASS_LABELS[class_idx]
                
                logger.info(f"\nGenerating signal for {class_label}...")
                signal = generate_synthetic_eeg_signal(
                    class_idx=class_idx,
                    n_samples=engine.buffer_size
                )
                
                engine.eeg_buffer.clear()
                engine.add_samples(signal)
                
                result = engine.predict()
                if result:
                    logger.info(f"Prediction: {result['class_label']} "
                               f"({result['confidence']:.4f})")
                    
                    action = engine.controller.predict_and_act(
                        result['predicted_class'],
                        result['confidence']
                    )
            
            elif command == 'p':
                paused = engine.controller.paused
                engine.controller.set_pause(not paused)
            
            elif command == 's':
                status = engine.get_status()
                logger.info(f"\nStatus:")
                logger.info(f"  Running: {status['running']}")
                logger.info(f"  Uptime: {status['uptime_seconds']:.1f}s")
                logger.info(f"  Buffer: {status['buffer_usage']}")
                logger.info(f"  Predictions: {status['predictions_made']}")
                logger.info(f"  Paused: {status['controller_paused']}")
                logger.info(f"  Actions: {status['controller_stats']['action_counts']}\n")
            
            else:
                logger.info("Unknown command")
    
    except KeyboardInterrupt:
        logger.info("\nInteractive mode interrupted")
    finally:
        engine.stop()


# ─────────────────────────────────────────────────────────────────────────────
# ARGUMENT PARSING
# ─────────────────────────────────────────────────────────────────────────────

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Real-Time BCI Mouse Control Demo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Simulate with default model
  python realtime_inference_demo.py --model models/best_eeg_model.h5 --simulate
  
  # Interactive mode
  python realtime_inference_demo.py --model models/best_eeg_model.h5 --interactive
  
  # Batch testing
  python realtime_inference_demo.py --model models/best_eeg_model.h5 --batch
  
  # Custom configuration
  python realtime_inference_demo.py --model models/best_eeg_model.h5 \\
    --config custom_config.yaml --simulate
        """
    )
    
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to trained model (.h5 or SavedModel directory)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to custom configuration YAML'
    )
    
    parser.add_argument(
        '--simulate',
        action='store_true',
        default=False,
        help='Run simulation mode with synthetic data (default)'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        default=False,
        help='Run interactive mode for manual testing'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        default=False,
        help='Run batch testing mode (test each class)'
    )
    
    parser.add_argument(
        '--iterations',
        type=int,
        default=20,
        help='Number of iterations for simulation mode (default: 20)'
    )
    
    parser.add_argument(
        '--move-distance',
        type=int,
        default=50,
        help='Pixels to move cursor per action (default: 50)'
    )
    
    parser.add_argument(
        '--confidence-threshold',
        type=float,
        default=0.7,
        help='Minimum confidence to trigger action (default: 0.7)'
    )
    
    return parser.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    """Main demo function."""
    # Parse arguments
    args = parse_arguments()
    
    # Load configuration (auto-detect config.yaml or use custom)
    config = load_config(args.config, defaults=DEFAULT_CONFIG)
    
    # Verify model exists
    if not Path(args.model).exists():
        logger.error(f"Model not found: {args.model}")
        sys.exit(1)
    
    logger.info("=" * 80)
    logger.info("REAL-TIME BCI MOUSE CONTROL DEMO")
    logger.info("=" * 80)
    logger.info(f"Model: {args.model}")
    logger.info(f"Move distance: {args.move_distance}px")
    logger.info(f"Confidence threshold: {args.confidence_threshold}\n")
    
    # Create inference engine
    try:
        engine = RealtimeInferenceEngine(
            model_path=args.model,
            config=config,
            move_distance=args.move_distance,
            confidence_threshold=args.confidence_threshold
        )
    except Exception as e:
        logger.error(f"Failed to create inference engine: {e}")
        sys.exit(1)
    
    # Run selected mode
    try:
        if args.batch:
            demo_batch_prediction(engine, n_per_class=3)
        elif args.interactive:
            demo_interactive(engine)
        else:
            # Default: simulation mode
            demo_simulation(engine, num_iterations=args.iterations)
    
    except KeyboardInterrupt:
        logger.info("\nDemo interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Demo error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
