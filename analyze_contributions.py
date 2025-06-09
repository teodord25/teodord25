# commit_pie.py ────────────────────────────────────────────────────────────────
from datetime import datetime, timedelta
import os, requests, yaml, logging, pprint
import matplotlib.pyplot as plt

# ── Logging: force DEBUG for everything ───────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,                                   # <- hard-wired DEBUG
    format="%(asctime)s  %(levelname)-7s  %(message)s")
log = logging.getLogger(__name__)

# ── GitHub constants ──────────────────────────────────────────────────────────
URL_BASE = "https://api.github.com"
TOKEN    = os.getenv("GITHUB_TOKEN")                # *must* be set in workflow
USER     = "teodord25"
EMAIL    = "djuric.teodor25@gmail.com"

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept":        "application/vnd.github+json",
}

# ── Linguist map (populated by load_languages) ────────────────────────────────
LANGUAGES, COLORS = {}, {}

# If you work in more orgs, add them here or via ORG_LIST env (comma-separated)
ORG_SLUGS = (os.getenv("ORG_LIST") or "yus-works").split(",")

# ──────────────────────────────────────────────────────────────────────────────
def load_languages():
    with open("languages.yml") as fh:
        data = yaml.safe_load(fh)

    for lang, spec in data.items():
        for ext in spec.get("extensions") or []:
            if ext not in LANGUAGES:                   # first win (Rust > RS)
                LANGUAGES[ext] = lang
        if color := spec.get("color"):
            COLORS[lang] = color

    for ext in (".rs", ".wgsl", ".svg"):
        log.debug("LANG map %s → %s", ext, LANGUAGES.get(ext))

# ──────────────────────────────────────────────────────────────────────────────
def is_mine(c):
    author_login    = c.get("author",    {}).get("login")
    committer_login = c.get("committer", {}).get("login")
    raw_email       = c["commit"]["author"]["email"]

    verdict = (
        USER in (author_login, committer_login)
        or raw_email == EMAIL
        or raw_email.endswith("users.noreply.github.com") and USER in raw_email
    )
    log.debug(
        "is_mine? %-5s | author=%s  committer=%s  email=%s",
        verdict, author_login, committer_login, raw_email
    )
    return verdict

# ──────────────────────────────────────────────────────────────────────────────
def fetch(url, **kw):
    r = requests.get(url, headers=HEADERS, **kw)
    log.debug("GET %s → %s  RL=%s",
              url, r.status_code, r.headers.get("X-RateLimit-Remaining"))
    return r.json()

# ──────────────────────────────────────────────────────────────────────────────
def get_repos():
    repos = []

    # 1. Personal & member repos
    page = 1
    while True:
        lst = fetch(f"{URL_BASE}/user/repos?affiliation=owner,collaborator,organization_member"
                    f"&per_page=100&page={page}")
        if not lst:
            break
        repos += [(r["owner"]["login"], r["name"]) for r in lst]
        page  += 1

    # 2. Explicit orgs
    for org in ORG_SLUGS:
        page = 1
        while True:
            lst = fetch(f"{URL_BASE}/orgs/{org}/repos?per_page=100&page={page}")
            if not lst:
                break
            repos += [(r["owner"]["login"], r["name"]) for r in lst]
            page  += 1

    log.info("Total repos to scan: %d", len(repos))
    return repos

# ──────────────────────────────────────────────────────────────────────────────
def compute_summary(repos):
    since = (datetime.utcnow() - timedelta(days=7)).isoformat(timespec="seconds") + "Z"
    log.info("Scanning commits since %s", since)

    summary = {}
    for owner, name in repos:
        if name in {".github", ".github-private"}:
            continue

        commits = fetch(f"{URL_BASE}/repos/{owner}/{name}/commits",
                        params={"since": since, "per_page": 100})

        if not isinstance(commits, list):
            continue
        log.debug("%s/%s → %3d commits", owner, name, len(commits))

        for c in commits:
            if not is_mine(c):
                continue

            sha   = c["sha"]
            full  = fetch(f"{URL_BASE}/repos/{owner}/{name}/commits/{sha}")
            files = full.get("files", [])

            langs = set()
            for f in files:
                ext  = os.path.splitext(f["filename"])[1]
                lang = LANGUAGES.get(ext)
                if lang:
                    langs.add(lang)
                    if ext == ".rs":
                        log.debug("Rust file %s in %s…", f["filename"], sha[:7])

            for lang in langs:
                summary[lang] = summary.get(lang, 0) + 1

    log.info("FINAL SUMMARY: %s", summary)
    return summary

# ──────────────────────────────────────────────────────────────────────────────
def plot_pie_chart(data):
    if not data:
        log.warning("No data to plot – exiting.")
        return

    data   = dict(sorted(data.items(), key=lambda kv: kv[1], reverse=True))
    labels = list(data); sizes = list(data.values())
    colors = [COLORS.get(l, "gray") for l in labels]

    explode = [0.1 if i < 3 else 0 for i in range(len(labels))]
    fig, ax = plt.subplots()
    wedges, _, autot = ax.pie(sizes, colors=colors, explode=explode,
                              autopct="%1.1f%%", shadow=True)

    for autotext in autot:
        autotext.set_color('white')
        autotext.set_fontsize('10')
        autotext.set_fontweight('bold')

    ax.axis("equal")
    ax.legend(wedges, [f"{l} ({v})" for l, v in data.items()],
              title="Languages", loc="center left", bbox_to_anchor=(1, .5))

    ax.set_title("Last week commit distribution", fontweight="bold")
    plt.show()

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not TOKEN:
        log.error("GITHUB_TOKEN env var missing!  Workflow must export it.")
        exit(1)

    load_languages()
    summary = compute_summary(get_repos())
    plot_pie_chart(summary)
