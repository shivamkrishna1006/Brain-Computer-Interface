"""
Click detection module for BCI.

This module provides click detection functionality for controlling
external devices through EEG-based commands.
"""

import logging
import time
from typing import Dict, List, Optional
from collections import deque
from dataclasses import dataclass


logger = logging.getLogger('BCI')


@dataclass
class ClickEvent:
    """Represents a detected click event."""
    timestamp: float
    confidence: float
    duration: float = 0.0
    position: Optional[tuple] = None


class ClickDetector:
    """
    Click detector for BCI system.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize click detector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        click_config = config.get('click_detection', {})
        
        # Click parameters
        self.min_duration = click_config.get('min_duration', 0.1)
        self.max_duration = click_config.get('max_duration', 2.0)
        self.hold_duration = click_config.get('hold_duration', 0.05)
        self.debounce_time = click_config.get('debounce_time', 0.2)
        
        # State tracking
        self.is_clicking = False
        self.click_start_time = None
        self.last_click_time = None
        self.last_click_confidence = 0.0
        
        # Event history
        self.click_history: deque = deque(maxlen=100)
        
        # Callbacks
        self.on_click_callback: Optional[callable] = None
        self.on_release_callback: Optional[callable] = None
        
        logger.info("Click detector initialized")
    
    def process_prediction(self, prediction: Dict) -> Optional[ClickEvent]:
        """
        Process model prediction and detect click events.
        
        Args:
            prediction: Prediction dictionary from real-time processor
            
        Returns:
            ClickEvent if click is detected, None otherwise
        """
        if prediction is None:
            return None
        
        predicted_class = prediction['predicted_class']
        confidence = prediction['confidence']
        timestamp = prediction['timestamp']
        has_artifact = prediction.get('has_artifact', False)
        
        # Skip if artifacts detected
        if has_artifact:
            confidence *= 0.5  # Reduce confidence for artifact samples
        
        # Confidence threshold
        confidence_threshold = self.config.get('realtime', {}).get(
            'confidence_threshold', 0.7)
        
        # Check for click detection
        click_detected = predicted_class == 1 and confidence > confidence_threshold
        
        # State machine for click detection
        if click_detected and not self.is_clicking:
            # Click started
            self._on_click_start(timestamp, confidence)
        
        elif click_detected and self.is_clicking:
            # Click continues
            self.last_click_confidence = max(self.last_click_confidence, confidence)
        
        elif not click_detected and self.is_clicking:
            # Click may have ended
            click_duration = timestamp - self.click_start_time
            
            if click_duration >= self.min_duration:
                # Valid click detected
                click_event = self._on_click_end(timestamp, click_duration)
                return click_event
            else:
                # Click too short, ignore
                self.is_clicking = False
                self.click_start_time = None
        
        return None
    
    def _on_click_start(self, timestamp: float, confidence: float) -> None:
        """Handle click start event."""
        current_time = time.time()
        
        # Check debounce
        if self.last_click_time and (current_time - self.last_click_time < self.debounce_time):
            return
        
        self.is_clicking = True
        self.click_start_time = timestamp
        self.last_click_confidence = confidence
        
        logger.debug(f"Click started at {timestamp:.3f}")
        
        if self.on_click_callback:
            self.on_click_callback(timestamp, confidence)
    
    def _on_click_end(self, timestamp: float, duration: float) -> ClickEvent:
        """Handle click end event."""
        self.is_clicking = False
        self.last_click_time = time.time()
        
        click_event = ClickEvent(
            timestamp=self.click_start_time,
            confidence=self.last_click_confidence,
            duration=duration
        )
        
        self.click_history.append(click_event)
        
        logger.info(f"Click detected: duration={duration:.3f}s, "
                   f"confidence={self.last_click_confidence:.2f}")
        
        if self.on_release_callback:
            self.on_release_callback(click_event)
        
        return click_event
    
    def hold_click(self, duration: float = None) -> None:
        """
        Maintain click hold for specified duration.
        
        Args:
            duration: Hold duration in seconds (default: config hold_duration)
        """
        duration = duration or self.hold_duration
        
        if not self.is_clicking:
            self.is_clicking = True
            self.click_start_time = time.time()
            self.last_click_confidence = 1.0
        
        logger.debug(f"Holding click for {duration:.3f}s")
        time.sleep(duration)
        
        self.is_clicking = False
    
    def reset(self) -> None:
        """Reset click detector state."""
        self.is_clicking = False
        self.click_start_time = None
        self.last_click_confidence = 0.0
        self.last_click_time = None
        logger.debug("Click detector reset")
    
    def get_click_history(self, count: int = 10) -> List[ClickEvent]:
        """
        Get last N click events.
        
        Args:
            count: Number of recent clicks to return
            
        Returns:
            List of recent ClickEvent objects
        """
        return list(self.click_history)[-count:]
    
    def get_statistics(self) -> Dict:
        """Get click detection statistics."""
        if len(self.click_history) == 0:
            return {
                'total_clicks': 0,
                'average_duration': 0.0,
                'average_confidence': 0.0
            }
        
        durations = [click.duration for click in self.click_history]
        confidences = [click.confidence for click in self.click_history]
        
        stats = {
            'total_clicks': len(self.click_history),
            'average_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'average_confidence': sum(confidences) / len(confidences),
            'min_confidence': min(confidences),
            'max_confidence': max(confidences)
        }
        
        return stats


class ClickEventHandler:
    """
    Handler for click events with support for custom actions.
    """
    
    def __init__(self):
        """Initialize click event handler."""
        self.click_actions: Dict = {}
        self.default_action: Optional[callable] = None
    
    def register_action(self, action_id: str, callback: callable) -> None:
        """
        Register a callback for a click action.
        
        Args:
            action_id: Unique action identifier
            callback: Callback function to execute
        """
        self.click_actions[action_id] = callback
        logger.info(f"Registered click action: {action_id}")
    
    def trigger_action(self, action_id: str, click_event: ClickEvent) -> None:
        """
        Trigger an action on click event.
        
        Args:
            action_id: Action identifier
            click_event: ClickEvent object
        """
        if action_id in self.click_actions:
            try:
                self.click_actions[action_id](click_event)
                logger.debug(f"Triggered action: {action_id}")
            except Exception as e:
                logger.error(f"Error executing action {action_id}: {e}")
        elif self.default_action:
            try:
                self.default_action(click_event)
            except Exception as e:
                logger.error(f"Error executing default action: {e}")
        else:
            logger.warning(f"No action registered for {action_id}")
    
    def set_default_action(self, callback: callable) -> None:
        """
        Set default action for unregistered click events.
        
        Args:
            callback: Default callback function
        """
        self.default_action = callback


def create_click_detector(config: Dict) -> ClickDetector:
    """
    Create and initialize click detector.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Initialized ClickDetector instance
    """
    return ClickDetector(config)
