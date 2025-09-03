# Copy handler and startup script
COPY handler.py /handler.py
COPY test_input.json /test_input.json

# Make sure ComfyUI directory exists and set proper permissions
RUN mkdir -p /workspace/ComfyUI

# Set the entrypoint to start ComfyUI directly
CMD ["/bin/bash", "-c", "cd /workspace/ComfyUI && source venv/bin/activate && python main.py --port 3001"]
