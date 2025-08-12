import os, json
from flask import Request, jsonify
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.cloud import storage

def upload_to_google_drive(video_uri: str, script_content: str, run_id: str):
    logging.info(f"Uploading {video_uri} to Google Drive...")
    
    # Authenticate with service account
    # The service account key should be stored securely, e.g., in Google Secret Manager
    # For this example, we assume the service account has access to Google Drive
    # and the necessary scopes are granted.
    # Replace 'path/to/your/service_account_key.json' with the actual path or method to access the key
    # For Cloud Functions, you might use the default service account or fetch from Secret Manager.
    
    # For simplicity, assuming the Cloud Function's default service account has Drive access
    # and the 'drive' scope is enabled for the function.
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = service_account.DefaultCredentials(scopes=SCOPES)
    
    drive_service = build('drive', 'v3', credentials=creds)

    # Download video from GCS
    storage_client = storage.Client()
    bucket_name = video_uri.split('/')[2]
    blob_name = '/'.join(video_uri.split('/')[3:])
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    video_content = blob.download_as_bytes()
    
    # Create file metadata
    file_metadata = {
        'name': f'longform_black_news_{run_id}.mp4',
        'mimeType': 'video/mp4'
    }
    
    # Upload to Google Drive
    media = MediaFileUpload(
        io.BytesIO(video_content),
        mimetype='video/mp4',
        resumable=True
    )
    
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    logging.info(f"Video uploaded to Google Drive with ID: {file.get('id')}")
    return file.get('id')

def handle(request: Request):
    data = request.get_json()
    final_uri = data["final_uri"]
    script_content = data["script_content"]
    run_id = data["run_id"]

    # Upload to Google Drive
    google_drive_file_id = upload_to_google_drive(final_uri, script_content, run_id)

    return jsonify({"status": "uploaded", "final_uri": final_uri, "google_drive_file_id": google_drive_file_id})

    # TODO: Download from GCS final_uri and upload to Google Drive (final destination)
    # This requires Google Drive API integration and authentication (e.g., using google-api-python-client with a service account).
    return jsonify({"status": "uploaded", "final_uri": final_uri, "youtube_video_id": youtube_video_id})
