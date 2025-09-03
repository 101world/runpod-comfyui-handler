# Network Volume Setup Guide

This guide explains how to prepare your RunPod network volume for the ComfyUI worker.

## Volume Requirements

### Minimum Specifications
- **Size**: 250GB (for FLUX models)
- **Region**: Same as your endpoint (EU-SE-1 recommended)
- **Type**: Network Volume (persistent storage)

### Directory Structure
Your network volume should have this structure:
```
/workspace/
 ComfyUI/
     main.py
     venv/
        bin/activate
        lib/python3.*/site-packages/
     models/
        unet/
           flux1-dev.safetensors
        clip/
           clip_l.safetensors
           t5xxl_fp8_e4m3fn.safetensors
        vae/
            ae.safetensors
     custom_nodes/
     input/
     output/
```

## Setup Process

### 1. Initial ComfyUI Installation
If you don't have ComfyUI installed yet:

```bash
# Mount volume and install ComfyUI
cd /workspace
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. FLUX Model Installation
Download required FLUX models:

```bash
cd /workspace/ComfyUI
source venv/bin/activate

# Create model directories
mkdir -p models/unet models/clip models/vae

# Download FLUX models (requires HuggingFace access token)
# UNET model
wget --header="Authorization: Bearer YOUR_HF_TOKEN" \
  -O models/unet/flux1-dev.safetensors \
  https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors

# CLIP models  
wget -O models/clip/clip_l.safetensors \
  https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors

wget -O models/clip/t5xxl_fp8_e4m3fn.safetensors \
  https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors

# VAE model
wget --header="Authorization: Bearer YOUR_HF_TOKEN" \
  -O models/vae/ae.safetensors \
  https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors
```

### 3. Verify Installation
Test that ComfyUI starts correctly:

```bash
cd /workspace/ComfyUI
source venv/bin/activate
python main.py --listen --port 3001

# Should see:
# Starting server
# To see the GUI go to: http://localhost:3001
```

### 4. Custom Nodes (Optional)
If you need custom nodes for your workflows:

```bash
cd /workspace/ComfyUI/custom_nodes
git clone https://github.com/your/custom-node.git
# Install node dependencies as needed
```

## Volume Management

### Mounting in RunPod
- **Mount Path**: `/workspace` (exactly this path)
- **Automatic**: RunPod auto-mounts network volumes
- **Persistence**: Data survives container restarts

### Backup Strategy
- Network volumes are persistent but consider backups
- Export critical workflows and model configurations
- Document custom node installations

## Troubleshooting

### Permission Issues
```bash
# Fix permissions if needed
sudo chown -R 1000:1000 /workspace/ComfyUI
sudo chmod -R 755 /workspace/ComfyUI
```

### Model Loading Problems
- Verify model file integrity with checksums
- Ensure sufficient disk space (FLUX models are large)
- Check file paths match expected locations

### Environment Issues
- Python version should be 3.8+
- Virtual environment must be activated
- Required packages installed in venv

## Performance Optimization

### Storage Performance
- Use SSD-backed network volumes when available
- Keep frequently accessed models in root directories
- Monitor I/O performance during generation

### Memory Management
- FLUX models require significant GPU memory
- Consider model variants (fp8 vs full precision)
- Monitor GPU memory usage in ComfyUI logs

This network volume setup provides the foundation for fast, persistent ComfyUI deployments.
