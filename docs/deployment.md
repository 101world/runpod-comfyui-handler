# Deployment Guide - Network Volume Edition

This guide covers deploying the ComfyUI worker with an existing network volume setup.

## Prerequisites

### Network Volume Setup
- **Volume Size**: 250GB+ recommended for FLUX models
- **ComfyUI Installation**: Pre-installed at `/workspace/ComfyUI`
- **Python Environment**: Virtual environment at `/workspace/ComfyUI/venv`
- **Required Models**: 
  - `flux1-dev.safetensors` (in models/unet/)
  - `clip_l.safetensors` (in models/clip/)
  - `t5xxl_fp8_e4m3fn.safetensors` (in models/clip/)
  - `ae.safetensors` (in models/vae/)

### Verified Working Setup
Your exact ComfyUI startup command that works:
```bash
cd /workspace/ComfyUI && source venv/bin/activate && python main.py --listen --port 3001
```

## Deployment Steps

### 1. GitHub Integration (Recommended)

1. **Connect Repository**: 
   - Go to RunPod Serverless endpoint settings
   - Choose `GitHub Integration`
   - Connect `101world/runpod-comfyui-handler` repository

2. **Configure Build**:
   - **Branch**: `main`
   - **Build Context**: Root directory
   - **Dockerfile Path**: `Dockerfile`

3. **Network Volume**:
   - **Mount Path**: `/workspace` (automatic)
   - **Volume**: Your existing 250GB volume with ComfyUI

### 2. Container Configuration

**Template Settings**:
- **Container Disk**: 10GB (minimal, models on network volume)
- **Memory**: 16GB+
- **GPU**: A40/A100 recommended for FLUX
- **CPU**: 8+ cores

**Environment Variables** (Optional):
```bash
COMFY_HOST=127.0.0.1
COMFY_PORT=3001
```

### 3. Testing Deployment

After deployment, test with the included workflow:
```bash
# Using your RunPod API key
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @test_input.json \
  https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync
```

## Troubleshooting

### Container Startup Issues
- Check if ComfyUI path exists: `/workspace/ComfyUI`
- Verify virtual environment: `/workspace/ComfyUI/venv`
- Ensure models are present in `/workspace/ComfyUI/models`

### ComfyUI Connection Issues
- ComfyUI should start on port 3001
- Handler connects via WebSocket at `ws://127.0.0.1:3001/ws`
- Check startup logs for nginx conflicts

### Model Loading Issues
- Verify FLUX models in correct directories
- Check file permissions on network volume
- Ensure sufficient GPU memory for FLUX models

## Network Volume Benefits

 **Persistent Storage**: Models and configurations survive container restarts
 **Fast Startup**: No model downloading or ComfyUI installation
 **Custom Setup**: Your exact environment preserved
 **Shared Resources**: Multiple endpoints can use same volume
