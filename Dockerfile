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

# Copy handler and startup script
COPY handler.py /handler.py
COPY src/start.sh /start.sh
COPY test_input.json /test_input.json

# Make startup script executable
RUN chmod +x /start.sh

# Set the entrypoint to our startup script
CMD ["/start.sh"]
