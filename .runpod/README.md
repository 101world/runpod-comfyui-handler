![Network Volume ComfyUI Worker](https://via.placeholder.com/800x200/1a1a1a/ffffff?text=Network+Volume+ComfyUI+Worker)

---

Custom RunPod serverless worker optimized for **existing ComfyUI installations** on network volumes.

---

[![RunPod](https://api.runpod.io/badge/101world/runpod-comfyui-handler)](https://www.runpod.io/console/hub)

---

## What makes this different?

This worker is specifically designed for users who already have ComfyUI installed on a RunPod network volume. Instead of downloading and installing ComfyUI in the container (which takes 3+ minutes), it connects to your existing installation for **instant startup**.

## Requirements

- **RunPod Network Volume** with ComfyUI at `/workspace/ComfyUI`
- **Virtual Environment** at `/workspace/ComfyUI/venv` 
- **FLUX Models** (flux1-dev, clip_l, t5xxl_fp8_e4m3fn, ae)

## Key Features

 **Instant Startup** - ComfyUI starts at container boot, not per request  
 **Network Volume Optimized** - Uses your existing ComfyUI installation  
 **FLUX Ready** - Optimized for Social Twin and professional portraits  
 **Websocket Communication** - Real-time job monitoring  
 **Cost Effective** - 5GB container vs 30GB+ official images  

## Usage

Deploy via GitHub integration and test with the included Social Twin workflow:

```json
{
  "input": {
    "workflow": {
      "6": {
        "inputs": {
          "text": "professional headshot portrait, studio lighting",
          "clip": ["30", 1]
        },
        "class_type": "CLIPTextEncode"
      }
    }
  }
}
```

## Architecture

Unlike official workers that install ComfyUI per container, this worker:
1. **Container Boot**: Starts ComfyUI from network volume once
2. **Request Processing**: Handler processes jobs via websocket
3. **Result**: Sub-second response times instead of 3+ minute timeouts

Perfect for users with existing ComfyUI setups who want serverless efficiency.
