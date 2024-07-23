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
    print("Starting to fetch repositories...", flush=True)
    repos = []
    page = 1
    while True:
        url = f"{URL_BASE}/user/repos?type=all&per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS).json()
        if not response:  # check if the page is empty
            print(f"No more repos found at page {page}. Exiting...", flush=True)
            break
        for repo in response:
            try:
                owner = repo["owner"]["login"]
            except Exception as e:
                print(f"Error: {e}")
                print(f"Response: {response}")
                exit(1)
            name = repo["name"]
            repos.append((owner, name))
        print(f"Page {page}: {len(response)} repos found.", flush=True)
        page += 1
    return repos


def plot_pie_chart(data):
    labels = list(data.keys())
    sizes = list(data.values())
    colors = [COLORS[lang] for lang in labels]

    explode = (0.1,) * len(data)

    fig, ax = plt.subplots()
    patches, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, explode=explode, shadow=True)

    for text in texts:
        text.set_color('white')
        text.set_fontsize('12')
        text.set_fontweight('bold')

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize('10')
        autotext.set_fontweight('bold')

    ax.axis('equal')

    plt.title('This week i used (commit distribution):', fontsize=14, fontweight='bold', color='white')
    plt.savefig('commit_distribution.png', bbox_inches='tight', transparent=True)


def compute_summary(repos):
    summary = {}
    seven_days_ago = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
    print(f"Computing summary for commits since {seven_days_ago}...", flush=True)

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

        print(f"Current summary after repo {name}: ", summary, flush=True)

    print("Summary of languages used:", summary, flush=True)
    return summary


def main():
    summary = compute_summary(get_repos())
    plot_pie_chart(summary)


if __name__ == "__main__":
    main()
