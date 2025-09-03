# Network Volume ComfyUI Worker

> Optimized RunPod serverless worker for **existing ComfyUI installations** on network volumes

![Network Volume Architecture](https://via.placeholder.com/800x200/1a1a1a/ffffff?text=Network+Volume+ComfyUI+Worker)

This RunPod worker is specifically designed for users who already have ComfyUI installed on a network volume. Instead of downloading and installing ComfyUI in the container, it connects to your existing installation for instant startup and cost-effective operation.

##  Key Advantages

- ** Instant Startup**: ComfyUI starts at container boot, not per request  
- ** Cost Effective**: 5GB container vs 30GB+ official images
- ** Persistent Storage**: Models stay on volume across deployments
- ** No Timeouts**: Eliminates 3+ minute startup delays
- ** FLUX Ready**: Optimized for Social Twin and professional workflows

##  Repository Structure

```
runpod-comfyui-handler/
 .runpod/              # RunPod platform configurations
 docs/                 # Documentation
    deployment.md     # Deployment guide
    network-volume-setup.md
 src/                  # Source code
    start.sh          # ComfyUI startup script
 tests/                # Unit tests
 Dockerfile           # Container definition
 handler.py           # Request processor
 requirements.txt     # Python dependencies
 test_input.json      # FLUX workflow sample
 test-handler.js      # API testing script
```

##  Architecture

### Traditional Workers
```
Request  Start ComfyUI (3+ min)  Process  Stop ComfyUI
```

### Network Volume Worker  
```
Container Boot  Start ComfyUI (30s)  Ready
Request  Process (seconds)  Response
```

##  Prerequisites

- **RunPod Network Volume** with ComfyUI at `/workspace/ComfyUI`
- **Virtual Environment** at `/workspace/ComfyUI/venv`
- **FLUX Models**: flux1-dev, clip_l, t5xxl_fp8_e4m3fn, ae

##  Quick Start

### 1. Set Up Network Volume
See [Network Volume Setup Guide](docs/network-volume-setup.md) for detailed instructions.

### 2. Deploy Worker
See [Deployment Guide](docs/deployment.md) for GitHub integration deployment.

### 3. Test Deployment
```bash
# Set your API key
export RUNPOD_API_KEY="your_api_key_here"

# Test with Social Twin workflow  
node test-handler.js
```

##  Sample Workflow

The included `test_input.json` contains a FLUX-based Social Twin workflow:

```json
{
  "input": {
    "workflow": {
      "6": {
        "inputs": {
          "text": "professional headshot portrait of a confident business person, studio lighting, clean background, high quality, detailed",
          "clip": ["30", 1]
        },
        "class_type": "CLIPTextEncode"
      }
    }
  }
}
```

##  Performance Comparison

| Method | Container Size | Startup Time | Request Time | Cost/Hour |
|--------|---------------|--------------|--------------|-----------|
| Official | 30GB+ | 3-5 min | 3-5 min | Higher |
| Network Volume | 5GB | 30 sec | 10-30 sec | Lower |

##  Configuration

### Environment Variables
```bash
COMFY_HOST=127.0.0.1          # ComfyUI host
COMFY_PORT=3001               # ComfyUI port  
SERVE_API_LOCALLY=false       # Local API mode
```

### Network Volume Requirements
```bash
/workspace/ComfyUI/           # ComfyUI installation
 main.py                   # ComfyUI main script
 venv/                     # Virtual environment
    bin/activate         # Activation script
 models/                   # Model directories
     unet/                 # FLUX UNet models
     clip/                 # CLIP text encoders  
     vae/                  # VAE models
```

##  Development

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Test handler locally
python handler.py
```

### Docker Build
```bash
# Build container
docker build --platform linux/amd64 -t network-volume-comfyui .

# Run locally (requires network volume mount)
docker run -v /path/to/volume:/workspace network-volume-comfyui
```

##  Documentation

- [Deployment Guide](docs/deployment.md) - Complete deployment instructions
- [Network Volume Setup](docs/network-volume-setup.md) - Volume preparation guide  
- [API Reference](test_input.json) - Sample workflow format

##  Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

This implementation follows the proven architecture patterns from:
- [runpod-workers/worker-template](https://github.com/runpod-workers/worker-template)
- [runpod-workers/worker-comfyui](https://github.com/runpod-workers/worker-comfyui)

Adapted specifically for network volume setups and FLUX workflows.
