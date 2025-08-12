
import os
import sys
import json

# Add the directory containing orchestrator.py to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import trigger_workflow

project_id = "carbon-broker-466711-d0"
location = "us-central1"
workflow_id = "longform-black-news-workflow" # Assuming this is the workflow ID

workflow_input = {
    "env": "production",
    "topic": "latest news",
    "scriptwriter_url": "https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/scriptwriter",
    "media_sourcing_url": "https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/media_sourcing",
    "narrator_url": "https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/narrator",
    "video_assembly_url": "https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/video_assembly",
    "uploader_url": "https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/uploader",
    "error_handler_url": "https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/workflow_logger", # Assuming workflow_logger handles errors
    "logger_url": "https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/workflow_logger"
}

try:
    print(f"Attempting to trigger workflow: {workflow_id} in project: {project_id}, location: {location}")
    print(f"With input: {json.dumps(workflow_input, indent=2)}")
    trigger_workflow(project_id, location, workflow_id, json.dumps(workflow_input))
    print("Workflow trigger initiated successfully.")
except Exception as e:
    print(f"Error triggering workflow: {e}")
