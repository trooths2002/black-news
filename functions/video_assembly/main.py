"""Video assembly Cloud Function stub.

This function accepts a JSON payload with `media_uris` (a list of image
paths) and `narration_uri` (a WAV file).  It composes the images into
a simple MP4 video using OpenCV.  Each image is displayed for one second.

The output video is saved in the `outputs/` directory.  Audio is not
embedded in this stub; the resulting video is silent.
"""

import os
try:
    from flask import Request  # type: ignore
except ImportError:  # pragma: no cover
    Request = object  # type: ignore
import cv2  # type: ignore
import json


def handle(request):  # type: ignore[override]
    """Entry point for the video assembly service.

    Args:
        request: Flask `Request` containing JSON with:
            - media_uris: List of file paths to images
            - narration_uri: Path to a WAV file (ignored in this stub)
            - gcs_bucket: Placeholder for bucket name
            - project_id, region: Unused placeholders

    Returns:
        JSON response with an `output_uri` pointing to the generated MP4 file.
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

    media_uris = data.get("media_uris", [])
    # Derive run_id from first media URI
    run_id = "test"
    if media_uris:
        parts = media_uris[0].split(os.sep)
        if len(parts) >= 2:
            parent = parts[-2]
            run_id = parent.replace("_media", "")

    if not media_uris:
        return {"error": "No media URIs provided"}

    # Determine frame size from first image
    first_img = cv2.imread(media_uris[0])
    if first_img is None:
        return jsonify({"error": "Unable to read image file"}), 400
    height, width, _ = first_img.shape

    # Create video writer
    output_path = os.path.join("outputs", f"{run_id}_final.mp4")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = 1  # 1 frame per second; adjust as needed
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for uri in media_uris:
        img = cv2.imread(uri)
        if img is None:
            continue
        # Resize to match first image's dimensions if necessary
        if img.shape[0] != height or img.shape[1] != width:
            img = cv2.resize(img, (width, height))
        video_writer.write(img)

    video_writer.release()

    return {"output_uri": output_path}