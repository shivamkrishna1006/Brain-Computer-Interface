# Deployment Guide

Complete guide for deploying the BCI Interface system in production and development environments.

## Table of Contents

- [Local Development Setup](#local-development-setup)
- [Docker Deployment](#docker-deployment)
- [Environment Configuration](#environment-configuration)
- [CLI Usage](#cli-usage)
- [Model Management](#model-management)
- [Troubleshooting](#troubleshooting)
- [Production Checklist](#production-checklist)

---

## Local Development Setup

### Windows

#### Step 1: Initial Setup
```bash
# Run entrypoint script (handles venv creation and installation)
entrypoint.bat install
```

#### Step 2: Training
```bash
entrypoint.bat train
```

#### Step 3: Evaluation
```bash
entrypoint.bat evaluate --model bci_model
```

#### Step 4: Real-Time Inference
```bash
entrypoint.bat realtime --model bci_model
```

#### Step 5: List Available Models
```bash
entrypoint.bat shell
# Then in Python:
# > from src.model_manager import ModelManager
# > mm = ModelManager()
# > models = mm.list_models()
# > print(models)
```

### macOS / Linux

#### Step 1: Initial Setup
```bash
# Make script executable
chmod +x entrypoint.sh

# Run setup (handles venv creation and installation)
./entrypoint.sh install
```

#### Step 2: Training
```bash
./entrypoint.sh train
```

#### Step 3: Evaluation
```bash
./entrypoint.sh evaluate --model bci_model
```

#### Step 4: Real-Time Inference
```bash
./entrypoint.sh realtime --model bci_model
```

#### Step 5: Shell Access
```bash
./entrypoint.sh shell
```

### Manual Setup

If you prefer manual setup without using the entrypoint scripts:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment file
cp .env.example .env

# 5. Run application
python main.py train
```

---

## Docker Deployment

### Prerequisites

- Docker (20.10+)
- Docker Compose (1.29+)
- 4GB RAM minimum
- 2GB GPU memory (optional, for GPU support)

### Basic Docker Usage

#### Step 1: Build Docker Image
```bash
# Build the image
docker build -t bci-interface:latest .

# Build with specific tag
docker build -t bci-interface:1.0.0 .
```

#### Step 2: Run Training
```bash
# Basic training
docker run --rm \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/data:/app/data \
  bci-interface:latest train

# With custom config
docker run --rm \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.yaml:/app/config.yaml \
  bci-interface:latest train --config config.yaml
```

#### Step 3: Run Evaluation
```bash
docker run --rm \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/outputs:/app/outputs \
  bci-interface:latest evaluate --model bci_model
```

#### Step 4: Run Real-Time System
```bash
docker run --rm -it \
  -v $(pwd)/models:/app/models \
  bci-interface:latest realtime --model bci_model
```

#### Step 5: List Models
```bash
docker run --rm \
  -v $(pwd)/models:/app/models \
  bci-interface:latest list-models --details
```

### Docker Compose Usage (Recommended)

#### Step 1: Setup Environment
```bash
# Copy and customize environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

#### Step 2: Build Services
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build bci
```

#### Step 3: Run Training
```bash
# Run training
docker-compose run --rm bci train

# With custom config
docker-compose run --rm bci train --config config.yaml --output my_model
```

#### Step 4: Run Evaluation
```bash
docker-compose run --rm bci evaluate --model my_model
```

#### Step 5: Run Real-Time System
```bash
docker-compose run --rm -it bci realtime --model my_model
```

#### Step 6: List Models
```bash
docker-compose run --rm bci list-models --details
```

#### Step 7: Development Mode (with Jupyter)
```bash
# Start Jupyter for interactive development
docker-compose --profile dev up jupyter

# Access Jupyter at http://localhost:8888
```

#### Step 8: Stop Services
```bash
# Stop specific service
docker-compose stop bci

# Stop all services
docker-compose down

# Remove volumes too (careful!)
docker-compose down -v
```

### GPU Support in Docker

#### NVIDIA GPU

```bash
# Verify NVIDIA Docker is installed
nvidia-docker --version

# Run with GPU support
docker run --rm --gpus all \
  -v $(pwd)/models:/app/models \
  bci-interface:latest train

# Docker Compose with GPU
docker-compose run --rm --gpus all bci train
```

#### Apple M1/M2 (Metal Performance Shaders)

The base image supports MPS on Apple Silicon. GPU should work automatically.

---

## Environment Configuration

### Configuration File (.env)

The `.env` file contains environment variables that control the application:

```bash
# Copy the template
cp .env.example .env

# Edit configuration
nano .env
```

### Key Settings

```env
# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bci.log

# Training
TRAIN_EPOCHS=50
TRAIN_BATCH_SIZE=32
TRAIN_LEARNING_RATE=0.001

# Data
EEG_CHANNELS=8
SAMPLING_RATE=250
NUM_CLASSES=5

# Real-Time
CONFIDENCE_THRESHOLD=0.7
DEBOUNCE_COUNT=3

# GPU
CUDA_VISIBLE_DEVICES=0  # GPU ID, or -1 for CPU
```

### Config.yaml

Main configuration file for model training and inference:

```yaml
training:
  epochs: 50
  batch_size: 32
  learning_rate: 0.001
  early_stopping_patience: 15

data:
  eeg_channels: 8
  sampling_rate: 250
  n_classes: 5

realtime:
  buffer_size: 250
  confidence_threshold: 0.7
  debounce_count: 3
```

---

## CLI Usage

### Main Entry Point: main.py

```bash
# Show help
python main.py --help

# Show version
python main.py --version

# Enable verbose mode
python main.py -v train
```

### Training Command

```bash
# Basic training with defaults
python main.py train

# Custom configuration
python main.py train --config my_config.yaml

# Specify output model name
python main.py train --output my_model

# Overwrite existing model
python main.py train --output my_model --force
```

### Evaluation Command

```bash
# Evaluate by model name
python main.py evaluate --model bci_model

# Evaluate by file path
python main.py evaluate --model ./models/bci_model.h5

# Custom configuration
python main.py evaluate --model bci_model --config config.yaml
```

### Real-Time Command

```bash
# Run real-time system
python main.py realtime --model bci_model

# Custom configuration
python main.py realtime --model bci_model --config config.yaml
```

### Model Management

```bash
# List all available models
python main.py list-models

# Show detailed information
python main.py list-models --details

# Delete a model
python main.py delete-model --model bci_model

# Delete without confirmation
python main.py delete-model --model bci_model --force
```

---

## Model Management

### Saving Models

Models are automatically saved during training:

```bash
python main.py train --output my_custom_model
```

Output structure:
```
models/
├── my_custom_model.h5              # Trained model
└── my_custom_model_metadata.json   # Training details
```

### Loading Models

Models are loaded via the ModelManager:

```python
from src.model_manager import ModelManager

mm = ModelManager()
model, metadata = mm.load_model('my_custom_model')
print(f"Accuracy: {metadata['metrics']['accuracy']}")
```

### Model Information

```python
from src.model_manager import ModelManager

mm = ModelManager()

# List all models
models = mm.list_models()
for name, metadata in models.items():
    print(f"{name}: {metadata['timestamp']}")

# Get detailed info
info = mm.get_model_info('my_custom_model')
print(info)
```

### Model Validation

```python
from src.model_manager import ModelValidator

validator = ModelValidator()
report = validator.validate_model(model)
print(f"Valid: {report['valid']}")
print(f"Errors: {report['errors']}")
```

---

## Troubleshooting

### Common Issues

#### 1. TensorFlow GPU Issues

```bash
# Check CUDA availability
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# Force CPU mode
export CUDA_VISIBLE_DEVICES=-1
python main.py train

# Check CUDA/cuDNN versions
python -c "import tensorflow as tf; tf.sysconfig.get_build_info()['cuda_version']"
```

#### 2. Out of Memory (OOM)

```yaml
# Reduce batch size
training:
  batch_size: 8  # From 32

# Reduce model size
model:
  lstm_units: 64  # From 128
```

#### 3. Docker Volume Issues

```bash
# Windows - use absolute paths
docker run -v C:\full\path\to\models:/app/models bci-interface:latest train

# Linux/Mac - use relative or absolute paths
docker run -v $(pwd)/models:/app/models bci-interface:latest train
```

#### 4. Model Not Found

```bash
# List available models
python main.py list-models

# Check models directory
ls -la models/

# Verify model file
python -c "from src.model_manager import ModelManager; mm = ModelManager(); print(mm.list_models())"
```

#### 5. Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check installation
python -c "import tensorflow; import mne; print('OK')"
```

### Debug Mode

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
python main.py train

# Enable debug mode
export DEBUG=true
python main.py train

# Verbose output
python main.py -v train
```

---

## Production Checklist

Before deploying to production:

- [ ] **Configuration**
  - [ ] Update `.env` with production values
  - [ ] Review `config.yaml` for optimal parameters
  - [ ] Set appropriate logging levels
  - [ ] Configure database (if using monitoring)

- [ ] **Models**
  - [ ] Train and validate model thoroughly
  - [ ] Test with diverse data
  - [ ] Verify model accuracy meets requirements
  - [ ] Document model version and training date

- [ ] **Security**
  - [ ] Change all default passwords
  - [ ] Secure model files and data
  - [ ] Enable HTTPS for APIs (if applicable)
  - [ ] Restrict file permissions

- [ ] **Performance**
  - [ ] Test with expected load
  - [ ] Profile memory and CPU usage
  - [ ] Optimize batch sizes and model parameters
  - [ ] Configure resource limits in Docker

- [ ] **Monitoring**
  - [ ] Set up logging and alerting
  - [ ] Monitor system health
  - [ ] Track model performance metrics
  - [ ] Log all inference requests

- [ ] **Documentation**
  - [ ] Document deployment process
  - [ ] Create runbooks for common operations
  - [ ] Document troubleshooting steps
  - [ ] Update README with production notes

- [ ] **Backup & Recovery**
  - [ ] Backup trained models
  - [ ] Backup configuration files
  - [ ] Document recovery procedures
  - [ ] Test backup restoration

- [ ] **Testing**
  - [ ] Perform integration testing
  - [ ] Test error handling
  - [ ] Verify graceful shutdown
  - [ ] Load testing

---

## Advanced Topics

### Custom Model Training

```python
from src.train import ModelTrainer
from src.utils import load_config

config = load_config('config.yaml')
trainer = ModelTrainer(config)
train_set, val_set, test_set = trainer.prepare_data()

# Custom training loop
history = trainer.train(*train_set, val_set[0], val_set[1])
```

### Real-Time Inference Integration

```python
from src.realtime_inference import RealtimeInferenceEngine

engine = RealtimeInferenceEngine(
    model_path='models/bci_model.h5',
    confidence_threshold=0.7
)

engine.start()

# Main loop
while engine.is_running():
    eeg_sample = get_eeg_sample()  # Your EEG hardware
    engine.add_sample(eeg_sample)
    
    if engine.is_ready():
        action, confidence = engine.process_signal()
        execute_action(action)

engine.stop()
```

### API Server (Optional)

```python
# Install FastAPI
pip install fastapi uvicorn

# Create app.py
from fastapi import FastAPI
from src.model_manager import ModelManager

app = FastAPI()

@app.get("/list-models")
async def list_models():
    mm = ModelManager()
    return mm.list_models()

@app.post("/predict")
async def predict(eeg_data: list):
    # Implement prediction endpoint
    pass

# Run server
# uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review [README.md](./README.md) for general information
3. Check [Configuration Guide](./CONFIGURATION_GUIDE.md)
4. Open an issue on GitHub

---

**Last Updated**: 2024
**Version**: 1.0.0
