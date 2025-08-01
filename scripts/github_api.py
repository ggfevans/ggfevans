"""
GitHub API wrapper for fetching user data
"""

import os
import requests
from typing import List, Dict, Any


class GitHubAPI:
    def __init__(self):
        self.token = os.environ.get('GITHUB_TOKEN')
        self.username = 'ggfevans'
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {self.token}' if self.token else ''
        }
    
    def _request(self, endpoint: str) -> Any:
        """Make a request to GitHub API"""
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        user_data = self._request(f'/users/{self.username}')
        
        # Calculate total stars from repositories
        repos = self.get_repositories()
        total_stars = sum(repo['stargazers_count'] for repo in repos)
        
        return {
            'public_repos': user_data['public_repos'],
            'followers': user_data['followers'],
            'following': user_data['following'],
            'total_stars': total_stars,
            'created_at': user_data['created_at'],
            'bio': user_data['bio'],
            'location': user_data['location'],
            'company': user_data['company']
        }
    
    def get_recent_activity(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get recent public events"""
        events = self._request(f'/users/{self.username}/events/public')
        return events[:limit]
    
    def get_repositories(self) -> List[Dict[str, Any]]:
        """Get all user repositories"""
        repos = []
        page = 1
        
        while True:
            page_repos = self._request(f'/users/{self.username}/repos?page={page}&per_page=100&sort=updated')
            if not page_repos:
                break
            repos.extend(page_repos)
            page += 1
            
        return repos
    
    def get_language_stats(self, repos: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate language statistics across all repositories"""
        language_stats = {}
        
        for repo in repos:
            if repo['fork']:  # Skip forks
                continue
                
            try:
                languages = self._request(f"/repos/{self.username}/{repo['name']}/languages")
                for lang, bytes_count in languages.items():
                    language_stats[lang] = language_stats.get(lang, 0) + bytes_count
            except:
                # Skip if we can't get language data for a repo
                continue
        
        return language_stats
    
    def get_contribution_stats(self) -> Dict[str, Any]:
        """Get contribution statistics (requires GraphQL)"""
        # This would require GraphQL API for more detailed contribution data
        # For now, returning placeholder
        return {
            'total_contributions': 0,
            'current_streak': 0,
            'longest_streak': 0
        }