"""
Real-Time EEG-Based Mouse Control System

Complete real-time inference system for BCI mouse control:
1. Loads trained CNN-LSTM model
2. Processes EEG samples in real-time
3. Predicts motor imagery class
4. Maps predictions to mouse actions:
   - Left → move cursor left
   - Right → move cursor right
   - Hands → move cursor up
   - Feet → move cursor down
   - Click → mouse click
5. Includes smoothing for natural cursor movement

Features:
- Model loading and inference
- Real-time EEG processing
- Confidence-based action triggering
- Exponential smoothing for cursor position
- Safety features (edge detection, pause mode)
- Comprehensive logging
- Performance monitoring

Author: BCI Interface Team
Version: 2.0
Status: Production-Ready
"""

import logging
import time
import numpy as np
from typing import Dict, Optional, Tuple, List
from pathlib import Path
from collections import deque
from datetime import datetime

import tensorflow as tf
from tensorflow import keras
import pyautogui

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING SETUP
# ─────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger('BCI_Inference')


# ─────────────────────────────────────────────────────────────────────────────
# CLASS MAPPING
# ─────────────────────────────────────────────────────────────────────────────

CLASS_LABELS = {
    0: 'Left',      # Move cursor left
    1: 'Right',     # Move cursor right
    2: 'Hands',     # Move cursor up
    3: 'Feet',      # Move cursor down
    4: 'Click'      # Mouse click
}

ACTION_MAPPING = {
    'Left': 'move_left',
    'Right': 'move_right',
    'Hands': 'move_up',
    'Feet': 'move_down',
    'Click': 'click'
}


# ─────────────────────────────────────────────────────────────────────────────
# CURSOR SMOOTHER
# ─────────────────────────────────────────────────────────────────────────────

class CursorSmoother:
    """
    Exponential smoothing for cursor movements to create natural motion.
    
    Features:
    - Exponential smoothing with configurable alpha
    - Velocity-based adaptive smoothing
    - Vector magnitude calculation
    - Position history tracking
    """
    
    def __init__(self, alpha: float = 0.3, enabled: bool = True):
        """
        Initialize cursor smoother.
        
        Args:
            alpha: Smoothing factor [0, 1]
                  0: high smoothing (slow response)
                  1: no smoothing (immediate response)
                  Default: 0.3 (good balance)
            enabled: Whether smoothing is enabled (default: True)
        """
        self.alpha = alpha
        self.enabled = enabled
        self.last_position = None
        self.smoothed_position = None
        self.position_history = deque(maxlen=10)
        
        logger.info(f"CursorSmoother initialized: alpha={alpha}, enabled={enabled}")
    
    def smooth(self, position: Tuple[int, int]) -> Tuple[int, int]:
        """
        Apply exponential smoothing to cursor position.
        
        Smoothing formula: smoothed = alpha * current + (1 - alpha) * previous
        
        Args:
            position: Current cursor position (x, y)
            
        Returns:
            Smoothed position (x, y)
        """
        if not self.enabled or self.smoothed_position is None:
            self.smoothed_position = position
            return position
        
        # Apply exponential smoothing independently for x and y
        x_smooth = int(self.alpha * position[0] + (1 - self.alpha) * self.smoothed_position[0])
        y_smooth = int(self.alpha * position[1] + (1 - self.alpha) * self.smoothed_position[1])
        
        self.smoothed_position = (x_smooth, y_smooth)
        self.position_history.append(self.smoothed_position)
        self.last_position = position
        
        return self.smoothed_position
    
    def get_velocity(self) -> float:
        """
        Calculate velocity of cursor movement.
        
        Returns:
            Magnitude of movement vector
        """
        if len(self.position_history) < 2:
            return 0.0
        
        current = self.position_history[-1]
        previous = self.position_history[-2]
        
        dx = current[0] - previous[0]
        dy = current[1] - previous[1]
        
        velocity = np.sqrt(dx**2 + dy**2)
        return float(velocity)
    
    def reset(self):
        """Reset smoother state."""
        self.smoothed_position = None
        self.position_history.clear()
        logger.debug("CursorSmoother reset")


# ─────────────────────────────────────────────────────────────────────────────
# MOUSE CONTROLLER
# ─────────────────────────────────────────────────────────────────────────────

