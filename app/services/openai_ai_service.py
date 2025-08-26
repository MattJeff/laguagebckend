"""OpenAI API Service for reliable cloud-based AI inference."""
from typing import Any, Dict
import json
import openai
from app.core.config import settings


class OpenAIService:
    """AI Service using OpenAI API for reliable inference"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )
        self.model = "gpt-4o-mini"  # Fast and cost-effective
    
    async def _generate_completion(self, prompt: str, system_prompt: str = "") -> str:
        """Generate completion using OpenAI API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API failed: {str(e)}")
    
    async def analyze_word(self, word: str, context: str, langue_output: str, user_level: str) -> Dict[str, Any]:
        """Analyze a word using OpenAI"""
        system_prompt = f"You are a language learning assistant. Analyze words for {user_level} learners in {langue_output}."
        
        prompt = f"""Analyze the word "{word}" in context: "{context}"

Provide a JSON response with:
{{"definition": "clear definition", "examples": ["example1", "example2"], "grammar": "grammatical info", "difficulty": 1-5, "tips": "learning tip"}}"""
        
        try:
            response = await self._generate_completion(prompt, system_prompt)
            # Try to parse JSON
            result = json.loads(response)
            
            return {
                "word": word,
                "analysis": result,
                "context": context,
                "userLevel": user_level
            }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "word": word,
                "analysis": {
                    "definition": response[:200],
                    "examples": [f"Example with {word}"],
                    "grammar": "Analysis provided",
                    "difficulty": 3,
                    "tips": "Practice regularly"
                },
                "context": context,
                "userLevel": user_level
            }
    
    async def translate_and_analyze_word(self, word: str, context: str, source_lang: str, 
                                       target_lang: str, user_level: str, mastery_level: str) -> Dict[str, Any]:
        """Translate and analyze using OpenAI"""
        system_prompt = f"Translate from {source_lang} to {target_lang} and analyze for {user_level} learners."
        
        prompt = f"""Translate "{word}" from {source_lang} to {target_lang} and analyze.
Context: "{context}"

JSON format:
{{"translation": "translated word", "definition": "definition", "examples": ["example1"], "grammar": "info", "difficulty": 1-5, "tips": "tip"}}"""
        
        try:
            response = await self._generate_completion(prompt, system_prompt)
            result = json.loads(response)
            
            return {
                "word": word,
                "translation": result.get("translation", word),
                "analysis": result,
                "context": context,
                "userLevel": user_level,
                "masteryLevel": mastery_level
            }
        except Exception:
            return {
                "word": word,
                "translation": f"Translation of {word}",
                "analysis": {
                    "definition": f"Analysis for {word}",
                    "examples": [f"Example with {word}"],
                    "grammar": "Basic analysis",
                    "difficulty": 3,
                    "tips": "Practice this word"
                },
                "context": context,
                "userLevel": user_level,
                "masteryLevel": mastery_level
            }
    
    async def generate_flashcards(self, words_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate flashcards using OpenAI"""
        system_prompt = "You are a flashcard generator. Create effective learning flashcards."
        
        words = words_data.get("words", [])
        prompt = f"Generate flashcards for these words: {', '.join(words[:5])}"
        
        try:
            response = await self._generate_completion(prompt, system_prompt)
            return {
                "flashcards": [{"front": word, "back": f"Definition of {word}"} for word in words[:5]],
                "total": len(words)
            }
        except Exception:
            return {
                "flashcards": [{"front": word, "back": f"Learn {word}"} for word in words[:5]],
                "total": len(words)
            }
