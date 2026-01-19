from django.urls import path
from api.views.tree_view import RepoTreeView
from api.views.file_analysis_view import FileAnalysisView
from api.views.vulnerability_view import VulnerabilityView
from api.views.report_view import RepoReportView
from api.views.roadmap_view import RoadmapView
from api.views.contribution_view import ContributionView
from api.views.pr_pattern_view import PRPatternView

urlpatterns = [
    path('repo/tree/', RepoTreeView.as_view(), name='repo-tree'),
    path('repo/analyze-file/', FileAnalysisView.as_view(), name='file-analysis'),
    path('repo/vulnerabilities/', VulnerabilityView.as_view(), name='vulnerabilities'),
    path('repo/report/', RepoReportView.as_view(), name='repo-report'),
    path('repo/roadmap/', RoadmapView.as_view(), name='repo-roadmap'),
    path('repo/contribution-guide/', ContributionView.as_view(), name='contribution-guide'),
    path('repo/pr-patterns/', PRPatternView.as_view(), name='pr-patterns'),
]
