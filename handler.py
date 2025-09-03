import runpod
import requests
import websocket
import json
import uuid
import time
import base64
import tempfile
import os
from io import BytesIO

# ComfyUI connection settings - adapted for your setup
COMFY_HOST = "127.0.0.1:3001"  # Your ComfyUI port
COMFY_API_AVAILABLE_INTERVAL_MS = 50
COMFY_API_AVAILABLE_MAX_RETRIES = 500

def check_server(url, retries=500, delay=50):
    """
    Check if ComfyUI server is reachable
    """
    print(f"🔍 Checking ComfyUI API server at {url}...")
    for i in range(retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ ComfyUI API is reachable")
                return True
        except requests.RequestException:
            pass
        time.sleep(delay / 1000)
    
    print(f"❌ Failed to connect to ComfyUI at {url} after {retries} attempts.")
    return False

def validate_input(job_input):
    """
    Validates the input for the handler function.
    """
    if job_input is None:
        return None, "Please provide input"
    
    if isinstance(job_input, str):
        try:
            job_input = json.loads(job_input)
        except json.JSONDecodeError:
            return None, "Invalid JSON format in input"
    
    workflow = job_input.get("workflow")
    if workflow is None:
        return None, "Missing 'workflow' parameter"
    
    images = job_input.get("images")
    if images is not None:
        if not isinstance(images, list) or not all(
            "name" in image and "image" in image for image in images
        ):
            return (
                None,
                "'images' must be a list of objects with 'name' and 'image' keys",
            )
    
    return {"workflow": workflow, "images": images}, None

def upload_images(images):
    """
    Upload base64 encoded images to ComfyUI
    """
    if not images:
        return {"status": "success", "message": "No images to upload", "details": []}
    
    responses = []
    upload_errors = []
    print(f"📤 Uploading {len(images)} image(s)...")
    
    for image in images:
        try:
            name = image["name"]
            image_data_uri = image["image"]
            
            # Strip Data URI prefix if present
            if "," in image_data_uri:
                base64_data = image_data_uri.split(",", 1)[1]
            else:
                base64_data = image_data_uri
            
            blob = base64.b64decode(base64_data)
            
            # Prepare form data
            files = {
                "image": (name, BytesIO(blob), "image/png"),
                "overwrite": (None, "true"),
            }
            
            # Upload to ComfyUI
            response = requests.post(
                f"http://{COMFY_HOST}/upload/image", files=files, timeout=30
            )
            response.raise_for_status()
            responses.append(f"Successfully uploaded {name}")
            print(f"✅ Successfully uploaded {name}")
            
        except Exception as e:
            error_msg = f"Error uploading {image.get('name', 'unknown')}: {e}"
            print(f"❌ {error_msg}")
            upload_errors.append(error_msg)
    
    if upload_errors:
        return {
            "status": "error",
            "message": "Some images failed to upload",
            "details": upload_errors,
        }
    
    return {
        "status": "success",
        "message": "All images uploaded successfully",
        "details": responses,
    }

def queue_workflow(workflow, client_id):
    """
    Queue a workflow to be processed by ComfyUI
    """
    payload = {"prompt": workflow, "client_id": client_id}
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(
        f"http://{COMFY_HOST}/prompt", data=data, headers=headers, timeout=30
    )
    
    if response.status_code == 400:
        print(f"❌ ComfyUI validation error: {response.text}")
        try:
            error_data = response.json()
            error_message = "Workflow validation failed"
            if "error" in error_data:
                error_info = error_data["error"]
                if isinstance(error_info, dict):
                    error_message = error_info.get("message", error_message)
                else:
                    error_message = str(error_info)
            raise ValueError(f"{error_message}. Response: {response.text}")
        except json.JSONDecodeError:
            raise ValueError(f"ComfyUI validation failed: {response.text}")
    
    response.raise_for_status()
    return response.json()

def get_history(prompt_id):
    """
    Retrieve the history of a prompt
    """
    response = requests.get(f"http://{COMFY_HOST}/history/{prompt_id}", timeout=30)
    response.raise_for_status()
    return response.json()

def get_image_data(filename, subfolder, image_type):
    """
    Fetch image bytes from ComfyUI
    """
    print(f"📥 Fetching image: type={image_type}, subfolder={subfolder}, filename={filename}")
    
    params = {"filename": filename, "subfolder": subfolder, "type": image_type}
    
    try:
        response = requests.get(f"http://{COMFY_HOST}/view", params=params, timeout=60)
        response.raise_for_status()
        print(f"✅ Successfully fetched image data for {filename}")
        return response.content
    except Exception as e:
        print(f"❌ Error fetching image data for {filename}: {e}")
        return None

def handler(job):
    """
    Main handler function for RunPod jobs
    """
    job_input = job["input"]
    job_id = job["id"]
    
    print(f"🚀 Processing job {job_id}")
    
    # Validate input
    validated_data, error_message = validate_input(job_input)
    if error_message:
        return {"error": error_message}
    
    workflow = validated_data["workflow"]
    input_images = validated_data.get("images")
    
    # Check if ComfyUI is available
    if not check_server(
        f"http://{COMFY_HOST}/",
        COMFY_API_AVAILABLE_MAX_RETRIES,
        COMFY_API_AVAILABLE_INTERVAL_MS,
    ):
        return {
            "error": f"ComfyUI server ({COMFY_HOST}) not reachable after multiple retries."
        }
    
    # Upload input images if provided
    if input_images:
        upload_result = upload_images(input_images)
        if upload_result["status"] == "error":
            return {
                "error": "Failed to upload one or more input images",
                "details": upload_result["details"],
            }
    
    # Set up WebSocket connection
    client_id = str(uuid.uuid4())
    ws_url = f"ws://{COMFY_HOST}/ws?clientId={client_id}"
    
    ws = None
    prompt_id = None
    output_data = []
    errors = []
    
    try:
        # Connect to WebSocket
        print(f"🔌 Connecting to WebSocket: {ws_url}")
        ws = websocket.WebSocket()
        ws.connect(ws_url, timeout=10)
        print(f"✅ WebSocket connected")
        
        # Queue the workflow
        try:
            queued_workflow = queue_workflow(workflow, client_id)
            prompt_id = queued_workflow.get("prompt_id")
            if not prompt_id:
                raise ValueError(f"No prompt_id in response: {queued_workflow}")
            print(f"📋 Workflow queued with prompt_id: {prompt_id}")
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            else:
                raise ValueError(f"Unexpected error queuing workflow: {e}")
        
        # Wait for execution completion via WebSocket
        print(f"⏳ Waiting for workflow execution ({prompt_id})...")
        execution_done = False
        
        while True:
            try:
                out = ws.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    
                    if message.get("type") == "status":
                        status_data = message.get("data", {}).get("status", {})
                        queue_remaining = status_data.get('exec_info', {}).get('queue_remaining', 'N/A')
                        print(f"📊 Status update: {queue_remaining} items remaining in queue")
                    
                    elif message.get("type") == "executing":
                        data = message.get("data", {})
                        if (
                            data.get("node") is None
                            and data.get("prompt_id") == prompt_id
                        ):
                            print(f"✅ Execution finished for prompt {prompt_id}")
                            execution_done = True
                            break
                    
                    elif message.get("type") == "execution_error":
                        data = message.get("data", {})
                        if data.get("prompt_id") == prompt_id:
                            error_details = f"Node Type: {data.get('node_type')}, Node ID: {data.get('node_id')}, Message: {data.get('exception_message')}"
                            print(f"❌ Execution error: {error_details}")
                            errors.append(f"Workflow execution error: {error_details}")
                            break
                
            except websocket.WebSocketTimeoutException:
                print(f"⏳ WebSocket timeout, still waiting...")
                continue
            except Exception as e:
                print(f"❌ WebSocket error: {e}")
                raise
        
        if not execution_done and not errors:
            raise ValueError("Workflow monitoring loop exited without confirmation of completion or error.")
        
        # Fetch results from history
        print(f"📚 Fetching history for prompt {prompt_id}...")
        history = get_history(prompt_id)
        
        if prompt_id not in history:
            error_msg = f"Prompt ID {prompt_id} not found in history after execution."
            print(f"❌ {error_msg}")
            if not errors:
                return {"error": error_msg}
            else:
                errors.append(error_msg)
                return {"error": "Job processing failed", "details": errors}
        
        # Process outputs
        prompt_history = history.get(prompt_id, {})
        outputs = prompt_history.get("outputs", {})
        
        if not outputs:
            warning_msg = f"No outputs found in history for prompt {prompt_id}."
            print(f"⚠️ {warning_msg}")
            if not errors:
                errors.append(warning_msg)
        
        print(f"🔄 Processing {len(outputs)} output nodes...")
        
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                print(f"🖼️ Node {node_id} contains {len(node_output['images'])} image(s)")
                
                for image_info in node_output["images"]:
                    filename = image_info.get("filename")
                    subfolder = image_info.get("subfolder", "")
                    img_type = image_info.get("type")
                    
                    # Skip temp images
                    if img_type == "temp":
                        print(f"⏭️ Skipping temp image {filename}")
                        continue
                    
                    if not filename:
                        warn_msg = f"Skipping image in node {node_id} due to missing filename"
                        print(f"⚠️ {warn_msg}")
                        errors.append(warn_msg)
                        continue
                    
                    image_bytes = get_image_data(filename, subfolder, img_type)
                    if image_bytes:
                        try:
                            base64_image = base64.b64encode(image_bytes).decode("utf-8")
                            output_data.append({
                                "filename": filename,
                                "type": "base64",
                                "data": base64_image,
                            })
                            print(f"✅ Encoded {filename} as base64")
                        except Exception as e:
                            error_msg = f"Error encoding {filename} to base64: {e}"
                            print(f"❌ {error_msg}")
                            errors.append(error_msg)
                    else:
                        error_msg = f"Failed to fetch image data for {filename}"
                        errors.append(error_msg)
    
    except Exception as e:
        print(f"❌ Handler error: {e}")
        return {"error": f"An error occurred: {e}"}
    
    finally:
        if ws:
            try:
                ws.close()
                print(f"🔌 WebSocket connection closed")
            except:
                pass
    
    # Prepare final result
    final_result = {}
    
    if errors:
        print(f"⚠️ Job completed with {len(errors)} error(s)")
        final_result["errors"] = errors
    
    if output_data:
        print(f"✅ Job completed successfully. Returning {len(output_data)} image(s)")
        final_result["images"] = output_data
    else:
        print(f"ℹ️ Job completed but produced no images")
        final_result["images"] = []
    
    return final_result

if __name__ == "__main__":
    print("🚀 Starting RunPod ComfyUI Handler...")
    runpod.serverless.start({"handler": handler})
