#!/bin/bash
set -euo pipefail

# Install envsubst if not present
if ! command -v envsubst &> /dev/null
then
    echo "envsubst not found, installing..."
    apt-get update && apt-get install -y --no-install-recommends gettext-base
fi

# If WF_SA is not set in the environment, default it.
# This block is now less critical as WF_SA is explicitly set in cloudbuild.yaml
# but kept for robustness if build.sh is run independently.
if [ -z "$WF_SA" ]; then
  WF_SA="workflow-service-account@$PROJECT_ID.iam.gserviceaccount.com"
fi

# Export all variables for envsubst to use.
export PROJECT_ID REGION ENVIRONMENT TZ WORKFLOW_NAME WF_SA SCRIPTWRITER_URL MEDIA_URL NARRATOR_URL ASSEMBLY_URL UPLOADER_URL

# Deploy the rendered workflow.
gcloud workflows deploy "$WORKFLOW_NAME" \
  --source="workflow.yaml" \
  --location="$REGION" \
  --project="$PROJECT_ID" \
  --service-account="$WF_SA"

echo "Workflow deployment submitted successfully."