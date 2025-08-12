"""Local test harness for the Black News video pipeline.

This script imports the stubbed Cloud Function handlers from the
`functions` package and calls them sequentially to simulate the
workflow defined in `workflow.yaml`.  It does not require Google
Cloud – all files are generated in the local `outputs/` directory.

Usage:

```bash
python3 test_pipeline.py --topic "community empowerment" --run_id "demo"
```
"""

import argparse
import json
import os

# Import the micro‑service handlers
from functions.scriptwriter.main import handle as scriptwriter_handle
from functions.media_sourcing.main import handle as media_sourcing_handle
from functions.narrator.main import handle as narrator_handle
from functions.video_assembly.main import handle as video_assembly_handle
from functions.uploader.main import handle as uploader_handle


class DummyRequest:
    """A simple stand‑in for Flask's Request to call Cloud Functions locally."""

    def __init__(self, json_body: dict):
        self._json = json_body

    def get_json(self, silent: bool = False):
        return self._json


def _parse_response(response):
    """Extract JSON data from a response.

    If the handler returns a Flask response object, use `get_data` to
    extract the body and parse as JSON.  If it returns a plain dict
    (our stubs), return it directly.
    """
    if hasattr(response, "get_data"):
        return json.loads(response.get_data(as_text=True))
    return response


def main(topic: str, run_id: str) -> None:
    # Step 1: Scriptwriter
    script_request = DummyRequest({"topic": topic, "bucket": "local", "run_id": run_id})
    script_response = scriptwriter_handle(script_request)
    script_data = _parse_response(script_response)
    script_uri = script_data["script_uri"]
    print(f"Script generated at: {script_uri}")

    # Step 2: Media sourcing
    media_request = DummyRequest({"script": script_uri, "gcs_bucket": "local"})
    media_response = media_sourcing_handle(media_request)
    media_data = _parse_response(media_response)
    media_uris = media_data.get("media_uris", [])
    print(f"Generated {len(media_uris)} media files: {media_uris}")

    # Step 3: Narration
    narrator_request = DummyRequest({"script_content": script_uri, "gcs_bucket": "local", "run_id": run_id})
    narrator_response = narrator_handle(narrator_request)
    narrator_data = _parse_response(narrator_response)
    audio_uri = narrator_data["audio_uri"]
    print(f"Narration audio generated at: {audio_uri}")

    # Step 4: Video assembly
    assembly_request = DummyRequest({
        "media_uris": media_uris,
        "narration_uri": audio_uri,
        "gcs_bucket": "local",
        "project_id": "local",
        "region": "local",
    })
    assembly_response = video_assembly_handle(assembly_request)
    assembly_data = _parse_response(assembly_response)
    final_uri = assembly_data["output_uri"]
    print(f"Video assembled at: {final_uri}")

    # Step 5: Upload
    uploader_request = DummyRequest({
        "final_uri": final_uri,
        "script_content": script_uri,
        "run_id": run_id,
    })
    uploader_response = uploader_handle(uploader_request)
    uploader_data = _parse_response(uploader_response)
    print(f"Upload response: {uploader_data}")

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the black news pipeline locally.")
    parser.add_argument("--topic", required=True, help="Topic for the news script")
    parser.add_argument("--run_id", default="test", help="Unique identifier for this run")
    args = parser.parse_args()
    main(args.topic, args.run_id)