from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.github_service import GitHubService
from services.ai_service import AIService
from api.serializers.repo_serializers import RepoRequestSerializer
import logging

logger = logging.getLogger(__name__)

class FileAnalysisView(APIView):
    def get(self, request):
        serializer = RepoRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        owner = serializer.validated_data['owner']
        repo = serializer.validated_data['repo']
        path = serializer.validated_data.get('path')
        
        if not path:
             return Response({"error": "Path is required for file analysis"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            github_service = GitHubService()
            content = github_service.get_file_content(owner, repo, path)
            
            if not content:
                return Response({"error": "File content is empty or not found"}, status=status.HTTP_404_NOT_FOUND)
            
            ai_service = AIService()
            analysis_result = ai_service.analyze_code(content, path)
            
            # If AI service fails or returns raw string, we try to parse or wrap it
            import json
            try:
                if analysis_result:
                    data = json.loads(analysis_result)
                else:
                    data = {"error": "AI analysis returned no result"}
            except json.JSONDecodeError:
                data = {"raw_analysis": analysis_result}

            return Response(data)
        except Exception as e:
            logger.error(f"Error in FileAnalysisView: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
