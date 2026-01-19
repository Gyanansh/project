from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.github_service import GitHubService
from api.serializers.repo_serializers import RepoRequestSerializer
import logging
import re

logger = logging.getLogger(__name__)

class RepoReportView(APIView):
    def get(self, request):
        serializer = RepoRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        owner = serializer.validated_data['owner']
        repo = serializer.validated_data['repo']
        
        try:
            github_service = GitHubService()
            tree = github_service.get_repo_tree(owner, repo)
            
            # Simple analysis of the tree
            files = [item['path'] for item in tree.get('tree', []) if item['type'] == 'blob']
            
            models_files = [f for f in files if 'models.py' in f]
            urls_files = [f for f in files if 'urls.py' in f]
            
            report = {
                "structure_summary": {
                    "total_files": len(files),
                    "models_detected": models_files,
                    "routes_detected": urls_files,
                },
                "components": []
            }
            
            # Fetch content of models.py to guess schema
            if models_files:
                content = github_service.get_file_content(owner, repo, models_files[0])
                # regex to find class X(models.Model)
                classes = re.findall(r'class\s+(\w+)\(', content)
                report["database_schema"] = {
                    "source": models_files[0],
                    "potential_tables": classes
                }
                
            return Response(report)
        except Exception as e:
            logger.error(f"Error in RepoReportView: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
