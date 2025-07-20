import requests
import dotenv
import os

dotenv.load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# The GraphQL query
query = """
query($username: String!) {
  user(login: $username) {
    name
    repositories(first: 5, orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        name
        url
        isPrivate
      }
    }
  }
}
"""

# Query variables
variables = {
    "username": "adrienX18"  # Change this to any GitHub username
}

# Send the POST request
response = requests.post(
    url="https://api.github.com/graphql",
    json={"query": query, "variables": variables},
    headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
)

# Print results
if response.status_code == 200:
    data = response.json()
    print("Repositories:")
    for repo in data["data"]["user"]["repositories"]["nodes"]:
        print(f"🔗 {repo['name']}: {repo['url']} (Private: {repo['isPrivate']})")
else:
    print(f"Query failed with status code {response.status_code}")
    print(response.text)
