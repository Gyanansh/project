from app.services.llm_service import llm_service
from app.models.schemas import AnalysisResult
import re

class AnalysisService:
    async def analyze_code(self, content: str, filename: str) -> AnalysisResult:
        # Static Analysis (Basic)
        loc = len(content.splitlines())
        # Rudimentary function counting (very basic regex)
        func_count = len(re.findall(r'def\s+\w+', content)) + len(re.findall(r'function\s+\w+', content))
        
        metrics = {
            "lines_of_code": loc,
            "function_count": func_count,
            "size_bytes": len(content)
        }
        
        # LLM Analysis (Parallelize in real app, sequential here for simplicity)
        explanation = await llm_service.analyze_file(content, filename)
        refactoring = await llm_service.suggest_refactoring(content)
        
        # Parse or structure LLM output - for now we return raw strings as part of the result
        # In a real app we might ask LLM to return JSON.
        
        return AnalysisResult(
            summary=explanation, 
            components=[],
            architecture_fit="Details in summary",
            patterns=[],
            docstring_suggestions=[],
            refactoring_suggestions=[refactoring],
            vulnerability_hints=[],
            metrics=metrics
        )

    async def generate_report(self, owner: str, repo: str) -> AnalysisResult: # Should return APIReport actually
        from app.services.github_service import github_service
        # Get tree to find relevant files
        tree_data = await github_service.get_repo_tree(owner, repo)
        files = [f['path'] for f in tree_data.get('tree', []) if 'path' in f]
        
        # Identity likely DB/API files
        db_files = [f for f in files if any(x in f.lower() for x in ['model', 'schema', 'migration', 'db', 'sql'])]
        api_files = [f for f in files if any(x in f.lower() for x in ['api', 'route', 'controller', 'resolver', 'service'])]
        
        # We could fetch content of top 3 suspected files to give context to LLM
        # For now, just listing them is a start, or we rely on filename analysis
        
        from app.models.schemas import APIReport
        return APIReport(
            database_overview=f"Detected potential DB files: {', '.join(db_files[:10])}...",
            api_overview=f"Detected potential API files: {', '.join(api_files[:10])}..."
        )

    async def analyze_pr_patterns(self, owner: str, repo: str) -> dict:
        from app.services.github_service import github_service
        prs = await github_service.get_pull_requests(owner, repo, state='closed', limit=10)
        
        if not prs:
             return {"patterns": "No recent closed PRs found."}

        # Extract text for LLM
        pr_text = "\n".join([f"Title: {pr['title']}, Merged: {pr.get('merged_at') is not None}, Labels: {[l['name'] for l in pr.get('labels', [])]}" for pr in prs])
        
        patterns = await llm_service.analyze_pr_patterns(pr_text)
        return {"patterns": patterns}

    async def generate_roadmap(self, owner: str, repo: str) -> dict:
        # Get context
        report = await self.generate_report(owner, repo)
        patterns = await self.analyze_pr_patterns(owner, repo)
        
        context = f"API/DB Context: {report}\nPR Patterns: {patterns}"
        roadmap_text = await llm_service.generate_roadamp(context)
        
        return {"roadmap": roadmap_text}


    async def generate_contribution_guide(self, owner: str, repo: str) -> dict:
        patterns = await self.analyze_pr_patterns(owner, repo)
        context = f"PR Patterns: {patterns}"
        guide = await llm_service.generate_contribution_guide(context)
        return {"guide": guide}

analysis_service = AnalysisService()
