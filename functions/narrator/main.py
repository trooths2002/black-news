"""Narrator Cloud Function stub.

This function accepts a JSON payload with `script_content` (path to the script
file), `gcs_bucket` (unused) and `run_id`.  It creates a silent WAV file
representing the narration.  In a real implementation you would invoke a
text‑to‑speech API to synthesise speech.
"""

import os
import json
import struct
import wave
try:
    from flask import Request  # type: ignore
except ImportError:  # pragma: no cover
    Request = object  # type: ignore


def _create_silent_wav(path: str, duration_sec: int = 6, sample_rate: int = 44100) -> None:
    """Generate a silent WAV file.

    Args:
        path: Output file path.
        duration_sec: Length of the audio in seconds.
        sample_rate: Samples per second.
    """
    n_samples = duration_sec * sample_rate
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "w") as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16 bits per sample
        wav_file.setframerate(sample_rate)
        # Write silence
        silence = (0).to_bytes(2, byteorder="little", signed=True)
        for _ in range(n_samples):
            wav_file.writeframesraw(silence)
        wav_file.writeframes(b"")


def handle(request):  # type: ignore[override]
    """Entry point for the narrator service.

    Args:
        request: Flask `Request` containing JSON with:
            - script_content: Path to the script file (ignored in this stub)
            - gcs_bucket: Placeholder for bucket name
            - run_id: Unique identifier for this run

    Returns:
        JSON response with an `audio_uri` pointing to the generated WAV file.
    """
    if hasattr(request, "get_json"):
        data = request.get_json(silent=True) or {}
    elif isinstance(request, dict):
        data = request
    else:
        try:
            data = json.loads(request)  # type: ignore
        except Exception:
            return {"error": "Invalid JSON payload"}
    run_id = data.get("run_id", "test")

    audio_path = os.path.join("outputs", f"{run_id}_narration.wav")
    _create_silent_wav(audio_path)
    return {"audio_uri": audio_path}