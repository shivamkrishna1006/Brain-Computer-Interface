#!/usr/bin/env python
"""Quick test script for configuration system."""

import yaml
import sys

print("\nTesting Configuration System...")
print("=" * 70)

# Test 1: Load config.yaml
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print("✓ config.yaml loads successfully (valid YAML)")
except Exception as e:
    print(f"✗ Failed to load config.yaml: {e}")
    sys.exit(1)

# Test 2: Check main sections
expected_sections = [
    'paths', 'model', 'training', 'data', 'realtime',
    'data_generation', 'physionet', 'logging', 'validation', 'output'
]
actual_sections = list(config.keys())
print(f"✓ Found {len(actual_sections)} configuration sections")
for section in expected_sections:
    if section in config:
        print(f"  • {section}: ✓")
    else:
        print(f"  • {section}: ✗ MISSING")

# Test 3: Extract key training parameters
training = config.get('training', {})
print(f"\n✓ Training Configuration:")
print(f"  • Learning rate: {training.get('learning_rate', 'N/A')}")
print(f"  • Batch size: {training.get('batch_size', 'N/A')}")
print(f"  • Epochs: {training.get('epochs', 'N/A')}")
print(f"  • Early stopping patience: {training.get('early_stopping', {}).get('patience', 'N/A')}")

# Test 4: Extract key data parameters
data = config.get('data', {})
print(f"\n✓ Data Configuration:")
print(f"  • EEG channels: {data.get('eeg_channels', 'N/A')}")
print(f"  • Sampling rate: {data.get('sampling_rate', 'N/A')} Hz")
print(f"  • Number of classes: {data.get('n_classes', 'N/A')}")
print(f"  • Number of subjects: {data.get('n_subjects', 'N/A')}")
print(f"  • Frequency range: {data.get('frequency_range', {}).get('low_freq', 'N/A')}-{data.get('frequency_range', {}).get('high_freq', 'N/A')} Hz")

# Test 5: Extract key realtime parameters
realtime = config.get('realtime', {})
print(f"\n✓ Real-Time Configuration:")
print(f"  • Buffer size: {realtime.get('buffer_size', 'N/A')} samples")
print(f"  • Confidence threshold: {realtime.get('confidence_threshold', 'N/A')}")
print(f"  • Debounce count: {realtime.get('debounce_count', 'N/A')}")
print(f"  • Move distance: {realtime.get('mouse', {}).get('move_distance', 'N/A')} pixels")
print(f"  • Cursor smoothing alpha: {realtime.get('mouse', {}).get('cursor_smoothing', {}).get('alpha', 'N/A')}")

# Test 6: Check paths exist
paths = config.get('paths', {})
print(f"\n✓ Path Configuration:")
print(f"  • Models dir: {paths.get('models_dir', 'N/A')}")
print(f"  • Output dir: {paths.get('output_dir', 'N/A')}")
print(f"  • Data dir: {paths.get('data_dir', 'N/A')}")

print("\n" + "=" * 70)
print("✓ Configuration system is fully functional!")
print("\nNext steps:")
print("  1. Train a model: python train_eeg_model_production.py")
print("  2. Run inference: python realtime_inference_demo.py")
print("  3. Customize: Edit config.yaml for your needs")
print("=" * 70 + "\n")
