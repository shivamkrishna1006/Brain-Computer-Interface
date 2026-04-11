# Quick Start: Deployment-Ready BCI Interface

Get the BCI system running in 5 minutes with one of these methods.

## 🚀 Method 1: Windows (Easiest)

```batch
# 1. Open Command Prompt in project directory

# 2. Run setup (installs everything)
entrypoint.bat install

# 3. Train model
entrypoint.bat train

# 4. Evaluate
entrypoint.bat evaluate --model bci_model

# 5. Real-time inference
entrypoint.bat realtime --model bci_model
```

---

## 🐧 Method 2: Linux / macOS (Easiest)

```bash
# 1. Open Terminal in project directory

# 2. Make script executable
chmod +x entrypoint.sh

# 3. Run setup (installs everything)
./entrypoint.sh install

# 4. Train model
./entrypoint.sh train

# 5. Evaluate
./entrypoint.sh evaluate --model bci_model

# 6. Real-time inference
./entrypoint.sh realtime --model bci_model
```

---

## 🐳 Method 3: Docker (Recommended for Production)

```bash
# 1. Build Docker image
docker build -t bci-interface:latest .

# 2. Train model
docker run --rm \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/outputs:/app/outputs \
  bci-interface:latest train

# 3. Evaluate
docker run --rm \
  -v $(pwd)/models:/app/models \
  bci-interface:latest evaluate --model bci_model

# 4. Real-time inference
docker run --rm -it \
  -v $(pwd)/models:/app/models \
  bci-interface:latest realtime --model bci_model
```

---

## 🐳 Method 4: Docker Compose (Best for Development)

```bash
# 1. Setup environment file
cp .env.example .env

# 2. Build services
docker-compose build

# 3. Train model
docker-compose run --rm bci train

# 4. Evaluate
docker-compose run --rm bci evaluate --model bci_model

# 5. Real-time inference
docker-compose run --rm -it bci realtime --model bci_model

# 6. Start Jupyter for interactive development
docker-compose --profile dev up jupyter
# Access at http://localhost:8888
```

---

## 📋 Method 5: Makefile (Recommended for Local)

```bash
# 1. Install dependencies
make install

# 2. Train model
make train

# 3. Evaluate
make evaluate MODEL=bci_model

# 4. Run real-time
make realtime MODEL=bci_model

# 5. List available models
make list-models

# 6. Clean up
make clean
```

---

## 🔍 View Available Commands

### Windows
```batch
entrypoint.bat help
```

### Linux/macOS
```bash
./entrypoint.sh help
```

### Makefile
```bash
make help
```

### Direct Python
```bash
python main.py --help
```

---

## 📊 Common Tasks

### List Trained Models
```bash
# Using Makefile
make list-models

# Using entrypoint
entrypoint.bat list-models      # Windows
./entrypoint.sh list-models     # Linux/Mac

# Using Docker Compose
docker-compose run --rm bci list-models --details

# Direct Python
python main.py list-models --details
```

### Delete a Model
```bash
# Using Makefile
make delete-model MODEL=my_model

# Using entrypoint
entrypoint.bat delete-model --model my_model

# Using Docker Compose
docker-compose run --rm bci delete-model --model my_model

# Direct Python
python main.py delete-model --model my_model
```

### Custom Training
```bash
# Train with custom configuration
python main.py train --output my_model --config custom_config.yaml

# Or via Makefile
make train-custom CONFIG=custom_config.yaml MODEL=my_model

# Or via Docker Compose
docker-compose run --rm bci train --output my_model
```

---

## 🐞 Troubleshooting

### Issue: "Python not found"
- **Windows**: Install Python from python.org
- **Linux/Mac**: `brew install python3` (macOS) or `apt-get install python3` (Linux)

### Issue: "Module not found"
```bash
pip install --upgrade -r requirements.txt
```

### Issue: Out of Memory
Edit `config.yaml`:
```yaml
training:
  batch_size: 8    # Reduce from 32
```

### Issue: GPU not detected
```bash
# Force CPU mode
export CUDA_VISIBLE_DEVICES=-1
python main.py train
```

### Issue: Docker can't find volumes
```bash
# Use absolute paths
docker run -v /full/path/to/models:/app/models bci-interface:latest
```

---

## 📚 Detailed Guides

For more information:
- **Deployment**: See `DEPLOYMENT_GUIDE.md`
- **Configuration**: See `CONFIGURATION_GUIDE.md`
- **Pre-Deployment**: See `PRODUCTION_CHECKLIST.md`

---

## ⚡ One-Liner Setups

### Windows One-Liner
```batch
entrypoint.bat install && entrypoint.bat train
```

### Linux/Mac One-Liner
```bash
./entrypoint.sh install && ./entrypoint.sh train
```

### Docker One-Liner (Train Only)
```bash
docker build -t bci . && docker run --rm -v $(pwd)/models:/app/models bci train
```

### Docker Compose One-Liner
```bash
docker-compose build && docker-compose run --rm bci train
```

---

## 🔄 Complete Workflow

### Local Development
```bash
# Install
make install

# Train
make train

# Evaluate
make evaluate MODEL=bci_model

# Real-time
make realtime MODEL=bci_model

# Clean up
make clean
```

### Docker Development
```bash
# Build
docker-compose build

# Train
docker-compose run --rm bci train

# Jupyter (interactive)
docker-compose --profile dev up jupyter

# Stop
docker-compose down
```

---

## ✅ What You Can Now Do

✓ Train BCI models easily  
✓ Evaluate trained models  
✓ Run real-time inference  
✓ List and manage trained models  
✓ Use Docker for containerization  
✓ Configure everything via .env and config.yaml  
✓ Deploy to production with confidence  
✓ Monitor with comprehensive logging  
✓ Scale with Docker Compose  
✓ Develop interactively with Jupyter  

---

## 🎯 Next Steps

1. **Choose your method** (entrypoint, Docker, or Makefile)
2. **Run setup** (`make install` or `entrypoint.bat install`)
3. **Train model** (`make train` or equivalent)
4. **Evaluate** (`make evaluate` or equivalent)
5. **Read full guides** for production deployment

---

## 🆘 Getting Help

1. Check this file for quick solutions
2. See `DEPLOYMENT_GUIDE.md` for detailed instructions
3. Check logs in `logs/` directory
4. Run `python main.py --help` for CLI help

---

**Version**: 1.0.0  
**Status**: ✅ Production-Ready  
**Last Updated**: 2024  

Get started now! 🚀
