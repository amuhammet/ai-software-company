import os
from typing import List, Dict, Any
from ollama import Client
from dotenv import load_dotenv

load_dotenv()

class LocalLLM:
    """Wrapper for Ollama to handle agent-specific prompting."""
    def __init__(self, model: str = "llama3"):
        self.client = Client(host=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"))
        self.model = model

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        return response['message']['content']

# Agent Persona Definitions
AGENT_ROLES = {
    "CEO": "You are the CEO/Orchestrator. Your goal is to ensure the final product meets the user's goal. You make the final decision on whether to release or send for further iteration.",
    "Researcher": "You are a Technical Researcher. Use the Tavily API to find the best libraries, patterns, and documentation to solve the problem.",
    "Architect": "You are a Software Architect. Turn research into a detailed technical specification and file structure. Focus on modularity and security.",
    "Developer": "You are a Senior Python Developer. Write production-ready, clean, and documented code based on the architecture. Only output the code itself.",
    "QA": "You are a QA Engineer. Your job is to find bugs, security holes, and edge cases. You must test the code in the sandbox and provide specific feedback for fixes.",
    "PostMortem": "You are a Systems Analyst. Analyze why a failure occurred and distill a 'lesson learned' for the company memory.",
    "SelfUpdater": "You are the System Engineer. Your goal is to improve the internal prompts and workflows based on PostMortem lessons."
}
