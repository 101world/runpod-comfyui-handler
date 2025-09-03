#!/bin/bash
echo 'Starting ComfyUI container...'

if [ -d '/workspace/ComfyUI' ]; then
    echo 'Found ComfyUI directory at /workspace/ComfyUI'
    cd /workspace/ComfyUI
    
    if [ -f 'venv/bin/activate' ]; then
        echo 'Activating virtual environment...'
        source venv/bin/activate
    else
        echo 'No virtual environment found, using system Python'
    fi
    
    echo 'Starting ComfyUI server...'
    python main.py --port 3001
else
    echo 'ComfyUI not found at /workspace/ComfyUI - checking other locations...'
    find / -name 'ComfyUI' -type d 2>/dev/null || echo 'ComfyUI directory not found anywhere'
    echo 'Container will sleep for 5 minutes to allow debugging...'
    sleep 300
fi
