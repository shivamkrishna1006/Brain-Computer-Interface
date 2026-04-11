"""
Configuration management utilities for BCI EEG system.

Provides functions to:
- Load YAML configuration files
- Merge configurations with defaults
- Validate configuration values
- Access configuration with defaults
"""

import yaml
from pathlib import Path
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None, defaults: Optional[Dict] = None) -> Dict:
    """
    Load configuration from YAML file or return defaults.
    
    Priority order:
    1. Specified config_path
    2. config.yaml in current directory
    3. Provided defaults parameter
    4. Empty dict
    
    Args:
        config_path: Optional explicit path to config file
        defaults: Optional default configuration dictionary
        
    Returns:
        Loaded and merged configuration dictionary
        
    Example:
        >>> config = load_config()  # Loads config.yaml with no defaults
        >>> config = load_config(defaults={'timeout': 30})  # With defaults
        >>> config = load_config('custom.yaml')  # Specific file
    """
    config = defaults.copy() if defaults else {}
    
    # Determine which config file to load
    config_file = None
    if config_path and Path(config_path).exists():
        config_file = Path(config_path)
        logger.info(f"Loading config from: {config_file}")
    elif Path('config.yaml').exists():
        config_file = Path('config.yaml')
        logger.debug(f"Loading config from: {config_file}")
    else:
        if defaults:
            logger.debug("Config file not found, using provided defaults")
        else:
            logger.debug("Config file not found, using empty defaults")
        return config
    
    # Load and merge
    try:
        with open(config_file, 'r') as f:
            file_config = yaml.safe_load(f)
        
        if file_config:
            config = deep_merge(config, file_config)
            logger.debug(f"✓ Config loaded from {config_file}")
        else:
            logger.warning(f"Config file {config_file} is empty")
    
    except yaml.YAMLError as e:
        logger.error(f"YAML parse error in {config_file}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load config from {config_file}: {e}")
        raise
    
    return config


def deep_merge(base_dict: Dict, update_dict: Dict) -> Dict:
    """
    Recursively merge update_dict into base_dict.
    
    Args:
        base_dict: Base configuration dictionary
        update_dict: Dictionary with updates/overrides
        
    Returns:
        Merged dictionary (base_dict is modified in-place)
        
    Example:
        >>> base = {'a': 1, 'b': {'c': 2}}
        >>> update = {'b': {'c': 3, 'd': 4}}
        >>> result = deep_merge(base, update)
        >>> result
        {'a': 1, 'b': {'c': 3, 'd': 4}}
    """
    for key, value in update_dict.items():
        if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
            deep_merge(base_dict[key], value)
        else:
            base_dict[key] = value
    return base_dict


def get_config_value(config: Dict, key_path: str, default: Any = None) -> Any:
    """
    Get nested config value using dot-notation path.
    
    Args:
        config: Configuration dictionary
        key_path: Dot-separated path (e.g., 'training.learning_rate')
        default: Default value if key not found
        
    Returns:
        Value from config or default
        
    Example:
        >>> config = {'training': {'learning_rate': 0.001, 'epochs': 50}}
        >>> get_config_value(config, 'training.learning_rate')
        0.001
        >>> get_config_value(config, 'missing.value', 0)
        0
    """
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


def set_config_value(config: Dict, key_path: str, value: Any) -> None:
    """
    Set nested config value using dot-notation path.
    
    Args:
        config: Configuration dictionary (modified in-place)
        key_path: Dot-separated path (e.g., 'training.learning_rate')
        value: Value to set
        
    Example:
        >>> config = {'training': {'learning_rate': 0.001}}
        >>> set_config_value(config, 'training.epochs', 100)
        >>> config
        {'training': {'learning_rate': 0.001, 'epochs': 100}}
    """
    keys = key_path.split('.')
    current = config
    
    # Navigate to parent
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # Set the final value
    current[keys[-1]] = value


def validate_config(config: Dict, required_keys: Dict) -> tuple:
    """
    Validate that config contains required keys.
    
    Args:
        config: Configuration dictionary to validate
        required_keys: Dict of required keys and their types
                      e.g., {'training.epochs': int, 'model.type': str}
        
    Returns:
        Tuple of (is_valid: bool, message: str)
        
    Example:
        >>> config = {'training': {'epochs': 50}}
        >>> validate_config(config, {'training.epochs': int})
        (True, 'Config valid')
        >>> validate_config(config, {'missing.key': int})
        (False, 'Missing required key: missing.key')
    """
    for key_path, expected_type in required_keys.items():
        value = get_config_value(config, key_path)
        
        if value is None:
            return False, f"Missing required key: {key_path}"
        
        if expected_type and not isinstance(value, expected_type):
            return False, f"Key {key_path} should be {expected_type.__name__}, got {type(value).__name__}"
    
    return True, "Config valid"


def print_config(config: Dict, title: str = "Configuration", indent: int = 0) -> None:
    """
    Pretty-print configuration dictionary.
    
    Args:
        config: Configuration dictionary
        title: Title to print
        indent: Indentation level
        
    Example:
        >>> config = {'training': {'epochs': 50, 'batch_size': 32}}
        >>> print_config(config)
    """
    if indent == 0:
        logger.info("")
        logger.info("=" * 70)
        logger.info(title)
        logger.info("=" * 70)
    
    for key, value in sorted(config.items()):
        prefix = "  " * indent + "• "
        
        if isinstance(value, dict):
            logger.info(f"{prefix}{key}:")
            print_config(value, "", indent + 1)
        else:
            logger.info(f"{prefix}{key}: {value}")
    
    if indent == 0:
        logger.info("=" * 70)
        logger.info("")


# Convenience functions for accessing common config values
def get_learning_rate(config: Dict) -> float:
    """Get learning rate from config."""
    return get_config_value(config, 'training.learning_rate', 0.001)


def get_batch_size(config: Dict) -> int:
    """Get batch size from config."""
    return get_config_value(config, 'training.batch_size', 32)


def get_epochs(config: Dict) -> int:
    """Get number of epochs from config."""
    return get_config_value(config, 'training.epochs', 50)


def get_model_path(config: Dict) -> str:
    """Get model save path from config."""
    return get_config_value(config, 'paths.best_model_path', 'models/best_eeg_model.h5')


def get_output_dir(config: Dict) -> str:
    """Get output directory from config."""
    return get_config_value(config, 'paths.output_dir', 'outputs')


def get_eeg_channels(config: Dict) -> int:
    """Get number of EEG channels from config."""
    return get_config_value(config, 'data.eeg_channels', 8)


def get_n_classes(config: Dict) -> int:
    """Get number of classes from config."""
    return get_config_value(config, 'data.n_classes', 5)


def get_sampling_rate(config: Dict) -> int:
    """Get EEG sampling rate from config."""
    return get_config_value(config, 'data.sampling_rate', 250)
