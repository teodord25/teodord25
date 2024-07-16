# NOTE: this is pretty scuffed so don't expect it to be 100% accurate

from datetime import datetime, timedelta
import requests
import os
import matplotlib.pyplot as plt

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
    '.tsx': 'TypeScript',
    '.ts': 'TypeScript',
    '.php': 'PHP',
    '.sh': 'Shell',
    '.lua': 'Lua',
}

COLORS = {
    'Rust': '#dea584',
    'Go': '#00ADD8',
    'Gleam': '#ffaff3',
    'HTML': '#e34c26',
    'CSS': '#563d7c',
    'Python': '#3572A5',
    'YAML': '#cb171e',
    'Kotlin': '#F88A02',
    'C++': '#00599C',
    'C': '#555555',
    'C#': '#178600',
    'JavaScript': '#f1e05a',
    'Java': '#b07219',
    'TypeScript': '#3178c6',
    'PHP': '#4F5D95',
    'Shell': '#89e051',
    'Lua': '#000080'
}


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


def plot_pie_chart(data):
    labels = data.keys()
    sizes = data.values()
    colors = plt.get_cmap('tab20')(range(len(data)))

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')

    plt.title('Commit Distribution by Programming Language')
    plt.show()
    plt.savefig('commit_distribution.png')


def compute_summary(repos):
    summary = {}
    seven_days_ago = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')

    for owner, name in repos:
        if name == ".github-private" or name == ".github":
            continue

        url = f"{URL_BASE}/repos/{owner}/{name}/commits?since={seven_days_ago}"
        response = requests.get(url, headers=HEADERS).json()

        if response == []:
            continue

        if isinstance(response, dict):
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
            response = requests.get(
                url, headers=HEADERS, allow_redirects=True
            ).json()
            files = response.get("files", [])

            languages_in_commit = set()

            for file in files:
                extension = os.path.splitext(file["filename"])[1]
                language = LANGUAGES.get(extension)

                if language:
                    languages_in_commit.add(language)

            for language in languages_in_commit:
                if language in summary:
                    summary[language] += 1
                else:
                    summary[language] = 1

    return summary


def main():
    summary = compute_summary(get_repos())
    plot_pie_chart(summary)


if __name__ == "__main__":
    main()
