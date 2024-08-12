# NOTE: this is pretty scuffed so don't expect it to be 100% accurate

from datetime import datetime, timedelta
import requests
import os
import yaml
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


HEADERS = {
    'Authorization': f'token {os.getenv("GITHUB_TOKEN")}',
    'Accept': 'application/vnd.github+json'
}

LANGUAGES = {
}

COLORS = {
}


URL_BASE = "https://api.github.com"
USER = "teodord25"
EMAIL = "djuric.teodor25@gmail.com"


def get_repos():
    logging.info("Starting to fetch repositories...")
    repos = []
    page = 1
    while True:
        url = f"{URL_BASE}/user/repos?type=all&per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS).json()
        if not response:  # check if the page is empty
            logging.info(f"No more repos found at page {page}. Exiting...")
            break
        for repo in response:
            try:
                owner = repo["owner"]["login"]
            except Exception as e:
                logging.info(f"Error: {e}")
                logging.info(f"Response: {response}")
                exit(1)
            name = repo["name"]
            repos.append((owner, name))
        logging.info(f"Page {page}: {len(response)} repos found.")
        page += 1
    return repos


def plot_pie_chart(data):
    data = {k: v for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True)}
    labels = list(data.keys())
    sizes = list(data.values())
    colors = [COLORS.get(label, 'gray') for label in labels]

    explode = (0.1,) * len(data)

    fig, ax = plt.subplots()
    patches, texts, autotexts = ax.pie(sizes, autopct='%1.1f%%', colors=colors, explode=explode, shadow=True)

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize('10')
        autotext.set_fontweight('bold')

    ax.axis('equal')

    legend_labels = [f"{label} ({size})" for label, size in zip(labels, sizes)]

    ax.legend(patches, legend_labels, title="Languages", loc="center left", bbox_to_anchor=(1, 0.5), fontsize='12')
    last_week_num = int(datetime.today().strftime('%U')) - 1
    old_week_num = last_week_num - 1

    plt.title('Last week I used (commit distribution):', fontsize=14, fontweight='bold', color='white')
    plt.savefig(f'commit_distribution_week_{last_week_num}.png', bbox_inches='tight', transparent=True)
    plt.show()


def compute_summary(repos):
    summary = {}
    seven_days_ago = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
    logging.info(f"Computing summary for commits since {seven_days_ago}...")

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

        logging.info(f"Current summary: {summary}")

    logging.info("Summary of languages used: {summary}")
    return summary


def load_languages():
    with open("languages.yml", "r") as f:
        data = yaml.safe_load(f)

        for lang in data:
            extensions = data[lang].get("extensions")
            if extensions:
                for ext in extensions:
                    # duplicates are ignored because they are usually just
                    # variations of the same language
                    LANGUAGES[ext] = lang
                    if data[lang].get("color"):
                        COLORS[lang] = data[lang].get("color")


def main():
    try:
        load_languages()
        summary = compute_summary(get_repos())
        logging.info(f"Summary: {summary}")
        plot_pie_chart(summary)
    except Exception as e:
        logging.info(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
