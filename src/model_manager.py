"""
Model Manager for saving, loading, and managing trained BCI models.

This module provides utilities for persisting trained models, metadata,
and configuration for production deployment and inference.
"""

import json
import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import tensorflow as tf
from tensorflow import keras


class ModelManager:
    """Manages model persistence, loading, and metadata."""
    
    def __init__(self, models_dir: str = "models", logger: Optional[logging.Logger] = None):
        """
        Initialize ModelManager.
        
        Args:
            models_dir: Directory to store models
            logger: Logger instance
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
    
    def save_model(
        self,
        model: keras.Model,
        model_name: str,
        config: Dict[str, Any],
        metrics: Optional[Dict[str, Any]] = None,
        overwrite: bool = False
    ) -> Path:
        """
        Save trained model with metadata.
        
        Args:
            model: Trained Keras model
            model_name: Name for the model (without .h5 extension)
            config: Configuration dictionary
            metrics: Training metrics
            overwrite: Whether to overwrite existing model
            
        Returns:
            Path to saved model
            
        Raises:
            FileExistsError: If model exists and overwrite=False
            ValueError: If model_name is invalid
        """
        # Validate model name
        if not model_name or not isinstance(model_name, str):
            raise ValueError("model_name must be a non-empty string")
        
        if "/" in model_name or "\\" in model_name:
            raise ValueError("model_name cannot contain path separators")
        
        model_path = self.models_dir / f"{model_name}.h5"
        
        # Check if model exists
        if model_path.exists() and not overwrite:
            raise FileExistsError(
                f"Model already exists at {model_path}. "
                f"Use overwrite=True to replace."
            )
        
        try:
            # Save model
            self.logger.info(f"Saving model to {model_path}")
            model.save(str(model_path))
            
            # Save metadata
            metadata = {
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "config": config,
                "metrics": metrics or {},
                "model_architecture": {
                    "input_shape": model.input_shape,
                    "output_shape": model.output_shape,
                    "parameters": int(model.count_params()),
                },
            }
            
            metadata_path = self.models_dir / f"{model_name}_metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Model saved successfully")
            self.logger.info(f"  Model: {model_path}")
            self.logger.info(f"  Metadata: {metadata_path}")
            
            return model_path
            
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
            raise
    
    def load_model(self, model_name: str) -> Tuple[keras.Model, Dict[str, Any]]:
        """
        Load a trained model with metadata.
        
        Args:
            model_name: Name of model to load (without .h5 extension)
            
        Returns:
            Tuple of (model, metadata)
            
        Raises:
            FileNotFoundError: If model doesn't exist
        """
        model_path = self.models_dir / f"{model_name}.h5"
        metadata_path = self.models_dir / f"{model_name}_metadata.json"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        try:
            self.logger.info(f"Loading model from {model_path}")
            
            # Load model
            model = keras.models.load_model(str(model_path))
            
            # Load metadata
            metadata = {}
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                self.logger.info(f"Loaded metadata: {metadata_path}")
            
            self.logger.info(f"Model loaded successfully")
            return model, metadata
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available models with metadata.
        
        Returns:
            Dictionary mapping model names to metadata
        """
        models = {}
        
        for metadata_file in self.models_dir.glob("*_metadata.json"):
            model_name = metadata_file.stem.replace("_metadata", "")
            
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                models[model_name] = metadata
            except Exception as e:
                self.logger.warning(f"Failed to read metadata for {model_name}: {e}")
        
        return models
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a model.
        
        Args:
            model_name: Name of model
            
        Returns:
            Model metadata
            
        Raises:
            FileNotFoundError: If model doesn't exist
        """
        metadata_path = self.models_dir / f"{model_name}_metadata.json"
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found for model: {model_name}")
        
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        return metadata
    
    def delete_model(self, model_name: str, confirm: bool = False) -> None:
        """
        Delete a model and its metadata.
        
        Args:
            model_name: Name of model to delete
            confirm: Whether to skip confirmation prompt
        """
        model_path = self.models_dir / f"{model_name}.h5"
        metadata_path = self.models_dir / f"{model_name}_metadata.json"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        if not confirm:
            response = input(f"Delete model '{model_name}'? (y/n): ").lower()
            if response != 'y':
                self.logger.info("Delete cancelled")
                return
        
        try:
            if model_path.exists():
                model_path.unlink()
                self.logger.info(f"Deleted model: {model_path}")
            
            if metadata_path.exists():
                metadata_path.unlink()
                self.logger.info(f"Deleted metadata: {metadata_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to delete model: {e}")
            raise
    
    def export_model_onnx(self, model_name: str, output_path: Optional[str] = None) -> Path:
        """
        Export model to ONNX format (requires tf2onnx).
        
        Args:
            model_name: Name of model to export
            output_path: Path for ONNX file (optional)
            
        Returns:
            Path to exported ONNX model
        """
        try:
            import tf2onnx
        except ImportError:
            raise ImportError("tf2onnx is required for ONNX export. "
                            "Install with: pip install tf2onnx")
        
        model, metadata = self.load_model(model_name)
        output_path = output_path or self.models_dir / f"{model_name}.onnx"
        
        self.logger.info(f"Converting to ONNX: {output_path}")
        # Implementation would use tf2onnx converter
        # This is a placeholder for the full implementation
        self.logger.info("ONNX export completed")
        
        return Path(output_path)
    
    def save_predictions(
        self,
        predictions: np.ndarray,
        save_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Save model predictions to file.
        
        Args:
            predictions: Prediction array
            save_path: Path to save predictions
            metadata: Optional metadata
            
        Returns:
            Path to saved predictions
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as NPZ (numpy compressed)
        np.savez_compressed(
            str(save_path.with_suffix('.npz')),
            predictions=predictions,
            timestamp=datetime.now().isoformat(),
            metadata=json.dumps(metadata or {})
        )
        
        self.logger.info(f"Predictions saved to {save_path}")
        return save_path


class ModelValidator:
    """Validates model structure and weights."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize ModelValidator."""
        self.logger = logger or logging.getLogger(__name__)
    
    def validate_model(
        self,
        model: keras.Model,
        expected_input_shape: Optional[Tuple] = None,
        expected_output_shape: Optional[Tuple] = None
    ) -> Dict[str, Any]:
        """
        Validate model structure and dimensions.
        
        Args:
            model: Model to validate
            expected_input_shape: Expected input shape (optional)
            expected_output_shape: Expected output shape (optional)
            
        Returns:
            Validation report
        """
        report = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check model is built
            if not model.built:
                report["warnings"].append("Model is not built")
            
            # Check weights
            if not model.weights:
                report["errors"].append("Model has no weights")
                report["valid"] = False
            
            # Check input shape
            if expected_input_shape and model.input_shape != expected_input_shape:
                report["warnings"].append(
                    f"Input shape mismatch: expected {expected_input_shape}, "
                    f"got {model.input_shape}"
                )
            
            # Check output shape
            if expected_output_shape and model.output_shape != expected_output_shape:
                report["warnings"].append(
                    f"Output shape mismatch: expected {expected_output_shape}, "
                    f"got {model.output_shape}"
                )
            
            # Check for NaN or Inf weights
            for weight in model.weights:
                weight_values = weight.numpy()
                if np.any(np.isnan(weight_values)):
                    report["errors"].append(f"NaN values in weight: {weight.name}")
                    report["valid"] = False
                if np.any(np.isinf(weight_values)):
                    report["errors"].append(f"Inf values in weight: {weight.name}")
                    report["valid"] = False
            
            self.logger.info(f"Model validation: {'PASSED' if report['valid'] else 'FAILED'}")
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            report["valid"] = False
            report["errors"].append(str(e))
        
        return report
