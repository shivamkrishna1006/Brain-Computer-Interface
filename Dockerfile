# Multi-stage build for BCI Interface
# Stage 1: Builder
FROM python:3.9-slim as builder

WORKDIR /tmp

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create wheels for faster installation
RUN pip install --user --no-cache-dir wheel && \
    pip install --user --no-cache-dir --no-warn-script-location -r requirements.txt


# Stage 2: Runtime
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TF_CPP_MIN_LOG_LEVEL=2

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/models /app/outputs /app/data/raw /app/data/processed /app/logs

# Verify installation
RUN python -c "import tensorflow; import numpy; print('✓ Dependencies installed successfully')"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import tensorflow; import sys; sys.exit(0)" || exit 1

# Default command
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]

# Metadata
LABEL maintainer="BCI Interface Team"
LABEL version="1.0.0"
LABEL description="Brain-Computer Interface - EEG Motor Imagery Classification"
