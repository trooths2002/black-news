"""Media sourcing Cloud Function stub.

This function accepts a JSON payload with `script` (path to the script
file) and `gcs_bucket` (ignored in this stub).  It reads the script,
breaks it into sentences and generates a simple placeholder image for
each sentence.  The images are saved into an `outputs/<run_id>_media/`
folder and the function returns a list of file paths.

Pillow is used to render the text; no external images are downloaded.
"""

import os
import json
from typing import List
from PIL import Image, ImageDraw, ImageFont

try:
    from flask import Request  # type: ignore
except ImportError:  # pragma: no cover
    Request = object  # type: ignore


def _create_image(text: str, path: str) -> None:
    """Create a simple image with white text on a black background.

    Args:
        text: The text to display.
        path: Output file path.
    """
    width, height = 1280, 720
    img = Image.new("RGB", (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Use a basic Pillow built‑in font; this avoids external dependencies.
    font = ImageFont.load_default()

    # Wrap text if it's too long
    max_width = width - 100
    lines: List[str] = []
    words = text.split()
    current_line = ""
    for word in words:
        # Check if adding the next word would exceed the max width
        test_line = f"{current_line} {word}".strip()
        w, _ = draw.textsize(test_line, font=font)
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Calculate starting y position so text is vertically centred
    total_height = sum(draw.textsize(line, font=font)[1] + 10 for line in lines)
    y = (height - total_height) // 2
    for line in lines:
        w, h = draw.textsize(line, font=font)
        x = (width - w) // 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += h + 10

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def handle(request):  # type: ignore[override]
    """Entry point for the media sourcing service.

    Args:
        request: Flask `Request` containing JSON with:
            - script: Path to the script file produced by scriptwriter
            - gcs_bucket: Unused placeholder for Cloud Storage bucket

    Returns:
        JSON response with a list of `media_uris` pointing to generated images.
    """
    # Parse input JSON similar to scriptwriter
    if hasattr(request, "get_json"):
        data = request.get_json(silent=True) or {}
    elif isinstance(request, dict):
        data = request
    else:
        try:
            data = json.loads(request)  # type: ignore
        except Exception:
            return {"error": "Invalid JSON payload"}
    script_path = data.get("script")
    run_id = os.path.basename(script_path).split("_")[0] if script_path else "test"

    if not script_path or not os.path.exists(script_path):
        return {"error": "Script file not found"}

    # Read the script and split into sentences
    with open(script_path, "r", encoding="utf-8") as f:
        script_content = f.read()
    # Simple split on periods; more robust NLP could be used here
    sentences = [s.strip() for s in script_content.split(".") if s.strip()]

    output_dir = os.path.join("outputs", f"{run_id}_media")
    media_uris: List[str] = []
    for idx, sentence in enumerate(sentences, start=1):
        image_path = os.path.join(output_dir, f"frame_{idx}.png")
        _create_image(sentence, image_path)
        media_uris.append(image_path)

    return {"media_uris": media_uris}