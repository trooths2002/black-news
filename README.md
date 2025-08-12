# Black News Video Pipeline

This repository contains a **proof‑of‑concept** implementation of an automated video generation pipeline for a Black news channel.  The goal of the project is to demonstrate how a cloud‑native workflow can orchestrate multiple micro‑services to produce an end‑to‑end video from a topic.

## Overview

At a high level the pipeline consists of five stages:

1. **Scriptwriter:** Generates a short news script based on a user‑supplied topic.
2. **Media sourcing:** Creates or downloads images and video clips that accompany the script.
3. **Narrator:** Produces a narration audio file from the script.
4. **Video assembly:** Composes the sourced media and narration into a video file.
5. **Uploader:** Uploads the finished video to a permanent storage location.

In production each stage would run as an independent Google Cloud Function behind an authenticated HTTP endpoint and the overall process would be orchestrated by a [Cloud Workflow](https://cloud.google.com/workflows).  For demonstration purposes this repository provides **local stubs** for each service that can be exercised directly from a Python script.

## Repository Structure

```
.
├── functions/               # Individual micro‑service implementations (stubs)
│   ├── scriptwriter/
│   │   └── main.py          # Generates a simple text script
│   ├── media_sourcing/
│   │   └── main.py          # Creates placeholder images based on the script
│   ├── narrator/
│   │   └── main.py          # Produces a silent audio file (stub)
│   ├── video_assembly/
│   │   └── main.py          # Assembles images into an MP4 video
│   └── uploader/
│       └── main.py          # Stub uploader that acknowledges upload
├── orchestrator.py          # Orchestration script for Cloud Workflows
├── workflow.yaml            # Cloud Workflow definition
├── test_pipeline.py         # Local test harness to run the entire pipeline
├── requirements.txt         # Python dependencies for local testing and Cloud Functions
└── README.md                # This file
```

## Local Development

To verify that the pipeline works end‑to‑end without deploying to Google Cloud you can run the `test_pipeline.py` script.  This will sequentially invoke each micro‑service, generate a simple video in the `outputs/` folder and print the final JSON response.

```bash
python3 test_pipeline.py --topic "community empowerment" --run_id "demo"
```

After running the script you should find the following files in the `outputs/` directory:

* `<run_id>_script.txt` – the generated script.
* `<run_id>_media/` – a set of placeholder images created from the script.
* `<run_id>_narration.wav` – a silent audio file (as narration is stubbed).
* `<run_id>_final.mp4` – the assembled video, displaying each placeholder image for one second.

> **Note:** These services are intentionally simple.  They are meant to illustrate the plumbing of the workflow rather than provide production‑quality content.  Replace them with your actual implementations when integrating with Gemini, Google Cloud Transcoder, etc.

## Deployment to Google Cloud

The repository includes a [`workflow.yaml`](workflow.yaml) file and a [`build.sh`](build.sh) script (refer to the original repository) which can be used in a Cloud Build pipeline to deploy the workflow.  In a production setting you would:

1. Write each micro‑service in the `functions/` directory as a Cloud Function with the same request/response contract shown here.
2. Deploy the Cloud Functions and record their HTTPS endpoints.
3. Update the `cloudbuild.yaml` substitutions or environment variables so that the workflow knows where to call each function.
4. Run `gcloud builds submit --config cloudbuild.yaml` to deploy the workflow.
5. Trigger the workflow via `gcloud workflows execute` or on a schedule via Cloud Scheduler.

## Requirements

The top‑level `requirements.txt` includes all Python dependencies required for the stubs and the orchestrator.  The major libraries are:

* **opencv-python** – used in `video_assembly` to create an MP4 video from images.
* **Pillow** – used in `media_sourcing` to generate placeholder images.
* **google-cloud-workflows**, **google-api-core** – needed if you choose to run the orchestrator against a deployed workflow.

When deploying each Cloud Function individually you should include only the dependencies required by that service in its respective `requirements.txt`.

## Next Steps

This repository serves as a starting point.  To make it production‑ready you should:

1. **Implement real business logic** for scriptwriting (using Gemini or other LLMs), media sourcing (downloading relevant stock footage and images), narration (using text‑to‑speech), and video assembly (with the Google Transcoder API).
2. **Secure your services** with the appropriate IAM roles and service accounts, as detailed in `gemini.md` and `OPERATIONS.md`.
3. **Integrate monitoring and alerting** using Cloud Logging and Cloud Monitoring.

If you plan to push this repository to GitHub, simply initialise a new repository and commit all files under version control.  The complete context of the project is included in this directory; there are no hidden dependencies.