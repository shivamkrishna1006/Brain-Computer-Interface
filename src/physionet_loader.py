"""
PhysioNet EEG Motor Imagery Dataset Loader using MNE.

This module provides functionality to load and preprocess the PhysioNet EEG 
Motor Imagery dataset for Brain-Computer Interface applications.

Dataset: https://physionet.org/content/eegmmidb/1.0.0/
- Multiple subjects (1-109)
- Motor imagery tasks: left hand, right hand, hands, feet
- 64 EEG channels
- 160 Hz sampling rate
- Multiple runs per session
"""

import logging
import os
from typing import Tuple, List, Dict, Optional

import numpy as np
import mne
from mne.datasets import eegbci

logger = logging.getLogger('BCI')


class PhysioNetEEGDataset:
    """
    Loader for PhysioNet EEG Motor Imagery Dataset.
    
    Supports loading multiple subjects with motor imagery classifications:
    - Left Hand (run 3, 7, 11)
    - Right Hand (run 4, 8, 12)
    - Both Hands (run 5, 9, 13)
    - Both Feet (run 6, 10, 14)
    """
    
    # Run configurations for different motor imagery tasks
    RUN_MAPPING = {
        'left_hand': [3, 7, 11],
        'right_hand': [4, 8, 12],
        'both_hands': [5, 9, 13],
        'both_feet': [6, 10, 14]
    }
    
    # Event mapping for motor imagery tasks
    EVENT_MAPPING = {
        'left_hand': 1,
        'right_hand': 2,
        'both_hands': 3,
        'both_feet': 4
    }
    
    # Labels to class mapping
    LABEL_MAPPING = {
        0: 'Rest',
        1: 'Left Hand',
        2: 'Right Hand',
        3: 'Both Hands',
        4: 'Both Feet'
    }
    
    def __init__(self, data_dir: str = 'data/physionet', verbose: bool = False):
        """
        Initialize PhysioNet EEG Dataset loader.
        
        Args:
            data_dir: Directory to store/load dataset
            verbose: Whether to print verbose MNE logging
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Set MNE verbosity
        mne.set_log_level('INFO' if verbose else 'WARNING')
        
        logger.info(f"PhysioNet EEG Dataset loader initialized with data_dir: {data_dir}")
    
    def load_subject(self, subject_id: int, 
                    tasks: Optional[List[str]] = None,
                    sessions: int = 1,
                    filter_freqs: Tuple[float, float] = (8, 30),
                    epoch_window: Tuple[float, float] = (0.5, 3.5)) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load data for a single subject.
        
        Args:
            subject_id: Subject ID (1-109)
            tasks: List of motor imagery tasks to load
                   ('left_hand', 'right_hand', 'both_hands', 'both_feet')
                   If None, loads all tasks
            sessions: Number of sessions to load (typically 1 or 2)
            filter_freqs: Bandpass filter frequencies (low, high) in Hz
            epoch_window: Epoch time window (tmin, tmax) in seconds
                         (0.5, 3.5) means 0.5-3.5s after stimulus onset
        
        Returns:
            Tuple of (X, y) where:
                X: EEG data array of shape (n_epochs, n_channels, n_times)
                y: Labels array of shape (n_epochs,)
        """
        if tasks is None:
            tasks = list(self.RUN_MAPPING.keys())
        
        logger.info(f"Loading subject {subject_id}: tasks={tasks}, sessions={sessions}")
        
        try:
            # Download and load dataset
            raw_list = self._download_and_load_runs(subject_id, tasks, sessions)
            
            if not raw_list:
                logger.warning(f"No data loaded for subject {subject_id}")
                return np.array([]), np.array([])
            
            # Concatenate all runs
            raw = mne.concatenate_raws(raw_list)
            
            # Preprocess: filter and extract epochs
            X, y = self._preprocess_and_extract_epochs(
                raw, filter_freqs=filter_freqs, epoch_window=epoch_window
            )
            
            logger.info(f"Loaded subject {subject_id}: {X.shape[0]} epochs, "
                       f"{X.shape[1]} channels, {X.shape[2]} time points")
            
            return X, y
        
        except Exception as e:
            logger.error(f"Error loading subject {subject_id}: {e}")
            return np.array([]), np.array([])
    
    def load_subjects(self, subject_ids: List[int],
                     tasks: Optional[List[str]] = None,
                     sessions: int = 1,
                     filter_freqs: Tuple[float, float] = (8, 30),
                     epoch_window: Tuple[float, float] = (0.5, 3.5)) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load data for multiple subjects.
        
        Args:
            subject_ids: List of subject IDs to load
            tasks: Motor imagery tasks to load
            sessions: Number of sessions per subject
            filter_freqs: Bandpass filter frequencies
            epoch_window: Epoch time window
        
        Returns:
            Tuple of (X, y) with data from all subjects concatenated
        """
        logger.info(f"Loading {len(subject_ids)} subjects...")
        
        X_all = []
        y_all = []
        
        for subject_id in subject_ids:
            X, y = self.load_subject(
                subject_id,
                tasks=tasks,
                sessions=sessions,
                filter_freqs=filter_freqs,
                epoch_window=epoch_window
            )
            
            if len(X) > 0:
                X_all.append(X)
                y_all.append(y)
        
        if not X_all:
            logger.warning("No data loaded for any subject")
            return np.array([]), np.array([])
        
        # Concatenate all subjects
        X_combined = np.concatenate(X_all, axis=0)
        y_combined = np.concatenate(y_all, axis=0)
        
        logger.info(f"Loaded {len(subject_ids)} subjects: total {X_combined.shape[0]} epochs")
        
        return X_combined, y_combined
    
    def _download_and_load_runs(self, subject_id: int, tasks: List[str],
                               sessions: int) -> List[mne.io.Raw]:
        """
        Download and load specific runs for given tasks and sessions.
        
        Args:
            subject_id: Subject ID
            tasks: List of motor imagery tasks
            sessions: Number of sessions
        
        Returns:
            List of Raw objects for each run
        """
        raw_list = []
        
        for session in range(1, sessions + 1):
            for task in tasks:
                if task not in self.RUN_MAPPING:
                    logger.warning(f"Unknown task: {task}")
                    continue
                
                # Load each run for this task-session combination
                for run in self.RUN_MAPPING[task]:
                    try:
                        # Download data
                        raw = eegbci.read_raw_eegbci(
                            subject=subject_id,
                            session=session,
                            run=run,
                            path=self.data_dir,
                            preload=True
                        )
                        
                        logger.debug(f"Loaded S{subject_id:03d} Session {session} Run {run:02d}")
                        raw_list.append(raw)
                    
                    except Exception as e:
                        logger.debug(f"Could not load S{subject_id:03d} Session {session} "
                                    f"Run {run:02d}: {e}")
                        continue
        
        return raw_list
    
    def _preprocess_and_extract_epochs(self, raw: mne.io.Raw,
                                      filter_freqs: Tuple[float, float],
                                      epoch_window: Tuple[float, float]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess data and extract epochs.
        
        Args:
            raw: Raw EEG data
            filter_freqs: Bandpass filter frequencies
            epoch_window: Epoch time window (tmin, tmax)
        
        Returns:
            Tuple of (X, y) epochs and labels
        """
        # Set montage
        raw.set_eeg_reference('average')
        
        # Apply bandpass filter
        raw.filter(filter_freqs[0], filter_freqs[1], l_trans_bandwidth=2, 
                   h_trans_bandwidth=2, filter_length='auto', phase='zero')
        
        logger.debug(f"Applied bandpass filter {filter_freqs[0]}-{filter_freqs[1]} Hz")
        
        # Extract events
        events, event_id = mne.events_from_annotations(raw)
        
        # Filter events to only motor imagery tasks (event IDs 1-4)
        motor_imagery_events = []
        for event in events:
            if 1 <= event[2] <= 4:  # Event IDs for motor imagery
                motor_imagery_events.append(event)
        
        motor_imagery_events = np.array(motor_imagery_events)
        
        if len(motor_imagery_events) == 0:
            logger.warning("No motor imagery events found")
            return np.array([]), np.array([])
        
        logger.debug(f"Found {len(motor_imagery_events)} motor imagery events")
        
        # Create epochs
        epochs = mne.Epochs(
            raw,
            motor_imagery_events,
            event_id={
                'Left Hand': 1,
                'Right Hand': 2,
                'Both Hands': 3,
                'Both Feet': 4
            },
            tmin=epoch_window[0],
            tmax=epoch_window[1],
            baseline=(epoch_window[0], 0),  # Baseline correct
            preload=True,
            picks='eeg',
            verbose=False
        )
        
        logger.debug(f"Extracted {len(epochs)} epochs")
        
        # Convert to data arrays
        X = epochs.get_data(units='uV')  # (n_epochs, n_channels, n_times)
        y = epochs.events[:, 2]  # Event IDs as labels
        
        return X, y
    
    def get_data_info(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """
        Get information about loaded dataset.
        
        Args:
            X: Data array
            y: Labels array
        
        Returns:
            Dictionary with dataset information
        """
        unique_labels, counts = np.unique(y, return_counts=True)
        
        info = {
            'n_epochs': X.shape[0],
            'n_channels': X.shape[1],
            'n_timepoints': X.shape[2],
            'n_classes': len(unique_labels),
            'class_distribution': {
                self.LABEL_MAPPING.get(label, f'Unknown_{label}'): int(count)
                for label, count in zip(unique_labels, counts)
            },
            'data_shape': X.shape,
            'labels_shape': y.shape,
            'data_dtype': str(X.dtype),
            'data_min': float(np.min(X)),
            'data_max': float(np.max(X)),
            'data_mean': float(np.mean(X)),
            'data_std': float(np.std(X))
        }
        
        return info


def load_physionet_data(subject_ids: List[int],
                       tasks: Optional[List[str]] = None,
                       sessions: int = 1,
                       filter_freqs: Tuple[float, float] = (8, 30),
                       epoch_window: Tuple[float, float] = (0.5, 3.5),
                       data_dir: str = 'data/physionet',
                       verbose: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convenience function to load PhysioNet EEG data.
    
    Args:
        subject_ids: List of subject IDs to load (1-109)
        tasks: Motor imagery tasks to load. Options:
               'left_hand', 'right_hand', 'both_hands', 'both_feet'
               Default: load all tasks
        sessions: Number of sessions per subject (1 or 2)
        filter_freqs: Bandpass filter frequencies (low, high) in Hz
        epoch_window: Epoch window (tmin, tmax) relative to stimulus onset (seconds)
        data_dir: Directory to download/store dataset
        verbose: Enable verbose MNE logging
    
    Returns:
        Tuple of (X, y):
            X: EEG data of shape (n_epochs, n_channels, n_times)
            y: Labels of shape (n_epochs,) with values 1-4 for motor imagery tasks
    
    Example:
        >>> # Load first 5 subjects, all tasks, 0.5-3.5s after stimulus
        >>> X, y = load_physionet_data([1, 2, 3, 4, 5])
        >>> print(f"Data shape: {X.shape}, Labels: {y.shape}")
        >>> 
        >>> # Load specific subject and task
        >>> X, y = load_physionet_data([1], tasks=['left_hand', 'right_hand'])
    """
    dataset = PhysioNetEEGDataset(data_dir=data_dir, verbose=verbose)
    X, y = dataset.load_subjects(
        subject_ids=subject_ids,
        tasks=tasks,
        sessions=sessions,
        filter_freqs=filter_freqs,
        epoch_window=epoch_window
    )
    
    return X, y


def prepare_data_splits(X: np.ndarray, y: np.ndarray,
                       train_ratio: float = 0.7,
                       val_ratio: float = 0.15,
                       test_ratio: float = 0.15,
                       random_seed: int = 42) -> Tuple[Tuple, Tuple, Tuple]:
    """
    Split data into train, validation, and test sets.
    
    Ensures balanced class distribution across splits.
    
    Args:
        X: Data array
        y: Labels array
        train_ratio: Training set ratio
        val_ratio: Validation set ratio
        test_ratio: Test set ratio
        random_seed: Random seed for reproducibility
    
    Returns:
        Tuple of ((X_train, y_train), (X_val, y_val), (X_test, y_test))
    """
    from sklearn.model_selection import train_test_split
    
    np.random.seed(random_seed)
    
    # First split: separate test set
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y,
        test_size=test_ratio,
        random_state=random_seed,
        stratify=y
    )
    
    # Second split: separate train and validation
    train_size = train_ratio / (train_ratio + val_ratio)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp,
        train_size=train_size,
        random_state=random_seed,
        stratify=y_temp
    )
    
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


def get_label_mapping() -> Dict[int, str]:
    """Get mapping from label IDs to label names."""
    return PhysioNetEEGDataset.LABEL_MAPPING.copy()


def get_task_mapping() -> Dict[str, List[int]]:
    """Get mapping from task names to run numbers."""
    return PhysioNetEEGDataset.RUN_MAPPING.copy()


if __name__ == '__main__':
    """
    Example usage and demonstration.
    """
    import logging
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger('BCI')
    
    # Example: Load first 3 subjects with left and right hand tasks
    logger.info("Loading PhysioNet EEG Motor Imagery data...")
    
    try:
        # Load data
        X, y = load_physionet_data(
            subject_ids=[1, 2, 3],  # Load first 3 subjects
            tasks=['left_hand', 'right_hand'],  # Only left and right hand
            sessions=1,
            filter_freqs=(8, 30),
            epoch_window=(0.5, 3.5),
            verbose=False
        )
        
        # Print data information
        logger.info(f"Data shape: {X.shape}")
        logger.info(f"Labels shape: {y.shape}")
        logger.info(f"Unique labels: {np.unique(y)}")
        logger.info(f"Label counts: {np.bincount(y)}")
        
        # Display label mapping
        label_map = get_label_mapping()
        logger.info("Label mapping:")
        for label_id, label_name in sorted(label_map.items()):
            if label_id in np.unique(y):
                count = np.sum(y == label_id)
                logger.info(f"  {label_id}: {label_name} ({count} epochs)")
        
        # Prepare data splits
        (X_train, y_train), (X_val, y_val), (X_test, y_test) = prepare_data_splits(X, y)
        
        logger.info(f"\nData split:")
        logger.info(f"  Training: {X_train.shape[0]} epochs")
        logger.info(f"  Validation: {X_val.shape[0]} epochs")
        logger.info(f"  Test: {X_test.shape[0]} epochs")
        
    except Exception as e:
        logger.error(f"Error during data loading: {e}")
        import traceback
        traceback.print_exc()
