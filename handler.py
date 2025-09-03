#!/usr/bin/env python3

import runpod
import json
import subprocess
import os
import time
import requests
import tempfile
import base64
from typing import Dict, Any

def setup_environment():
    """Set up the environment before processing - matches user's exact commands"""
    
    print("🔧 Setting up environment...")
    
    # Your exact cleanup commands
    cleanup_commands = [
        "systemctl stop nginx 2>/dev/null || true",
        "systemctl disable nginx 2>/dev/null || true", 
        "pkill -f nginx || true",
        "fuser -k 3001/tcp || true"
    ]
    
    for cmd in cleanup_commands:
        try:
            print(f"Running: {cmd}")
            subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
        except Exception as e:
            print(f"Command failed (expected): {e}")
            pass  # Ignore errors like your || true
    
    print("✅ Environment setup completed")
    return True

def start_comfyui():
    """Start ComfyUI using the exact same process as user's Jupyter Lab"""
    
    comfyui_path = "/workspace/ComfyUI"
    venv_activate = "/workspace/ComfyUI/venv/bin/activate"
    main_py = "/workspace/ComfyUI/main.py"
    
    print(f"🔍 Checking ComfyUI setup...")
    print(f"ComfyUI path: {comfyui_path}")
    print(f"Virtual env: {venv_activate}")
    print(f"Main script: {main_py}")
    
    # Check if paths exist
    if not os.path.exists(comfyui_path):
        raise Exception(f"ComfyUI directory not found at {comfyui_path}")
    
    if not os.path.exists(venv_activate):
        raise Exception(f"Virtual environment activation script not found at {venv_activate}")
        
    if not os.path.exists(main_py):
        raise Exception(f"ComfyUI main.py not found at {main_py}")
    
    print("✅ All ComfyUI components found")
    
    # Use the exact same command as user's Jupyter Lab
    startup_command = f"""
    cd /workspace/ComfyUI && 
    source venv/bin/activate && 
    fuser -k 3001/tcp || true && 
    python main.py --listen --port 3001
    """
    
    print(f"🚀 Starting ComfyUI with command: {startup_command}")
    
    # Start ComfyUI in background using shell=True to handle the source command
    process = subprocess.Popen(
        startup_command,
        shell=True,
        cwd=comfyui_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid  # Create new process group
    )
    
    # Wait for ComfyUI to start (check if port is responding)
    max_wait = 60  # 60 seconds max
    for i in range(max_wait):
        try:
            response = requests.get("http://127.0.0.1:3001", timeout=5)
            if response.status_code == 200:
                print(f"ComfyUI started successfully after {i} seconds")
                return process
        except:
            time.sleep(1)
    
    raise Exception("ComfyUI failed to start within 60 seconds")

def process_workflow(workflow_data: Dict[str, Any]):
    """Process the ComfyUI workflow"""
    
    try:
        # Send workflow to ComfyUI API
        response = requests.post(
            "http://127.0.0.1:3001/prompt",
            json={"prompt": workflow_data},
            timeout=300  # 5 minutes timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"ComfyUI API error: {response.status_code}")
        
        result = response.json()
        prompt_id = result.get("prompt_id")
        
        if not prompt_id:
            raise Exception("No prompt_id returned from ComfyUI")
        
        # Poll for completion
        max_wait = 300  # 5 minutes
        for i in range(max_wait):
            history_response = requests.get(f"http://127.0.0.1:3001/history/{prompt_id}")
            
            if history_response.status_code == 200:
                history = history_response.json()
                
                if prompt_id in history:
                    # Get the generated images
                    outputs = history[prompt_id].get("outputs", {})
                    images = []
                    
                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            for image_info in node_output["images"]:
                                filename = image_info["filename"]
                                # Get image from ComfyUI
                                img_response = requests.get(f"http://127.0.0.1:3001/view?filename={filename}")
                                if img_response.status_code == 200:
                                    # Convert to base64
                                    img_base64 = base64.b64encode(img_response.content).decode()
                                    images.append({
                                        "filename": filename,
                                        "data": img_base64
                                    })
                    
                    return {"images": images, "prompt_id": prompt_id}
            
            time.sleep(1)
        
        raise Exception("Workflow processing timed out")
        
    except Exception as e:
        raise Exception(f"Workflow processing failed: {str(e)}")

def handler(job):
    """Main handler function for RunPod serverless"""
    
    try:
        print("Starting job processing...")
        
        # Set up environment
        setup_environment()
        
        # Start ComfyUI
        comfyui_process = start_comfyui()
        
        try:
            # Get workflow from job input
            job_input = job.get("input", {})
            workflow = job_input.get("workflow", {})
            
            if not workflow:
                raise Exception("No workflow provided in job input")
            
            # Process the workflow
            result = process_workflow(workflow)
            
            return {"status": "success", "output": result}
            
        finally:
            # Clean up ComfyUI process
            try:
                comfyui_process.terminate()
                comfyui_process.wait(timeout=10)
            except:
                comfyui_process.kill()
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("Starting RunPod Serverless Handler for ComfyUI...")
    runpod.serverless.start({"handler": handler})
