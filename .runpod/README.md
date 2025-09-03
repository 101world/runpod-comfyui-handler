# RunPod ComfyUI Handler - Network Volume Edition

> Custom RunPod serverless worker optimized for existing ComfyUI installations on network volumes

## What is included?

This worker is specifically designed for **network volume deployments** where ComfyUI is already installed and configured. Unlike standard workers that install ComfyUI in the container, this worker:

- Connects to your existing ComfyUI installation at `/workspace/ComfyUI`
- Preserves your exact startup commands and environment setup
- Uses your custom models, nodes, and configurations
- Starts ComfyUI once at container boot for optimal performance

## Network Volume Requirements

- **ComfyUI Installation**: Pre-installed at `/workspace/ComfyUI` 
- **Python Environment**: Virtual environment at `/workspace/ComfyUI/venv`
- **Models**: FLUX models (flux1-dev.safetensors, clip_l.safetensors, t5xxl_fp8_e4m3fn.safetensors, ae.safetensors)
- **Port Configuration**: ComfyUI configured to run on port 3001

## Usage

The worker accepts standard ComfyUI workflow inputs:

| Parameter  | Type     | Required | Description                                                                                     |
| :--------- | :------- | :------- | :---------------------------------------------------------------------------------------------- |
| `workflow` | `object` | **Yes**  | Complete ComfyUI workflow in API JSON format exported from ComfyUI interface                   |
| `images`   | `array`  | No       | Optional input images array with `name` and `image` (base64) fields                           |

## Architecture Benefits

**Network Volume Approach:**
-  Persistent model storage (no re-download)
-  Custom node configurations preserved
-  Fast container startup (ComfyUI already installed)
-  Shared storage across multiple endpoints

**Optimized Startup:**
-  ComfyUI starts once at container boot
-  Handler only processes requests (no per-request startup)
-  WebSocket communication for efficiency
-  Sub-second request processing after warmup

## Deployment

Deploy using RunPod GitHub integration with network volume attached at `/workspace`.
