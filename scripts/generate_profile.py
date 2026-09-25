import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

USER = "Joyal01-01"
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN", "")

def get(path):
    request = urllib.request.Request(
        API + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Joyal01-01-profile-generator",
        },
    )
    if TOKEN:
        request.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def get_repositories():
    repositories = []
    for page in range(1, 11):
        data = get(f"/users/{USER}/repos?per_page=100&page={page}&sort=updated")
        if not isinstance(data, list):
            return repositories if repositories else None
        repositories.extend(data)
        if len(data) < 100:
            break
    return repositories


def value_or_unavailable(value):
    return value if value not in (None, "") else "Data unavailable"

def write_svg(name, title, lines, width=900, height=260):
    body = [
        '<rect width="100%" height="100%" rx="18" fill="#0d1117" stroke="#30363d"/>',
        f'<text x="30" y="45" fill="#58a6ff" font-family="Arial,sans-serif" font-size="25" font-weight="700">{escape(title)}</text>',
    ]
    y = 90
    for text, color, size in lines:
        body.append(f'<text x="30" y="{y}" fill="{color}" font-family="Arial,sans-serif" font-size="{size}">{escape(str(text))}</text>')
        y += 42
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">' + ''.join(body) + '</svg>'
    (ASSETS / name).write_text(svg, encoding="utf-8")


def write_decorative_svg(name, color):
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="80" '
        'viewBox="0 0 1200 80" role="img" aria-label="Decorative profile banner">'
        '<rect width="1200" height="80" fill="#0d1117"/>'
        f'<path d="M0 58 C180 12 300 78 480 34 S780 8 940 45 S1090 68 1200 24" fill="none" stroke="{color}" stroke-width="3" opacity=".9"/>'
        '<circle cx="88" cy="44" r="5" fill="#f0f6fc"/>'
        '<circle cx="1112" cy="36" r="5" fill="#f0f6fc"/>'
        '</svg>'
    )
    (ASSETS / name).write_text(svg, encoding="utf-8")

u = get(f"/users/{USER}") or {}
repos = get_repositories()
repositories_available = repos is not None
repos = repos or []

languages = {}
original_repositories = [repo for repo in repos if not repo.get("fork")]
total_stars = sum(repo.get("stargazers_count", 0) for repo in original_repositories) if repositories_available else "Data unavailable"
languages_available = repositories_available
for repo in repos:
    if repo.get("fork"): continue
    data = get(f"/repos/{USER}/{repo['name']}/languages")
    if data is None:
        languages_available = False
        continue
    if isinstance(data, dict):
        for language, byte_count in data.items():
            languages[language] = languages.get(language, 0) + byte_count

total_bytes = sum(languages.values())
top = sorted(languages.items(), key=lambda x:x[1], reverse=True)[:6]
lang_text = " | ".join(f"{language} {byte_count / total_bytes * 100:.1f}%" for language, byte_count in top) if total_bytes and languages_available else "Data unavailable"

public_repositories = value_or_unavailable(u.get("public_repos"))
followers = value_or_unavailable(u.get("followers"))
following = value_or_unavailable(u.get("following"))
display_name = value_or_unavailable(u.get("name"))
bio = value_or_unavailable(u.get("bio"))
created_at = value_or_unavailable(u.get("created_at", "")[:10] if u.get("created_at") else None)

write_svg("github-stats.svg", "GitHub Statistics", [
    (f"Public repositories: {public_repositories}", "#f0f6fc", 19),
    (f"Followers: {followers}    Following: {following}", "#c9d1d9", 18),
    (f"Stars on original repositories: {total_stars}", "#58a6ff", 18),
    (f"GitHub profile: {USER}", "#8b949e", 15),
])
write_svg("top-languages.svg", "Top Languages", [
    (lang_text, "#f0f6fc", 18),
    (f"Original repositories analysed: {len(original_repositories) if repositories_available else 'Data unavailable'}", "#c9d1d9", 17),
    ("Calculated from GitHub repository language bytes", "#8b949e", 15),
])
write_svg("repository-languages.svg", "Repository Languages", [
    (lang_text, "#f0f6fc", 18),
    (f"Original repositories analysed: {len(original_repositories) if repositories_available else 'Data unavailable'}", "#c9d1d9", 17),
    ("Language totals are byte counts from the public GitHub API", "#8b949e", 15),
])
write_svg("streak.svg", "Contribution Streak", [
    ("Data unavailable via GitHub's public REST API", "#f0f6fc", 18),
    ("No contribution number has been invented", "#c9d1d9", 17),
    (f"Profile: {USER}", "#8b949e", 16),
])
write_svg("productive-time.svg", "Productive Time", [
    ("Data unavailable via GitHub's public REST API", "#f0f6fc", 18),
    ("GitHub does not publish hourly activity totals here", "#c9d1d9", 17),
    (f"Profile: {USER}", "#8b949e", 16),
])
write_svg("profile-details.svg", "Profile Details", [
    (f"Name: {display_name}", "#f0f6fc", 19),
    (f"Username: {USER}", "#c9d1d9", 18),
    (f"Bio: {bio}", "#c9d1d9", 17),
    (f"Account created: {created_at}", "#58a6ff", 18),
])
write_svg("trophies.svg", "GitHub Profile", [
    (f"Public repositories: {public_repositories}", "#f0f6fc", 19),
    (f"Followers: {followers}    Stars: {total_stars}", "#c9d1d9", 18),
    ("Achievement data based only on verifiable public GitHub fields", "#8b949e", 16),
])
write_svg("profile-views.svg", "Profile", [
    ("Data unavailable via GitHub's public API", "#f0f6fc", 19),
    (f"Profile: {USER}", "#8b949e", 15),
], width=650, height=150)
write_decorative_svg("top-banner.svg", "#58a6ff")
write_decorative_svg("bottom-banner.svg", "#79c0ff")
