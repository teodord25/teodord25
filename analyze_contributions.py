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
        repo_names.append(repo["name"])
    page += 1

name = "teodord25"
print(f"Repo: {name}")
url = f"{url_base}/repos/{user}/{name}/commits"
response = requests.get(url, headers=HEADERS).json()
# if status not 200 skip
for commit in response:
    sha = commit["sha"]
    url = f"{url_base}/repos/{user}/{name}/commits/{sha}"
    response = requests.get(url, headers=HEADERS, allow_redirects=True).json()
    files = response["files"]
    for file in files:
        print("File: " + file["filename"])
        print("Diff: \n" + file["patch"])

    print("\n")
