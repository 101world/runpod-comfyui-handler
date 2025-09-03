# Use RunPod base image
FROM runpod/base:0.4.0-cuda12.1.0

# Set working directory
WORKDIR /

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-venv \
    python3-pip \
    wget \
    curl \
    fuser \
    && rm -rf /var/lib/apt/lists/*

# Copy handler and requirements
COPY handler.py /handler.py
COPY requirements.txt /requirements.txt

# Install Python dependencies for handler
RUN pip install -r /requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint
CMD ["/entrypoint.sh"]
