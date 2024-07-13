import requests
import os

HEADERS = {
    'Authorization': f'token {os.getenv("GITHUB_TOKEN")}',
    'Accept': 'application/vnd.github+json'
}

LANGUAGES = {
    '.rs': 'Rust',
    '.go': 'Go',
    '.gleam': 'Gleam',
    '.html': 'HTML',
    '.css': 'CSS',
    '.py': 'Python',
    '.yml': 'YAML',
    '.yaml': 'YAML',
    '.kts': 'Kotlin',
    '.kt': 'Kotlin',
    '.cpp': 'C++',
    '.c': 'C',
    '.js': 'JavaScript',
    '.java': 'Java',
}

summary = {
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
url = f"{url_base}/repos/{user}/{name}/commits"
response = requests.get(url, headers=HEADERS).json()
# if status not 200 skip
for commit in response:
    sha = commit["sha"]
    url = f"{url_base}/repos/{user}/{name}/commits/{sha}"
    response = requests.get(url, headers=HEADERS, allow_redirects=True).json()
    files = response["files"]
    for file in files:
        filename = file["filename"]

        file_ext = os.path.splitext(filename)[1]

        if file_ext not in LANGUAGES or file_ext == ".md":  # ignore markdown files
            continue

        language = LANGUAGES[file_ext]

        patch = file["patch"]

        added = sum(1 for line in patch.split('\n') if line.startswith('+') and not line.startswith('+++'))
        removed = sum(1 for line in patch.split('\n') if line.startswith('-') and not line.startswith('---'))

        lines_changed = added + removed
        if language not in summary:
            summary[language] = {
                "lines_changed": lines_changed,
            }
        else:
            summary[language]["lines_changed"] += lines_changed

print(summary)
