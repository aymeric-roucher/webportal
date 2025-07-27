# Deployment Setup Guide

## 1. Create GCP Service Account

In GCP Console:

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Name: `webportal-deploy`
4. Description: `Service account for GitHub Actions deployment`
5. Click **Create and Continue**

## 2. Grant Permissions

Add these roles to the service account:
- **Storage Object Admin** (to upload files to bucket)
- **Storage Admin** (to manage bucket settings)

## 3. Create Service Account Key

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON** format
5. Download the key file

## 4. Set GitHub Secrets

In your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:

```
GCP_SA_KEY: [Paste the entire contents of the JSON key file]
GCP_BUCKET_NAME: your-bucket-name-here
```

## 5. Create GCS Bucket

Either via console or CLI:

```bash
# Create bucket
gsutil mb gs://your-bucket-name

# Enable website hosting
gsutil web set -m index.html -e index.html gs://your-bucket-name

# Make bucket public
gsutil iam ch allUsers:objectViewer gs://your-bucket-name
```

## 6. Deploy!

Push to main branch or manually trigger the workflow:
- The pipeline will run on every push to `main` that changes `frontend/` files
- You can also manually trigger it from GitHub Actions tab

## 7. Access Your Site

Your site will be available at:
`https://storage.googleapis.com/your-bucket-name/index.html`

## Optional: Custom Domain

To use a custom domain:
1. In GCS bucket settings, add your domain to **Website configuration**
2. Create CNAME record: `CNAME www.yourdomain.com storage.googleapis.com`
3. Verify domain ownership in Google Search Console