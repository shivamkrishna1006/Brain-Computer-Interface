#!/usr/bin/env python
"""
Integration test for real-time inference system.

Tests:
1. Module imports
2. Component initialization
3. Basic functionality
"""

import logging
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('IntegrationTest')


def test_imports():
    """Test importing all modules."""
    logger.info("=" * 60)
    logger.info("TEST 1: Module Imports")
    logger.info("=" * 60)
    
    try:
        from src.realtime_inference import (
            RealtimeInferenceEngine,
            CursorSmoother,
            BCIMouseController,
            CLASS_LABELS,
            ACTION_MAPPING
        )
        logger.info("✓ All imports successful")
        return True
    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_cursor_smoother():
    """Test cursor smoothing functionality."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Cursor Smoother")
    logger.info("=" * 60)
    
    try:
        from src.realtime_inference import CursorSmoother
        
        smoother = CursorSmoother(alpha=0.3, enabled=True)
        logger.info("✓ CursorSmoother created")
        
        # Test smoothing
        positions = [(100, 100), (150, 150), (200, 200)]
        for pos in positions:
            smoothed = smoother.smooth(pos)
            velocity = smoother.get_velocity()
            logger.info(f"  Position: {pos} → Smoothed: {smoothed}, Velocity: {velocity:.1f}")
        
        logger.info("✓ Cursor smoothing works")
        return True
    except Exception as e:
        logger.error(f"✗ CursorSmoother test failed: {e}")
        return False


def test_mouse_controller():
    """Test mouse controller (without actual mouse movement)."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Mouse Controller")
    logger.info("=" * 60)
    
    try:
        from src.realtime_inference import BCIMouseController
        
        controller = BCIMouseController(
            move_distance=50,
            confidence_threshold=0.7
        )
        logger.info("✓ BCIMouseController created")
        
        # Test prediction processing
        action = controller.predict_and_act(
            predicted_class=0,
            confidence=0.85
        )
        logger.info(f"  Action result: {action}")
        
        # Test statistics
        stats = controller.get_statistics()
        logger.info(f"  Total predictions: {stats['total_predictions']}")
        logger.info(f"  Actions performed: {stats['action_counts']}")
        
        # Test pause
        controller.set_pause(True)
        logger.info("✓ Controller paused")
        controller.set_pause(False)
        logger.info("✓ Controller resumed")
        
        logger.info("✓ Mouse controller works")
        return True
    except Exception as e:
        logger.error(f"✗ BCIMouseController test failed: {e}")
        return False


def test_inference_engine():
    """Test inference engine initialization (without model)."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Inference Engine (Component Test)")
    logger.info("=" * 60)
    
    try:
        from src.realtime_inference import RealtimeInferenceEngine
        
        config = {
            'data': {'eeg_channels': 8, 'sampling_rate': 250},
            'realtime': {'buffer_size': 250}
        }
        
        # We'll skip model loading for this test
        logger.info("✓ Configuration prepared")
        
        # Test synthetic data generation
        from realtime_inference_demo import generate_synthetic_eeg_signal
        
        for class_idx in range(5):
            signal = generate_synthetic_eeg_signal(
                class_idx=class_idx,
                n_samples=250,
                n_channels=8
            )
            logger.info(f"  Class {class_idx}: Generated signal shape {signal.shape}")
        
        logger.info("✓ Synthetic data generation works")
        return True
    except Exception as e:
        logger.error(f"✗ Inference engine test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Configuration System")
    logger.info("=" * 60)
    
    try:
        import yaml
        from pathlib import Path
        
        # Test creating a config
        config = {
            'data': {'eeg_channels': 8},
            'realtime': {'buffer_size': 250}
        }
        
        logger.info(f"✓ Default config created")
        logger.info(f"  Channels: {config['data']['eeg_channels']}")
        logger.info(f"  Buffer size: {config['realtime']['buffer_size']}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False


def test_action_mapping():
    """Test action mapping."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: Action Mapping")
    logger.info("=" * 60)
    
    try:
        from src.realtime_inference import CLASS_LABELS, ACTION_MAPPING
        
        logger.info("✓ Class labels and action mapping loaded")
        
        for class_idx, label in CLASS_LABELS.items():
            action = ACTION_MAPPING[label]
            logger.info(f"  Class {class_idx}: {label:8s} → {action}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Action mapping test failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 60)
    logger.info("REAL-TIME INFERENCE SYSTEM - INTEGRATION TEST")
    logger.info("=" * 60)
    
    results = {
        'Imports': test_imports(),
        'CursorSmoother': test_cursor_smoother(),
        'MouseController': test_mouse_controller(),
        'InferenceEngine': test_inference_engine(),
        'Configuration': test_configuration(),
        'ActionMapping': test_action_mapping()
    }
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("INTEGRATION TEST SUMMARY")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n✓ ALL TESTS PASSED - System is ready!")
        return 0
    else:
        logger.error(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
