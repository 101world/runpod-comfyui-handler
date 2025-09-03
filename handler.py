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
    
    # Based on standard RunPod network volume setup - prioritize /runpod-volume
    possible_paths = [
        "/runpod-volume/ComfyUI",    # MOST LIKELY - Standard RunPod network volume mount
        "/workspace/ComfyUI",       # Alternative mount path  
        "/content/ComfyUI",         # Google Colab style mount
        "/ComfyUI",                 # Root level (unlikely)
        "/opt/ComfyUI",            # System directory
        "/app/ComfyUI",            # Application directory
        "/home/ComfyUI",           # Home directory
        "/mnt/ComfyUI",            # Manual mount point
        "/vol/ComfyUI"             # Volume mount alternative
    ]
    
    # First, let's discover what directories actually exist
    print("🔍 Discovering available directories...")
    
    # Check root level directories
    try:
        root_dirs = os.listdir("/")
        print(f"📁 Root directories: {[d for d in root_dirs if not d.startswith('.')][:10]}")
        
        # Look for anything that might be ComfyUI-related
        comfyui_related = [d for d in root_dirs if 'comfy' in d.lower() or 'ComfyUI' in d]
        if comfyui_related:
            print(f"🎯 ComfyUI-related directories in root: {comfyui_related}")
            # Add these to possible paths
            for d in comfyui_related:
                full_path = f"/{d}"
                if full_path not in possible_paths:
                    possible_paths.append(full_path)
    except Exception as e:
        print(f"Could not list root directories: {e}")
    
    # Check workspace if it exists
    if os.path.exists("/workspace"):
        try:
            workspace_dirs = os.listdir("/workspace")
            print(f"📁 Workspace directories: {workspace_dirs[:10]}")
            
            # Look for ComfyUI in workspace
            for d in workspace_dirs:
                if 'comfy' in d.lower() or 'ComfyUI' in d:
                    full_path = f"/workspace/{d}"
                    if full_path not in possible_paths:
                        possible_paths.append(full_path)
        except Exception as e:
            print(f"Could not list workspace directories: {e}")
    
    # Check runpod-volume if it exists
    if os.path.exists("/runpod-volume"):
        try:
            volume_dirs = os.listdir("/runpod-volume")
            print(f"📁 RunPod volume directories: {volume_dirs[:10]}")
            
            # Look for ComfyUI in volume
            for d in volume_dirs:
                if 'comfy' in d.lower() or 'ComfyUI' in d:
                    full_path = f"/runpod-volume/{d}"
                    if full_path not in possible_paths:
                        possible_paths.append(full_path)
        except Exception as e:
            print(f"Could not list volume directories: {e}")
    
    print(f"🔍 Checking these possible paths: {possible_paths}")
    
    comfyui_path = None
    for path in possible_paths:
        print(f"Checking: {path}")
        if os.path.exists(path):
            # Verify it's actually ComfyUI by checking for key files
            main_py = os.path.join(path, "main.py")
            if os.path.exists(main_py):
                comfyui_path = path
                print(f"✅ Found ComfyUI at: {path}")
                break
            else:
                print(f"⚠️  Directory {path} exists but no main.py found")
        else:
            print(f"❌ Path {path} does not exist")
    
    if not comfyui_path:
        # Final attempt - search the filesystem
        print("🔍 Searching filesystem for ComfyUI...")
        try:
            # Search for main.py files that might be ComfyUI
            result = subprocess.run(
                "find / -name 'main.py' -path '*/ComfyUI/*' 2>/dev/null | head -5",
                shell=True, capture_output=True, text=True, timeout=30
            )
            if result.stdout.strip():
                print(f"Found potential ComfyUI main.py files: {result.stdout.strip()}")
                # Take the first one
                main_py_path = result.stdout.strip().split('\n')[0]
                potential_path = os.path.dirname(main_py_path)
                if potential_path and os.path.exists(potential_path):
                    comfyui_path = potential_path
                    print(f"✅ Found ComfyUI via filesystem search at: {potential_path}")
        except Exception as e:
            print(f"Filesystem search failed: {e}")
        
        if not comfyui_path:
            discovered_info = {
                "root_dirs": root_dirs if 'root_dirs' in locals() else "Could not list",
                "workspace_exists": os.path.exists("/workspace"),
                "volume_exists": os.path.exists("/runpod-volume"),
                "checked_paths": possible_paths
            }
            raise Exception(f"ComfyUI not found. Discovery info: {discovered_info}")
    
    venv_activate = f"{comfyui_path}/venv/bin/activate"
    main_py = f"{comfyui_path}/main.py"
    
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
    
    # Use the exact same command as user's Jupyter Lab, but with dynamic path
    startup_command = f"""
    cd {comfyui_path} && 
    source venv/bin/activate && 
    fuser -k 3001/tcp || true && 
    python main.py --listen --port 3001
    """
    
    print(f"🚀 Starting ComfyUI with command: {startup_command}")
    
    # Update PYTHONPATH to match the found ComfyUI location
    os.environ["PYTHONPATH"] = comfyui_path
    
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
    max_wait = 180  # 3 minutes max - increased timeout
    print(f"⏱️  Waiting up to {max_wait} seconds for ComfyUI to start...")
    
    for i in range(max_wait):
        try:
            response = requests.get("http://127.0.0.1:3001", timeout=5)
            if response.status_code == 200:
                print(f"✅ ComfyUI started successfully after {i} seconds")
                return process
        except Exception as e:
            if i % 10 == 0:  # Log every 10 seconds
                print(f"⏳ Still waiting for ComfyUI... ({i}/{max_wait}s)")
            time.sleep(1)
    
    # ComfyUI failed to start - gather diagnostic info
    try:
        stdout, stderr = process.communicate(timeout=5)
        print(f"🔍 ComfyUI stdout: {stdout.decode()[:1000]}...")
        print(f"🔍 ComfyUI stderr: {stderr.decode()[:1000]}...")
    except:
        print("Could not capture ComfyUI logs")
    
    raise Exception(f"ComfyUI failed to start within {max_wait} seconds")

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

