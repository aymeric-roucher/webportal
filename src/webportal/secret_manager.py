import os
from typing import Optional

from google.cloud import secretmanager
from google.api_core.exceptions import NotFound, PermissionDenied
from functools import cache

def get_secret(secret_name: str, project_id: Optional[str] = None) -> Optional[str]:
    """
    Retrieve a secret from Google Secret Manager with fallback to environment variables.
    
    Args:
        secret_name: Name of the secret (e.g., 'OPENAI_API_KEY')
        project_id: Google Cloud project ID. If None, uses GOOGLE_CLOUD_PROJECT env var
        
    Returns:
        Secret value or None if not found
    """
    try:
        if project_id is None:
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            
        if not project_id:
            return os.getenv(secret_name)
            
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
        
    except (NotFound, PermissionDenied):
        return os.getenv(secret_name)

@cache
def get_openai_api_key() -> str:
    """Get OpenAI API key from Secret Manager or environment variables."""
    api_key = get_secret("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError("OPENAI_API_KEY is not set in Secret Manager or environment variables")
    return api_key


@cache
def get_huggingface_token() -> str:
    """Get Hugging Face token from Secret Manager or environment variables."""
    token = get_secret("HUGGINGFACE_API_KEY") or get_secret("HF_TOKEN")
    if token is None:
        raise ValueError("HUGGINGFACE_API_KEY or HF_TOKEN is not set in Secret Manager or environment variables")
    return token
