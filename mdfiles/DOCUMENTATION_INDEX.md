# Documentation Index

Complete documentation for the EEG-based Brain Computer Interface project.

## 🚀 Getting Started

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [QUICKSTART.md](QUICKSTART.md) | Get the project running in 5 minutes | 5 min |
| [README.md](README.md) | Complete project overview and features | 15 min |

---

## 📊 Data Preparation (NEW)

The data preparation module handles normalization, reshaping, and splitting of EEG data for model training.

| Document | Purpose | Audience | Read Time |
|----------|---------|----------|-----------|
| [DATA_PREPARATION_GUIDE.md](DATA_PREPARATION_GUIDE.md) | **Comprehensive API documentation** with detailed explanations, usage patterns, best practices, integration examples, troubleshooting, and performance notes | Developers needing complete reference | 30 min |
| [DATA_PREPARATION_QUICK_REFERENCE.md](DATA_PREPARATION_QUICK_REFERENCE.md) | **Quick lookup reference** with API tables, common patterns, full example, and troubleshooting | Developers needing quick answers | 5 min |
| [example_data_preparation.py](example_data_preparation.py) | **Working code examples** (5 complete examples) demonstrating all usage patterns | Copy-paste ready examples | Script |

**Quick Start**:
```python
from src.data_preparation import prepare_eeg_data

(X_train, y_train), (X_test, y_test), prep = prepare_eeg_data(
    X, y, 
    n_channels=64,
    time_steps=250
)
```

---

## 🧠 CNN-LSTM Model (NEW)

Production-ready CNN-LSTM model with bidirectional LSTM and 5-class classification support.

| Document | Purpose | Audience | Read Time |
|----------|---------|----------|-----------|
| [MODEL_GUIDE.md](MODEL_GUIDE.md) | **Comprehensive model API documentation** with architecture details, usage patterns, training examples, inference guide, and best practices | Developers needing complete reference | 30 min |
| [MODEL_QUICK_REFERENCE.md](MODEL_QUICK_REFERENCE.md) | **Quick lookup reference** with API tables, one-liners, common patterns, and troubleshooting | Developers needing quick answers | 5 min |
| [example_cnn_lstm_model.py](example_cnn_lstm_model.py) | **5 complete working examples**, from model creation through training, inference, and advanced configurations | Copy-paste ready examples | Script |

**Quick Start**:
```python
from src.model import create_model

config = {
    'model': {
        'input_shape': [320, 64],  # time_steps, channels
        'cnn_filters': [32, 64, 128],
        'lstm_units': [128, 64],
        'dense_units': [64, 32],
        'l2_regularization': 0.001
    },
    'training': {
        'optimizer': {'name': 'adam'},
        'learning_rate': 0.001
    }
}

model = create_model(config, n_classes=5)  # Ready to train!
```

**Key Features**:
- Bidirectional LSTM for complete temporal context
- 5-class classification (Left, Right, Hands, Feet, Click)
- Conv1D + BatchNorm + MaxPooling for feature extraction
- Production-ready code with full utilities
- Model save/load and inference utilities

---

## 🚀 Training System (NEW)

Production-ready training infrastructure with early stopping, learning rate reduction, and class weight handling.

| Document | Purpose | Audience | Read Time |
|----------|---------|----------|-----------|
| [TRAINING_GUIDE.md](TRAINING_GUIDE.md) | **Comprehensive training API documentation** with architecture, configuration, all methods, callbacks explanation, usage patterns, hyperparameter tuning, advanced features, and troubleshooting | Developers training models | 30 min |
| [train_eeg_model.py](train_eeg_model.py) | **Complete working example** demonstrating full training pipeline from data generation through training, evaluation, and results saving | Copy-paste ready example | Script |

**Key Features**:
- Early stopping on validation loss plateau
- Learning rate reduction (ReduceLROnPlateau)
- Automatic balanced class weight computation
- Best model checkpointing
- Custom progress callback with ETA
- Training history export to JSON
- Comprehensive statistics reporting
- Multi-class support (any number of classes)
- TensorBoard integration

**Quick Start**:
```python
from src.train import ModelTrainer

config = {
    'model': {'input_shape': (320, 64)},
    'training': {'epochs': 50, 'batch_size': 32},
    'output': {'model_path': 'models/best_model.h5'}
}

trainer = ModelTrainer(config, n_classes=5)
results = trainer.train(X_train, y_train, X_val, y_val)
summary = trainer.training_summary()
trainer.save_history('outputs/training_history.json')
```

---

## 🧠 PhysioNet Integration

Load real-world EEG motor imagery data from the PhysioNet database.

