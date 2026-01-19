from openai import OpenAI
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY is not set.")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def analyze_code(self, code_content, filename):
        if not settings.OPENAI_API_KEY:
            # Mock response for demonstration
            return """
            {
                "explanation": "THIS IS A MOCK ANALYSIS (No OpenAI Key provided).\\n\\nThe code appears to be a Python file. It imports libraries and defines functions. To get real analysis, please set OPENAI_API_KEY in your .env file.",
                "complexity": "Unknown (Mock)",
                "suggestions": ["Add API Key for real analysis", "Add docstrings", "Check error handling"],
                "docstrings": "No docstrings generated in mock mode."
            }
            """

        prompt = f"""
        You are an expert Python developer. Analyze the following code from file '{filename}'.
        Provide a JSON response with the following keys:
        - explanation: A human-readable explanation of what the code does.
        - complexity: An assessment of the code's complexity.
        - suggestions: A list of suggestions for improvement.
        - docstrings: Suggested module-level or class-level docstrings.
        
        Code:
        ```python
        {code_content[:8000]}  # Truncate to avoid context limit issues for now
        ```
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Using a capable model
                messages=[
                    {"role": "system", "content": "You are a helpful coding assistant that analyzes code and outpust raw JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            return None

    def suggest_improvements(self, project_summary):
        """
        Generate roadmap and improvement suggestions based on project summary.
        """
        prompt = f"""
        Based on the following project analysis summary, suggest a contribution roadmap and improvements.
        
        Summary:
        {project_summary}
        
        Return a JSON with keys: 'roadmap', 'improvements', 'good_first_issues'.
        """
        # Similar implementation
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a helpful technical project manager who suggests improvements and roadmaps."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error suggesting improvements: {e}")
            return None

    def generate_contribution_guide(self, project_summary):
        """
        Generate a contribution guide based on the project summary.
        """
        prompt = f"""
        Based on the following project analysis summary, generate a contribution guide.
        
        Summary:
        {project_summary}
        
        Return a JSON with the following keys:
        - getting_started: A step-by-step guide to setting up the project locally (inferred from tech stack).
        - code_style: Suggested code style guidelines (e.g., PEP8 for Python, ESLint for JS).
        - testing: How to run tests (inferred).
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a helpful open source maintainer who writes clear contribution guides."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating contribution guide: {e}")
            return None
