from pydantic import BaseModel
from typing import List, Optional, Any

class FileNode(BaseModel):
    path: str
    mode: str
    type: str
    sha: str
    size: int = 0
    url: str

class RepoTree(BaseModel):
    sha: str
    url: str
    tree: List[FileNode]
    truncated: bool

class AnalysisRequest(BaseModel):
    owner: str
    repo: str
    path: str

class AnalysisResult(BaseModel):
    summary: str
    components: List[str]
    architecture_fit: str
    patterns: List[str]
    docstring_suggestions: List[str]
    refactoring_suggestions: List[str]
    vulnerability_hints: List[str]
    metrics: dict

class RoadmapItem(BaseModel):
    title: str
    description: str
    difficulty: str # Easy, Medium, Hard
    files_involved: List[str]
    code_snippet: Optional[str] = None

class Roadmap(BaseModel):
    items: List[RoadmapItem]
    pr_patterns: str

class APIReport(BaseModel):
    database_overview: str
    api_overview: str

