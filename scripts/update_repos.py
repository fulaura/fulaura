import urllib.request
import json
import re
import os

USERNAME = "fulaura"
README_PATH = "README.md"
MARKER_START = "<!-- START_LATEST_REPOS -->"
MARKER_END = "<!-- END_LATEST_REPOS -->"

def fetch_latest_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?sort=pushed&per_page=50"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        repos = json.loads(response.read().decode())
    
    # Filter out forks and the profile repo
    valid_repos = [r for r in repos if not r['fork'] and r['name'] != USERNAME]
    
    # Get top 2
    return valid_repos[:2]

def update_readme(repos):
    if not os.path.exists(README_PATH):
        print(f"{README_PATH} not found.")
        return

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    cards = []
    for repo in repos:
        name = repo['name']
        card_url = f"https://github-readme-stats.vercel.app/api/pin/?username={USERNAME}&repo={name}&theme=algolia&bg_color=0D1117"
        repo_url = repo['html_url']
        cards.append(f'  <a href="{repo_url}"><img src="{card_url}" alt="{name}" /></a>')
    
    replacement = f"{MARKER_START}\n" + "\n".join(cards) + f"\n  {MARKER_END}"
    
    # Regex to replace content between markers
    pattern = re.compile(rf"{MARKER_START}.*?{MARKER_END}", re.DOTALL)
    new_content = re.sub(pattern, replacement, content)

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("README updated successfully.")

if __name__ == "__main__":
    latest_repos = fetch_latest_repos()
    update_readme(latest_repos)
