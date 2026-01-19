import requests
from django.conf import settings
import base64
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if settings.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"
        else:
            logger.warning("GITHUB_TOKEN is not set. API rate limits will be restricted to 60 requests/hour.")

    def get_repo_tree(self, owner, repo):
        """
        Fetch the entire file tree of a repository recursively.
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees/main?recursive=true"
        # Try main first, then master if fails? Or get default branch first.
        # For simplicity, let's first get the default branch.
        
        try:
            repo_info = self.get_repo_info(owner, repo)
            default_branch = repo_info.get("default_branch", "main")
            
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=true"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching repo tree: {e}")
            raise

    def get_repo_info(self, owner, repo):
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_file_content(self, owner, repo, path):
        """
        Fetch raw file content from GitHub.
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if "content" in data and data["encoding"] == "base64":
                return base64.b64decode(data["content"]).decode("utf-8")
            return "" 
        except Exception as e:
            logger.error(f"Error fetching file content: {e}")
            raise

    def get_pull_requests(self, owner, repo, state="closed", per_page=100):
        """
        Fetch pull requests.
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls"
        params = {"state": state, "per_page": per_page}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_issues(self, owner, repo, labels=None, state="open", per_page=10):
        """
        Fetch issues from the repository.
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/issues"
        params = {"state": state, "per_page": per_page}
        if labels:
            params["labels"] = labels
            
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching issues: {e}")
            return []
