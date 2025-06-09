# NOTE: this is pretty scuffed so don't expect it to be 100% accurate

from datetime import datetime, timedelta
import requests
import os
import yaml
import matplotlib.pyplot as plt
import logging
import textwrap
import pprint   # DEBUG pretty–print helpers

# -----------------------------------------------------------------------------
#  Debug configuration
# -----------------------------------------------------------------------------
DEBUG_MODE = os.getenv("DEBUG", "0") == "1"              # DEBUG
_log_level  = logging.DEBUG if DEBUG_MODE else logging.INFO   # DEBUG
logging.basicConfig(                                       # DEBUG
    level=_log_level,                                      # DEBUG
    format="%(asctime)s - %(levelname)s - %(message)s")    # DEBUG
logger = logging.getLogger(__name__)                       # DEBUG
# -----------------------------------------------------------------------------

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



# -----------------------------------------------------------------------------
#  Helper: decide whether a commit is mine
# -----------------------------------------------------------------------------
def is_mine(c):
    """Return True if commit `c` should be counted as yours."""
    # DEBUG capture as much author / committer info as possible
    author_login    = c.get("author",    {}).get("login")
    committer_login = c.get("committer", {}).get("login")
    raw_email       = c["commit"]["author"]["email"]

    login_ok    = USER in (author_login, committer_login)
    noreply_ok  = raw_email.endswith("users.noreply.github.com") and USER in raw_email
    explicit_ok = raw_email == EMAIL

    verdict = login_ok or noreply_ok or explicit_ok                 # final answer

    # DEBUG log *why* accepted / rejected
    logger.debug(
        "is_mine? %-5s | author=%s committer=%s email=%s",
        verdict, author_login, committer_login, raw_email
    )
    return verdict

# -----------------------------------------------------------------------------
#  Fetch all repos the token can see
# -----------------------------------------------------------------------------
def get_repos():
    logger.info("Fetching repositories …")
    repos, page = [], 1
    while True:
        url = f"{URL_BASE}/user/repos?type=all&per_page=100&page={page}"
        r   = requests.get(url, headers=HEADERS)
        # DEBUG: dump rate-limit info every page
        logger.debug("RateLimit remaining: %s", r.headers.get("X-RateLimit-Remaining"))
        response = r.json()

        if not response:                                            # empty page
            logger.info("Page %d empty – done.", page)
            break

        for repo in response:
            owner, name = repo["owner"]["login"], repo["name"]
            repos.append((owner, name))
        logger.info("Page %d: %d repos", page, len(response))
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
    plt.savefig(f'commit_distribution_week_{last_week_num:0>2}.png', bbox_inches='tight', transparent=True)
    plt.show()


# -----------------------------------------------------------------------------
#  Crunch commits
# -----------------------------------------------------------------------------
def compute_summary(repos):
    summary       = {}
    seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat(timespec="seconds") + "Z"
    logger.info("Analysing commits since %s …", seven_days_ago)

    for owner, name in repos:
        if name in {".github", ".github-private"}:
            continue

        # ask GitHub to filter by author on the server side – fewer bytes to parse
        params = dict(since=seven_days_ago, author=USER, per_page=100)      # DEBUG
        url    = f"{URL_BASE}/repos/{owner}/{name}/commits"
        commits = requests.get(url, headers=HEADERS, params=params).json()

        logger.debug("Repo %-30s → %3d candidate commits", f"{owner}/{name}", len(commits))  # DEBUG
        if not commits or isinstance(commits, dict):
            continue

        for c in commits:
            sha = c["sha"][:7]
            if not is_mine(c):
                logger.debug("• skip %s (not mine)", sha)
                continue

            # full commit (get added / deleted lines, list of files, etc.)
            full = requests.get(f"{url}/{sha}", headers=HEADERS).json()
            files = full.get("files", [])
            logger.debug("• keep %s – %d files", sha, len(files))

            languages_in_commit = set()
            for f in files:
                ext = os.path.splitext(f["filename"])[1]
                lang = LANGUAGES.get(ext)
                if not lang:
                    # DEBUG surface unmapped extensions once
                    if DEBUG_MODE and ext not in ("", None):
                        logger.debug("  └─ unmapped ext %s in %s", ext, f["filename"])
                    continue
                languages_in_commit.add(lang)

            if DEBUG_MODE:
                logger.debug("  └─ languages in commit: %s", languages_in_commit)

            for lang in languages_in_commit:
                summary[lang] = summary.get(lang, 0) + 1

    logger.info("Current summary: %s", summary)
    return summary

# -----------------------------------------------------------------------------
#  Load GitHub Linguist map
# -----------------------------------------------------------------------------
def load_languages():
    with open("languages.yml") as fh:
        data = yaml.safe_load(fh)

    for lang, spec in data.items():
        for ext in spec.get("extensions", []) or []:
            LANGUAGES[ext] = lang
        if spec.get("color"):
            COLORS[lang] = spec["color"]

    # DEBUG – sanity-check critical mappings
    for critical in (".rs", ".svg", ".wgsl"):
        logger.debug("LANG map %4s → %s", critical, LANGUAGES.get(critical))

# -----------------------------------------------------------------------------


def main():
    load_languages()
    summary = compute_summary(get_repos())
    plot_pie_chart(summary)


if __name__ == "__main__":
    main()
