import os
import openai
from fastapi import HTTPException

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("AIzaSyBPLPrNPxuk4eQVub-vqa8yFpL8OX0ZFn0")
        self.client = None
        if self.api_key:
            openai.api_key = self.api_key
            self.client = openai.AsyncOpenAI(api_key=self.api_key)

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if not self.client:
            # Mock response if no key provided, or raise error. 
            # For development, returning a mock is friendlier but we should warn.
            print("WARNING: No OPENAI_API_KEY found. returning mock response.")
            return "LLM analysis disabled (No API Key). Please set OPENAI_API_KEY."

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o", # Use a smart model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")

    async def analyze_file(self, content: str, filename: str) -> str:
        system = "You are an expert code analyst. Explain the code structure, purpose, and key components."
        user = f"Analyze this file ({filename}):\n\n```\n{content[:10000]}\n```" # Truncate for safety
        return await self._call_llm(system, user)

    async def suggest_refactoring(self, content: str) -> str:
        system = "You are a senior developer. Suggest refactorings to improve code quality, readability, and performance. Be specific."
        user = f"Code:\n```\n{content[:8000]}\n```"
        return await self._call_llm(system, user)

    async def generate_roadamp(self, context: str) -> str:
        system = "You are a project manager and tech lead. Create a prioritized roadmap for contributers."
        user = f"Project Context:\n{context}"
        return await self._call_llm(system, user)
    
    async def analyze_pr_patterns(self, pr_data: str) -> str:
        system = "You are a data scientist analyzing git patterns. Summarize PR acceptance criteria and patterns."
        user = f"PR Data:\n{pr_data}"
        return await self._call_llm(system, user)

    async def generate_contribution_guide(self, context: str) -> str:
        system = "You are an open source maintainer. Write a contribution guide for new contributors based on these patterns."
        user = f"Context:\n{context}"
        return await self._call_llm(system, user)

llm_service = LLMService()
