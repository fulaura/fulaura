import urllib.request
import json
import re
import os
from collections import defaultdict

USERNAME = "fulaura"
README_PATH = "README.md"
MARKER_START = "<!-- START_LATEST_REPOS -->"
MARKER_END = "<!-- END_LATEST_REPOS -->"

def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
    # The Accept header is needed to ensure topics are returned in the response
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/vnd.github.mercy-preview+json'})
    with urllib.request.urlopen(req) as response:
        repos = json.loads(response.read().decode())
    
    # Filter out forks and the profile repo
    return [r for r in repos if not r.get('fork') and r.get('name') != USERNAME]

def group_repos_by_tag(repos):
    grouped = defaultdict(list)
    for repo in repos:
        topics = repo.get('topics', [])
        for topic in topics:
            grouped[topic].append(repo)
    return grouped

def update_readme(grouped_repos):
    if not os.path.exists(README_PATH):
        print(f"{README_PATH} not found.")
        return

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    markdown_lines = []
    
    # Sort topics alphabetically
    for topic in sorted(grouped_repos.keys()):
        # Format the topic name nicely (e.g. "machine-learning" -> "Machine Learning")
        display_topic = topic.replace('-', ' ').title()
        markdown_lines.append(f"#### 🏷️ {display_topic}")
        markdown_lines.append('<div align="center">')
        
        for repo in grouped_repos[topic]:
            name = repo['name']
            card_url = f"https://github-readme-stats.vercel.app/api/pin/?username={USERNAME}&repo={name}&theme=algolia&bg_color=0D1117"
            repo_url = repo['html_url']
            markdown_lines.append(f'  <a href="{repo_url}"><img src="{card_url}" alt="{name}" /></a>')
        
        markdown_lines.append('</div>')
        markdown_lines.append('<br>')

    replacement = f"{MARKER_START}\n" + "\n".join(markdown_lines) + f"\n  {MARKER_END}"
    
    # Regex to replace content between markers
    pattern = re.compile(rf"{MARKER_START}.*?{MARKER_END}", re.DOTALL)
    new_content = re.sub(pattern, replacement, content)

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("README updated successfully.")

def update_contributions():
    url = f"https://github.com/users/{USERNAME}/contributions"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            match = re.search(r'([\d,]+)\s+contributions\s+in the last year', html)
            if match:
                count = match.group(1)
                
                with open(README_PATH, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                marker_start = "<!-- START_CONTRIBUTIONS -->"
                marker_end = "<!-- END_CONTRIBUTIONS -->"
                
                replacement = f"{marker_start}{count}{marker_end}"
                pattern = re.compile(rf"{marker_start}.*?{marker_end}", re.DOTALL)
                new_content = re.sub(pattern, replacement, content)
                
                with open(README_PATH, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated contributions to {count}.")
    except Exception as e:
        print("Failed to fetch contributions:", e)

if __name__ == "__main__":
    repos = fetch_repos()
    grouped = group_repos_by_tag(repos)
    if grouped:
        update_readme(grouped)
    else:
        # If no tags are found at all, we should probably clear the section or just leave it empty.
        update_readme({})
        print("No tagged repositories found. Section cleared.")
    
    update_contributions()
