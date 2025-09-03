# RunPod ComfyUI Handler - Network Volume Edition

> Optimized RunPod serverless worker for existing ComfyUI installations on network volumes

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)
![RunPod](https://img.shields.io/badge/platform-RunPod-purple.svg)

---

## Overview

This RunPod worker is specifically designed for **network volume deployments** where ComfyUI is already installed and configured. Instead of installing ComfyUI in the container, it connects to your existing installation, preserving your custom setup while providing optimal performance.

## Key Features

###  Network Volume Optimization
- Connects to existing ComfyUI at `/workspace/ComfyUI`
- Preserves your exact startup commands and environment
- No model re-downloading (persistent on network volume)
- Custom nodes and configurations maintained

###  Performance Benefits
- ComfyUI starts once at container boot
- Handler processes requests only (no per-request startup)
- WebSocket communication for efficiency
- Sub-second processing after warmup

###  FLUX Model Support
- Optimized for FLUX.1-dev workflows
- Social Twin portrait generation ready
- Professional headshot workflows included

## Quick Start

### 1. Network Volume Requirements
- **ComfyUI Installation**: `/workspace/ComfyUI`
- **Python Environment**: `/workspace/ComfyUI/venv`
- **FLUX Models**: flux1-dev.safetensors, clip_l.safetensors, t5xxl_fp8_e4m3fn.safetensors, ae.safetensors
- **Working Command**: `cd /workspace/ComfyUI && source venv/bin/activate && python main.py --listen --port 3001`

### 2. Deploy to RunPod
1. Create serverless endpoint
2. Use GitHub integration: `101world/runpod-comfyui-handler`
3. Attach your network volume at `/workspace`
4. Deploy and test

### 3. Test Workflow
```bash
# Set your API key
export RUNPOD_API_KEY=""your_api_key""
node test-handler.js

# Or use curl with test_input.json
curl -X POST \
  -H ""Authorization: Bearer "" \
  -H ""Content-Type: application/json"" \
  -d @test_input.json \
  https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync
```

## Architecture

### Container Structure
```
runpod-comfyui-handler/
 src/
    start.sh              # ComfyUI startup script
 docs/
    deployment.md         # Deployment guide
    network-volume.md     # Volume setup guide
 tests/
    test_handler.py       # Unit tests
 .runpod/
    README.md            # RunPod hub documentation
 Dockerfile               # Network volume optimized
 handler.py               # WebSocket request processor
 requirements.txt         # Minimal dependencies
 test_input.json         # FLUX workflow sample
 test-handler.js         # API testing script
```

### Startup Flow
1. **Container Boot**: `start.sh` executes
2. **ComfyUI Launch**: Your exact command runs
3. **Readiness Check**: WebSocket connection verified
4. **Handler Start**: Request processing begins
5. **Ready**: Sub-second response times

## Network Volume vs Standard Workers

| Aspect | Network Volume (This) | Standard Workers |
|--------|----------------------|------------------|
| **ComfyUI Installation** | Pre-installed on volume | Downloaded each build |
| **Model Storage** | Persistent on volume | Downloaded each container |
| **Custom Nodes** | Preserved configurations | Lost on rebuild |
| **Startup Time** | ~30 seconds | ~5-10 minutes |
| **Storage Cost** | Volume storage only | Volume + container storage |
| **Flexibility** | Full control | Limited to pre-built images |

## API Specification

### Input Format
```json
{
  ""input"": {
    ""workflow"": {
      ""6"": {
        ""inputs"": {
          ""text"": ""professional headshot portrait"",
          ""clip"": [""30"", 1]
        },
        ""class_type"": ""CLIPTextEncode""
      }
    }
  }
}
```

### Output Format
```json
{
  ""output"": {
    ""images"": [
      {
        ""filename"": ""ComfyUI_00001_.png"",
        ""type"": ""base64"",
        ""data"": ""iVBORw0KGgoAAAANSUhEUg...""
      }
    ]
  }
}
```

## Documentation

-  [Deployment Guide](docs/deployment.md) - Complete deployment instructions
-  [Network Volume Setup](docs/network-volume.md) - Volume preparation guide
-  [Testing Guide](tests/) - Unit tests and validation

## Based On Official Patterns

This implementation follows the proven architecture from:
- [runpod-workers/worker-template](https://github.com/runpod-workers/worker-template)
- [runpod-workers/worker-comfyui](https://github.com/runpod-workers/worker-comfyui)

Specifically adapted for network volume deployments with user's exact ComfyUI setup.

## License

MIT License - see [LICENSE](LICENSE) file for details.
