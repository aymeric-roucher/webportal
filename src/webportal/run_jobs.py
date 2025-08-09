import subprocess
from datetime import datetime
import os
from webportal.ingest import get_domain_name

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = "us-east1"
CRAWLER_IMAGE = os.getenv("CRAWLER_IMAGE")
BUCKET_WEBPORTAL = os.getenv("BUCKET_WEBPORTAL")
print(CRAWLER_IMAGE)
def launch_crawl(url: str):
    domain_name = get_domain_name(url).replace(".", "-").lower()
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    job_name = f"webportal-crawl-{domain_name}-{timestamp}"
    
    # Create the job first
    create_cmd = [
        "gcloud", "run", "jobs", "create", job_name,
        f"--image={CRAWLER_IMAGE}:latest",
        f"--project={PROJECT}",
        f"--region={REGION}",
        "--task-timeout=1800",
        "--max-retries=0",
        "--parallelism=1",
        "--tasks=1",
        f"--set-env-vars=BUCKET_WEBPORTAL={BUCKET_WEBPORTAL},GOOGLE_CLOUD_PROJECT={PROJECT},TARGET_WEBSITE={url},JOB_ID={timestamp}",
        "--set-secrets=HUGGINGFACE_API_KEY=HUGGINGFACE_API_KEY:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest",
        "--memory=2Gi"
    ]
    
    print(f"Creating crawl job: {job_name}")
    print(f"Command: {' '.join(create_cmd)}")
    
    create_result = subprocess.run(create_cmd, capture_output=True, text=True)
    
    if create_result.returncode != 0:
        print("Job creation failed!")
        print(create_result.stderr)
        raise RuntimeError(f"gcloud create command failed with return code {create_result.returncode}")
    
    print("Job created successfully!")
    print(create_result.stdout)
    
    # Now execute the job
    execute_cmd = [
        "gcloud", "run", "jobs", "execute", job_name,
        f"--project={PROJECT}",
        f"--region={REGION}",
        "--wait"
    ]
    
    print(f"Executing job: {job_name}")
    print(f"Command: {' '.join(execute_cmd)}")
    
    execute_result = subprocess.run(execute_cmd, capture_output=True, text=True)
    
    if execute_result.returncode == 0:
        print("Job executed successfully!")
        print(execute_result.stdout)
    else:
        print("Job execution failed!")
        print(execute_result.stderr)
        raise RuntimeError(f"gcloud execute command failed with return code {execute_result.returncode}")

if __name__ == "__main__":
    launch_crawl("https://clinicaltrials.gov")