"""
Utility functions for BCI Interface project.

This module provides common utility functions including logging setup,
configuration loading, and data manipulation helpers.
"""

import logging
import logging.handlers
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import numpy as np
import yaml
from datetime import datetime


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        config: Configuration dictionary containing logging settings
        
    Returns:
        Configured logger instance
    """
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_format = log_config.get('format', 
                                 '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = log_config.get('log_file', 'outputs/bci.log')
    
    # Create logger
    logger = logging.getLogger('BCI')
    logger.setLevel(log_level)
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers if not already present
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def save_config(config: Dict[str, Any], save_path: str) -> None:
    """
    Save configuration to YAML file.
    
    Args:
        config: Configuration dictionary
        save_path: Path to save configuration file
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def save_training_history(history: Dict[str, List], save_path: str) -> None:
    """
    Save training history to JSON file.
    
    Args:
        history: Training history dictionary
        save_path: Path to save history file
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Convert numpy arrays to lists for JSON serialization
    history_serializable = {}
    for key, value in history.items():
        if isinstance(value, np.ndarray):
            history_serializable[key] = value.tolist()
        elif isinstance(value, list):
            history_serializable[key] = [
                float(v) if isinstance(v, (np.floating, np.integer)) else v 
                for v in value
            ]
        else:
            history_serializable[key] = value
    
    with open(save_path, 'w') as f:
        json.dump(history_serializable, f, indent=4)


def normalize_data(data: np.ndarray, method: str = 'zscore') -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Normalize data using specified method.
    
    Args:
        data: Input data array
        method: Normalization method ('zscore', 'minmax', or 'robust')
        
    Returns:
        Normalized data and normalization parameters
    """
    params = {}
    
    if method == 'zscore':
        mean = np.mean(data, axis=0, keepdims=True)
        std = np.std(data, axis=0, keepdims=True)
        std[std == 0] = 1  # Avoid division by zero
        normalized_data = (data - mean) / std
        params = {'mean': mean.flatten(), 'std': std.flatten()}
        
    elif method == 'minmax':
        data_min = np.min(data, axis=0, keepdims=True)
        data_max = np.max(data, axis=0, keepdims=True)
        range_val = data_max - data_min
        range_val[range_val == 0] = 1  # Avoid division by zero
        normalized_data = (data - data_min) / range_val
        params = {'min': data_min.flatten(), 'max': data_max.flatten()}
        
    elif method == 'robust':
        q1 = np.percentile(data, 25, axis=0, keepdims=True)
        q3 = np.percentile(data, 75, axis=0, keepdims=True)
        iqr = q3 - q1
        iqr[iqr == 0] = 1  # Avoid division by zero
        median = np.median(data, axis=0, keepdims=True)
        normalized_data = (data - median) / iqr
        params = {'q1': q1.flatten(), 'q3': q3.flatten(), 'median': median.flatten()}
    else:
        raise ValueError(f"Unknown normalization method: {method}")
    
    return normalized_data, params


def denormalize_data(data: np.ndarray, params: Dict[str, float], method: str = 'zscore') -> np.ndarray:
    """
    Denormalize data using provided parameters.
    
    Args:
        data: Normalized data array
        params: Normalization parameters
        method: Normalization method used
        
    Returns:
        Denormalized data
    """
    if method == 'zscore':
        mean = params['mean']
        std = params['std']
        denormalized_data = data * std + mean
        
    elif method == 'minmax':
        data_min = params['min']
        data_max = params['max']
        range_val = data_max - data_min
        denormalized_data = data * range_val + data_min
        
    elif method == 'robust':
        q1 = params['q1']
        q3 = params['q3']
        median = params['median']
        iqr = q3 - q1
        denormalized_data = data * iqr + median
    else:
        raise ValueError(f"Unknown normalization method: {method}")
    
    return denormalized_data


def split_data(data: np.ndarray, labels: np.ndarray, 
               train_ratio: float = 0.8, val_ratio: float = 0.1,
               test_ratio: float = 0.1, random_seed: int = 42) -> Tuple[Tuple, Tuple, Tuple]:
    """
    Split data into train, validation, and test sets.
    
    Args:
        data: Input data array
        labels: Labels array
        train_ratio: Proportion of data for training
        val_ratio: Proportion of data for validation
        test_ratio: Proportion of data for testing
        random_seed: Random seed for reproducibility
        
    Returns:
        Tuples of (train_data, train_labels), (val_data, val_labels), (test_data, test_labels)
    """
    np.random.seed(random_seed)
    
    # Normalize ratios
    total_ratio = train_ratio + val_ratio + test_ratio
    train_ratio /= total_ratio
    val_ratio /= total_ratio
    test_ratio /= total_ratio
    
    # Get indices
    n_samples = len(data)
    indices = np.random.permutation(n_samples)
    
    # Calculate split points
    train_end = int(n_samples * train_ratio)
    val_end = train_end + int(n_samples * val_ratio)
    
    # Split indices
    train_idx = indices[:train_end]
    val_idx = indices[train_end:val_end]
    test_idx = indices[val_end:]
    
    # Split data
    train_data, train_labels = data[train_idx], labels[train_idx]
    val_data, val_labels = data[val_idx], labels[val_idx]
    test_data, test_labels = data[test_idx], labels[test_idx]
    
    return (train_data, train_labels), (val_data, val_labels), (test_data, test_labels)


def create_directories(config: Dict[str, Any]) -> None:
    """
    Create necessary directories based on configuration.
    
    Args:
        config: Configuration dictionary
    """
    directories = ['data', 'models', 'outputs', 'notebooks']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Create logging directory
    log_file = config.get('logging', {}).get('log_file', 'outputs/bci.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)


def get_timestamp() -> str:
    """Get current timestamp as string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def compute_class_weights(labels: np.ndarray) -> Dict[int, float]:
    """
    Compute class weights for imbalanced datasets.
    
    Args:
        labels: Labels array
        
    Returns:
        Dictionary of class weights
    """
    unique_labels = np.unique(labels)
    n_samples = len(labels)
    
    weights = {}
    for label in unique_labels:
        n_class = np.sum(labels == label)
        weights[int(label)] = n_samples / (len(unique_labels) * n_class)
    
    return weights


def print_config(config: Dict[str, Any], logger: logging.Logger) -> None:
    """
    Print configuration in a readable format.
    
    Args:
        config: Configuration dictionary
        logger: Logger instance
    """
    logger.info("=" * 80)
    logger.info("Configuration Settings")
    logger.info("=" * 80)
    
    for section, settings in config.items():
        logger.info(f"\n{section.upper()}:")
        if isinstance(settings, dict):
            for key, value in settings.items():
                logger.info(f"  {key}: {value}")
        else:
            logger.info(f"  {settings}")
    
    logger.info("=" * 80)
