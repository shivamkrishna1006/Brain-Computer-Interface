"""
Real-time EEG processing module.

This module provides real-time EEG signal processing capabilities
for continuous monitoring and classification.
"""

import logging
import time
from typing import Callable, Dict, Optional, Tuple
from collections import deque

import numpy as np
import tensorflow as tf
from tensorflow import keras

from preprocessing import EEGPreprocessor


logger = logging.getLogger('BCI')


class RealtimeEEGProcessor:
    """
    Real-time EEG processor for continuous signal monitoring and classification.
    """
    
    def __init__(self, config: Dict, model: keras.Model = None):
        """
        Initialize real-time EEG processor.
        
        Args:
            config: Configuration dictionary
            model: Trained Keras model for classification
        """
        self.config = config
        self.model = model
        
        # Buffer parameters
        self.buffer_size = config.get('realtime', {}).get('buffer_size', 250)
        self.overlap = config.get('realtime', {}).get('overlap', 0)
        self.update_interval = config.get('realtime', {}).get('update_interval', 0.1)
        
        # Initialize buffer
        self.n_channels = config['data']['eeg_channels']
        self.eeg_buffer = deque(maxlen=self.buffer_size)
        
        # Preprocessing
        prep_config = config.get('preprocessing', {})
        self.preprocessor = EEGPreprocessor(
            sampling_rate=config['data']['sampling_rate'],
            lowpass_freq=prep_config.get('lowpass_freq', 50),
            highpass_freq=prep_config.get('highpass_freq', 0.5),
            notch_freq=prep_config.get('notch_freq', 50)
        )
        
        # Timing
        self.last_update_time = time.time()
        self.last_prediction_time = time.time()
        
        # Callbacks
        self.on_prediction_callback: Optional[Callable] = None
        
        logger.info("Real-time EEG processor initialized")
    
    def add_sample(self, eeg_sample: np.ndarray) -> None:
        """
        Add a single EEG sample to the buffer.
        
        Args:
            eeg_sample: Single EEG sample (channels,)
        """
        if len(eeg_sample) != self.n_channels:
            logger.warning(f"Expected {self.n_channels} channels, got {len(eeg_sample)}")
            return
        
        self.eeg_buffer.append(eeg_sample)
    
    def add_samples(self, eeg_samples: np.ndarray) -> None:
        """
        Add multiple EEG samples to the buffer.
        
        Args:
            eeg_samples: Multiple EEG samples (num_samples, channels)
        """
        if eeg_samples.ndim != 2:
            logger.warning(f"Expected 2D array, got shape {eeg_samples.shape}")
            return
        
        if eeg_samples.shape[1] != self.n_channels:
            logger.warning(f"Expected {self.n_channels} channels, "
                          f"got {eeg_samples.shape[1]}")
            return
        
        for sample in eeg_samples:
            self.add_sample(sample)
    
    def is_buffer_ready(self) -> bool:
        """Check if buffer has enough samples for processing."""
        return len(self.eeg_buffer) >= self.buffer_size
    
    def process_buffer(self) -> Tuple[np.ndarray, bool]:
        """
        Process the current buffer of EEG data.
        
        Returns:
            Tuple of (processed_data, has_artifact)
        """
        if not self.is_buffer_ready():
            return None, False
        
        # Convert buffer to numpy array
        eeg_data = np.array(list(self.eeg_buffer))
        
        # Preprocess
        eeg_data = self.preprocessor.remove_baseline(eeg_data)
        eeg_data = self.preprocessor.filter_eeg(eeg_data)
        
        # Check artifacts
        artifact_mask = self.preprocessor.remove_artifacts(eeg_data)
        has_artifact = np.any(artifact_mask)
        
        if has_artifact:
            logger.warning("Artifacts detected in current buffer")
        
        return eeg_data, has_artifact
    
    def predict(self) -> Optional[Dict]:
        """
        Process buffer and make prediction if ready.
        
        Returns:
            Dictionary with prediction results or None
        """
        current_time = time.time()
        
        # Check if enough time has passed since last update
        if current_time - self.last_update_time < self.update_interval:
            return None
        
        # Check if buffer is ready
        if not self.is_buffer_ready():
            return None
        
        # Process buffer
        eeg_data, has_artifact = self.process_buffer()
        
        if eeg_data is None:
            return None
        
        # Make prediction
        if self.model is None:
            logger.warning("No model loaded for prediction")
            return None
        
        # Prepare input (add batch dimension and reshape)
        input_data = eeg_data.reshape(1, eeg_data.shape[0], eeg_data.shape[1])
        
        # Get prediction
        prediction = self.model.predict(input_data, verbose=0)
        predicted_class = int((prediction[0, 0] > 0.5).astype(int))
        confidence = float(prediction[0, 0])
        
        # Adjust confidence for class 0
        if predicted_class == 0:
            confidence = 1.0 - confidence
        
        result = {
            'timestamp': current_time,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'raw_output': float(prediction[0, 0]),
            'has_artifact': has_artifact,
            'buffer_size': len(self.eeg_buffer)
        }
        
        # Call callback if registered
        if self.on_prediction_callback:
            self.on_prediction_callback(result)
        
        self.last_update_time = current_time
        self.last_prediction_time = current_time
        
        return result
    
    def load_model(self, model_path: str) -> None:
        """
        Load a trained model.
        
        Args:
            model_path: Path to model file
        """
        try:
            self.model = keras.models.load_model(model_path)
            logger.info(f"Model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    
    def reset_buffer(self) -> None:
        """Reset the EEG buffer."""
        self.eeg_buffer.clear()
        logger.debug("Buffer reset")
    
    def get_buffer_stats(self) -> Dict:
        """Get statistics of current buffer."""
        if len(self.eeg_buffer) == 0:
            return {'buffer_empty': True}
        
        buffer_array = np.array(list(self.eeg_buffer))
        
        stats = {
            'buffer_size': len(self.eeg_buffer),
            'buffer_full': self.is_buffer_ready(),
            'mean': float(np.mean(buffer_array)),
            'std': float(np.std(buffer_array)),
            'min': float(np.min(buffer_array)),
            'max': float(np.max(buffer_array))
        }
        
        return stats


class StreamingDataAdapter:
    """
    Adapter for connecting various data streams to the real-time processor.
    """
    
    def __init__(self, processor: RealtimeEEGProcessor):
        """
        Initialize streaming data adapter.
        
        Args:
            processor: RealtimeEEGProcessor instance
        """
        self.processor = processor
        self.is_running = False
    
    def send_data(self, eeg_sample: np.ndarray) -> None:
        """Send a single sample to processor."""
        self.processor.add_sample(eeg_sample)
        
        # Try to predict
        prediction = self.processor.predict()
        if prediction:
            logger.debug(f"Prediction: class={prediction['predicted_class']}, "
                        f"confidence={prediction['confidence']:.2f}")
    
    def send_batch(self, eeg_batch: np.ndarray) -> None:
        """Send a batch of samples to processor."""
        self.processor.add_samples(eeg_batch)
        
        # Try to predict
        prediction = self.processor.predict()
        if prediction:
            logger.debug(f"Prediction: class={prediction['predicted_class']}, "
                        f"confidence={prediction['confidence']:.2f}")


def create_realtime_processor(config: Dict, model_path: str = None) -> RealtimeEEGProcessor:
    """
    Create and initialize real-time EEG processor.
    
    Args:
        config: Configuration dictionary
        model_path: Path to trained model (optional)
        
    Returns:
        Initialized RealtimeEEGProcessor instance
    """
    processor = RealtimeEEGProcessor(config)
    
    if model_path:
        processor.load_model(model_path)
    
    return processor
