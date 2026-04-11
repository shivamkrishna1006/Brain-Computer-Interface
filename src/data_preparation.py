"""
EEG Data Preparation Module for Machine Learning.

This module provides data preprocessing, normalization, reshaping, and splitting
functionality for EEG data to prepare it for CNN-LSTM models.

Features:
- StandardScaler normalization
- Data reshaping for CNN-LSTM (samples, time, channels)
- Stratified train-test splitting
- Modular design for easy integration
"""

import logging
from typing import Tuple, Dict, Optional

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


logger = logging.getLogger('BCI')


class EEGDataPreparation:
    """
    Modular EEG data preparation for machine learning.
    
    Handles normalization, reshaping, and stratified splitting.
    """
    
    def __init__(self, n_channels: int, time_steps: int):
        """
        Initialize data preparation pipeline.
        
        Args:
            n_channels: Number of EEG channels
            time_steps: Number of time points per sample
        """
        self.n_channels = n_channels
        self.time_steps = time_steps
        self.scaler = StandardScaler()
        self.is_fitted = False
        
        logger.info(f"EEG Data Preparation initialized: "
                   f"{n_channels} channels, {time_steps} time steps")
    
    def normalize(self, X: np.ndarray, fit: bool = True) -> np.ndarray:
        """
        Normalize EEG data using StandardScaler.
        
        Performs z-score normalization (zero mean, unit variance) on flattened data,
        then reshapes back to original format.
        
        Args:
            X: Input data array
            fit: Whether to fit the scaler (use for training data)
                 For test data, use fit=False with already fitted scaler
        
        Returns:
            Normalized data with same shape as input
        """
        original_shape = X.shape
        
        # Reshape to (n_samples, n_features)
        X_reshaped = X.reshape(X.shape[0], -1)
        
        # Fit or transform
        if fit:
            logger.debug("Fitting StandardScaler on training data")
            X_normalized = self.scaler.fit_transform(X_reshaped)
            self.is_fitted = True
        else:
            if not self.is_fitted:
                logger.warning("Scaler not fitted yet. Fitting on current data.")
                X_normalized = self.scaler.fit_transform(X_reshaped)
                self.is_fitted = True
            else:
                logger.debug("Transforming data with fitted scaler")
                X_normalized = self.scaler.transform(X_reshaped)
        
        # Reshape back to original shape
        X_normalized = X_normalized.reshape(original_shape)
        
        logger.debug(f"Data normalized: min={X_normalized.min():.4f}, "
                    f"max={X_normalized.max():.4f}, "
                    f"mean={X_normalized.mean():.4f}, "
                    f"std={X_normalized.std():.4f}")
        
        return X_normalized
    
    def reshape_for_model(self, X: np.ndarray, 
                         expected_shape: Optional[Tuple] = None) -> np.ndarray:
        """
        Reshape data for CNN-LSTM model.
        
        Expected format: (samples, time_steps, channels)
        
        Args:
            X: Input data array
            expected_shape: Expected shape for validation
        
        Returns:
            Reshaped data (samples, time_steps, channels)
        """
        logger.debug(f"Reshaping data from {X.shape}")
        
        # Check if already in correct format
        if X.ndim == 3:
            # Already 3D, check if it's (samples, time_steps, channels)
            if X.shape[1] == self.time_steps and X.shape[2] == self.n_channels:
                logger.debug("Data already in correct format")
                return X
            # Maybe it's (samples, channels, time_steps) - transpose it
            elif X.shape[1] == self.n_channels and X.shape[2] == self.time_steps:
                logger.debug("Transposing from (samples, channels, time_steps)")
                return np.transpose(X, (0, 2, 1))
            else:
                raise ValueError(f"Cannot reshape {X.shape} to "
                               f"({X.shape[0]}, {self.time_steps}, {self.n_channels})")
        
        # Handle 2D input (samples, features)
        elif X.ndim == 2:
            n_samples = X.shape[0]
            expected_features = self.time_steps * self.n_channels
            
            if X.shape[1] != expected_features:
                raise ValueError(f"Expected {expected_features} features, got {X.shape[1]}")
            
            X_reshaped = X.reshape(n_samples, self.time_steps, self.n_channels)
            logger.debug(f"Reshaped 2D data to {X_reshaped.shape}")
            return X_reshaped
        
        else:
            raise ValueError(f"Unexpected input shape: {X.shape}. "
                           f"Expected 2D or 3D array.")
    
    def validate_shape(self, X: np.ndarray, name: str = "data") -> bool:
        """
        Validate that data has correct shape.
        
        Args:
            X: Data array to validate
            name: Name for logging purposes
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if X.ndim != 3:
            raise ValueError(f"{name}: Expected 3D array, got {X.ndim}D with shape {X.shape}")
        
        if X.shape[1] != self.time_steps:
            raise ValueError(f"{name}: Expected {self.time_steps} time steps, "
                           f"got {X.shape[1]}")
        
        if X.shape[2] != self.n_channels:
            raise ValueError(f"{name}: Expected {self.n_channels} channels, "
                           f"got {X.shape[2]}")
        
        logger.debug(f"{name} shape validated: {X.shape}")
        return True
    
    def split_data(self, X: np.ndarray, y: np.ndarray,
                   test_size: float = 0.2,
                   random_state: int = 42,
                   stratify: bool = True) -> Tuple[Tuple, Tuple]:
        """
        Split data into train and test sets with stratification.
        
        Uses scikit-learn's train_test_split with stratification to maintain
        class balance across train and test sets.
        
        Args:
            X: Input data array (samples, time_steps, channels)
            y: Labels array (samples,)
            test_size: Proportion of data for testing (default: 0.2 = 80-20 split)
            random_state: Random seed for reproducibility
            stratify: Use stratified split to maintain class distribution
        
        Returns:
            Tuple of ((X_train, y_train), (X_test, y_test))
        """
        logger.info(f"Splitting data: {100*(1-test_size):.0f}% train, "
                   f"{100*test_size:.0f}% test")
        
        # Validate input shapes
        if len(X) != len(y):
            raise ValueError(f"X and y have different lengths: {len(X)} vs {len(y)}")
        
        # Perform split with stratification if requested
        stratify_arg = y if stratify else None
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify_arg
        )
        
        # Log split results
        logger.info(f"Train set: {len(X_train)} samples")
        logger.info(f"Test set:  {len(X_test)} samples")
        
        # Log class distribution
        if stratify:
            import numpy as np
            unique_labels, train_counts = np.unique(y_train, return_counts=True)
            unique_labels_test, test_counts = np.unique(y_test, return_counts=True)
            
            logger.debug("Train class distribution:")
            for label, count in zip(unique_labels, train_counts):
                logger.debug(f"  Class {label}: {count} samples "
                           f"({100*count/len(y_train):.1f}%)")
            
            logger.debug("Test class distribution:")
            for label, unique_labels_test in zip(unique_labels_test, test_counts):
                logger.debug(f"  Class {label}: {count} samples "
                           f"({100*count/len(y_test):.1f}%)")
        
        return (X_train, y_train), (X_test, y_test)
    
    def get_normalization_params(self) -> Dict:
        """
        Get normalization parameters (mean and std).
        
        Returns:
            Dictionary with 'mean' and 'scale' (std) arrays
        """
        if not self.is_fitted:
            raise RuntimeError("Scaler not fitted yet. Call normalize() first.")
        
        params = {
            'mean': self.scaler.mean_,
            'scale': self.scaler.scale_,
            'var': self.scaler.var_,
            'n_features': self.scaler.n_features_in_
        }
        
        return params
    
    def denormalize(self, X: np.ndarray) -> np.ndarray:
        """
        Reverse normalization using fitted scaler.
        
        Args:
            X: Normalized data array
        
        Returns:
            Denormalized data
        """
        if not self.is_fitted:
            raise RuntimeError("Scaler not fitted yet. Call normalize() first.")
        
        original_shape = X.shape
        X_reshaped = X.reshape(X.shape[0], -1)
        X_denormalized = self.scaler.inverse_transform(X_reshaped)
        X_denormalized = X_denormalized.reshape(original_shape)
        
        return X_denormalized
    
    def get_statistics(self, X: np.ndarray, name: str = "data") -> Dict:
        """
        Compute and log data statistics.
        
        Args:
            X: Data array
            name: Name for logging
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'shape': X.shape,
            'dtype': str(X.dtype),
            'min': float(np.min(X)),
            'max': float(np.max(X)),
            'mean': float(np.mean(X)),
            'std': float(np.std(X)),
            'median': float(np.median(X)),
            'q25': float(np.percentile(X, 25)),
            'q75': float(np.percentile(X, 75))
        }
        
        logger.debug(f"{name} statistics:")
        logger.debug(f"  Shape: {stats['shape']}")
        logger.debug(f"  Min: {stats['min']:.4f}, Max: {stats['max']:.4f}")
        logger.debug(f"  Mean: {stats['mean']:.4f}, Std: {stats['std']:.4f}")
        
        return stats


