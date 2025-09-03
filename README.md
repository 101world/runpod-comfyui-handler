# RunPod ComfyUI Handler

> Custom RunPod serverless worker for ComfyUI with optimized startup and Social Twin workflows

This repository provides a RunPod serverless worker implementation for ComfyUI that:
- Starts ComfyUI once at container boot (not per request)
- Uses your exact ComfyUI installation at `/workspace/ComfyUI` 
- Connects to ComfyUI via websockets for efficient communication
- Supports FLUX model workflows including Social Twin image generation

## Architecture

**Fixed Architecture:**
- `entrypoint.sh`: Starts ComfyUI at container boot with your exact commands
- `handler.py`: Connects to running ComfyUI instance, processes requests only
- **Result**: Fast request processing (seconds vs minutes)

**Previous Issue:**
- Handler tried to start ComfyUI for every request  3+ minute timeouts

## Files

- **`Dockerfile`**: Uses RunPod base image with proper entrypoint approach
- **`entrypoint.sh`**: Starts ComfyUI at boot with user's exact setup commands
- **`handler.py`**: Based on official runpod-workers/worker-comfyui, adapted for port 3001
- **`requirements.txt`**: Minimal dependencies (runpod, requests, websocket-client)
- **`test-handler.js`**: Social Twin FLUX workflow test with environment variable for API key

## User Setup Preserved

Your exact ComfyUI startup commands are preserved:
```bash
cd /workspace/ComfyUI && source venv/bin/activate && python main.py --listen --port 3001
```

## Deployment

This worker is designed for RunPod GitHub integration deployment:

1. Connect your RunPod endpoint to this GitHub repository
2. RunPod will automatically build and deploy on pushes to main branch
3. Test with the included Social Twin workflow

## Testing

```bash
# Set your API key
export RUNPOD_API_KEY="your_actual_api_key"
node test-handler.js
```

## Based On

This implementation follows the proven architecture patterns from:
- [runpod-workers/worker-template](https://github.com/runpod-workers/worker-template)
- [runpod-workers/worker-comfyui](https://github.com/runpod-workers/worker-comfyui)

Adapted specifically for Social Twin FLUX workflows with user's exact ComfyUI setup.
