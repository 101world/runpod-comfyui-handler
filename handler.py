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
    """Clean up environment before starting ComfyUI - matches your exact commands"""
    
    print(" Setting up environment...")
    
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
            print(f"Command completed: {e}")
            pass
    
    print(" Environment cleanup completed")
    return True

def start_comfyui():
    """Start ComfyUI using your exact working commands"""
    
    comfyui_path = "/workspace/ComfyUI"
    
    # Verify ComfyUI exists
    if not os.path.exists(comfyui_path):
        raise Exception(f"ComfyUI not found at {comfyui_path} - please ensure it is installed")
    
    if not os.path.exists(f"{comfyui_path}/main.py"):
        raise Exception(f"ComfyUI main.py not found at {comfyui_path}")
    
    if not os.path.exists(f"{comfyui_path}/venv"):
        raise Exception(f"ComfyUI virtual environment not found at {comfyui_path}/venv")
    
    print(f" ComfyUI verified at: {comfyui_path}")
    
    # Your exact restart/startup command
    startup_command = """
    systemctl stop nginx 2>/dev/null || true && 
    systemctl disable nginx 2>/dev/null || true && 
    pkill -f nginx || true && 
    cd /workspace/ComfyUI && 
    source venv/bin/activate && 
    fuser -k 3001/tcp || true && 
    python main.py --listen --port 3001
    """
    
    print(f" Starting ComfyUI with your exact command...")
    
    # Start ComfyUI process
    process = subprocess.Popen(
        startup_command,
        shell=True,
        cwd=comfyui_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Wait for ComfyUI to start
    max_wait = 180  # 3 minutes
    print(f"  Waiting up to {max_wait} seconds for ComfyUI to start...")
    
    for i in range(max_wait):
        try:
            response = requests.get("http://127.0.0.1:3001", timeout=5)
            if response.status_code == 200:
                print(f" ComfyUI started successfully after {i} seconds")
                return process
        except Exception as e:
            if i % 10 == 0:
                print(f" Still waiting for ComfyUI... ({i}/{max_wait}s)")
            time.sleep(1)
    
    # Failed to start - get logs
    print(" ComfyUI failed to start")
    try:
        if process.poll() is None:
            stdout, stderr = process.communicate(timeout=10)
        else:
            stdout, stderr = process.communicate()
        
        if stdout:
            print(f" ComfyUI stdout: {stdout.decode()[:1000]}")
        if stderr:
            print(f" ComfyUI stderr: {stderr.decode()[:1000]}")
            
    except Exception as e:
        print(f"Could not capture logs: {e}")
    
    raise Exception(f"ComfyUI failed to start within {max_wait} seconds")

def process_workflow(workflow_data):
    """Process the ComfyUI workflow"""
    
    try:
        print(" Sending workflow to ComfyUI...")
        
        response = requests.post(
            "http://127.0.0.1:3001/prompt",
            json={"prompt": workflow_data},
            timeout=300
        )
        
        if response.status_code != 200:
            raise Exception(f"ComfyUI API error: {response.status_code}")
        
        result = response.json()
        prompt_id = result.get("prompt_id")
        
        if not prompt_id:
            raise Exception("No prompt_id returned from ComfyUI")
        
        print(f" Workflow submitted with prompt_id: {prompt_id}")
        
        # Poll for completion
        for i in range(300):  # 5 minutes
            try:
                history_response = requests.get(f"http://127.0.0.1:3001/history/{prompt_id}")
                
                if history_response.status_code == 200:
                    history = history_response.json()
                    
                    if prompt_id in history:
                        print(" Workflow completed!")
                        
                        outputs = history[prompt_id].get("outputs", {})
                        images = []
                        
                        for node_id, node_output in outputs.items():
                            if "images" in node_output:
                                for image_info in node_output["images"]:
                                    filename = image_info["filename"]
                                    img_response = requests.get(f"http://127.0.0.1:3001/view?filename={filename}")
                                    if img_response.status_code == 200:
                                        img_base64 = base64.b64encode(img_response.content).decode()
                                        images.append({
                                            "filename": filename,
                                            "image_data": img_base64
                                        })
                        
                        return {
                            "status": "success",
                            "prompt_id": prompt_id,
                            "images": images,
                            "message": f"Generated {len(images)} image(s)"
                        }
                
                if i % 10 == 0:
                    print(f" Waiting for workflow... ({i}/300s)")
                    
                time.sleep(1)
                
            except Exception as e:
                print(f"Error checking status: {e}")
                time.sleep(5)
        
        raise Exception("Workflow timed out")
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def handler(event):
    """Main handler function"""
    
    print(" Starting RunPod Serverless Handler for ComfyUI...")
    
    try:
        # Setup environment
        setup_environment()
        
        # Start ComfyUI
        comfyui_process = start_comfyui()
        
        # Get workflow
        input_data = event.get("input", {})
        workflow = input_data.get("workflow")
        
        if not workflow:
            return {
                "status": "error",
                "message": "No workflow provided"
            }
        
        # Process workflow
        result = process_workflow(workflow)
        
        print(f" Handler completed: {result.get('status')}")
        return result
        
    except Exception as e:
        error_msg = f"Handler error: {str(e)}"
        print(f" {error_msg}")
        return {
            "status": "error",
            "message": error_msg
        }

# RunPod serverless function
runpod.serverless.start({"handler": handler})
