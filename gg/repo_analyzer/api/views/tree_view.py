from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.github_service import GitHubService
from api.serializers.repo_serializers import RepoRequestSerializer
import logging

logger = logging.getLogger(__name__)

class RepoTreeView(APIView):
    def get(self, request):
        serializer = RepoRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        owner = serializer.validated_data['owner']
        repo = serializer.validated_data['repo']
        
        try:
            github_service = GitHubService()
            tree_data = github_service.get_repo_tree(owner, repo)
            return Response(tree_data)
        except Exception as e:
            logger.error(f"Error in RepoTreeView: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
