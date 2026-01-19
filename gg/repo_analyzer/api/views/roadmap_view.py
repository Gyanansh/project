from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.ai_service import AIService
from api.serializers.repo_serializers import RepoRequestSerializer
import logging

logger = logging.getLogger(__name__)

class RoadmapView(APIView):
    def get(self, request):
        serializer = RepoRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        owner = serializer.validated_data['owner']
        repo = serializer.validated_data['repo']
        
        # In a real scenario, we would aggregate data from other services
        summary = f"Analysis for repo: {owner}/{repo}. Features: Django backend, React frontend..."
        
        try:
            ai_service = AIService()
            # Mocking AI call or actually calling it if key exists
            # result = ai_service.suggest_improvements(summary)
            
            # Returning a structured mock for now to ensure endpoint works without burning tokens or if key missing
            result = {
                "roadmap": [
                    {"phase": "1. Refactoring", "items": ["Extract services", "Add type hints"]},
                    {"phase": "2. Features", "items": ["Add user auth", "Integrate CI/CD"]}
                ],
                "improvements": ["Use Select2 for dropdowns", "Optimize database queries"]
            }
            return Response(result)
        except Exception as e:
            logger.error(f"Error in RoadmapView: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
