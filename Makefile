# Makefile for BCI Interface
# Provides convenient commands for development and deployment

.PHONY: help install dev-install test lint format train evaluate realtime docker-build docker-run clean

# Default target
.DEFAULT_GOAL := help

# Configuration
PYTHON := python3
PIP := pip3
PYTHON_VERSION := 3.7
DOCKER_IMAGE := bci-interface
DOCKER_TAG := latest
VENV := venv

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)▼ Available Commands$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)Examples:$(NC)"
	@echo "  make install      # Install dependencies"
	@echo "  make train        # Train the model"
	@echo "  make docker-build # Build Docker image"
	@echo ""

check-python: ## Check Python version
	@echo "$(BLUE)Checking Python version...$(NC)"
	@$(PYTHON) --version
	@echo "$(GREEN)✓ Python check passed$(NC)"

install: check-python ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@$(PIP) install --upgrade pip setuptools wheel
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

dev-install: install ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	@$(PIP) install pytest pytest-cov black flake8 isort mypy
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

venv: ## Create virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created at $(VENV)$(NC)"
	@echo "$(YELLOW)Activate with: source $(VENV)/bin/activate (Linux/Mac) or $(VENV)\\Scripts\\activate (Windows)$(NC)"

lint: ## Run linter (flake8)
	@echo "$(BLUE)Running flake8...$(NC)"
	@flake8 src/ main.py --max-line-length=100
	@echo "$(GREEN)✓ Linting passed$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code with black...$(NC)"
	@black src/ main.py
	@echo "$(BLUE)Organizing imports with isort...$(NC)"
	@isort src/ main.py
	@echo "$(GREEN)✓ Code formatting complete$(NC)"

test: ## Run unit tests
	@echo "$(BLUE)Running tests...$(NC)"
	@pytest tests/ -v --cov=src --cov-report=html
	@echo "$(GREEN)✓ Tests passed$(NC)"
	@echo "$(YELLOW)Coverage report: htmlcov/index.html$(NC)"

test-config: ## Test configuration system
	@echo "$(BLUE)Testing configuration...$(NC)"
	@$(PYTHON) test_config.py
	@echo "$(GREEN)✓ Configuration tests passed$(NC)"

train: ## Train the model
	@echo "$(BLUE)Starting training...$(NC)"
	@$(PYTHON) main.py train
	@echo "$(GREEN)✓ Training complete$(NC)"

train-custom: ## Train with custom config
	@echo "$(BLUE)Starting training with custom config...$(NC)"
	@$(PYTHON) main.py train --config $(CONFIG) --output $(MODEL)
	@echo "$(GREEN)✓ Training complete$(NC)"

evaluate: ## Evaluate a trained model
	@echo "$(BLUE)Evaluating model...$(NC)"
	@$(PYTHON) main.py evaluate --model $(MODEL)
	@echo "$(GREEN)✓ Evaluation complete$(NC)"

realtime: ## Run real-time inference
	@echo "$(BLUE)Starting real-time system...$(NC)"
	@$(PYTHON) main.py realtime --model $(MODEL)
	@echo "$(GREEN)✓ Real-time system stopped$(NC)"

list-models: ## List all available models
	@echo "$(BLUE)Available models:$(NC)"
	@$(PYTHON) main.py list-models --details

delete-model: ## Delete a model (requires MODEL variable)
	@echo "$(BLUE)Deleting model: $(MODEL)$(NC)"
	@$(PYTHON) main.py delete-model --model $(MODEL) --force
	@echo "$(GREEN)✓ Model deleted$(NC)"

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	@docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)✓ Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)$(NC)"

docker-run-train: ## Run training in Docker
	@echo "$(BLUE)Running training in Docker...$(NC)"
	@docker run --rm \
		-v $(PWD)/models:/app/models \
		-v $(PWD)/outputs:/app/outputs \
		-v $(PWD)/data:/app/data \
		$(DOCKER_IMAGE):$(DOCKER_TAG) train

docker-run-evaluate: ## Run evaluation in Docker
	@echo "$(BLUE)Running evaluation in Docker...$(NC)"
	@docker run --rm \
		-v $(PWD)/models:/app/models \
		-v $(PWD)/outputs:/app/outputs \
		$(DOCKER_IMAGE):$(DOCKER_TAG) evaluate --model bci_model

