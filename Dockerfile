# Use the official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy handler script
COPY handler.py /app/

# Install Python dependencies from PyPI first
RUN pip install --no-cache-dir \
    runpod \
    requests

# Install PyTorch packages from CUDA index
RUN pip install --no-cache-dir \
    torch \
    torchvision \
    torchaudio \
    --index-url https://download.pytorch.org/whl/cu121

# Set environment variables
ENV PYTHONPATH=/workspace/ComfyUI
ENV CUDA_VISIBLE_DEVICES=0

# Expose port (optional, for debugging)
EXPOSE 3001

# Run the handler
CMD ["python", "handler.py"]
