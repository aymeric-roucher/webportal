# Manual Debugging Commands for GCP Container Jobs

## Prerequisites
```bash
# Install gcloud CLI and authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```


## 2. Build and Push to GCP
```bash
# Build with local tag first
docker build --platform linux/amd64 -t webportal-selenium:latest .

# Tag for Artifact Registry
docker tag webportal-selenium:latest us-east1-docker.pkg.dev/webportal-468213/webportal-registry/webportal:latest

# Push to Artifact Registry
docker push us-east1-docker.pkg.dev/webportal-468213/webportal-registry/webportal:latest
```

## 3. Deploy Cloud Run Job
```bash
# Deploy the job (job.yaml already configured)
gcloud run jobs replace job.yaml \
    --region=us-east1 \
    --set-env-vars="TARGET_WEBSITE=clinicaltrials.gov"
```

## 4. Execute Job Manually
```bash
# Execute job and wait for completion
gcloud run jobs execute webportal-job \
    --region=us-east1 \
    --wait

# Execute with different website
gcloud run jobs execute webportal-job \
    --region=us-east1 \
    --set-env-vars="TARGET_WEBSITE=example.com" \
    --wait
```

## 5. Monitor and Debug
```bash
# List job executions
gcloud run jobs executions list --job=webportal-job --region=us-east1

# Get logs from latest execution
gcloud run jobs executions describe EXECUTION_NAME \
    --region=us-east1

# Stream logs in real-time
gcloud logging tail "resource.type=cloud_run_job AND resource.labels.job_name=webportal-job"
```

## 6. Quick Commands Using Script
```bash
# Use the deploy-job.sh script (update PROJECT_ID in script first)
./deploy-job.sh build
./deploy-job.sh deploy clinicaltrials.gov
./deploy-job.sh execute
./deploy-job.sh all github.com  # Build, deploy, and execute in one command
```