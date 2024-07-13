import requests
import os

HEADERS = {
    'Authorization': f'token {os.getenv("GITHUB_TOKEN")}',
    'Accept': 'application/vnd.github+json'
}

url_base = "https://api.github.com"
user = "teodord25"
repo_names = []

page = 1
while True:
    url = f"{url_base}/user/repos?type=all&per_page=100&page={page}"
    response = requests.get(url, headers=HEADERS).json()
    if not response:  # check if the page is empty
        break
    for repo in response:
        print(repo["name"])
        repo_names.append(repo["name"])
    page += 1

print(f"Repo names: {repo_names}")
