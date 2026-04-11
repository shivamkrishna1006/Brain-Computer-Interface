#!/bin/bash
# Entrypoint script for BCI Interface deployment
# This script sets up the environment and runs the BCI application

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_DIR="${PROJECT_ROOT}/venv"
CONFIG_FILE="${PROJECT_ROOT}/config.yaml"
ENV_FILE="${PROJECT_ROOT}/.env"

# Functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check Python installation
check_python() {
    print_header "Checking Python Installation"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.7 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
}

# Create virtual environment
create_venv() {
    print_header "Setting Up Virtual Environment"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        read -p "Do you want to recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
        else
            return
        fi
    fi
    
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created at $VENV_DIR"
}

# Activate virtual environment
activate_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
        print_success "Virtual environment activated"
    elif [ -f "$VENV_DIR/Scripts/activate" ]; then  # Windows
        source "$VENV_DIR/Scripts/activate"
        print_success "Virtual environment activated"
    else
        print_error "Could not find virtual environment activation script"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"
    
    if [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
        print_error "requirements.txt not found in $PROJECT_ROOT"
        exit 1
    fi
    
    pip install --upgrade pip setuptools wheel
    pip install -r "$PROJECT_ROOT/requirements.txt"
    print_success "Dependencies installed"
}

# Setup environment file
setup_env_file() {
    print_header "Setting Up Environment Configuration"
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "${ENV_FILE}.example" ]; then
            cp "${ENV_FILE}.example" "$ENV_FILE"
            print_success "Environment file created from template"
            print_warning "Please update .env with your configuration"
        else
            print_warning "No .env.example found"
        fi
    else
        print_success "Environment file already exists"
    fi
}

# Verify installation
verify_installation() {
    print_header "Verifying Installation"
    
    python3 -c "import tensorflow; print('TensorFlow:', tensorflow.__version__)" && \
    print_success "TensorFlow import successful" || \
    (print_error "TensorFlow import failed"; exit 1)
    
    python3 -c "import numpy; print('NumPy:', numpy.__version__)" && \
    print_success "NumPy import successful" || \
    (print_error "NumPy import failed"; exit 1)
    
    python3 -c "import mne; print('MNE:', mne.__version__)" && \
    print_success "MNE import successful" || \
    (print_error "MNE import failed"; exit 1)
}

# Show usage information
show_usage() {
    cat << EOF

${BLUE}BCI Interface - Usage Guide${NC}

Available commands:
  ./entrypoint.sh install    - Install dependencies
  ./entrypoint.sh train      - Train the BCI model
  ./entrypoint.sh evaluate   - Evaluate a trained model
  ./entrypoint.sh realtime   - Run in real-time mode
  ./entrypoint.sh shell      - Start Python shell in virtual environment
  ./entrypoint.sh verify     - Verify installation

Examples:
  ./entrypoint.sh install
  ./entrypoint.sh train
  ./entrypoint.sh evaluate --model bci_model
  ./entrypoint.sh realtime --model bci_model

For more information, see README.md

EOF
}

# Main entrypoint logic
main() {
    # Check if running in virtual environment already
    if [ "$VIRTUAL_ENV" == "" ]; then
        print_header "BCI Interface Setup"
        
        # Initial setup
        check_python
        create_venv
        activate_venv
        
        # Re-run with activated venv
        exec "$0" "$@"
    fi
    
    # Handle commands
    case "${1:-help}" in
        install)
            install_dependencies
            setup_env_file
            verify_installation
            print_header "Installation Complete"
            print_success "BCI Interface is ready to use!"
            show_usage
            ;;
        train)
            setup_env_file
            shift
            python3 "$PROJECT_ROOT/main.py" train "$@"
            ;;
        evaluate)
            setup_env_file
            shift
            python3 "$PROJECT_ROOT/main.py" evaluate "$@"
            ;;
        realtime)
            setup_env_file
            shift
            python3 "$PROJECT_ROOT/main.py" realtime "$@"
            ;;
        list-models)
            python3 "$PROJECT_ROOT/main.py" list-models "$@"
            ;;
        delete-model)
            shift
            python3 "$PROJECT_ROOT/main.py" delete-model "$@"
            ;;
        shell)
            # Start interactive Python shell
            print_header "Python Shell"
            python3
            ;;
        verify)
            verify_installation
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
