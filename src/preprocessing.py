"""
EEG signal preprocessing module.

This module provides functions for preprocessing EEG signals including
filtering, artifact removal, and normalization.
"""

import logging
from typing import Tuple

import numpy as np
from scipy import signal
from scipy.fft import fft


logger = logging.getLogger('BCI')


class EEGPreprocessor:
    """
    EEG signal preprocessor for filtering and artifact removal.
    """
    
    def __init__(self, sampling_rate: int, lowpass_freq: float, 
                 highpass_freq: float, notch_freq: float = 50.0):
        """
        Initialize EEG preprocessor.
        
        Args:
            sampling_rate: Sampling rate in Hz
            lowpass_freq: Lowpass filter cutoff frequency in Hz
            highpass_freq: Highpass filter cutoff frequency in Hz
            notch_freq: Notch filter frequency in Hz (power line noise)
        """
        self.sampling_rate = sampling_rate
        self.lowpass_freq = lowpass_freq
        self.highpass_freq = highpass_freq
        self.notch_freq = notch_freq
        
        # Design filters
        self._design_filters()
        
    def _design_filters(self) -> None:
        """Design filtering coefficients."""
        nyquist_freq = self.sampling_rate / 2
        
        # Bandpass filter (highpass + lowpass)
        low = self.highpass_freq / nyquist_freq
        high = self.lowpass_freq / nyquist_freq
        
        # Ensure valid frequency ranges
        low = np.clip(low, 0.001, 0.999)
        high = np.clip(high, 0.001, 0.999)
        
        if low >= high:
            low, high = high * 0.9, high
        
        self.sos_bandpass = signal.butter(5, [low, high], 'band', output='sos')
        
        # Notch filter for power line noise
        notch_normalized = self.notch_freq / nyquist_freq
        notch_normalized = np.clip(notch_normalized, 0.001, 0.999)
        self.sos_notch = signal.butter(4, [notch_normalized - 0.01, notch_normalized + 0.01], 
                                       'bandstop', output='sos')
    
    def filter_eeg(self, eeg_data: np.ndarray) -> np.ndarray:
        """
        Apply bandpass and notch filters to EEG signal.
        
        Args:
            eeg_data: Input EEG data (samples, channels)
            
        Returns:
            Filtered EEG data
        """
        # Handle single channel
        if eeg_data.ndim == 1:
            eeg_data = eeg_data.reshape(-1, 1)
        
        filtered_data = eeg_data.copy()
        
        # Apply filters to each channel
        for ch in range(eeg_data.shape[1]):
            # Bandpass filter
            filtered_data[:, ch] = signal.sosfilt(self.sos_bandpass, filtered_data[:, ch])
            
            # Notch filter
            filtered_data[:, ch] = signal.sosfilt(self.sos_notch, filtered_data[:, ch])
        
        return filtered_data
    
    def remove_artifacts(self, eeg_data: np.ndarray, threshold: float = 100.0) -> np.ndarray:
        """
        Remove artifact samples based on amplitude threshold.
        
        Args:
            eeg_data: Input EEG data (samples, channels)
            threshold: Amplitude threshold in μV
            
        Returns:
            Artifact indicator mask (True = artifact, False = clean)
        """
        if eeg_data.ndim == 1:
            eeg_data = eeg_data.reshape(-1, 1)
        
        # Calculate RMS amplitude for each sample
        rms_amplitude = np.sqrt(np.mean(eeg_data ** 2, axis=1))
        
        # Mark artifacts
        artifact_mask = rms_amplitude > threshold
        
        return artifact_mask
    
    def remove_baseline(self, eeg_data: np.ndarray, window_size: int = 250) -> np.ndarray:
        """
        Remove baseline drift using moving average detrending.
        
        Args:
            eeg_data: Input EEG data (samples, channels)
            window_size: Window size for moving average
            
        Returns:
            Detrended EEG data
        """
        if eeg_data.ndim == 1:
            eeg_data = eeg_data.reshape(-1, 1)
        
        detrended_data = eeg_data.copy()
        
        # Apply moving average detrending to each channel
        for ch in range(eeg_data.shape[1]):
            baseline = signal.savgol_filter(eeg_data[:, ch], 
                                           window_length=min(window_size, len(eeg_data)),
                                           polyorder=1)
            detrended_data[:, ch] = eeg_data[:, ch] - baseline
        
        return detrended_data
    
    def extract_features(self, eeg_data: np.ndarray) -> np.ndarray:
        """
        Extract statistical features from EEG signal.
        
        Features include: mean, std, min, max, median, skewness, kurtosis, RMS.
        
        Args:
            eeg_data: Input EEG data (samples, channels)
            
        Returns:
            Feature matrix (channels, num_features)
        """
        if eeg_data.ndim == 1:
            eeg_data = eeg_data.reshape(-1, 1)
        
        features = []
        
        for ch in range(eeg_data.shape[1]):
            channel_data = eeg_data[:, ch]
            
            # Statistical features
            feature_vector = np.array([
                np.mean(channel_data),
                np.std(channel_data),
                np.min(channel_data),
                np.max(channel_data),
                np.median(channel_data),
                signal.skew(channel_data),
                signal.kurtosis(channel_data),
                np.sqrt(np.mean(channel_data ** 2))  # RMS
            ])
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def extract_spectral_features(self, eeg_data: np.ndarray, 
                                  frequency_bands: dict = None) -> np.ndarray:
        """
        Extract spectral features using power spectral density.
        
        Default frequency bands: delta, theta, alpha, beta, gamma.
        
        Args:
            eeg_data: Input EEG data (samples, channels)
            frequency_bands: Dictionary of frequency bands to extract
            
        Returns:
            Spectral feature matrix (channels, num_bands)
        """
        if frequency_bands is None:
            frequency_bands = {
                'delta': (0.5, 4),
                'theta': (4, 8),
                'alpha': (8, 12),
                'beta': (12, 30),
                'gamma': (30, 50)
            }
        
        if eeg_data.ndim == 1:
            eeg_data = eeg_data.reshape(-1, 1)
        
        features = []
        
        for ch in range(eeg_data.shape[1]):
            channel_data = eeg_data[:, ch]
            
            # Compute power spectral density using Welch's method
            freqs, psd = signal.welch(channel_data, self.sampling_rate, 
                                     nperseg=min(256, len(channel_data)))
            
            # Extract power in each frequency band
            band_powers = []
            for band_name, (low_freq, high_freq) in frequency_bands.items():
                band_mask = (freqs >= low_freq) & (freqs <= high_freq)
                band_power = np.sum(psd[band_mask])
                band_powers.append(band_power)
            
            features.append(band_powers)
        
        return np.array(features)


