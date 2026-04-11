# GitHub Project Organization Guide

Complete guide to the BCI Interface project structure optimized for GitHub.

## 🎯 Project Structure Overview

```
📦 BCI-INTERFACE                    # Root directory
│
├── 📄 Root Level Configuration (Essential Files)
│   ├── README.md                   ⭐ Main documentation - START HERE
│   ├── LICENSE                     MIT license
│   ├── CHANGELOG.md                Version history
│   ├── CONTRIBUTING.md             How to contribute
│   ├── PROJECT_STRUCTURE.md        This guide
│   │
│   ├── setup.py                    Package distribution
│   ├── setup.cfg                   Setup configuration
│   ├── pyproject.toml             Project metadata
│   ├── requirements.txt            Dependencies
│   └── Makefile                    Development commands
│
├── 🚀 Deployment (Docker & Scripts)
│   ├── Dockerfile                  Docker image
│   ├── docker-compose.yml          Container orchestration
│   ├── .dockerignore              Docker build ignore
│   ├── entrypoint.sh              Unix/Linux/Mac deploy
│   ├── entrypoint.bat             Windows deploy
│   └── .env.example               Config template
│
├── 🔧 Main Entry Point
│   └── main.py                     CLI entry point
│
├── 📂 Source Code (src/)           ⭐ Core modules
│   ├── __init__.py
│   ├── model.py                    CNN-LSTM model
│   ├── model_manager.py            Model persistence
│   ├── train.py                    Training pipeline
│   ├── evaluate.py                 Evaluation metrics
│   ├── realtime_inference.py       Real-time engine
│   ├── data_loader.py              Data loading
│   ├── data_preparation.py         Data preprocessing
│   ├── preprocessing.py            Signal processing
│   ├── physionet_loader.py         PhysioNet integration
│   ├── click_detection.py          Click detection
│   ├── config.py                   Config management
│   └── utils.py                    Utilities
│
├── 🧪 Tests (tests/)               ⭐ Unit & integration tests
│   ├── __init__.py
│   ├── test_config.py              Config validation
│   ├── test_training_module.py     Training tests
│   ├── test_realtime_inference.py Real-time tests
│   └── conftest.py                 Pytest configuration
│
├── 📚 Documentation (docs/)        ⭐ Comprehensive guides
│   ├── README.md                   Doc index
│   │
│   ├── Getting Started
│   │   ├── QUICKSTART_DEPLOYMENT.md
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   └── DEPLOYMENT_READINESS.md
│   │
│   ├── Configuration
│   │   ├── CONFIGURATION_GUIDE.md
│   │   └── CONFIGURATION_QUICK_REFERENCE.md
│   │
│   ├── Training & Models
│   │   ├── TRAINING_GUIDE.md
│   │   ├── TRAINING_IMPLEMENTATION_SUMMARY.md
│   │   ├── TRAINING_QUICK_REFERENCE.md
│   │   ├── CNN_LSTM_MODEL_SUMMARY.md
│   │   └── MODEL_QUICK_REFERENCE.md
│   │
│   ├── Real-Time Inference
│   │   ├── REALTIME_INFERENCE_GUIDE.md
│   │   ├── REALTIME_INFERENCE_IMPLEMENTATION.md
│   │   └── REALTIME_INFERENCE_QUICK_REFERENCE.md
│   │
│   ├── Data & Datasets
│   │   ├── DATA_PREPARATION_GUIDE.md
│   │   ├── PHYSIONET_GUIDE.md
│   │   └── DATA_PREPARATION_QUICK_REFERENCE.md
│   │
│   ├── Advanced Topics
│   │   ├── EVALUATION_GUIDE.md
│   │   ├── EVALUATION_QUICK_REFERENCE.md
│   │   ├── INTEGRATION_PIPELINE_GUIDE.md
│   │   ├── API.md
│   │   ├── TROUBLESHOOTING.md
│   │   └── PRODUCTION_CHECKLIST.md
│
├── 💾 Configuration (config/)
│   └── config.yaml                 Main configuration file
│
├── 🔬 Examples (examples/)
│   ├── example_cnn_lstm_model.py   Model usage
│   ├── example_data_preparation.py Data prep
│   └── examples_physionet.py       PhysioNet usage
│
├── 🛠️ Scripts (scripts/)
│   ├── train_eeg_model.py          Training script
│   ├── train_eeg_model_production.py Prod training
│   ├── evaluate_eeg_model.py       Evaluation
│   ├── realtime_inference_demo.py  Real-time demo
│   └── validate_physionet.py       Dataset validation
│
├── 📓 Notebooks (notebooks/)
│   ├── exploration.ipynb           EDA
│   ├── training.ipynb              Training notebook
│   └── inference.ipynb             Inference notebook
│
├── 📁 Data Directory (data/)        ⸰ Not in git, local only
│   ├── raw/                        Raw EEG data
│   ├── processed/                  Processed data
│   └── .gitkeep                    Keep folder in git
│
├── 🎯 Models Directory (models/)   ⸰ Not in git, generated
│   ├── README.md                   Models guide
│   └── *.h5                        Trained models
│
├── 📊 Outputs (outputs/)           ⸰ Not in git, generated
│   ├── training_history.json       Training metrics
│   ├── evaluation_results.json     Eval results
│   └── logs/                       Training logs
│
├── 📋 Logs Directory (logs/)        ⸰ Not in git, generated
│   └── *.log                       Application logs
│
├── 🔐 Git Configuration
│   ├── .gitignore                  Git exclusions
│   ├── .gitattributes             Git attributes
│   └── .github/                    GitHub specific
│       ├── workflows/              CI/CD workflows (optional)
│       ├── pull_request_template.md PR template
│       └── ISSUE_TEMPLATE/
│           ├── bug_report.md       Bug report template
│           └── feature_request.md  Feature request
│
└── 🐍 Virtual Environment (venv/)  ⸰ Not in git, local
    └── (Python packages)
```

