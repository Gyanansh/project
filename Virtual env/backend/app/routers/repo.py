from fastapi import APIRouter, HTTPException, Query
from app.services.github_service import github_service
from app.models.schemas import RepoTree

router = APIRouter(
    prefix="/repo",
    tags=["repo"],
)

@router.get("/tree", response_model=RepoTree)
async def get_repo_tree(owner: str, repo: str):
    data = await github_service.get_repo_tree(owner, repo)
    return data

@router.get("/file")
async def get_file_content(owner: str, repo: str, path: str):
    content = await github_service.get_file_content(owner, repo, path)
    return {"content": content}
