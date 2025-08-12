"""Scriptwriter Cloud Function stub.

This function accepts a JSON payload with `topic`, `bucket` and `run_id` keys
and returns a simple text script.  The script is saved to the local
`outputs/` directory for inspection.  In a production environment you
would replace this logic with a call to Gemini or another LLM and upload
the script to Cloud Storage.
"""

import os
import json

try:
    # Flask is optional; the stubs can run without it for local testing
    from flask import Request
except ImportError:  # pragma: no cover
    Request = object  # type: ignore



def handle(request):  # type: ignore[override]
    """Entry point for the scriptwriter service.

    Args:
        request: Flask `Request` object containing JSON with the keys:
            - topic: the topic for the news video
            - bucket: name of the storage bucket (ignored in this stub)
            - run_id: unique identifier for this run

    Returns:
        JSON response with a `script_uri` pointing to the saved script file.
    """
    # Extract JSON from the request object.  This allows the handler to be
    # invoked either by Flask (via request.get_json) or directly with a
    # dictionary in local tests.
    if hasattr(request, "get_json"):
        data = request.get_json(silent=True) or {}
    elif isinstance(request, dict):
        data = request
    else:
        try:
            data = json.loads(request)  # type: ignore
        except Exception:
            return {"error": "Invalid JSON payload"}
    topic = data.get("topic", "black news")
    run_id = data.get("run_id", "test")

    # Compose a simple script.  In reality you'd call an LLM here.
    lines = [
        f"Welcome to our black news update on {topic}.",
        "We bring you the latest stories and updates impacting black communities worldwide.",
        "Stay tuned for more details and insights.",
    ]
    script_content = "\n".join(lines)

    # Ensure output directory exists
    os.makedirs("outputs", exist_ok=True)
    script_path = os.path.join("outputs", f"{run_id}_script.txt")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    return {"script_uri": script_path}