def preprocess_eeg_segment(eeg_segment: np.ndarray, preprocessor: EEGPreprocessor,
                          remove_artifacts: bool = True) -> Tuple[np.ndarray, bool]:
    """
    Preprocess a single EEG segment.
    
    Args:
        eeg_segment: Single EEG segment (samples, channels)
        preprocessor: EEGPreprocessor instance
        remove_artifacts: Whether to remove artifacts
        
    Returns:
        Preprocessed segment and artifact flag
    """
    # Remove baseline drift
    eeg_segment = preprocessor.remove_baseline(eeg_segment)
    
    # Apply filters
    eeg_segment = preprocessor.filter_eeg(eeg_segment)
    
    # Check for artifacts
    has_artifact = False
    if remove_artifacts:
        artifact_mask = preprocessor.remove_artifacts(eeg_segment)
        has_artifact = np.any(artifact_mask)
    
    return eeg_segment, has_artifact


def preprocess_eeg_batch(eeg_data: np.ndarray, config: dict) -> Tuple[np.ndarray, np.ndarray]:
    """
    Preprocess a batch of EEG data.
    
    Args:
        eeg_data: EEG data array (num_samples, time_steps, channels)
        config: Configuration dictionary
        
    Returns:
        Preprocessed data and artifact flags
    """
    prep_config = config.get('preprocessing', {})
    
    preprocessor = EEGPreprocessor(
        sampling_rate=config['data']['sampling_rate'],
        lowpass_freq=prep_config.get('lowpass_freq', 50),
        highpass_freq=prep_config.get('highpass_freq', 0.5),
        notch_freq=prep_config.get('notch_freq', 50)
    )
    
    processed_data = []
    artifact_flags = []
    
    logger.info(f"Preprocessing {len(eeg_data)} EEG segments...")
    
    for i, segment in enumerate(eeg_data):
        segment_processed, has_artifact = preprocess_eeg_segment(
            segment, preprocessor,
            remove_artifacts=prep_config.get('remove_artifacts', True)
        )
        processed_data.append(segment_processed)
        artifact_flags.append(has_artifact)
        
        if (i + 1) % 100 == 0:
            logger.info(f"Processed {i + 1} segments")
    
    processed_data = np.array(processed_data)
    artifact_flags = np.array(artifact_flags)
    
    return processed_data, artifact_flags