| Document | Purpose | Audience | Read Time |
|----------|---------|----------|-----------|
| [PHYSIONET_GUIDE.md](PHYSIONET_GUIDE.md) | **Complete API reference** for PhysioNet loader with dataset info, all methods, parameters, return types, event/run mappings | Developers using PhysioNet data | 20 min |
| [PHYSIONET_INTEGRATION.md](PHYSIONET_INTEGRATION.md) | **Integration guide** showing how to use PhysioNet data with the BCI pipeline (preprocessing, splitting, training) | Setup and integration | 15 min |
| [PHYSIONET_SUMMARY.md](PHYSIONET_SUMMARY.md) | **Implementation overview** with architecture, features, class structure, and performance considerations | Architecture understanding | 15 min |
| [PHYSIONET_CHECKLIST.md](PHYSIONET_CHECKLIST.md) | **Verification checklist** for validating PhysioNet setup and data loading | Troubleshooting | 5 min |
| [examples_physionet.py](examples_physionet.py) | **Working code examples** (multiple complete examples) for loading and using PhysioNet data | Copy-paste ready | Script |
| [validate_physionet.py](validate_physionet.py) | **Validation test suite** with 7+ tests to verify PhysioNet integration | Testing/validation | Script |

**Quick Start**:
```python
from src.physionet_loader import load_physionet_data

X, y = load_physionet_data([1, 2, 3, 4, 5])  # Load 5 subjects
# X.shape = (n_epochs, 64, 320)  # 64 channels, 320 samples
```

---

## 🔗 Full Pipeline Integration

Complete end-to-end workflow from data loading through evaluation.

| Document | Purpose | Audience | Read Time |
|----------|---------|----------|-----------|
| [INTEGRATION_PIPELINE_GUIDE.md](INTEGRATION_PIPELINE_GUIDE.md) | **Complete system integration guide** with end-to-end example, module-by-module integration steps, data flow, configuration setup, multi-subject validation, and error handling | Full pipeline implementation | 25 min |

**Complete Pipeline Example**:
```python
# 1. Load PhysioNet data
X, y = load_physionet_data([1, 2, 3, 4, 5])

# 2. Prepare data
(X_train, y_train), (X_test, y_test), prep = prepare_eeg_data(X, y, 64, 320)

# 3. Create and train model
model = create_model(config)
model.fit(X_train, y_train, validation_data=(X_test, y_test))

# 4. Evaluate
evaluator = ModelEvaluator(model, config)
metrics = evaluator.evaluate(X_test, y_test)
```

---

## 📚 Core Modules

The main BCI system components.

| Module | Purpose | File | Status |
|--------|---------|------|--------|
| **Data Loading** | Load/generate EEG data | [src/data_loader.py](src/data_loader.py) | ✅ Complete |
| **Preprocessing** | Filter, artifact removal, feature extraction | [src/preprocessing.py](src/preprocessing.py) | ✅ Complete |
| **Data Preparation** | Normalization, reshaping, splitting | [src/data_preparation.py](src/data_preparation.py) | ✅ NEW |
| **PhysioNet Loader** | Load PhysioNet motor imagery dataset | [src/physionet_loader.py](src/physionet_loader.py) | ✅ Complete |
| **Model** | CNN-LSTM architecture | [src/model.py](src/model.py) | ✅ Complete |
| **Training** | Training pipeline with callbacks | [src/train.py](src/train.py) | ✅ Complete |
| **Evaluation** | Metrics and visualization | [src/evaluate.py](src/evaluate.py) | ✅ Complete |
| **Real-time** | Live EEG processing | [src/realtime.py](src/realtime.py) | ✅ Complete |
| **Click Detection** | Click event detection | [src/click_detection.py](src/click_detection.py) | ✅ Complete |
| **Utilities** | Logging, config, helpers | [src/utils.py](src/utils.py) | ✅ Complete |

---

## 📖 Documentation Map

```
├── Getting Started
│   ├── QUICKSTART.md (5 min overview)
│   └── README.md (detailed introduction)
│
├── Data Preparation (NEW)
│   ├── DATA_PREPARATION_GUIDE.md (comprehensive reference)
│   ├── DATA_PREPARATION_QUICK_REFERENCE.md (quick lookup)
│   └── example_data_preparation.py (working examples)
│
├── PhysioNet Integration
│   ├── PHYSIONET_GUIDE.md (API reference)
│   ├── PHYSIONET_INTEGRATION.md (integration steps)
│   ├── PHYSIONET_SUMMARY.md (architecture overview)
│   ├── PHYSIONET_CHECKLIST.md (verification)
│   ├── examples_physionet.py (working examples)
│   └── validate_physionet.py (test suite)
│
├── Complete Pipeline
│   └── INTEGRATION_PIPELINE_GUIDE.md (end-to-end workflow)
│
├── Configuration
│   └── configs/config.yaml (all settings)
│
└── Tests & Examples
    ├── examples_physionet.py
    ├── example_data_preparation.py
    └── validate_physionet.py
```

---

