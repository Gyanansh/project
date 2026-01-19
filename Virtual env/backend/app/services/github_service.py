import httpx
import os
from fastapi import HTTPException

GITHUB_API_BASE = "https://api.github.com"

class GitHubService:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    async def get_repo_tree(self, owner: str, repo: str, branch: str = "main") -> dict:
        # First try to get default branch if not specified (or just assume main/master? better to query repo info first)
        # For simplicity, we'll try 'main' then 'master' or let caller specify.
        # Actually, let's get the default branch from repo info first.
        
        async with httpx.AsyncClient() as client:
            # Get repo info for default branch
            repo_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
            repo_resp = await client.get(repo_url, headers=self.headers)
            if repo_resp.status_code == 404:
                raise HTTPException(status_code=404, detail="Repository not found")
            repo_data = repo_resp.json()
            default_branch = repo_data.get("default_branch", "main")
            
            # Fetch tree
            tree_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
            resp = await client.get(tree_url, headers=self.headers)
            
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to fetch repository tree")
                
            return resp.json()

    async def get_file_content(self, owner: str, repo: str, path: str) -> str:
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            if resp.status_code != 200:
                 # Fallback for raw content if needed, but contents API returns base64
                 # Let's try raw media type
                 headers = self.headers.copy()
                 headers["Accept"] = "application/vnd.github.v3.raw"
                 raw_resp = await client.get(url, headers=headers)
                 if raw_resp.status_code != 200:
                     raise HTTPException(status_code=404, detail="File not found")
                 return raw_resp.text
            
            # If we used json, we'd have to decode base64. 
            # Using raw media type is easier.
            # But the first request above didn't use raw header. 
            # Optimally:
            headers = self.headers.copy()
            headers["Accept"] = "application/vnd.github.v3.raw"
            raw_resp = await client.get(url, headers=headers)
            if raw_resp.status_code != 200:
                raise HTTPException(status_code=raw_resp.status_code, detail="Failed to fetch file content")
            return raw_resp.text

    async def get_pull_requests(self, owner: str, repo: str, state: str = "closed", limit: int = 20) -> list:
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls?state={state}&per_page={limit}&sort=updated&direction=desc"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            if resp.status_code != 200:
                return []
            return resp.json()

github_service = GitHubService()
