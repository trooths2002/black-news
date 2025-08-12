call C:\Users\tjd20.LAPTOP-PCMC2SUO\Downloads\agv-pilot-posting\longform-black-news\venv\Scripts\activate.bat

set SCRIPTWRITER_URL=https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/scriptwriter
set MEDIA_SOURCING_URL=https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/media_sourcing
set NARRATOR_URL=https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/narrator
set ASSEMBLY_URL=https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/video_assembly
set UPLOADER_URL=https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/uploader
set ERROR_HANDLER_URL=https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/workflow_logger
set LOGGER_URL=https://us-central1-carbon-broker-466711-d0.cloudfunctions.net/workflow_logger

python C:\Users\tjd20.LAPTOP-PCMC2SUO\Downloads\agv-pilot-posting\longform-black-news\orchestrator.py --topic "latest news" --env production
