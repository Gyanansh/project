from rest_framework import serializers

class RepoRequestSerializer(serializers.Serializer):
    owner = serializers.CharField(required=True)
    repo = serializers.CharField(required=True)
    path = serializers.CharField(required=False)

class AnalysisResponseSerializer(serializers.Serializer):
    filename = serializers.CharField()
    explanation = serializers.CharField(required=False)
    vulnerabilities = serializers.ListField(required=False)
    suggestions = serializers.ListField(required=False)

class TreeItemSerializer(serializers.Serializer):
    path = serializers.CharField()
    mode = serializers.CharField()
    type = serializers.CharField()
    sha = serializers.CharField()
    size = serializers.IntegerField(required=False)
    url = serializers.CharField()
