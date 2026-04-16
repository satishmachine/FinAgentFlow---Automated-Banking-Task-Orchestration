"""
AI Content Generation layer — Interfaces with EuriAI for LLM-powered text generation.
"""

from app.generation.content_generator import ContentGenerator
from app.generation.prompts import PromptTemplates

__all__ = ["ContentGenerator", "PromptTemplates"]