def prepare_eeg_data(X: np.ndarray, y: np.ndarray,
                    n_channels: int,
                    time_steps: int,
                    test_size: float = 0.2,
                    random_state: int = 42) -> Tuple[Tuple, Tuple, EEGDataPreparation]:
    """
    Complete EEG data preparation pipeline.
    
    Performs normalization, reshaping, and stratified splitting in one call.
    
    Args:
        X: Input data array (shape depends on format)
        y: Labels array
        n_channels: Number of EEG channels
        time_steps: Number of time points per sample
        test_size: Test set proportion (default: 0.2 for 80-20 split)
        random_state: Random seed for reproducibility
    
    Returns:
        Tuple of (
            (X_train, y_train),  # Training data and labels
            (X_test, y_test),    # Test data and labels
            preparation         # Fitted EEGDataPreparation object
        )
    """
    logger.info("Starting complete EEG data preparation pipeline")
    
    # Initialize preparation object
    prep = EEGDataPreparation(n_channels, time_steps)
    
    # Step 1: Reshape data
    logger.info("Step 1: Reshaping data for CNN-LSTM model")
    X_reshaped = prep.reshape_for_model(X)
    logger.info(f"  Reshaped to: {X_reshaped.shape}")
    
    # Step 2: Normalize data
    logger.info("Step 2: Normalizing data using StandardScaler")
    X_normalized = prep.normalize(X_reshaped, fit=True)
    logger.info(f"  Normalized: mean={X_normalized.mean():.4f}, "
               f"std={X_normalized.std():.4f}")
    
    # Step 3: Split data with stratification
    logger.info("Step 3: Splitting data with stratification")
    (X_train, y_train), (X_test, y_test) = prep.split_data(
        X_normalized, y,
        test_size=test_size,
        random_state=random_state,
        stratify=True
    )
    
    # Validate shapes
    prep.validate_shape(X_train, "Training data")
    prep.validate_shape(X_test, "Test data")
    
    logger.info("Data preparation completed successfully")
    
    return (X_train, y_train), (X_test, y_test), prep


