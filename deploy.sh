#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Load configuration
if [ -f config.env ]; then
    source config.env
else
    echo "config.env not found! Please create it based on the template."
    exit 1
fi

echo "Using Project: $PROJECT_ID"
echo "Using Region: $REGION"

# 1. Build Docker image using Cloud Build
echo "Building Docker image with Cloud Build..."
IMAGE_URI="gcr.io/$PROJECT_ID/face-matching-backend"
gcloud builds submit --tag $IMAGE_URI ./backend --project=$PROJECT_ID

# 2. Initialize and Apply Terraform
echo "Applying Terraform configuration..."
cd terraform
terraform init

terraform apply \
  -var="project_id=$PROJECT_ID" \
  -var="region=$REGION" \
  -var="db_password=$DB_PASSWORD" \
  -var="image_uri=$IMAGE_URI" \
  -var="model_location=$MODEL_LOCATION" \
  -auto-approve

# 3. Get Cloud Run URL
echo "Retrieving Cloud Run URL..."
CLOUD_RUN_URL=$(terraform output -raw cloud_run_url)
echo "Cloud Run URL: $CLOUD_RUN_URL"

# 4. Update Frontend Script
echo "Updating frontend/script.js with Cloud Run URL..."
cd ..
SED_CMD="s|const API_URL = 'http://localhost:8000';|const API_URL = '$CLOUD_RUN_URL';|g"
# Use sed to replace the URL in script.js
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "$SED_CMD" frontend/script.js
else
  sed -i "$SED_CMD" frontend/script.js
fi

echo "Deployment complete! You can now open frontend/index.html in your browser."
