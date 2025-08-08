#!/bin/bash

# Configuration
PROJECT_ID="webportal-468213"
REGION="us-east1"
JOB_NAME="webportal-job"
IMAGE_NAME="webportal"
REGISTRY_PATH="us-east1-docker.pkg.dev/webportal-468213/webportal-registry"

# Function to build and push image
build_and_push() {
    echo "Building Docker image..."
    docker build -t $REGISTRY_PATH/$IMAGE_NAME:latest .
    
    echo "Pushing to Google Artifact Registry..."
    docker push $REGISTRY_PATH/$IMAGE_NAME:latest
}

# Function to create/update job
deploy_job() {
    local target_website=${1:-"clinicaltrials.gov"}
    
    echo "Deploying Cloud Run Job for website: $target_website"
    
    gcloud run jobs replace job.yaml \
        --region=$REGION \
        --project=$PROJECT_ID \
        --set-env-vars="TARGET_WEBSITE=$target_website"
}

# Function to execute job
execute_job() {
    local target_website=${1:-"clinicaltrials.gov"}
    local execution_name="${JOB_NAME}-$(date +%s)"
    
    echo "Executing job for website: $target_website"
    echo "Execution name: $execution_name"
    
    gcloud run jobs execute $JOB_NAME \
        --region=$REGION \
        --project=$PROJECT_ID \
        --wait
}

# Main execution
case "$1" in
    "build")
        build_and_push
        ;;
    "deploy")
        deploy_job "$2"
        ;;
    "execute")
        execute_job "$2"
        ;;
    "all")
        build_and_push
        deploy_job "$2"
        execute_job "$2"
        ;;
    *)
        echo "Usage: $0 {build|deploy|execute|all} [website_url]"
        echo "Examples:"
        echo "  $0 build"
        echo "  $0 deploy clinicaltrials.gov"
        echo "  $0 execute example.com"
        echo "  $0 all github.com"
        exit 1
        ;;
esac