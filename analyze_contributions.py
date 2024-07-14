# NOTE: this is pretty scuffed so don't expect it to be 100% accurate

from datetime import datetime, timedelta
from typing import List
import requests
import os
import json

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
    '.cs': 'C#',
    '.js': 'JavaScript',
    '.java': 'Java',
}


def compute_commit(summary, language, lines):
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

    if 'patch' not in file:
        return []

    return file["patch"].split('\n')


URL_BASE = "https://api.github.com"
USER = "teodord25"
EMAIL = "djuric.teodor25@gmail.com"


def get_repos():
    repos = []
    page = 1
    while True:
        url = f"{URL_BASE}/user/repos?type=all&per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS).json()
        if not response:  # check if the page is empty
            break
        for repo in response:
            owner = repo["owner"]["login"]
            name = repo["name"]
            repos.append((owner, name))
        page += 1
    return repos


def compute_summary_for_week(repos, start_date):
    summary = {}
    formatted_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    for owner, name in repos:
        if name == ".github-private" or name == ".github":
            continue

        url = f"{URL_BASE}/repos/{owner}/{name}/commits?since={formatted_date}&until={start_date + timedelta(days=7)}"
        response = requests.get(url, headers=HEADERS).json()

        if isinstance(response, dict) and response.get("message") == "Not Found":
            continue

        for commit in response:
            if (
                commit is None or
                isinstance(commit, str) or
                commit["commit"]["author"]["email"] != EMAIL
            ):
                continue

            sha = commit["sha"]
            url = f"{URL_BASE}/repos/{owner}/{name}/commits/{sha}"
            response = requests.get(url, headers=HEADERS,
                                    allow_redirects=True).json()
            files = response["files"]
            for file in files:
                lines = parse_file(file)
                if not lines:
                    continue

                language = LANGUAGES.get(os.path.splitext(file["filename"])[1])

                compute_commit(summary, language, lines)

    return summary


def load_data():
    try:
        with open('weekly_data.json', 'r') as file:
            data = json.load(file)
            if len(data) != 52:
                raise Exception("Invalid data")
            return data
    except FileNotFoundError:
        return []


def save_data(data):
    # keep the latest 52 weeks
    if len(data) > 52:
        data = data[-52:]
    with open('weekly_data.json', 'w') as file:
        json.dump(data, file, indent=4)


def main():
    repos = get_repos()
    data = load_data()
    today = datetime.now()
    summary = compute_summary_for_week(repos, today - timedelta(days=7))

    data.pop(0)
    data.append(summary)

    save_data(data)

    return summary


if __name__ == "__main__":
    main()
