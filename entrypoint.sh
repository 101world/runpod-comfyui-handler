#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting RunPod ComfyUI Handler..."

# Function to check if ComfyUI is ready
check_comfyui_ready() {
    curl -s http://127.0.0.1:3001/ > /dev/null 2>&1
}

# Function to start ComfyUI
start_comfyui() {
    echo "🔍 Checking if ComfyUI exists at /workspace/ComfyUI..."
    
    if [ ! -d "/workspace/ComfyUI" ]; then
        echo "❌ ComfyUI not found at /workspace/ComfyUI"
        echo "📝 Please ensure your network volume contains ComfyUI installation"
        exit 1
    fi
    
    echo "✅ Found ComfyUI at /workspace/ComfyUI"
    
    # Stop any existing nginx/processes
    echo "🧹 Cleaning up environment..."
    systemctl stop nginx 2>/dev/null || true
    systemctl disable nginx 2>/dev/null || true
    pkill -f nginx || true
    fuser -k 3001/tcp || true
    
    # Start ComfyUI in background
    echo "🚀 Starting ComfyUI on port 3001..."
    cd /workspace/ComfyUI
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "❌ Virtual environment not found at /workspace/ComfyUI/venv"
        echo "📝 Please ensure ComfyUI is properly installed with virtual environment"
        exit 1
    fi
    
    # Activate virtual environment and start ComfyUI
    source venv/bin/activate
    nohup python main.py --listen --port 3001 > /tmp/comfyui.log 2>&1 &
    COMFYUI_PID=$!
    
    echo "⏳ Waiting for ComfyUI to be ready (PID: $COMFYUI_PID)..."
    
    # Wait up to 5 minutes for ComfyUI to start
    for i in {1..60}; do
        if check_comfyui_ready; then
            echo "✅ ComfyUI is ready after ${i} attempts ($(($i * 5)) seconds)"
            return 0
        fi
        echo "⏳ Waiting for ComfyUI... attempt $i/60"
        sleep 5
    done
    
    echo "❌ ComfyUI failed to start within 5 minutes"
    echo "📋 ComfyUI logs:"
    cat /tmp/comfyui.log || echo "No logs available"
    exit 1
}

# Function to start handler
start_handler() {
    echo "🔧 Starting RunPod handler..."
    cd /
    python handler.py
}

# Main execution
echo "🏁 Starting entrypoint script..."

# Start ComfyUI first
start_comfyui

# Start the handler
start_handler
