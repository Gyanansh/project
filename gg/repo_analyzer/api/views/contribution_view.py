from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.github_service import GitHubService
from api.serializers.repo_serializers import RepoRequestSerializer
from services.ai_service import AIService
import json
import logging

logger = logging.getLogger(__name__)

class ContributionView(APIView):
    def get(self, request):
        serializer = RepoRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        owner = serializer.validated_data['owner']
        repo = serializer.validated_data['repo']
        
        try:
            github_service = GitHubService()
            repo_info = github_service.get_repo_info(owner, repo)
            
            # Fetch "good first issues"
            issues = github_service.get_issues(owner, repo, labels="good first issue")
            formatted_issues = [
                {"title": i["title"], "url": i["html_url"], "number": i["number"]}
                for i in issues
            ]
            
            # Generate guide using AI
            ai_service = AIService()
            summary = f"Repo: {owner}/{repo}. Description: {repo_info.get('description', '')}. Language: {repo_info.get('language', 'Unknown')}."
            
            guide_json = ai_service.generate_contribution_guide(summary)
            
            if guide_json:
                try:
                    guide_data = json.loads(guide_json)
                except json.JSONDecodeError:
                    guide_data = {
                        "getting_started": "Error parsing AI response.",
                        "code_style": "Standard guidelines apply.",
                        "testing": "Check the README."
                    }
            else:
                logger.warning("AI Service returned no content, falling back to defaults.")
                guide_data = {
                    "getting_started": "Fork the repo, clone it, creating a virtualenv...",
                    "code_style": "Use flake8 and black.",
                    "testing": "Run pytest."
                }
            
            # Merge data
            result = {
                "project_name": repo_info.get("name"),
                "description": repo_info.get("description"),
                **guide_data,
                "good_first_issues": formatted_issues
            }
            
            return Response(result)
        except Exception as e:
            logger.error(f"Error in ContributionView: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
