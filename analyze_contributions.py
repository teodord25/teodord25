# NOTE: this is pretty scuffed so don't expect it to be 100% accurate

from datetime import datetime, timedelta
from typing import List
import requests
import os
import json
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator  # Added to handle y-axis ticks
import numpy as np
import pprint

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
    '.h': 'C/C++ Header',
}


URL_BASE = "https://api.github.com"
USER = "teodord25"
EMAIL = "djuric.teodor25@gmail.com"


def compute_lines(lines):
    added = sum(
        1 for line in lines
        if line.startswith('+') and not line.startswith('+++')
    )
    removed = sum(
        1 for line in lines
        if line.startswith('-') and not line.startswith('---')
    )

    lines_changed = added + removed

    return lines_changed


def parse_file(file) -> List[str]:
    filename = file["filename"]

    file_ext = os.path.splitext(filename)[1]

    if file_ext not in LANGUAGES or file_ext == ".md":  # ignore markdown files
        return []

    if 'patch' not in file:
        return []

    return file["patch"].split('\n')


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

                lines_changed = compute_lines(lines)

                week = start_date.strftime('%Y-%m-%d')

                if week not in summary:
                    summary[week] = [
                        {
                            "language": language,
                            "lines_changed": lines_changed
                        }
                    ]

                elif len(summary[week]) == 0:
                    summary[week].append(
                        {
                            "language": language,
                            "lines_changed": lines_changed
                        }
                    )
                elif language not in [commit["language"] for commit in summary[week]]:
                    summary[week].append(
                        {
                            "language": language,
                            "lines_changed": lines_changed
                        }
                    )
                else:
                    for commit in summary[week]:
                        if commit["language"] == language:
                            commit["lines_changed"] += lines_changed

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


def plot_stacked_bar_chart(data, y_limit=4000):
    all_languages = set()
    for week in data:
        for date, entries in week.items():
            for entry in entries:
                all_languages.add(entry['language'])

    dates = []
    curr_date = ""
    for week in data:
        if week == {}:
            dates.append((datetime.strptime(curr_date, '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d'))
        for date, entries in week.items():
            dates.append(date)
            curr_date = date

    weekly_summaries = {lang: [0] * len(dates) for lang in all_languages}

    for i, week in enumerate(data):
        for date, entries in week.items():
            if date not in dates:
                continue
            index = dates.index(date)
            for entry in entries:
                weekly_summaries[entry['language']][index] += entry['lines_changed']

    # plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = np.zeros(len(dates))

    total_lines_per_week = [sum(weekly_summaries[lang][i] for lang in all_languages) for i in range(len(dates))]

    # color map
    cmap = plt.get_cmap('tab20', len(all_languages))

    colors = cmap(range(len(all_languages)))

    language_colors = {lang: color for lang, color in zip(sorted(all_languages), colors)}

    for lang in all_languages:
        values = weekly_summaries[lang]
        bars = ax.bar(dates, values, bottom=bottom, label=lang, color=language_colors[lang])
        bottom += np.array(values)
        # annotate bars that go off the chart
        for i, (bar, total) in enumerate(zip(bars, total_lines_per_week)):
            if bar.get_height() + bar.get_y() > y_limit:
                ax.text(bar.get_x() + bar.get_width() / 2, y_limit - 50, f'{int(total)}', ha='center', va='top', color='white', fontsize=8, rotation=90)

    ax.set_ylim([0, y_limit])
    ax.set_xlabel('Weeks')
    ax.set_ylabel('Lines Changed')

    fig.suptitle('Weekly Lines Changed by Language', fontsize=16)
    plt.title('Overflowing bars represent integrating and updating legacy code', fontsize=10, pad=10)

    ax.legend(title='Languages', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()
    plt.savefig('weekly_lines_changed.png')


def update_data(data):
    summary = compute_summary_for_week(get_repos(), datetime.today() - timedelta(days=7))

    data.append(summary)  # add new week
    data.pop(0)  # remove oldest week

    save_data(data)


def main():
    data = load_data()

    update_data(data)

    plot_stacked_bar_chart(data)


if __name__ == "__main__":
    main()
