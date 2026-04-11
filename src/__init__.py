"""
BCI Interface Package

A production-ready EEG-based Brain Computer Interface using CNN-LSTM.
"""

__version__ = '1.0.0'
__author__ = 'BCI Development Team'

from . import utils
from . import data_loader
from . import preprocessing
from . import data_preparation
from . import model
from . import train
from . import evaluate
from . import realtime
from . import click_detection
from . import physionet_loader

__all__ = [
    'utils',
    'data_loader',
    'preprocessing',
    'data_preparation',
    'model',
    'train',
    'evaluate',
    'realtime',
    'click_detection',
    'physionet_loader'
]