def run_path_discovery():
    """Comprehensive path discovery to find where ComfyUI is mounted"""
    
    discovery_info = {
        "root_directories": [],
        "potential_comfy_locations": [],
        "mounted_volumes": [],
        "environment_variables": {},
        "current_working_directory": os.getcwd(),
        "user_info": {},
        "disk_usage": [],
        "filesystem_search_results": []
    }
    
    print("🔍 Starting comprehensive path discovery...")
    
    try:
        # Get root directories
        print("📁 Scanning root directories...")
        for item in os.listdir('/'):
            full_path = f'/{item}'
            if os.path.isdir(full_path):
                try:
                    size = len(os.listdir(full_path)) if os.access(full_path, os.R_OK) else "no_access"
                    discovery_info["root_directories"].append({
                        "name": item,
                        "path": full_path,
                        "size": size,
                        "accessible": os.access(full_path, os.R_OK)
                    })
                except Exception as e:
                    discovery_info["root_directories"].append({
                        "name": item,
                        "path": full_path,
                        "size": "error",
                        "error": str(e)
                    })
    except Exception as e:
        discovery_info["root_scan_error"] = str(e)
    
    # Check common mount points for ComfyUI
    potential_paths = [
        "/workspace/ComfyUI",
        "/runpod-volume/ComfyUI", 
        "/content/ComfyUI",
        "/opt/ComfyUI",
        "/app/ComfyUI",
        "/root/ComfyUI",
        "/home/ComfyUI",
        "/mnt/ComfyUI",
        "/vol/ComfyUI",
        "/ComfyUI",
        # Check parent directories too
        "/workspace",
        "/runpod-volume",
        "/content",
        "/opt",
        "/app",
        "/root",
        "/home",
        "/mnt",
        "/vol"
    ]
    
    print("🔍 Checking potential ComfyUI locations...")
    for path in potential_paths:
        try:
            exists = os.path.exists(path)
            location_info = {
                "path": path,
                "exists": exists
            }
            
            if exists:
                location_info["is_directory"] = os.path.isdir(path)
                location_info["readable"] = os.access(path, os.R_OK)
                
                if os.path.isdir(path) and os.access(path, os.R_OK):
                    try:
                        contents = os.listdir(path)
                        location_info["contents_count"] = len(contents)
                        location_info["contents_sample"] = contents[:10]  # First 10 items
                        
                        # Check for ComfyUI-specific files
                        has_main_py = "main.py" in contents
                        has_comfyui_files = any("comfy" in item.lower() for item in contents)
                        location_info["has_main_py"] = has_main_py
                        location_info["has_comfyui_files"] = has_comfyui_files
                        
                    except Exception as e:
                        location_info["list_error"] = str(e)
            
            discovery_info["potential_comfy_locations"].append(location_info)
            
        except Exception as e:
            discovery_info["potential_comfy_locations"].append({
                "path": path,
                "error": str(e)
            })
    
    # Get mount information
    print("💾 Checking mount points...")
    try:
        mount_result = subprocess.run(['mount'], capture_output=True, text=True, timeout=10)
        if mount_result.returncode == 0:
            mounts = []
            for line in mount_result.stdout.split('\n'):
                if line.strip():
                    mounts.append(line.strip())
            discovery_info["mounted_volumes"] = mounts
    except Exception as e:
        discovery_info["mount_error"] = str(e)
    
    # Get disk usage for directories
    print("📊 Checking disk usage...")
    try:
        df_result = subprocess.run(['df', '-h'], capture_output=True, text=True, timeout=10)
        if df_result.returncode == 0:
            discovery_info["disk_usage"] = df_result.stdout.split('\n')
    except Exception as e:
        discovery_info["df_error"] = str(e)
    
    # Get environment variables related to paths
    print("🌐 Checking environment variables...")
    for key, value in os.environ.items():
        if any(keyword in key.lower() for keyword in ['path', 'home', 'workspace', 'volume', 'mount', 'comfy']):
            discovery_info["environment_variables"][key] = value
    
    # Get user information
    try:
        discovery_info["user_info"]["uid"] = os.getuid()
        discovery_info["user_info"]["gid"] = os.getgid()
        discovery_info["user_info"]["username"] = os.getenv('USER', 'unknown')
    except Exception as e:
        discovery_info["user_error"] = str(e)
    
    # Search for ComfyUI installations
    print("🔎 Searching for ComfyUI installations...")
    try:
        # Search for main.py files that might be ComfyUI
        search_result = subprocess.run(
            "find / -name 'main.py' 2>/dev/null | head -20",
            shell=True, capture_output=True, text=True, timeout=30
        )
        if search_result.stdout.strip():
            main_py_files = search_result.stdout.strip().split('\n')
            discovery_info["filesystem_search_results"] = main_py_files
    except Exception as e:
        discovery_info["search_error"] = str(e)
    
    print("✅ Path discovery completed")
    return {
        "status": "success",
        "discovery": discovery_info,
        "message": "Comprehensive path discovery completed"
    }

def handler(job):
    """Main handler function for RunPod serverless"""
    
    try:
        print("Starting job processing...")
        
        # Get job input
        job_input = job.get("input", {})
        
        # Check if this is a discovery request
        if job_input.get('action') == 'discover_paths' or job_input.get('debug_mode') or job_input.get('debug'):
            print("🔍 Running path discovery...")
            return run_path_discovery()
        
        # Set up environment
        setup_environment()
        
        # Start ComfyUI
        comfyui_process = start_comfyui()
        
        try:
            # Get workflow from job input
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
