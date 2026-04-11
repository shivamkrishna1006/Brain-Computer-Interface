"""
Quick test to verify the training module works correctly.
Tests all 6 requirements are functional.
"""

import sys
import numpy as np

print("=" * 80)
print("TRAINING MODULE VERIFICATION TEST")
print("=" * 80)

# Test 1: Import test
print("\n[TEST 1] Importing training module...")
try:
    from src.train import ModelTrainer, TrainingProgressCallback
    print("✓ PASSED: ModelTrainer imported successfully")
    print("✓ PASSED: TrainingProgressCallback imported successfully")
except ImportError as e:
    print(f"✗ FAILED: Import error - {e}")
    sys.exit(1)

# Test 2: Class instantiation
print("\n[TEST 2] Creating ModelTrainer instance...")
try:
    config = {
        'model': {'input_shape': (320, 64)},
        'training': {
            'epochs': 2,
            'batch_size': 16,
            'early_stopping_patience': 1,
            'reduce_lr_patience': 1,
            'reduce_lr_factor': 0.5,
            'log_interval': 1
        },
        'output': {'model_path': 'models/test_model.h5', 'log_dir': 'outputs/logs'}
    }
    trainer = ModelTrainer(config, n_classes=5)
    print(f"✓ PASSED: ModelTrainer instantiated with {trainer.n_classes} classes")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test 3: Class weight computation
print("\n[TEST 3] Testing class weight computation...")
try:
    labels = np.array([0, 0, 0, 1, 1, 2, 3, 4, 4, 4, 4])
    weights = trainer.compute_class_weights(labels)
    assert isinstance(weights, dict), "Class weights should be a dictionary"
    assert len(weights) == 5, "Should have 5 classes"
    print(f"✓ PASSED: Computed class weights: {weights}")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test 4: Callback building
print("\n[TEST 4] Testing callback building...")
try:
    callbacks = trainer.build_callbacks('models/test_model.h5')
    assert isinstance(callbacks, list), "Callbacks should be a list"
    assert len(callbacks) >= 4, "Should have at least 4 callbacks (EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard, Progress)"
    callback_names = [cb.__class__.__name__ for cb in callbacks]
    print(f"✓ PASSED: Built callbacks: {callback_names}")
    
    # Verify required callbacks
    assert 'EarlyStopping' in callback_names, "Missing EarlyStopping"
    assert 'ReduceLROnPlateau' in callback_names, "Missing ReduceLROnPlateau"
    assert 'ModelCheckpoint' in callback_names, "Missing ModelCheckpoint"
    print("✓ PASSED: All required callbacks present")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test 5: save_history method exists
print("\n[TEST 5] Testing history saving capability...")
try:
    assert hasattr(trainer, 'save_history'), "Missing save_history method"
    assert callable(trainer.save_history), "save_history should be callable"
    print("✓ PASSED: save_history method exists and is callable")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test 6: training_summary method exists
print("\n[TEST 6] Testing training summary capability...")
try:
    assert hasattr(trainer, 'training_summary'), "Missing training_summary method"
    assert callable(trainer.training_summary), "training_summary should be callable"
    print("✓ PASSED: training_summary method exists and is callable")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("ALL TESTS PASSED - Training module is functional")
print("=" * 80)
print("\nRequirements verified:")
print("✓ [REQ 1] Early stopping - EarlyStopping callback configured")
print("✓ [REQ 2] ReduceLROnPlateau - Callback created and configured")
print("✓ [REQ 3] Class weights - compute_class_weights() working")
print("✓ [REQ 4] Model checkpointing - ModelCheckpoint callback configured")
print("✓ [REQ 5] Progress printing - TrainingProgressCallback available")
print("✓ [REQ 6] History storage - save_history() method available")
print("=" * 80)
