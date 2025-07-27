#!/bin/bash

# Local deployment script for testing
# Run this from the root directory: ./scripts/deploy-local.sh

set -e

echo "🏗️  Building frontend..."
cd frontend
npm run build

echo "📦 Deploying to GCS..."
# Replace 'your-bucket-name' with your actual bucket name
BUCKET_NAME=${1:-"webportal-frontend"}

if [ -z "$1" ]; then
  echo "Usage: ./scripts/deploy-local.sh <bucket-name>"
  echo "Example: ./scripts/deploy-local.sh my-webportal-bucket"
  exit 1
fi

# Upload files
gsutil -m rsync -r -d dist/ gs://$BUCKET_NAME/

# Set content types
echo "⚙️  Setting content types..."
gsutil -m setmeta -h "Content-Type:text/html" -h "Cache-Control:no-cache" gs://$BUCKET_NAME/index.html
gsutil -m setmeta -h "Content-Type:text/css" gs://$BUCKET_NAME/**/*.css 2>/dev/null || true
gsutil -m setmeta -h "Content-Type:application/javascript" gs://$BUCKET_NAME/**/*.js 2>/dev/null || true

echo "🚀 Deployment completed!"
echo "🌐 Website URL: https://storage.googleapis.com/$BUCKET_NAME/index.html"

cd ..