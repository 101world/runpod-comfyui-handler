# Deployment Guide

This guide explains how to deploy the **Network Volume ComfyUI Worker** on RunPod. This worker is specifically designed to work with existing ComfyUI installations on RunPod network volumes.

## Prerequisites

- **RunPod Network Volume** with ComfyUI installed at `/workspace/ComfyUI`
- **ComfyUI Setup** with virtual environment at `/workspace/ComfyUI/venv`
- **FLUX Models** (flux1-dev.safetensors, clip_l.safetensors, t5xxl_fp8_e4m3fn.safetensors, ae.safetensors)

## Deployment Method: GitHub Integration (Recommended)

This is the easiest method for deploying our network volume worker.

### Step 1: Prepare GitHub Repository

Ensure your repository contains:
```
runpod-comfyui-handler/
 Dockerfile              # Container definition
 src/start.sh            # ComfyUI startup script
 handler.py              # Request processor
 requirements.txt        # Dependencies
 test_input.json         # Test workflow
 docs/                   # Documentation
```

### Step 2: Create RunPod Template

1. Navigate to [RunPod Templates](https://runpod.io/console/serverless/user/templates)
2. Click `New Template`
3. Configure:
   - **Template Name**: `network-volume-comfyui`
   - **Template Type**: `serverless`
   - **Container Disk**: `5 GB` (minimal, since ComfyUI is on network volume)
   - **Environment Variables** (optional):
     ```
     COMFY_HOST=127.0.0.1
     COMFY_PORT=3001
     ```

### Step 3: Create Serverless Endpoint with GitHub Integration

1. Navigate to [RunPod Endpoints](https://runpod.io/console/serverless/user/endpoints)
2. Click `New Endpoint`
3. Select `Start from GitHub Repo`
4. Configure:
   - **Repository**: `101world/runpod-comfyui-handler`
   - **Branch**: `main`
   - **Context Path**: `/`
   - **Dockerfile Path**: `Dockerfile`

### Step 4: Configure Endpoint Settings

#### GPU Configuration
| Model Type | Recommended GPU | VRAM | Container Disk |
|-----------|----------------|------|---------------|
| FLUX.1-dev | RTX 4090 | 24 GB | 5 GB |
| FLUX.1-schnell | RTX 4090 | 24 GB | 5 GB |

#### Worker Settings
- **Active Workers**: `0` (scale as needed)
- **Max Workers**: `3` (adjust based on budget)
- **GPUs/Worker**: `1`
- **Idle Timeout**: `5` minutes
- **Flash Boot**: `enabled` (faster startup)

#### **CRITICAL: Network Volume**
- **Select Network Volume**: Choose your ComfyUI network volume
- **Mount Path**: `/workspace` (default, ComfyUI should be at `/workspace/ComfyUI`)

### Step 5: Deploy

1. Click `Deploy`
2. Wait for build completion (2-3 minutes)
3. Test with included workflow

## Testing Your Deployment

### Using the Test Script

```bash
# Set your API key
export RUNPOD_API_KEY="your_api_key_here"

# Test with Social Twin workflow
node test-handler.js
```

### Using curl

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @test_input.json \
  https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync
```

## Architecture Benefits

### Network Volume Approach
-  **Persistent Storage**: Models stay on volume across deployments
-  **Fast Startup**: No model downloading in container
-  **Cost Effective**: Small container size (5GB vs 30GB+)
-  **Flexibility**: Easy model updates without rebuilding

### Container Optimization
-  **Boot-time Startup**: ComfyUI starts once at container boot
-  **Request Processing**: Handler only processes requests
-  **Websocket Communication**: Efficient real-time monitoring
-  **No Timeouts**: Avoids 3+ minute startup delays

## Troubleshooting

### Common Issues

1. **ComfyUI Not Found**
   ```
   Error: ComfyUI directory not found at /workspace/ComfyUI
   ```
   - Verify network volume is mounted correctly
   - Check ComfyUI installation path

2. **Virtual Environment Issues**
   ```
   Error: No such file or directory: /workspace/ComfyUI/venv/bin/activate
   ```
   - Ensure venv is created in ComfyUI directory
   - Check activation script path

3. **Port Conflicts**
   ```
   Error: Address already in use: 3001
   ```
   - Container restart should fix this
   - Check no other services on port 3001

4. **Model Loading Errors**
   ```
   Error: Unable to load model flux1-dev.safetensors
   ```
   - Verify FLUX models are in correct directories
   - Check file permissions on network volume

### Debug Commands

Check ComfyUI status in container:
```bash
# Check if ComfyUI is running
curl http://127.0.0.1:3001/

# Check ComfyUI logs
tail -f /tmp/comfyui.log

# Check handler status
ps aux | grep handler
```

## Network Volume Setup Guide

If you need to set up your network volume:

1. **Create Network Volume** (250GB recommended for FLUX models)
2. **Install ComfyUI**:
   ```bash
   cd /workspace
   git clone https://github.com/comfyanonymous/ComfyUI.git
   cd ComfyUI
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Download FLUX Models**:
   ```bash
   # Download to appropriate directories in ComfyUI/models/
   # - models/unet/flux1-dev.safetensors
   # - models/clip/clip_l.safetensors
   # - models/clip/t5xxl_fp8_e4m3fn.safetensors
   # - models/vae/ae.safetensors
   ```

## Auto-Deployment

Every push to the `main` branch automatically triggers:
1. Container rebuild
2. Deployment update
3. Endpoint restart

Monitor deployment status in RunPod console.

## Further Resources

- [RunPod GitHub Integration](https://docs.runpod.io/serverless/github-integration)
- [Network Volumes Guide](https://docs.runpod.io/storage/network-volumes)
- [ComfyUI Documentation](https://github.com/comfyanonymous/ComfyUI)
- [FLUX Models](https://huggingface.co/black-forest-labs)