---

## 📊 File Organization Legend

| Symbol | Meaning |
|--------|---------|
| 📄 | File |
| 📂 | Directory |
| 📦 | Package/Module |
| ⭐ | Important/Critical |
| ⸰ | Not tracked by Git |

---

## 🎯 Key Directories

### 1. **src/** - Source Code
**Purpose**: All core Python modules

**Structure**:
```
src/
├── __init__.py                 # Package initialization
├── model.py                    # Model architecture
├── model_manager.py           # Model persistence
├── train.py                   # Training pipeline
├── evaluate.py                # Evaluation module
├── realtime_inference.py      # Real-time engine
├── data_loader.py             # Load data
├── preprocessing.py           # Signal processing
├── config.py                  # Configuration
└── utils.py                   # Helpers
```

### 2. **tests/** - Unit Tests
**Purpose**: Test coverage for all modules

**Structure**:
```
tests/
├── __init__.py               # Test package
├── test_config.py            # Config tests
├── test_training_module.py   # Training tests
├── test_realtime_inference.py # Real-time tests
└── conftest.py               # Pytest configuration
```

### 3. **docs/** - Documentation
**Purpose**: Comprehensive guides (27+ files)

**Organization**:
- Getting Started (5 docs)
- Configuration (2 docs)
- Training (4 docs)
- Models (2 docs)
- Real-Time (3 docs)
- Data (3 docs)
- Evaluation (2 docs)
- Advanced (2 docs)
- Index (1 doc)

### 4. **config/** - Configuration
**Purpose**: Configuration files

**Files**:
- `config.yaml` - Main configuration (100+ parameters)

### 5. **examples/** - Sample Code
**Purpose**: Usage examples

**Files**:
- `example_cnn_lstm_model.py` - Model usage
- `example_data_preparation.py` - Data example
- `examples_physionet.py` - PhysioNet usage

### 6. **scripts/** - Utility Scripts
**Purpose**: Standalone scripts

**Files**:
- `train_eeg_model.py` - Basic training
- `train_eeg_model_production.py` - Production training
- `evaluate_eeg_model.py` - Evaluation
- `realtime_inference_demo.py` - Real-time demo
- `validate_physionet.py` - Data validation

### 7. **notebooks/** - Jupyter Notebooks
**Purpose**: Interactive exploration and development

**Files**:
- `exploration.ipynb` - Data exploration
- `training.ipynb` - Training notebook
- `inference.ipynb` - Inference notebook

---

## 📍 File Location Reference

### "Where do I find...?"

| Item | Location |
|------|----------|
| How to install | `docs/QUICKSTART_DEPLOYMENT.md` |
| Configuration options | `docs/CONFIGURATION_GUIDE.md` |
| How to train | `docs/TRAINING_GUIDE.md` |
| Real-time code | `src/realtime_inference.py` |
| Training code | `src/train.py` |
| Model code | `src/model.py` |
| Tests | `tests/test_*.py` |
| Examples | `examples/` |
| Contribution guidelines | `CONTRIBUTING.md` |
| Version history | `CHANGELOG.md` |
| Main configuration | `config/config.yaml` |
| Environment setup | `.env.example` |
| Docker setup | `Dockerfile`, `docker-compose.yml` |
| CLI entry point | `main.py` |
| Package setup | `setup.py` |