def prepare_eeg_data_with_validation(X: np.ndarray, y: np.ndarray,
                                     n_channels: int,
                                     time_steps: int,
                                     train_size: float = 0.8,
                                     random_state: int = 42) -> Tuple[Tuple, Tuple, EEGDataPreparation]:
    """
    Alternative interface using train_size instead of test_size.
    
    Args:
        X: Input data array
        y: Labels array
        n_channels: Number of EEG channels
        time_steps: Number of time points per sample
        train_size: Training set proportion (default: 0.8 for 80% train)
        random_state: Random seed
    
    Returns:
        Same as prepare_eeg_data()
    """
    test_size = 1.0 - train_size
    return prepare_eeg_data(X, y, n_channels, time_steps, test_size, random_state)


if __name__ == '__main__':
    """
    Example usage and demonstration.
    """
    import logging as log
    
    # Setup logging
    log.basicConfig(
        level=log.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = log.getLogger('BCI')
    
    # Create synthetic EEG data for testing
    logger.info("=" * 80)
    logger.info("EEG Data Preparation Example")
    logger.info("=" * 80)
    
    # Synthetic data parameters
    n_samples = 1000
    n_channels = 64
    time_steps = 250
    n_classes = 2
    
    # Generate synthetic data
    logger.info(f"\nGenerating synthetic EEG data:")
    logger.info(f"  Samples: {n_samples}")
    logger.info(f"  Channels: {n_channels}")
    logger.info(f"  Time steps: {time_steps}")
    logger.info(f"  Classes: {n_classes}")
    
    X = np.random.randn(n_samples, n_channels, time_steps)
    y = np.random.randint(0, n_classes, n_samples)
    
    logger.info(f"\nInitial data shape: {X.shape}")
    logger.info(f"Initial labels shape: {y.shape}")
    logger.info(f"Class distribution: {np.bincount(y)}")
    
    # Example 1: Using main function
    logger.info("\n" + "=" * 80)
    logger.info("Example 1: Using prepare_eeg_data()")
    logger.info("=" * 80)
    
    (X_train, y_train), (X_test, y_test), prep = prepare_eeg_data(
        X, y, n_channels, time_steps, test_size=0.2
    )
    
    logger.info(f"\nTraining data shape: {X_train.shape}")
    logger.info(f"Test data shape: {X_test.shape}")
    logger.info(f"Training labels: {np.bincount(y_train)}")
    logger.info(f"Test labels: {np.bincount(y_test)}")
    
    # Example 2: Using class directly
    logger.info("\n" + "=" * 80)
    logger.info("Example 2: Using EEGDataPreparation class directly")
    logger.info("=" * 80)
    
    prep2 = EEGDataPreparation(n_channels, time_steps)
    
    # Step 1: Get statistics before normalization
    logger.info("\nBefore normalization:")
    stats_before = prep2.get_statistics(X, "Raw data")
    
    # Step 2: Reshape
    X_reshaped = prep2.reshape_for_model(X)
    logger.info(f"After reshaping: {X_reshaped.shape}")
    
    # Step 3: Normalize
    X_normalized = prep2.normalize(X_reshaped, fit=True)
    logger.info("\nAfter normalization:")
    stats_after = prep2.get_statistics(X_normalized, "Normalized data")
    
    # Step 4: Split
    (X_train2, y_train2), (X_test2, y_test2) = prep2.split_data(
        X_normalized, y, test_size=0.2
    )
    
    # Step 5: Get normalization parameters
    logger.info("\nNormalization parameters:")
    norm_params = prep2.get_normalization_params()
    logger.info(f"  Mean shape: {norm_params['mean'].shape}")
    logger.info(f"  Scale shape: {norm_params['scale'].shape}")
    logger.info(f"  N features: {norm_params['n_features']}")
    
    # Example 3: Denormalization
    logger.info("\n" + "=" * 80)
    logger.info("Example 3: Denormalization")
    logger.info("=" * 80)
    
    X_denorm = prep2.denormalize(X_normalized)
    logger.info(f"Original data range: [{X.min():.4f}, {X.max():.4f}]")
    logger.info(f"Denormalized data range: [{X_denorm.min():.4f}, {X_denorm.max():.4f}]")
    logger.info(f"Reconstruction error (MSE): {np.mean((X - X_denorm)**2):.6f}")
    
    logger.info("\n" + "=" * 80)
    logger.info("Examples completed successfully!")
    logger.info("=" * 80)