docker-run-realtime: ## Run real-time in Docker
	@echo "$(BLUE)Running real-time system in Docker...$(NC)"
	@docker run --rm -it \
		-v $(PWD)/models:/app/models \
		$(DOCKER_IMAGE):$(DOCKER_TAG) realtime --model bci_model

docker-compose-build: ## Build Docker Compose services
	@echo "$(BLUE)Building Docker Compose services...$(NC)"
	@docker-compose build
	@echo "$(GREEN)✓ Docker Compose services built$(NC)"

docker-compose-train: ## Run training with Docker Compose
	@echo "$(BLUE)Running training with Docker Compose...$(NC)"
	@docker-compose run --rm bci train

docker-compose-evaluate: ## Run evaluation with Docker Compose
	@echo "$(BLUE)Running evaluation with Docker Compose...$(NC)"
	@docker-compose run --rm bci evaluate --model bci_model

docker-compose-jupyter: ## Start Jupyter with Docker Compose
	@echo "$(BLUE)Starting Jupyter...$(NC)"
	@docker-compose --profile dev up jupyter
	@echo "$(YELLOW)Access Jupyter at http://localhost:8888$(NC)"

docker-compose-up: ## Start all Docker Compose services
	@echo "$(BLUE)Starting all services...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@docker-compose ps

docker-compose-down: ## Stop all Docker Compose services
	@echo "$(BLUE)Stopping all services...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

docker-compose-logs: ## View Docker Compose logs
	@docker-compose logs -f bci

docker-push: ## Push Docker image to registry
	@echo "$(BLUE)Pushing Docker image...$(NC)"
	@docker push $(DOCKER_IMAGE):$(DOCKER_TAG)
	@echo "$(GREEN)✓ Image pushed$(NC)"

clean: ## Clean up generated files and caches
	@echo "$(BLUE)Cleaning up...$(NC)"
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.egg-info" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ *.egg-info/
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-models: ## Clean up all models (careful!)
	@echo "$(RED)WARNING: This will delete all trained models!$(NC)"
	@read -p "Are you sure? (y/n) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf models/*.h5 models/*.json; \
		echo "$(GREEN)✓ Models deleted$(NC)"; \
	else \
		echo "Cancelled"; \
	fi

clean-data: ## Clean up processed data (careful!)
	@echo "$(RED)WARNING: This will delete all processed data!$(NC)"
	@read -p "Are you sure? (y/n) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf data/processed/*; \
		echo "$(GREEN)✓ Processed data deleted$(NC)"; \
	else \
		echo "Cancelled"; \
	fi

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "$(YELLOW)Documentation files:$(NC)"
	@ls -1 *.md | grep -i guide
	@echo "$(GREEN)✓ Documentation available$(NC)"

status: ## Show project status
	@echo "$(BLUE)Project Status$(NC)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Pip: $$($(PIP) --version | cut -d' ' -f2)"
	@echo "TensorFlow: $$($(PYTHON) -c 'import tensorflow; print(tensorflow.__version__)' 2>/dev/null || echo 'Not installed')"
	@echo "MNE: $$($(PYTHON) -c 'import mne; print(mne.__version__)' 2>/dev/null || echo 'Not installed')"
	@echo ""
	@echo "Models: $$(ls models/*.h5 2>/dev/null | wc -l) available"
	@echo "Logs: $$(ls logs/*.log 2>/dev/null | wc -l) files"
	@echo ""
	@echo "$(GREEN)✓ Status check complete$(NC)"

.PHONY: all check-python install dev-install venv lint format test train evaluate realtime
.PHONY: docker-build docker-run-train docker-run-evaluate docker-run-realtime
.PHONY: docker-compose-build docker-compose-train docker-compose-evaluate docker-compose-jupyter
.PHONY: docker-compose-up docker-compose-down docker-compose-logs docker-push
.PHONY: clean clean-models clean-data docs status help

# Variables that can be overridden
# Example: make train-custom CONFIG=my_config.yaml MODEL=my_model
# Example: make evaluate MODEL=my_model
# Example: make docker-build DOCKER_TAG=1.0.0
