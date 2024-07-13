from datetime import datetime, timedelta
from typing import List
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


def compute_summary(summary, language, lines):
    added = sum(
        1 for line in lines
        if line.startswith('+') and not line.startswith('+++')
    )
    removed = sum(
        1 for line in lines
        if line.startswith('-') and not line.startswith('---')
    )

    lines_changed = added + removed

    if language not in summary:
        summary[language] = {
            "lines_changed": lines_changed,
        }
    else:
        summary[language]["lines_changed"] += lines_changed


def parse_file(file) -> List[str]:
    filename = file["filename"]

    file_ext = os.path.splitext(filename)[1]

    if file_ext not in LANGUAGES or file_ext == ".md":  # ignore markdown files
        return []

    return file["patch"].split('\n')


SEVEN_DAYS_AGO = (datetime.now() - timedelta(days=7)
                  ).strftime('%Y-%m-%dT%H:%M:%SZ')

URL_BASE = "https://api.github.com"
USER = "teodord25"
EMAIL = "djuric.teodor25@gmail.com"


def main():
    summary = {}
    repo_names = []

    page = 1
    while True:
        url = f"{URL_BASE}/user/repos?type=all&per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS).json()
        if not response:  # check if the page is empty
            break
        for repo in response:
            repo_names.append(repo["name"])
        page += 1

    for repo_name in repo_names:
        if repo_name == ".github-private" or repo_name == ".github":
            continue

        url = f"{URL_BASE}/repos/{USER}/{repo_name}/commits?since={SEVEN_DAYS_AGO}"
        response = requests.get(url, headers=HEADERS).json()

        if isinstance(response, dict) and response.get("message") == "Not Found":
            print(f"Skipping {repo_name}")
            continue

        for commit in response:
            if (
                commit is None or
                isinstance(commit, str) or
                commit["commit"]["author"]["email"] != EMAIL
            ):
                continue

            sha = commit["sha"]
            url = f"{URL_BASE}/repos/{USER}/{repo_name}/commits/{sha}"
            response = requests.get(url, headers=HEADERS,
                                    allow_redirects=True).json()
            files = response["files"]
            for file in files:
                lines = parse_file(file)
                if not lines:
                    continue

                language = LANGUAGES.get(os.path.splitext(file["filename"])[1])

                compute_summary(summary, language, lines)

    print(summary)


if __name__ == "__main__":
    main()