class BCIMouseController:
    """
    BCI-based mouse controller with safety features.
    
    Maps EEG predictions to mouse actions with:
    - Confidence-based triggering
    - Movement smoothing
    - Edge detection (prevents moving off-screen)
    - Action debouncing
    - Safety pause mode
    """
    
    def __init__(self, 
                 move_distance: int = 50,
                 confidence_threshold: float = 0.7,
                 smoothing_alpha: float = 0.3,
                 debounce_count: int = 3):
        """
        Initialize BCI mouse controller.
        
        Args:
            move_distance: Pixels to move per action (default: 50)
            confidence_threshold: Min confidence to trigger action (default: 0.7)
            smoothing_alpha: Cursor smoothing factor [0,1] (default: 0.3)
            debounce_count: Number of consistent predictions before acting (default: 3)
        """
        self.move_distance = move_distance
        self.confidence_threshold = confidence_threshold
        self.debounce_count = debounce_count
        
        # Cursor smoothing
        self.smoother = CursorSmoother(alpha=smoothing_alpha, enabled=True)
        
        # Action state
        self.last_action = None
        self.last_action_time = 0
        self.action_cooldown = 0.1  # seconds
        self.prediction_history = deque(maxlen=debounce_count)
        
        # Safety
        self.paused = False
        self.screen_width, self.screen_height = pyautogui.size()
        self.safety_margin = 20  # pixels from edge
        
        # Statistics
        self.action_count = {action: 0 for action in ACTION_MAPPING.values()}
        self.total_predictions = 0
        
        logger.info(f"BCIMouseController initialized:")
        logger.info(f"  Move distance: {move_distance}px")
        logger.info(f"  Confidence threshold: {confidence_threshold}")
        logger.info(f"  Smoothing alpha: {smoothing_alpha}")
        logger.info(f"  Debounce count: {debounce_count}")
        logger.info(f"  Screen size: {self.screen_width}x{self.screen_height}")
    
    def execute_action(self, action: str) -> bool:
        """
        Execute mouse action with safety checks.
        
        Args:
            action: Action to execute (move_left, move_right, move_up, move_down, click)
            
        Returns:
            True if action executed, False otherwise
        """
        if self.paused:
            logger.debug("Controller paused, action skipped")
            return False
        
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_action_time < self.action_cooldown:
            return False
        
        # Get current position
        x, y = pyautogui.position()
        
        try:
            if action == 'move_left':
                new_x = max(self.safety_margin, x - self.move_distance)
                new_y = y
                self._move_cursor(new_x, new_y)
                
            elif action == 'move_right':
                new_x = min(self.screen_width - self.safety_margin, x + self.move_distance)
                new_y = y
                self._move_cursor(new_x, new_y)
                
            elif action == 'move_up':
                new_x = x
                new_y = max(self.safety_margin, y - self.move_distance)
                self._move_cursor(new_x, new_y)
                
            elif action == 'move_down':
                new_x = x
                new_y = min(self.screen_height - self.safety_margin, y + self.move_distance)
                self._move_cursor(new_x, new_y)
                
            elif action == 'click':
                pyautogui.click()
                logger.info(f"Action: CLICK at ({x}, {y})")
                
            else:
                logger.warning(f"Unknown action: {action}")
                return False
            
            # Update statistics
            self.action_count[action] = self.action_count.get(action, 0) + 1
            self.last_action = action
            self.last_action_time = current_time
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return False
    
    def _move_cursor(self, target_x: int, target_y: int):
        """
        Move cursor with smoothing.
        
        Args:
            target_x: Target X position
            target_y: Target Y position
        """
        # Apply smoothing
        smoothed_x, smoothed_y = self.smoother.smooth((target_x, target_y))
        
        # Move cursor
        pyautogui.moveTo(smoothed_x, smoothed_y, duration=0.05)
        
        velocity = self.smoother.get_velocity()
        logger.debug(f"Action: MOVE to ({smoothed_x}, {smoothed_y}) [velocity: {velocity:.1f}px]")
    
    def predict_and_act(self, predicted_class: int, confidence: float) -> Optional[str]:
        """
        Process prediction and execute action with debouncing.
        
        Args:
            predicted_class: Predicted class index (0-4)
            confidence: Confidence score (0-1)
            
        Returns:
            Action executed or None
        """
        self.total_predictions += 1
        
        # Check if prediction meets confidence threshold
        if confidence < self.confidence_threshold:
            logger.debug(f"Low confidence prediction ignored: class={predicted_class}, "
                        f"conf={confidence:.3f}")
            self.prediction_history.clear()
            return None
        
        # Track prediction
        class_label = CLASS_LABELS.get(predicted_class, 'Unknown')
        self.prediction_history.append((predicted_class, confidence))
        
        # Debouncing: check if we have consistent predictions
        if len(self.prediction_history) < self.debounce_count:
            logger.debug(f"Accumulating predictions: {len(self.prediction_history)}/{self.debounce_count}")
            return None
        
        # Check if all recent predictions are the same
        classes = [p[0] for p in self.prediction_history]
        if len(set(classes)) > 1:
            logger.debug(f"Inconsistent predictions, debouncing...")
            self.prediction_history.clear()
            return None
        
        # Execute action
        action = ACTION_MAPPING.get(class_label)
        if action:
            success = self.execute_action(action)
            if success:
                avg_confidence = np.mean([p[1] for p in self.prediction_history])
                logger.info(f"Action executed: {action} (class: {class_label}, "
                           f"avg_confidence: {avg_confidence:.3f})")
                self.prediction_history.clear()
                return action
        
        return None
    
    def set_pause(self, paused: bool):
        """
        Pause/resume controller.
        
        Args:
            paused: True to pause, False to resume
        """
        self.paused = paused
        status = "PAUSED" if paused else "RESUMED"
        logger.info(f"Controller {status}")
    
    def get_statistics(self) -> Dict:
        """
        Get controller statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            'total_predictions': self.total_predictions,
            'action_counts': dict(self.action_count),
            'paused': self.paused,
            'screen_size': (self.screen_width, self.screen_height),
            'cursor_smoother_velocity': self.smoother.get_velocity()
        }
    
    def reset(self):
        """Reset controller state."""
        self.prediction_history.clear()
        self.smoother.reset()
        self.action_count = {action: 0 for action in ACTION_MAPPING.values()}
        self.total_predictions = 0
        logger.info("Controller reset")


# ─────────────────────────────────────────────────────────────────────────────
# REAL-TIME INFERENCE ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class RealtimeInferenceEngine:
    """
    Complete real-time inference engine.
    
    Orchestrates:
    1. Model loading
    2. EEG buffer management
    3. Prediction
    4. Mouse control
    5. Statistics and logging
    """
    
    def __init__(self, 
                 model_path: str,
                 config: Dict,
                 move_distance: int = 50,
                 confidence_threshold: float = 0.7):
        """
        Initialize real-time inference engine.
        
        Args:
            model_path: Path to trained model (.h5 or SavedModel)
            config: Configuration dictionary with 'realtime' section
            move_distance: Pixels to move per action (default: 50)
            confidence_threshold: Min confidence for action (default: 0.7)
        """
        self.model_path = model_path
        self.config = config
        
        # Load model
        self.model = self._load_model(model_path)
        if self.model is None:
            raise ValueError(f"Failed to load model from {model_path}")
        
        # Configuration
        realtime_cfg = config.get('realtime', {})
        self.buffer_size = realtime_cfg.get('buffer_size', 250)
        self.n_channels = config.get('data', {}).get('eeg_channels', 8)
        self.sampling_rate = config.get('data', {}).get('sampling_rate', 250)
        
        # EEG buffer
        self.eeg_buffer = deque(maxlen=self.buffer_size)
        
        # Mouse controller
        self.controller = BCIMouseController(
            move_distance=move_distance,
            confidence_threshold=confidence_threshold,
            smoothing_alpha=0.3,
            debounce_count=3
        )
        
        # Timing
        self.prediction_count = 0
        self.start_time = None
        self.is_running = False
        
        logger.info(f"Inference engine initialized:")
        logger.info(f"  Model: {Path(model_path).name}")
        logger.info(f"  Buffer size: {self.buffer_size} samples")
        logger.info(f"  Channels: {self.n_channels}")
        logger.info(f"  Sampling rate: {self.sampling_rate} Hz")
    
    @staticmethod
    def _load_model(model_path: str) -> Optional[keras.Model]:
        """
        Load trained Keras model.
        
        Args:
            model_path: Path to model file
            
        Returns:
            Loaded model or None if failed
        """
        try:
            if not Path(model_path).exists():
                logger.error(f"Model file not found: {model_path}")
                return None
            
            logger.info(f"Loading model from {model_path}...")
            model = keras.models.load_model(model_path)
            logger.info(f"✓ Model loaded successfully")
            logger.info(f"  Input shape: {model.input_shape}")
            logger.info(f"  Output shape: {model.output_shape}")
            
            return model
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return None
    
    def add_sample(self, eeg_sample: np.ndarray) -> None:
        """
        Add single EEG sample to buffer.
        
        Args:
            eeg_sample: Single sample (n_channels,)
        """
        if eeg_sample.shape[0] != self.n_channels:
            logger.warning(f"Invalid sample shape: expected {self.n_channels}, "
                          f"got {eeg_sample.shape[0]}")
            return
        
        self.eeg_buffer.append(eeg_sample)
    
    def add_samples(self, eeg_samples: np.ndarray) -> None:
        """
        Add multiple EEG samples to buffer.
        
        Args:
            eeg_samples: Multiple samples (n_samples, n_channels)
        """
        if eeg_samples.ndim != 2:
            logger.warning(f"Expected 2D array, got {eeg_samples.ndim}D")
            return
        
        if eeg_samples.shape[1] != self.n_channels:
            logger.warning(f"Invalid channel count: expected {self.n_channels}, "
                          f"got {eeg_samples.shape[1]}")
            return
        
        for sample in eeg_samples:
            self.eeg_buffer.append(sample)
    
    def is_ready(self) -> bool:
        """Check if buffer has enough samples for inference."""
        return len(self.eeg_buffer) >= self.buffer_size
    
    def predict(self) -> Optional[Dict]:
        """
        Make prediction from current buffer.
        
        Returns:
            Dictionary with prediction results or None
        """
        if not self.is_ready():
            return None
        
        try:
            # Prepare input
            eeg_data = np.array(list(self.eeg_buffer), dtype=np.float32)
            input_data = eeg_data.reshape(1, self.buffer_size, self.n_channels)
            
            # Normalize
            input_data = (input_data - input_data.mean(axis=(0, 1), keepdims=True)) / \
                        (input_data.std(axis=(0, 1), keepdims=True) + 1e-8)
            
            # Predict
            output = self.model.predict(input_data, verbose=0)
            predicted_class = int(np.argmax(output[0]))
            confidence = float(np.max(output[0]))
            
            self.prediction_count += 1
            
            result = {
                'predicted_class': predicted_class,
                'class_label': CLASS_LABELS[predicted_class],
                'confidence': confidence,
                'probability_distribution': output[0].tolist(),
                'timestamp': datetime.now().isoformat(),
                'buffer_size': len(self.eeg_buffer)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None
    
    def process_signal(self) -> Optional[str]:
        """
        Process EEG signal and execute action if needed.
        
        Returns:
            Action executed or None
        """
        if not self.is_ready():
            return None
        
        # Get prediction
        result = self.predict()
        if result is None:
            return None
        
        # Execute action
        action = self.controller.predict_and_act(
            result['predicted_class'],
            result['confidence']
        )
        
        return action
    
    def start(self):
        """Start inference engine."""
        self.is_running = True
        self.start_time = datetime.now()
        logger.info("Inference engine started")
    
    def stop(self):
        """Stop inference engine."""
        self.is_running = False
        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        logger.info(f"Inference engine stopped")
        logger.info(f"  Duration: {duration:.1f}s")
        logger.info(f"  Predictions: {self.prediction_count}")
        logger.info(f"  Stats: {self.controller.get_statistics()}")
    
    def get_status(self) -> Dict:
        """
        Get current engine status.
        
        Returns:
            Status dictionary
        """
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            'running': self.is_running,
            'uptime_seconds': uptime,
            'buffer_usage': f"{len(self.eeg_buffer)}/{self.buffer_size}",
            'predictions_made': self.prediction_count,
            'controller_paused': self.controller.paused,
            'controller_stats': self.controller.get_statistics()
        }