## 🎯 Quick Navigation

### By Use Case

**"I want to load PhysioNet data"**
→ Start: [5-minute quick start](DATA_PREPARATION_QUICK_REFERENCE.md#3️⃣-with-physionet-data)  
→ Full guide: [PHYSIONET_GUIDE.md](PHYSIONET_GUIDE.md)  
→ Working code: [examples_physionet.py](examples_physionet.py)

**"I want to prepare my EEG data"**
→ Quick reference: [DATA_PREPARATION_QUICK_REFERENCE.md](DATA_PREPARATION_QUICK_REFERENCE.md)  
→ Full guide: [DATA_PREPARATION_GUIDE.md](DATA_PREPARATION_GUIDE.md)  
→ Working examples: [example_data_preparation.py](example_data_preparation.py)

**"I want to build a complete BCI pipeline"**
→ Overview: [QUICKSTART.md](QUICKSTART.md)  
→ Complete guide: [INTEGRATION_PIPELINE_GUIDE.md](INTEGRATION_PIPELINE_GUIDE.md)  
→ Configuration: [configs/config.yaml](configs/config.yaml)

**"I need API reference for a module"**
→ Data preparation: [DATA_PREPARATION_GUIDE.md#module-structure](DATA_PREPARATION_GUIDE.md#module-structure)  
→ PhysioNet: [PHYSIONET_GUIDE.md#api-reference](PHYSIONET_GUIDE.md#api-reference)  
→ Main modules: [README.md#module-documentation](README.md#module-documentation)

**"Something isn't working"**
→ Data preparation: [DATA_PREPARATION_GUIDE.md#troubleshooting](DATA_PREPARATION_GUIDE.md#troubleshooting)  
→ PhysioNet: [PHYSIONET_CHECKLIST.md](PHYSIONET_CHECKLIST.md)  
→ General: [README.md#troubleshooting](README.md#troubleshooting)

---

## 📋 Documentation by Complexity

### Beginner (5-10 min)
- [QUICKSTART.md](QUICKSTART.md) - Get running in 5 minutes
- [DATA_PREPARATION_QUICK_REFERENCE.md](DATA_PREPARATION_QUICK_REFERENCE.md) - Quick API lookup
- Example scripts: `example_data_preparation.py`, `examples_physionet.py`

### Intermediate (15-20 min)
- [DATA_PREPARATION_GUIDE.md](DATA_PREPARATION_GUIDE.md) - Complete data prep reference
- [PHYSIONET_INTEGRATION.md](PHYSIONET_INTEGRATION.md) - Integration steps
- [PHYSIONET_GUIDE.md](PHYSIONET_GUIDE.md) - PhysioNet API

### Advanced (30+ min)
- [INTEGRATION_PIPELINE_GUIDE.md](INTEGRATION_PIPELINE_GUIDE.md) - Full system architecture
- [README.md](README.md) - Complete project guide
- Source code in `src/` directory

---

## 🔑 Key Concepts

### Data Preparation Pipeline
1. **Load**: `physionet_loader.py` → (n_epochs, 64, 320)
2. **Reshape**: `data_preparation.py` → (n_epochs, 320, 64) for CNN-LSTM
3. **Normalize**: StandardScaler → zero mean, unit variance
4. **Split**: Stratified 80-20 train-test split

### Normalization Details
- **Method**: StandardScaler (z-score)
- **Formula**: X_norm = (X - mean) / std
- **Properties**: Zero mean, unit variance, reversible
- **Best Practice**: Fit on training data only, apply to test data

### PhysioNet Dataset
- **Subjects**: 1-109
- **Tasks**: 4 motor imagery (left/right/both_hands/both_feet)
- **Runs**: 14 runs per session, multiple sessions
- **Format**: Auto-downloaded, cached locally
- **Preprocessing**: 8-30 Hz bandpass, 2-second epochs

---

## 📝 File Types in Documentation

| Type | Purpose | Examples |
|------|---------|----------|
| **GUIDE** | Comprehensive reference | DATA_PREPARATION_GUIDE.md, PHYSIONET_GUIDE.md |
| **REFERENCE** | Quick lookup | DATA_PREPARATION_QUICK_REFERENCE.md |
| **INTEGRATION** | Workflow steps | PHYSIONET_INTEGRATION.md, INTEGRATION_PIPELINE_GUIDE.md |
| **SUMMARY** | Overview | PHYSIONET_SUMMARY.md |
| **CHECKLIST** | Verification | PHYSIONET_CHECKLIST.md |
| **EXAMPLES** | Working code | example_data_preparation.py, examples_physionet.py |
| **VALIDATION** | Test suite | validate_physionet.py |

---

## 🔄 Related Documentation

### Between Data Preparation and PhysioNet
- [DATA_PREPARATION_GUIDE.md](DATA_PREPARATION_GUIDE.md#pattern-3-with-physionet-data) - Using PhysioNet with data prep
- [PHYSIONET_INTEGRATION.md](PHYSIONET_INTEGRATION.md) - Integration steps
- [example_data_preparation.py](example_data_preparation.py) - Example using PhysioNet

### Between PhysioNet and Complete Pipeline
- [INTEGRATION_PIPELINE_GUIDE.md](INTEGRATION_PIPELINE_GUIDE.md#step-21-data-loading-physionet_loaderpy) - PhysioNet in pipeline
- [PHYSIONET_INTEGRATION.md](PHYSIONET_INTEGRATION.md) - Integration details

### Between Complete Pipeline and Training
- [INTEGRATION_PIPELINE_GUIDE.md](INTEGRATION_PIPELINE_GUIDE.md#step-24-model-training-trainpy) - Training section
- [README.md#usage](README.md#usage) - Training commands

---

## 📊 Documentation Statistics

| Category | Count | Status |
|----------|-------|--------|
| **Main Guides** | 3 | ✅ Complete |
| **Module References** | 5 | ✅ Complete |
| **Integration Guides** | 2 | ✅ Complete (+ new) |
| **Quick References** | 1 | ✅ Complete (NEW) |
| **Checklists & Validation** | 2 | ✅ Complete |
| **Working Examples** | 3 | ✅ Complete |
| **Total Documentation Files** | 16+ | ✅ Production Ready |

---

## 🎓 Learning Path

**Complete Beginner:**
1. [QUICKSTART.md](QUICKSTART.md) (5 min)
2. [DATA_PREPARATION_QUICK_REFERENCE.md](DATA_PREPARATION_QUICK_REFERENCE.md) (5 min)
3. Run [example_data_preparation.py](example_data_preparation.py) (10 min)
4. Read [INTEGRATION_PIPELINE_GUIDE.md](INTEGRATION_PIPELINE_GUIDE.md) (25 min)

**Intermediate Developer:**
1. [DATA_PREPARATION_GUIDE.md](DATA_PREPARATION_GUIDE.md) (30 min)
2. [PHYSIONET_GUIDE.md](PHYSIONET_GUIDE.md) (20 min)
3. [PHYSIONET_INTEGRATION.md](PHYSIONET_INTEGRATION.md) (15 min)
4. Review [configs/config.yaml](configs/config.yaml) (10 min)

**Advanced Implementation:**
1. [INTEGRATION_PIPELINE_GUIDE.md](INTEGRATION_PIPELINE_GUIDE.md) (25 min)
2. Study [src/](src/) modules (40+ min)
3. Review source code and examples (ongoing)
4. Customize and extend (ongoing)

---

## ✅ Verification Checklist

- [ ] Read QUICKSTART.md (understand basic workflow)
- [ ] Review DATA_PREPARATION_GUIDE or Quick Reference
- [ ] Check PHYSIONET_GUIDE if using PhysioNet data
- [ ] Review INTEGRATION_PIPELINE_GUIDE for complete setup
- [ ] Run example scripts to verify installation
- [ ] Customize configs/config.yaml for your needs
- [ ] Review relevant source code in src/

---

## 📞 Support Resources

| Category | Resource |
|----------|----------|
| **Quick answers** | [DATA_PREPARATION_QUICK_REFERENCE.md](DATA_PREPARATION_QUICK_REFERENCE.md) |
| **API details** | [DATA_PREPARATION_GUIDE.md](DATA_PREPARATION_GUIDE.md), [PHYSIONET_GUIDE.md](PHYSIONET_GUIDE.md) |
| **Integration help** | [INTEGRATION_PIPELINE_GUIDE.md](INTEGRATION_PIPELINE_GUIDE.md) |
| **Troubleshooting** | Search relevant guide's "Troubleshooting" section |
| **Code examples** | See example_*.py and examples_*.py files |
| **Validation** | Run validate_physionet.py or check PHYSIONET_CHECKLIST.md |

---

## 🎯 Next Steps

1. **Quick Start**: [QUICKSTART.md](QUICKSTART.md) (5 minutes)
2. **Load Data**: [PHYSIONET_QUICK_REFERENCE.md](PHYSIONET_GUIDE.md) or [examples_physionet.py](examples_physionet.py)
3. **Prepare Data**: [DATA_PREPARATION_QUICK_REFERENCE.md](DATA_PREPARATION_QUICK_REFERENCE.md) or [example_data_preparation.py](example_data_preparation.py)
4. **Full Pipeline**: [INTEGRATION_PIPELINE_GUIDE.md](INTEGRATION_PIPELINE_GUIDE.md)
5. **Customize**: Modify [configs/config.yaml](configs/config.yaml) for your needs

---

**Last Updated**: April 2026  
**Status**: ✅ Complete & Production-Ready  
**Documentation Version**: 2.0
