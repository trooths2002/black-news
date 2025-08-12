"""Top‑level package for micro‑service stubs.

This package contains individual modules for each stage of the video generation
pipeline.  Each module exposes a `handle` function that matches the Google
Cloud Functions HTTP signature (accepts a `flask.Request` and returns
a Flask response).  The services are intentionally simple for testing
purposes; replace the implementations with real logic when deploying
to production.
"""
