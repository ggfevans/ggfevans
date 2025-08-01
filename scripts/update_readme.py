#!/usr/bin/env python3
"""
Update GitHub profile README with dynamic content
"""

import os
import re
from datetime import datetime
from github_api import GitHubAPI


def update_section(content, section_name, new_content):
    """Replace content between section markers"""
    pattern = f"<!-- {section_name}_START -->.*?<!-- {section_name}_END -->"
    replacement = f"<!-- {section_name}_START -->\n{new_content}\n<!-- {section_name}_END -->"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)


def format_stats(stats):
    """Format GitHub stats into markdown"""
    return f"""
### 📊 GitHub Stats

![GitHub Stats](https://github-readme-stats.vercel.app/api?username=ggfevans&show_icons=true&theme=dracula)

- **Public Repos:** {stats['public_repos']}
- **Total Stars:** {stats['total_stars']}
- **Followers:** {stats['followers']}
- **Following:** {stats['following']}
"""


def format_recent_activity(events):
    """Format recent GitHub activity"""
    activity_lines = ["### 🚀 Recent Activity\n"]
    
    for event in events[:5]:  # Show last 5 events
        event_type = event['type']
        repo = event['repo']['name']
        created_at = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        time_str = created_at.strftime("%b %d")
        
        if event_type == "PushEvent":
            commits = event['payload'].get('commits', [])
            if commits:
                activity_lines.append(f"- 🔨 Pushed to [{repo}](https://github.com/{repo}) on {time_str}")
        elif event_type == "CreateEvent":
            ref_type = event['payload'].get('ref_type', 'repository')
            activity_lines.append(f"- 🌟 Created {ref_type} in [{repo}](https://github.com/{repo}) on {time_str}")
        elif event_type == "IssuesEvent":
            action = event['payload']['action']
            activity_lines.append(f"- 📝 {action.capitalize()} issue in [{repo}](https://github.com/{repo}) on {time_str}")
        elif event_type == "PullRequestEvent":
            action = event['payload']['action']
            activity_lines.append(f"- 🔀 {action.capitalize()} PR in [{repo}](https://github.com/{repo}) on {time_str}")
        elif event_type == "WatchEvent":
            activity_lines.append(f"- ⭐ Starred [{repo}](https://github.com/{repo}) on {time_str}")
    
    return "\n".join(activity_lines)


def format_top_projects(repos):
    """Format top repositories"""
    project_lines = ["### 💼 Featured Projects\n"]
    
    # Sort by stars + forks
    sorted_repos = sorted(repos, key=lambda x: x['stargazers_count'] + x['forks_count'], reverse=True)
    
    for repo in sorted_repos[:6]:  # Show top 6 projects
        if repo['fork']:
            continue  # Skip forks
            
        name = repo['name']
        description = repo['description'] or "No description available"
        stars = repo['stargazers_count']
        language = repo['language'] or "Various"
        
        project_lines.append(f"#### [{name}](https://github.com/ggfevans/{name})")
        project_lines.append(f"- {description}")
        project_lines.append(f"- **Language:** {language} | **Stars:** {stars}")
        project_lines.append("")
    
    return "\n".join(project_lines)


def format_languages(language_stats):
    """Format programming language statistics"""
    total_bytes = sum(language_stats.values())
    
    lines = ["### 🛠️ Tech Stack\n"]
    lines.append("#### Top Languages by Usage")
    
    # Sort languages by bytes
    sorted_langs = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
    
    for lang, bytes_count in sorted_langs[:8]:  # Show top 8 languages
        percentage = (bytes_count / total_bytes) * 100
        bar_length = int(percentage / 5)  # Scale to 20 chars max
        bar = "█" * bar_length + "░" * (20 - bar_length)
        lines.append(f"- **{lang}:** {bar} {percentage:.1f}%")
    
    return "\n".join(lines)


def main():
    # Initialize API client
    api = GitHubAPI()
    
    # Read current README
    with open('README.md', 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    # Fetch data
    print("Fetching GitHub stats...")
    stats = api.get_user_stats()
    
    print("Fetching recent activity...")
    events = api.get_recent_activity()
    
    print("Fetching repositories...")
    repos = api.get_repositories()
    
    print("Calculating language statistics...")
    language_stats = api.get_language_stats(repos)
    
    # Update sections
    print("Updating README sections...")
    readme_content = update_section(readme_content, "STATS", format_stats(stats))
    readme_content = update_section(readme_content, "ACTIVITY", format_recent_activity(events))
    readme_content = update_section(readme_content, "PROJECTS", format_top_projects(repos))
    readme_content = update_section(readme_content, "SKILLS", format_languages(language_stats))
    
    # Add last updated timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    readme_content = re.sub(
        r"<!-- LAST_UPDATED -->.*?<!-- LAST_UPDATED_END -->",
        f"<!-- LAST_UPDATED -->Last updated: {timestamp}<!-- LAST_UPDATED_END -->",
        readme_content
    )
    
    # Write updated README
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"README updated successfully at {timestamp}")


if __name__ == "__main__":
    main()