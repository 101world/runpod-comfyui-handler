# Network Volume ComfyUI Worker
# Designed for existing ComfyUI installations on RunPod network volumes
FROM runpod/base:0.6.3-cuda11.8.0

# Set working directory
WORKDIR /

# Install system dependencies needed for network volume ComfyUI
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    fuser \
    psmisc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for handler
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Copy application files
COPY handler.py /handler.py
COPY test_input.json /test_input.json

# Copy startup script from src directory
COPY src/start.sh /start.sh
RUN chmod +x /start.sh

# Network volume will be mounted at /workspace containing:
# - /workspace/ComfyUI (your existing installation)
# - /workspace/ComfyUI/venv (your python environment)
# - /workspace/ComfyUI/models (your FLUX models)

# Set the entrypoint to our startup script
CMD ["/start.sh"]
