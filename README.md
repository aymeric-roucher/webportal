# Webportal

Make your website agent-accessible.

## Workflow

1. **Manual navigation on a website** - Browse the website manually to explore it and cover as much as possible / desired 
2. **Extract HAR file** - Manually extract the HAR file containing all API calls (in Google Chrome)
3. **Process HAR file** - Use `har_extractor.py` to convert the HAR file into a JSON file of existing APIs
4. **Convert to tools** - Use `json_to_tools.py` to convert the JSON file into a list of smolagents tools (Python functions with docstrings and `@tool` decorator)
5. **Agent interaction** - Use `agent.py` to answer questions or do work on the considered website by manually editing the "task" prompt at the end of the file

## Running

All data is stored in a bucket shared by all of the instances of the webportal crawlers.

To enable this feature, one must set the BUCKET_WEBPORTAL environment variable, otherwise the data is stored in the data directory.

Building the container:
```bash
docker build --platform linux/amd64 -t webportal-selenium . 
```

Running the container (sharing the src folder allows to instantly propagate changes to the docker):
```bash
docker run -it --rm --platform linux/amd64 --ulimit nofile=32768 \
    -e OPENAI_API_KEY=$OPENAI_API_KEY \
    -e HF_TOKEN=$HUGGINGFACE_API_KEY \
    -e BUCKET_WEBPORTAL=$BUCKET_WEBPORTAL \
    -e BUCKET_ENV_VAR=$BUCKET_ENV_VAR \
    -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/key.json \
    -e GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
    -v ~/.config/gcloud/application_default_credentials.json:/tmp/keys/key.json \
    webportal-selenium /bin/bash
```

**Note**: Container auto-removes after exit (`--rm`). Selenium Grid starts automatically for multiprocessing support.

## Gcloud configuration:

1. The docker should use a service account with only write access to the bucket, beware, compared to AWS, this is done directly in the UI from the bucket settings.
1. The user account must have permissions to give tokens for local debugging:
```bash
gcloud iam service-accounts add-iam-policy-binding \                  
    project-name@service-account.iam.gserviceaccount.com \ # <- Must be the service account used by the docker
    --member="user:email@gmail.com" \ # <- Must be the email of the user
    --role="roles/iam.serviceAccountTokenCreator"
```


### Testing Multiprocessing

```bash
docker run --rm --platform linux/amd64 --ulimit nofile=32768 \
    -v "$(pwd)/test_grid_multiprocessing.py:/app/test_grid_multiprocessing.py" \
    webportal-selenium \
    /bin/bash -c "/opt/bin/start-selenium-standalone.sh & sleep 5 && uv run python test_grid_multiprocessing.py"
```

# Aymeric to Charles

### Which sites to scrape first

The 5 Most Frequent Domains:
nas.er.usgs.gov - 3 questions
wikipedia.org - 3 questions
arxiv.org - 2 questions
nature.com - 2 questions
metmuseum.org - 2 questions

9 out of 27 questions (33.3%) can be completely solved using only these top 5 domains.

### I've repaired selenium

Multiprocessing is a bad idea with selenium.

In this PR https://github.com/aymeric-roucher/webportal/pull/21 I fix selenium and remove multiprocessing.

```markdown
What has been done here:
- remove multiprocessing with selenium, 
- fix dockerfile to add src on the last layer to avoid storage issues

What remains to be done;
- a docker (or the backend honestly) crawls all of the links of a website
- dockers spawn and find the urls using selenium
- in the end (docker or backend), a markdown is stored on a bucket 
```