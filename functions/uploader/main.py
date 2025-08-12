"""Uploader Cloud Function stub.

In a full implementation this function would download the final video from
Cloud Storage and upload it to Google Drive or YouTube.  In this stub it
simply acknowledges the upload and echoes back the provided URIs.
"""

import json

try:
    from flask import Request  # type: ignore
except ImportError:  # pragma: no cover
    Request = object  # type: ignore


def handle(request):  # type: ignore[override]
    """Entry point for the uploader service.

    Args:
        request: Flask `Request` containing JSON with:
            - final_uri: Path to the video file produced by video assembly
            - script_content: Path to the script file
            - run_id: Unique identifier for this run

    Returns:
        JSON response indicating that the upload has completed.
    """
    # Parse input JSON
    if hasattr(request, "get_json"):
        data = request.get_json(silent=True) or {}
    elif isinstance(request, dict):
        data = request
    else:
        try:
            data = json.loads(request)  # type: ignore
        except Exception:
            return {"error": "Invalid JSON payload"}

    final_uri = data.get("final_uri")
    script_content = data.get("script_content")
    run_id = data.get("run_id")
    return {
        "status": "uploaded",
        "final_uri": final_uri,
        "script_content": script_content,
        "run_id": run_id,
    }