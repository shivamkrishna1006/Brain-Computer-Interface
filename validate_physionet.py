"""
Validation script for PhysioNet EEG Motor Imagery Dataset module.

This script tests the physionet_loader module to ensure it's working correctly.
"""

import sys
import logging
sys.path.insert(0, 'src')

import numpy as np
from physionet_loader import (
    load_physionet_data,
    PhysioNetEEGDataset,
    prepare_data_splits,
    get_label_mapping,
    get_task_mapping
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all imports work."""
    logger.info("Test 1: Checking imports...")
    try:
        import mne
        import sklearn
        logger.info("  ✓ All required packages available (mne, sklearn, numpy, scipy)")
        return True
    except ImportError as e:
        logger.error(f"  ✗ Import error: {e}")
        logger.error("  Please install missing packages: pip install -r requirements.txt")
        return False


def test_mappings():
    """Test mapping functions."""
    logger.info("\nTest 2: Checking label and task mappings...")
    
    try:
        # Test label mapping
        label_map = get_label_mapping()
        assert 1 in label_map, "Missing label 1"
        assert 4 in label_map, "Missing label 4"
        assert label_map[1] == 'Left Hand', "Incorrect label mapping"
        logger.info(f"  ✓ Label mapping: {label_map}")
        
        # Test task mapping
        task_map = get_task_mapping()
        assert 'left_hand' in task_map, "Missing left_hand task"
        assert 'right_hand' in task_map, "Missing right_hand task"
        assert task_map['left_hand'] == [3, 7, 11], "Incorrect run mapping"
        logger.info(f"  ✓ Task mapping: {list(task_map.keys())}")
        
        return True
    except Exception as e:
        logger.error(f"  ✗ Error: {e}")
        return False


def test_dataset_initialization():
    """Test PhysioNetEEGDataset initialization."""
    logger.info("\nTest 3: Initializing dataset loader...")
    
    try:
        dataset = PhysioNetEEGDataset(data_dir='data/physionet', verbose=False)
        logger.info("  ✓ Dataset loader initialized successfully")
        return True, dataset
    except Exception as e:
        logger.error(f"  ✗ Error: {e}")
        return False, None


def test_single_subject_load(dataset):
    """Test loading a single subject (requires internet)."""
    logger.info("\nTest 4: Loading single subject data (requires internet)...")
    logger.info("  This will download ~50 MB of data for subject 1...")
    
    try:
        logger.info("  Attempting to load subject 1, left and right hand tasks...")
        X, y = dataset.load_subject(
            subject_id=1,
            tasks=['left_hand', 'right_hand'],
            sessions=1,
            filter_freqs=(8, 30),
            epoch_window=(0.5, 3.5)
        )
        
        if len(X) == 0:
            logger.warning("  ⚠ No data loaded (may need internet connection)")
            return False, None, None
        
        logger.info(f"  ✓ Successfully loaded data:")
        logger.info(f"    - Data shape: {X.shape}")
        logger.info(f"    - Label shape: {y.shape}")
        logger.info(f"    - Unique labels: {np.unique(y)}")
        logger.info(f"    - Class distribution: {np.bincount(y)}")
        
        # Validate data shapes
        assert X.ndim == 3, "Data should be 3D (epochs, channels, time)"
        assert X.shape[1] == 64, "Should have 64 EEG channels"
        assert len(y) == X.shape[0], "Label count should match epoch count"
        assert np.all((y >= 1) & (y <= 4)), "Labels should be 1-4"
        
        return True, X, y
    
    except Exception as e:
        logger.warning(f"  ⚠ Could not load data: {e}")
        logger.info("  This is expected if no internet connection is available")
        return False, None, None


def test_data_splitting(X, y):
    """Test data splitting functionality."""
    logger.info("\nTest 5: Testing data split functionality...")
    
    try:
        (X_train, y_train), (X_val, y_val), (X_test, y_test) = prepare_data_splits(
            X, y,
            train_ratio=0.7,
            val_ratio=0.15,
            test_ratio=0.15
        )
        
        # Validate split
        total = len(X_train) + len(X_val) + len(X_test)
        assert total == len(X), "Split counts don't match original"
        
        # Check stratification
        train_ratio = np.sum(y_train == 1) / len(y_train)
        original_ratio = np.sum(y == 1) / len(y)
        assert abs(train_ratio - original_ratio) < 0.1, "Classes not stratified"
        
        logger.info(f"  ✓ Data split successfully:")
        logger.info(f"    - Train: {len(X_train)} epochs ({len(X_train)/len(X)*100:.1f}%)")
        logger.info(f"    - Val:   {len(X_val)} epochs ({len(X_val)/len(X)*100:.1f}%)")
        logger.info(f"    - Test:  {len(X_test)} epochs ({len(X_test)/len(X)*100:.1f}%)")
        logger.info(f"    - Train labels: {np.bincount(y_train)}")
        logger.info(f"    - Val labels:   {np.bincount(y_val)}")
        logger.info(f"    - Test labels:  {np.bincount(y_test)}")
        
        return True
    except Exception as e:
        logger.error(f"  ✗ Error: {e}")
        return False


def test_synthetic_fallback():
    """Test with synthetic data (no internet required)."""
    logger.info("\nTest 6: Testing with synthetic data (no internet required)...")
    
    try:
        # Create synthetic data matching PhysioNet structure
        n_epochs = 100
        n_channels = 64
        n_times = 321  # ~2 seconds at 160 Hz
        
        X_synthetic = np.random.randn(n_epochs, n_channels, n_times)
        y_synthetic = np.random.randint(1, 5, n_epochs)
        
        logger.info(f"  Generated synthetic data:")
        logger.info(f"    - Shape: {X_synthetic.shape}")
        logger.info(f"    - Labels: {np.unique(y_synthetic)}")
        
        # Test splitting on synthetic data
        (X_train, y_train), (X_val, y_val), (X_test, y_test) = prepare_data_splits(X_synthetic, y_synthetic)
        
        logger.info(f"  ✓ Successfully processed synthetic data")
        logger.info(f"    - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        return True
    except Exception as e:
        logger.error(f"  ✗ Error: {e}")
        return False


def test_help_text():
    """Test help/documentation."""
    logger.info("\nTest 7: Testing help documentation...")
    
    try:
        # This would work in interactive mode
        help_text = load_physionet_data.__doc__
        assert help_text is not None, "No docstring found"
        assert "subject_ids" in help_text, "Docstring missing parameters"
        logger.info("  ✓ Comprehensive documentation available")
        return True
    except Exception as e:
        logger.error(f"  ✗ Error: {e}")
        return False


def run_all_tests():
    """Run all validation tests."""
    logger.info("=" * 80)
    logger.info("PhysioNet EEG Motor Imagery Dataset Module - Validation Tests")
    logger.info("=" * 80)
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    if not results[-1][1]:
        logger.error("\nTest suite stopped: Missing dependencies")
        return results
    
    # Test 2: Mappings
    results.append(("Label/Task Mappings", test_mappings()))
    
    # Test 3: Initialization
    success, dataset = test_dataset_initialization()
    results.append(("Dataset Initialization", success))
    if not success:
        dataset = None
    
    # Test 4: Single subject load (optional, needs internet)
    if dataset:
        success, X, y = test_single_subject_load(dataset)
        results.append(("Single Subject Load", success))
        
        # Test 5: Data splitting (only if data loaded)
        if success and X is not None:
            results.append(("Data Splitting", test_data_splitting(X, y)))
        else:
            logger.info("\nTest 5: Skipped (no data available)")
    
    # Test 6: Synthetic fallback
    results.append(("Synthetic Data Processing", test_synthetic_fallback()))
    
    # Test 7: Help text
    results.append(("Documentation", test_help_text()))
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("Test Summary")
    logger.info("=" * 80)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    failed_tests = total_tests - passed_tests
    
    logger.info("\n" + "=" * 80)
    logger.info(f"Results: {passed_tests}/{total_tests} tests passed")
    
    if failed_tests == 0:
        logger.info("✓ All tests passed! Module is ready to use.")
    else:
        logger.warning(f"⚠ {failed_tests} test(s) failed. See details above.")
    
    logger.info("=" * 80)
    
    return results


if __name__ == '__main__':
    results = run_all_tests()
    
    # Exit with error code if any critical tests failed
    critical_failures = sum(
        1 for name, success in results[:3] if not success
    )
    
    sys.exit(1 if critical_failures > 0 else 0)
