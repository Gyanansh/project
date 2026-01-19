from fastapi import APIRouter
from app.models.schemas import AnalysisResult

router = APIRouter(
    prefix="/repo", # Keeping prefix same as generic repo/ since requirements asked for /repo/analyze-file etc
    tags=["analysis"],
)

@router.get("/analyze-file", response_model=AnalysisResult)
async def analyze_file(owner: str, repo: str, path: str):
    # Fetch content first
    from app.services.github_service import github_service
    content = await github_service.get_file_content(owner, repo, path)
    
    # Analyze
    from app.services.analysis_service import analysis_service
    result = await analysis_service.analyze_code(content, path)
    return result

@router.get("/report")
async def get_report(owner: str, repo: str):
    from app.services.analysis_service import analysis_service
    return await analysis_service.generate_report(owner, repo)

@router.get("/roadmap")
async def get_roadmap(owner: str, repo: str):
    from app.services.analysis_service import analysis_service
    return await analysis_service.generate_roadmap(owner, repo)

@router.get("/pr-patterns")
async def get_pr_patterns(owner: str, repo: str):
    from app.services.analysis_service import analysis_service
    return await analysis_service.analyze_pr_patterns(owner, repo)

@router.get("/contribution-guide")
async def get_contribution_guide(owner: str, repo: str):
    from app.services.analysis_service import analysis_service
    return await analysis_service.generate_contribution_guide(owner, repo)
