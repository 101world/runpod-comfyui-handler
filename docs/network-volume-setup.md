# Network Volume Setup Guide

This guide explains how to set up a RunPod network volume with ComfyUI for use with this worker.

## Prerequisites

- RunPod account with network volume support
- Access to FLUX model files (Hugging Face account recommended)

## Step 1: Create Network Volume

1. Navigate to [RunPod Storage](https://www.runpod.io/console/storage)
2. Click "New Network Volume"
3. Configure:
   - **Name**: `comfyui-flux`
   - **Size**: `250 GB` (minimum for FLUX models)
   - **Region**: Choose same as your preferred GPU region

## Step 2: Set Up ComfyUI on Volume

### Launch Setup Pod

1. Create a temporary GPU pod with your network volume attached
2. SSH into the pod
3. Navigate to mounted volume: `cd /workspace`

### Install ComfyUI

```bash
# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Install additional packages for FLUX
pip install accelerate transformers sentencepiece
```

### Download FLUX Models

Create model directories:
```bash
mkdir -p models/unet
mkdir -p models/clip  
mkdir -p models/vae
```

Download FLUX models (you may need Hugging Face token):
```bash
# FLUX UNet
wget -O models/unet/flux1-dev.safetensors \
  "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors"

# CLIP models  
wget -O models/clip/clip_l.safetensors \
  "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors"

wget -O models/clip/t5xxl_fp8_e4m3fn.safetensors \
  "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors"

# VAE
wget -O models/vae/ae.safetensors \
  "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors"
```

### Test ComfyUI Installation

```bash
# Activate environment
source venv/bin/activate

# Start ComfyUI to verify setup
python main.py --listen --port 3001
```

Access ComfyUI at `http://pod-ip:3001` to verify it loads correctly.

## Step 3: Verify Structure

Your network volume should have this structure:
```
/workspace/
 ComfyUI/
     main.py
     venv/
        bin/activate
     models/
        unet/
           flux1-dev.safetensors
        clip/
           clip_l.safetensors
           t5xxl_fp8_e4m3fn.safetensors
        vae/
            ae.safetensors
     [other ComfyUI files]
```

## Step 4: Terminate Setup Pod

Once verified, terminate the setup pod. Your network volume is ready for serverless deployment.

## Troubleshooting

### Permission Issues
```bash
# Fix permissions if needed
chmod -R 755 /workspace/ComfyUI
chown -R root:root /workspace/ComfyUI
```

### Large File Downloads
For faster downloads, consider using:
```bash
# Use aria2 for parallel downloads
apt-get update && apt-get install -y aria2
aria2c -x 16 -s 16 [URL]
```

### Model Verification
Verify model files downloaded correctly:
```bash
ls -la models/unet/    # Should show flux1-dev.safetensors (~23GB)
ls -la models/clip/    # Should show two CLIP files  
ls -la models/vae/     # Should show ae.safetensors (~335MB)
```

## Next Steps

Once your network volume is set up, proceed to the [Deployment Guide](deployment.md) to deploy the serverless worker.
