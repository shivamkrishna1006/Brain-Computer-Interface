"""
Data loading module for BCI interface.

This module provides functionality for loading, generating, and managing
EEG data for the BCI system.
"""

import logging
import os
from typing import Tuple

import numpy as np
import pandas as pd
from pathlib import Path


logger = logging.getLogger('BCI')


class EEGDataLoader:
    """
    Data loader for EEG signals with support for various formats.
    """
    
    def __init__(self, data_dir: str = 'data', config: dict = None):
        """
        Initialize EEG data loader.
        
        Args:
            data_dir: Directory containing EEG data
            config: Configuration dictionary
        """
        self.data_dir = data_dir
        self.config = config or {}
        os.makedirs(data_dir, exist_ok=True)
    
    def load_numpy_data(self, filepath: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load data from numpy files.
        
        Args:
            filepath: Path to numpy file or directory with X.npy and y.npy
            
        Returns:
            Tuple of (data, labels)
        """
        if os.path.isdir(filepath):
            x_path = os.path.join(filepath, 'X.npy')
            y_path = os.path.join(filepath, 'y.npy')
        else:
            x_path = filepath
            y_path = filepath.replace('.npy', '_labels.npy')
        
        if not os.path.exists(x_path):
            raise FileNotFoundError(f"Data file not found: {x_path}")
        if not os.path.exists(y_path):
            raise FileNotFoundError(f"Labels file not found: {y_path}")
        
        data = np.load(x_path)
        labels = np.load(y_path)
        
        logger.info(f"Loaded data: {data.shape}, labels: {labels.shape}")
        return data, labels
    
    def load_csv_data(self, filepath: str, label_column: str = 'label') -> Tuple[np.ndarray, np.ndarray]:
        """
        Load data from CSV file.
        
        Args:
            filepath: Path to CSV file
            label_column: Name of label column
            
        Returns:
            Tuple of (data, labels)
        """
        df = pd.read_csv(filepath)
        
        # Extract labels
        labels = df[label_column].values
        
        # Extract features (all columns except label)
        data = df.drop(columns=[label_column]).values
        
        logger.info(f"Loaded data: {data.shape}, labels: {labels.shape}")
        return data, labels
    
    def generate_synthetic_data(self, n_samples: int = 1000, 
                               n_channels: int = 8, 
                               segment_duration: float = 1.0,
                               sampling_rate: int = 250,
                               num_classes: int = 2) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic EEG data for testing and development.
        
        Args:
            n_samples: Number of samples to generate
            n_channels: Number of EEG channels
            segment_duration: Duration of each segment in seconds
            sampling_rate: Sampling rate in Hz
            num_classes: Number of classes
            
        Returns:
            Tuple of (data, labels)
        """
        logger.info(f"Generating synthetic EEG data: {n_samples} samples, "
                   f"{n_channels} channels, {segment_duration}s duration")
        
        n_timesteps = int(segment_duration * sampling_rate)
        data = np.zeros((n_samples, n_timesteps, n_channels))
        labels = np.random.randint(0, num_classes, n_samples)
        
        # Generate realistic EEG-like signals
        for i in range(n_samples):
            for ch in range(n_channels):
                # Mix of sine waves at different frequencies (delta, theta, alpha, beta)
                t = np.linspace(0, segment_duration, n_timesteps)
                
                # Generate oscillations in different frequency bands
                delta = 5 * np.sin(2 * np.pi * 2 * t)      # 2 Hz
                theta = 8 * np.sin(2 * np.pi * 5 * t)      # 5 Hz
                alpha = 15 * np.sin(2 * np.pi * 10 * t)    # 10 Hz
                beta = 10 * np.sin(2 * np.pi * 20 * t)     # 20 Hz
                
                # Combine oscillations with random weights
                signal_base = (delta + theta + alpha + beta) * 0.25
                
                # Add label-specific modulation
                if labels[i] == 1:
                    signal_base += 5 * np.sin(2 * np.pi * 25 * t)  # Gamma for class 1
                
                # Add noise
                noise = np.random.normal(0, 2, n_timesteps)
                
                data[i, :, ch] = signal_base + noise
        
        return data, labels
    
    def save_data(self, data: np.ndarray, labels: np.ndarray, 
                  output_dir: str = None) -> None:
        """
        Save data to numpy files.
        
        Args:
            data: Data array
            labels: Labels array
            output_dir: Output directory (default: self.data_dir)
        """
        output_dir = output_dir or self.data_dir
        os.makedirs(output_dir, exist_ok=True)
        
        data_path = os.path.join(output_dir, 'X.npy')
        labels_path = os.path.join(output_dir, 'y.npy')
        
        np.save(data_path, data)
        np.save(labels_path, labels)
        
        logger.info(f"Saved data to {output_dir}")
        logger.info(f"  Data shape: {data.shape}")
        logger.info(f"  Labels shape: {labels.shape}")
    
    def get_data_info(self, data: np.ndarray, labels: np.ndarray) -> dict:
        """
        Get information about the dataset.
        
        Args:
            data: Data array
            labels: Labels array
            
        Returns:
            Dictionary with dataset information
        """
        unique_labels, counts = np.unique(labels, return_counts=True)
        
        info = {
            'n_samples': len(data),
            'n_timesteps': data.shape[1] if data.ndim > 1 else 1,
            'n_channels': data.shape[2] if data.ndim > 2 else 1,
            'n_classes': len(unique_labels),
            'class_distribution': dict(zip(unique_labels, counts)),
            'data_shape': data.shape,
            'labels_shape': labels.shape,
            'data_dtype': str(data.dtype),
            'data_min': float(np.min(data)),
            'data_max': float(np.max(data)),
            'data_mean': float(np.mean(data)),
            'data_std': float(np.std(data))
        }
        
        return info


def create_data_loaders(config: dict) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create data loaders and generate/load data.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (data, labels)
    """
    loader = EEGDataLoader(config=config)
    
    # Check if data exists
    data_path = os.path.join(loader.data_dir, 'X.npy')
    
    if os.path.exists(data_path):
        logger.info("Loading existing data...")
        data, labels = loader.load_numpy_data(data_path)
    else:
        logger.info("Generating synthetic data...")
        data, labels = loader.generate_synthetic_data(
            n_samples=1000,
            n_channels=config['data']['eeg_channels'],
            segment_duration=config['data']['segment_duration'],
            sampling_rate=config['data']['sampling_rate'],
            num_classes=config['data']['num_classes']
        )
        loader.save_data(data, labels)
    
    return data, labels


def get_batch(data: np.ndarray, labels: np.ndarray, 
              batch_size: int, 
              shuffle: bool = True) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a generator for mini-batches.
    
    Args:
        data: Data array
        labels: Labels array
        batch_size: Batch size
        shuffle: Whether to shuffle data
        
    Yields:
        Tuples of (batch_data, batch_labels)
    """
    n_samples = len(data)
    indices = np.arange(n_samples)
    
    if shuffle:
        np.random.shuffle(indices)
    
    for start_idx in range(0, n_samples, batch_size):
        batch_indices = indices[start_idx:start_idx + batch_size]
        yield data[batch_indices], labels[batch_indices]
