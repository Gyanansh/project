from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.github_service import GitHubService
from api.serializers.repo_serializers import RepoRequestSerializer
import logging
from collections import Counter

logger = logging.getLogger(__name__)

class PRPatternView(APIView):
    def get(self, request):
        serializer = RepoRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        owner = serializer.validated_data['owner']
        repo = serializer.validated_data['repo']
        
        try:
            github_service = GitHubService()
            # method get_pull_requests was defined in github_service
            prs = github_service.get_pull_requests(owner, repo, state='closed')
            
            # Analyze PRs
            merged_prs = [pr for pr in prs if pr.get('merged_at')]
            
            authors = [pr['user']['login'] for pr in merged_prs if pr.get('user')]
            top_contributors = Counter(authors).most_common(5)
            
            # Simple topic extraction from titles
            words = []
            for pr in merged_prs:
                words.extend(pr['title'].lower().split())
            
            common_topics = Counter([w for w in words if len(w) > 4]).most_common(10)
            
            return Response({
                "total_closed_prs": len(prs),
                "merged_prs": len(merged_prs),
                "top_contributors": top_contributors,
                "common_topics_in_titles": common_topics
            })
        except Exception as e:
            logger.error(f"Error in PRPatternView: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
