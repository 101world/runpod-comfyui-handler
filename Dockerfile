# Network Volume ComfyUI Worker
# Optimized for existing ComfyUI installations on RunPod network volumes
FROM runpod/base:0.4.0-cuda12.1.0

# Set working directory
WORKDIR /

# Install system dependencies for network volume ComfyUI
RUN apt-get update && apt-get install -y \
    curl \
    psmisc \
    && rm -rf /var/lib/apt/lists/*

# Install Python runtime dependencies for the handler
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Copy handler and test files
COPY handler.py /handler.py
COPY test_input.json /test_input.json

# Make sure ComfyUI directory exists and set proper permissions
RUN mkdir -p /workspace/ComfyUI

# Set the entrypoint to start ComfyUI directly
# Copy startup script
COPY start-comfyui.sh /start-comfyui.sh
RUN chmod +x /start-comfyui.sh

# Set the entrypoint to our startup script
CMD ["/start-comfyui.sh"]