---

## 📂 Directory Creation Checklist

When adding new features:

```
✅ For new modules:
   - Add to src/
   - Add tests to tests/
   - Update docs/ if needed

✅ For new features:
   - Document in docs/
   - Add examples in examples/
   - Include tests

✅ For scripts:
   - Put in scripts/
   - Document usage
   - Test thoroughly

✅ For notebooks:
   - Put in notebooks/
   - Include documentation
   - Ensure reproducibility
```

---

## 🔄 Common Workflows

### Adding a New Module

```
1. Create src/new_module.py
2. Create tests/test_new_module.py
3. Add to src/__init__.py if needed
4. Document in docs/
5. Update PROJECT_STRUCTURE.md
```

### Adding Documentation

```
1. Create docs/NEW_TOPIC.md
2. Add to docs/README.md index
3. Link from main README.md if major
4. Add to PROJECT_STRUCTURE.md
```

### Adding an Example

```
1. Create examples/example_new.py
2. Document in the file
3. Link from README.md
4. Update docs/README.md
```

### Adding Tests

```
1. Create tests/test_new.py
2. Cover main functionality
3. Test edge cases
4. Aim for 80%+ coverage
```

---

## 🚀 GitHub-Specific Files

### `.github/`
**Purpose**: GitHub-specific configurations

**Contents**:
- `pull_request_template.md` - PR template for consistency
- `ISSUE_TEMPLATE/` - Issue templates
  - `bug_report.md` - Bug reporting template
  - `feature_request.md` - Feature request template

### `.gitignore`
**Purpose**: Exclude unnecessary files from git

**Excludes**:
- `__pycache__/`, `*.pyc` - Python compiled files
- `venv/`, `.venv/` - Virtual environments
- `models/*.h5` - Large model files
- `data/` - Training data
- `outputs/`, `logs/` - Generated files
- `.env` - Environment secrets
- IDE files (`.vscode`, `.idea`)

---

## 📏 Naming Conventions

### Python Files
- Modules: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case()`
- Constants: `UPPER_CASE`

### Documentation Files
- Guides: `SUBJECT_GUIDE.md`
- References: `SUBJECT_QUICK_REFERENCE.md`
- Summaries: `SUBJECT_SUMMARY.md`

### Directories
- Source: `src/`
- Tests: `tests/`
- Documentation: `docs/`
- Examples: `examples/`
- Scripts: `scripts/`

---

## 🌳 View Directory Tree

To visualize the structure:

```bash
# Using tree command (Linux/Mac)
tree -L 2 -I '__pycache__|*.pyc|venv|.venv'

# Or using find (all platforms)
find . -type d -not -path '*/\.*' | head -30
```

---

## 📝 Summary

| Aspect | Organization |
|--------|--------------|
| **Source Code** | `src/` directory |
| **Tests** | `tests/` directory |
| **Documentation** | `docs/` directory (27+ files) |
| **Examples** | `examples/` directory |
| **Scripts** | `scripts/` directory |
| **Configuration** | `config/config.yaml` |
| **Setup** | `setup.py`, `requirements.txt` |
| **Deployment** | `Dockerfile`, `docker-compose.yml` |
| **CLI** | `main.py` |
| **Development** | `Makefile` |
| **Git** | `.gitignore`, `.github/` |
| **Data/Models** | `data/`, `models/` (local, not in git) |

---

## ✅ Quality Checklist

Before publishing to GitHub:

- [ ] README.md is clear and complete
- [ ] PROJECT_STRUCTURE.md documents organization
- [ ] docs/README.md indexes all documentation
- [ ] CONTRIBUTING.md has contribution guidelines
- [ ] CHANGELOG.md documents version history
- [ ] LICENSE file is present (MIT)
- [ ] .gitignore is comprehensive
- [ ] setup.py is properly configured
- [ ] requirements.txt lists all dependencies
- [ ] All tests pass
- [ ] Code follows PEP 8
- [ ] Documentation is comprehensive
- [ ] Examples are working

---

## 🎓 Learning Path

1. **Start**: Read `README.md`
2. **Get Started**: Follow `docs/QUICKSTART_DEPLOYMENT.md`
3. **Explore**: Check `examples/` directory
4. **Understand**: Read relevant `docs/` guides
5. **Contribute**: See `CONTRIBUTING.md`
6. **Navigate**: Use `PROJECT_STRUCTURE.md`

---

**Version**: 1.0.0  
**Last Updated**: 2024-04-11  
**Status**: ✅ Production-Ready

For questions, see `docs/TROUBLESHOOTING.md` or open an issue on GitHub.
