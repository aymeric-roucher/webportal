from pathlib import Path

WEBPORTAL_PATH = Path(__file__).parent
WEBPORTAL_REPO_PATH = WEBPORTAL_PATH.parent.parent
TEST_PATH = WEBPORTAL_REPO_PATH / "tests"
MOCK_REQUESTS_PATH = TEST_PATH / "mock"
DATA_PATH = WEBPORTAL_REPO_PATH / "data"
