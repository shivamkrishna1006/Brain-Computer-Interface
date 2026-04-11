"""
Setup script for BCI Interface package distribution.

This allows the package to be installed via pip:
    pip install -e .
    pip install .
    pip install ./dist/bci-interface-*.whl
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    # Package information
    name="bci-interface",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Brain-Computer Interface for EEG-based Motor Imagery Control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bci-eeg-interface",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/bci-eeg-interface/issues",
        "Documentation": "https://github.com/yourusername/bci-eeg-interface/blob/main/README.md",
        "Source Code": "https://github.com/yourusername/bci-eeg-interface",
    },
    
    # License
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    
    # Package discovery
    packages=find_packages(where=".", include=["src*"]),
    package_dir={"": "."},
    include_package_data=True,
    
    # Python version requirement
    python_requires=">=3.7",
    
    # Dependencies
    install_requires=requirements,
    
    # Optional dependencies for development and extras
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "isort>=5.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "sphinx-autodoc-typehints>=1.0",
        ],
        "onnx": [
            "tf2onnx>=1.10",
            "onnx>=1.12",
            "onnxruntime>=1.12",
        ],
        "server": [
            "fastapi>=0.85",
            "uvicorn>=0.19",
            "python-multipart>=0.0.5",
        ],
    },
    
    # Command-line entry points
    entry_points={
        "console_scripts": [
            "bci=main:main_cli",  # If adding a main_cli function
        ],
    },
    
    # Additional metadata
    keywords=[
        "bci",
        "brain-computer-interface",
        "eeg",
        "motor-imagery",
        "deep-learning",
        "cnn-lstm",
        "tensorflow",
        "neural-networks",
    ],
    
    # Zip safety
    zip_safe=False,
)
