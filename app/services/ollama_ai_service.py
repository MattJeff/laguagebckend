"""
Ollama AI Service for production deployment
Compatible with Linux servers and Docker containers
Feature-complete equivalent to MLX AI Service
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional
from ollama import AsyncClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaAIService:
    """AI Service using Ollama for server deployment - Full MLX equivalent"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.client = AsyncClient(host=self.base_url)
        logger.info(f"Initialized Ollama AI Service with model: {self.model}")
    
    async def _generate_completion(self, prompt: str, system_prompt: str = "") -> str:
        """Generate completion using Ollama API with chat endpoint"""
        try:
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user", 
                "content": prompt
            })
            
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": 0.1,
                    "top_p": 0.5,
                    "num_predict": 200,
                    "num_ctx": 1024
                }
            )
            
            return response['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"Ollama completion failed: {str(e)}")
            raise Exception(f"AI generation failed: {str(e)}")
    
    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Extract and parse JSON from LLM response - MLX equivalent"""
        # Clean response from chat tokens and artifacts
        cleaned = re.sub(r'<\|[^\|]*\|>', '', response)  # Remove chat tokens
        cleaned = re.sub(r'```json\s*', '', cleaned)     # Remove markdown
        cleaned = re.sub(r'```\s*$', '', cleaned)        # Remove closing markdown
        cleaned = cleaned.strip()
        
        # Try to find JSON object
        json_patterns = [
            r'\{.*\}',  # Complete JSON object
            r'\[.*\]',  # JSON array
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, cleaned, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # Try parsing the entire cleaned response
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        raise Exception("No valid JSON object found in LLM response")
    
    async def analyze_word(self, word: str, context: str, langue_output: str, user_level: str) -> Dict[str, Any]:
        """Analyze a word with known translation using Ollama"""
        system_prompt = f"""You are a multilingual language learning assistant. 
        Analyze the given word in context for a {user_level} level learner.
        Respond in {langue_output} language.
        Provide: definition, usage examples, grammar notes, difficulty level."""
        
        prompt = f"""
        Analyze this word: "{word}"
        Context: "{context}"
        User level: {user_level}
        
        Provide a detailed analysis in JSON format with:
        - definition: clear definition
        - examples: 3 usage examples
        - grammar: grammatical information
        - difficulty: difficulty level (1-5)
        - tips: learning tips
        """
        
        try:
            response = await self._generate_completion(prompt, system_prompt)
            # Parse JSON response
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
                    "grammar": "Grammar analysis",
                    "difficulty": 3,
                    "tips": "Practice using this word in context"
                },
                "context": context,
                "userLevel": user_level
            }
    
    async def translate_and_analyze_word(self, word: str, context: str, source_lang: str, 
                                       target_lang: str, user_level: str, mastery_level: str) -> Dict[str, Any]:
        """Translate and analyze unknown word using Ollama"""
        system_prompt = f"""You are a multilingual translator and language teacher.
        Translate from {source_lang} to {target_lang} and provide detailed analysis
        for a {user_level} level learner."""
        
        prompt = f"""
        Translate and analyze: "{word}"
        Context: "{context}"
        From: {source_lang} to {target_lang}
        User level: {user_level}
        
        Provide JSON response with:
        - translation: accurate translation
        - definition: definition in {target_lang}
        - examples: 3 examples in both languages
        - pronunciation: phonetic guide
        - difficulty: 1-5 scale
        - cultural_notes: cultural context if relevant
        """
        
        try:
            response = await self._generate_completion(prompt, system_prompt)
            result = json.loads(response)
            
            return {
                "word": {
                    "text": word,
                    "translation": result.get("translation", word),
                    "context": context,
                    "masteryLevel": mastery_level
                },
                "analysis": result,
                "config": {
                    "sourceLanguage": source_lang,
                    "targetLanguage": target_lang,
                    "userLevel": user_level
                }
            }
            
        except json.JSONDecodeError:
            return {
                "word": {
                    "text": word,
                    "translation": f"Translation of {word}",
                    "context": context,
                    "masteryLevel": mastery_level
                },
                "analysis": {
                    "definition": response[:200],
                    "examples": [f"Example with {word}"],
                    "difficulty": 3
                },
                "config": {
                    "sourceLanguage": source_lang,
                    "targetLanguage": target_lang,
                    "userLevel": user_level
                }
            }
    
    async def generate_flashcards(self, words_data: List[Dict], session_config: Dict) -> Dict[str, Any]:
        """Generate flashcards using Ollama"""
        system_prompt = """You are a flashcard generation expert. 
        Create effective, memorable flashcards for language learning."""
        
        words_list = [word.get("text", "") for word in words_data]
        
        prompt = f"""
        Generate flashcards for these words: {words_list}
        Session config: {json.dumps(session_config)}
        
        Create JSON response with:
        - flashcards: array of flashcard objects
        - each flashcard: front, back, difficulty, tags, hints
        - total_count: number of flashcards
        - estimated_time: study time estimate
        """
        
        try:
            response = await self._generate_completion(prompt, system_prompt)
            result = json.loads(response)
            
            return {
                "flashcards": result.get("flashcards", []),
                "totalCount": result.get("total_count", len(words_data)),
                "estimatedTime": result.get("estimated_time", len(words_data) * 2),
                "sessionConfig": session_config
            }
            
        except json.JSONDecodeError:
            # Generate basic flashcards as fallback
            flashcards = []
            for word_data in words_data:
                flashcards.append({
                    "front": word_data.get("text", ""),
                    "back": word_data.get("translation", ""),
                    "difficulty": 3,
                    "tags": ["vocabulary"],
                    "hints": [f"Remember the context: {word_data.get('context', '')}"]
                })
            
            return {
                "flashcards": flashcards,
                "totalCount": len(flashcards),
                "estimatedTime": len(flashcards) * 2,
                "sessionConfig": session_config
            }
    
    async def create_test(self, user_words: List[str], test_type: str, 
                         target_level: str, question_count: int) -> Dict[str, Any]:
        """Create adaptive test using Ollama"""
        system_prompt = f"""You are a language testing expert. 
        Create a {test_type} test for {target_level} level with {question_count} questions."""
        
        prompt = f"""
        Create test questions for words: {user_words}
        Test type: {test_type}
        Target level: {target_level}
        Question count: {question_count}
        
        Generate JSON with:
        - questions: array of question objects
        - each question: question, options, correct_answer, explanation
        - test_metadata: difficulty, estimated_time, scoring
        """
        
        try:
            response = await self._generate_completion(prompt, system_prompt)
            result = json.loads(response)
            
            return {
                "questions": result.get("questions", []),
                "testMetadata": result.get("test_metadata", {
                    "difficulty": target_level,
                    "estimatedTime": question_count * 1.5,
                    "totalQuestions": question_count
                }),
                "testType": test_type,
                "targetLevel": target_level
            }
            
        except json.JSONDecodeError:
            # Generate basic questions as fallback
            questions = []
            for i, word in enumerate(user_words[:question_count]):
                questions.append({
                    "question": f"What does '{word}' mean?",
                    "options": [f"Definition of {word}", "Wrong answer 1", "Wrong answer 2", "Wrong answer 3"],
                    "correct_answer": 0,
                    "explanation": f"'{word}' means..."
                })
            
            return {
                "questions": questions,
                "testMetadata": {
                    "difficulty": target_level,
                    "estimatedTime": len(questions) * 1.5,
                    "totalQuestions": len(questions)
                },
                "testType": test_type,
                "targetLevel": target_level
            }
    
    async def generate_recommendations(self, user_progress: Dict) -> Dict[str, Any]:
        """Generate learning recommendations using Ollama"""
        system_prompt = """You are a personalized learning advisor. 
        Analyze user progress and provide actionable learning recommendations."""
        
        prompt = f"""
        Analyze user progress: {json.dumps(user_progress)}
        
        Generate JSON recommendations with:
        - focus_areas: areas needing attention
        - suggested_activities: specific learning activities
        - difficulty_adjustment: recommended difficulty changes
        - study_schedule: optimal study timing
        - motivation_tips: encouragement and tips
        """
        
        try:
            response = await self._generate_completion(prompt, system_prompt)
            result = json.loads(response)
            
            return {
                "recommendations": result,
                "userProgress": user_progress,
                "generatedAt": "2024-01-01T00:00:00Z"  # Would use actual timestamp
            }
            
        except json.JSONDecodeError:
            return {
                "recommendations": {
                    "focus_areas": ["vocabulary", "grammar"],
                    "suggested_activities": ["flashcard review", "context practice"],
                    "difficulty_adjustment": "maintain current level",
                    "study_schedule": "15 minutes daily",
                    "motivation_tips": ["Practice regularly", "Use spaced repetition"]
                },
                "userProgress": user_progress,
                "generatedAt": "2024-01-01T00:00:00Z"
            }
    
    # === MLX EQUIVALENT HELPER METHODS ===
    
    def _get_language_config(self, source_lang: str, target_lang: str, learning_direction: str) -> Dict:
        """Get language configuration for multilingual support - MLX equivalent"""
        
        # Language name mappings
        lang_names = {
            'en': 'anglais',
            'fr': 'français',
            'es': 'espagnol',
            'de': 'allemand',
            'it': 'italien'
        }
        
        return {
            'source_name': lang_names.get(source_lang, source_lang),
            'target_name': lang_names.get(target_lang, target_lang),
            'learning_direction': learning_direction,
            'question_lang': target_lang,
            'answer_lang': source_lang if learning_direction.startswith(target_lang) else target_lang,
            'explanation_lang': target_lang
        }
    
    def _get_card_type_prompt(self, card_type: str, learning_direction: str) -> str:
        """Get specific prompt instructions for each card type - MLX equivalent"""
        
        if card_type == "classic":
            return self._get_classic_prompt(learning_direction)
        elif card_type == "contextual":
            return self._get_contextual_prompt(learning_direction)
        elif card_type == "audio":
            return self._get_audio_prompt(learning_direction)
        elif card_type == "speed":
            return self._get_speed_prompt(learning_direction)
        else:
            return self._get_classic_prompt(learning_direction)  # fallback
    
    def _get_classic_prompt(self, learning_direction: str) -> str:
        """Prompt for classic translation cards - MLX equivalent"""
        if learning_direction == "en->fr":
            return """
TYPE: CLASSIC - Traduction directe
- Question: mot anglais
- Réponse: traduction française
- Format simple et efficace
- Exemple: "apple" → "pomme"
"""
        elif learning_direction == "fr->en":
            return """
TYPE: CLASSIC - Direct translation
- Question: French word
- Answer: English translation
- Simple and effective format
- Example: "pomme" → "apple"
"""
        else:
            return "TYPE: CLASSIC - Basic translation card"
    
    def _get_contextual_prompt(self, learning_direction: str) -> str:
        """Prompt for contextual completion cards - MLX equivalent"""
        if learning_direction == "en->fr":
            return """
TYPE: CONTEXTUEL - Complétion de phrase
- Question: "Complete the sentence: '[phrase avec _____]'"
- OBLIGATOIRE: La question DOIT contenir _____ à la place du mot cible
- Réponse: le mot anglais original
- Options: [mot correct, distracteur1, distracteur2, distracteur3] TOUS EN ANGLAIS
- questionLanguage: "en", answerLanguage: "en"
- contextTranslation: traduction française de la phrase complète

EXEMPLES CORRECTS:
Question: "Complete the sentence: 'The movie was _____'"
Answer: "amazing"
Options: ["amazing", "terrible", "boring", "okay"]
contextTranslation: "Le film était incroyable"
"""
        elif learning_direction == "fr->en":
            return """
TYPE: CONTEXTUAL - Sentence completion
- Question: "Complete the sentence: '[sentence with _____]'"
- MANDATORY: Question MUST contain _____ in place of target word
- Answer: the original French word
- Options: [correct word, distractor1, distractor2, distractor3] ALL IN FRENCH
- questionLanguage: "fr", answerLanguage: "fr"
- contextTranslation: English translation of complete sentence
"""
        else:
            return """
TYPE: CONTEXTUAL - Sentence completion
- Question: Complete the sentence with missing word
- Answer: correct word in original language
- Options: [correct word, distractor1, distractor2, distractor3] in original language
"""
    
    def _get_audio_prompt(self, learning_direction: str) -> str:
        """Prompt for audio pronunciation cards - MLX equivalent"""
        return """
TYPE: AUDIO - Pronunciation focus
- Emphasize phonetic transcription
- Include pronunciation hints
"""
    
    def _get_speed_prompt(self, learning_direction: str) -> str:
        """Prompt for speed challenge cards - MLX equivalent"""
        return """
TYPE: SPEED - Quick recognition
- Simple, direct questions
- Focus on instant recognition
"""
    
    def _build_multilingual_prompt(self, words_list: str, available_types: List[str], 
                                 user_level: str, is_premium: bool, target_count: int,
                                 source_lang: str, target_lang: str, learning_direction: str,
                                 lang_config: Dict, schema: Dict, difficulty: str = "adaptive") -> str:
        """Build comprehensive multilingual prompt - MLX equivalent"""
        
        # Get type-specific instructions
        type_instructions = []
        for card_type in available_types:
            instruction = self._get_card_type_prompt(card_type, learning_direction)
            type_instructions.append(instruction)
        
        type_instructions_str = "\n".join(type_instructions)
        type_distribution = self._calculate_type_distribution(available_types, target_count)
        difficulty_instruction = self._get_difficulty_instruction(difficulty, user_level)
        
        return f"""
Génère {target_count} flashcards multilingues pour l'apprentissage {lang_config['source_name']} → {lang_config['target_name']}.

MOTS À TRAITER:
{words_list}

CONFIGURATION:
- Niveau utilisateur: {user_level}
- Direction d'apprentissage: {learning_direction}
- Types de cartes disponibles: {available_types}
- Distribution souhaitée: {type_distribution}
- Difficulté: {difficulty} {difficulty_instruction}
- Premium: {is_premium}

INSTRUCTIONS PAR TYPE:
{type_instructions_str}

RÈGLES IMPORTANTES:
1. Respecter EXACTEMENT le schéma JSON fourni
2. Générer exactement {target_count} cartes
3. Varier les types selon la distribution
4. Adapter la difficulté au niveau {user_level}
5. Utiliser les vrais mots et contextes fournis
6. Pour les cartes contextuelles: TOUJOURS utiliser _____ dans la question

Schéma JSON à respecter: {json.dumps(schema)}

Réponds UNIQUEMENT en JSON valide.
"""
    
    def _generate_fallback_card(self, word_data: Dict, card_id: str, card_type: str, 
                                  card_difficulty: str, source_lang: str, target_lang: str, 
                                  learning_direction: str) -> Dict:
        """Generate multilingual fallback card when AI fails - MLX equivalent"""
        
        word_text = word_data.get('text', 'unknown')
        word_translation = word_data.get('translation', f'traduction de {word_text}')
        word_context = word_data.get('context', f'contexte avec {word_text}')
        
        # Base card structure
        card = {
            "id": card_id,
            "type": card_type,
            "difficulty": card_difficulty,
            "tags": ["vocabulary", source_lang, target_lang],
            "hints": [f"Pensez au contexte: {word_context[:50]}..."],
            "options": []
        }
        
        # Generate card content based on type and direction
        if card_type == "classic":
            if learning_direction == "en->fr":
                card.update({
                    "front": word_text,
                    "back": word_translation,
                    "questionLanguage": "en",
                    "answerLanguage": "fr"
                })
            elif learning_direction == "fr->en":
                card.update({
                    "front": word_translation,
                    "back": word_text,
                    "questionLanguage": "fr",
                    "answerLanguage": "en"
                })
            else:
                card.update({
                    "front": word_text,
                    "back": word_translation,
                    "questionLanguage": source_lang,
                    "answerLanguage": target_lang
                })
        
        elif card_type == "contextual":
            # Create contextual sentence with blank
            if learning_direction == "en->fr":
                context_with_blank = word_context.replace(word_text, "_____", 1)
                if "_____" not in context_with_blank:
                    context_with_blank = f"The _____ is important in this context."
                
                card.update({
                    "front": f"Complete the sentence: '{context_with_blank}'",
                    "back": word_text,
                    "questionLanguage": "en",
                    "answerLanguage": "en",
                    "contextTranslation": f"Traduction: {word_context.replace(word_text, word_translation)}",
                    "options": [word_text, "wrong1", "wrong2", "wrong3"]
                })
            else:
                context_with_blank = word_context.replace(word_text, "_____", 1)
                if "_____" not in context_with_blank:
                    context_with_blank = f"Le _____ est important dans ce contexte."
                
                card.update({
                    "front": f"Complétez la phrase: '{context_with_blank}'",
                    "back": word_text,
                    "questionLanguage": target_lang,
                    "answerLanguage": source_lang,
                    "contextTranslation": f"Translation: {word_context}",
                    "options": [word_text, "mauvais1", "mauvais2", "mauvais3"]
                })
        
        elif card_type == "audio":
            card.update({
                "front": f"🔊 Pronunciation: {word_text}",
                "back": f"{word_translation} [/{word_text}/]",
                "questionLanguage": source_lang,
                "answerLanguage": target_lang,
                "pronunciation": f"/{word_text}/"
            })
        
        elif card_type == "speed":
            card.update({
                "front": word_text,
                "back": word_translation,
                "questionLanguage": source_lang,
                "answerLanguage": target_lang,
                "timeLimit": 3  # seconds for speed challenge
            })
        
        return card
    
    def _create_type_cycle(self, available_types: List[str], target_count: int) -> List[str]:
        """Create a cycle of card types for the requested count - MLX equivalent"""
        if not available_types:
            return ["classic"] * target_count
        
        cycle = []
        for i in range(target_count):
            cycle.append(available_types[i % len(available_types)])
        return cycle
    
    def _determine_card_difficulty(self, difficulty_setting: str, user_level: str, card_index: int, total_cards: int) -> str:
        """Determine individual card difficulty based on settings - MLX equivalent"""
        if difficulty_setting == "easy":
            return "easy"
        elif difficulty_setting == "hard":
            return "hard"
        elif difficulty_setting == "adaptive":
            # Progressive difficulty
            progress = card_index / total_cards
            if progress < 0.3:
                return "easy"
            elif progress < 0.7:
                return "medium"
            else:
                return "hard"
        else:  # medium or default
            return "medium"
    
    def _get_difficulty_instruction(self, difficulty: str, user_level: str) -> str:
        """Get difficulty-specific instructions for AI - MLX equivalent"""
        if difficulty == "easy":
            return "(Questions simples, plus d'indices, vocabulaire de base)"
        elif difficulty == "hard":
            return "(Questions complexes, moins d'indices, vocabulaire avancé)"
        else:
            return "(Difficulté équilibrée)"
    
    def _calculate_type_distribution(self, available_types: List[str], target_count: int) -> str:
        """Calculate and format type distribution - MLX equivalent"""
        if not available_types:
            return "classic: 100%"
        
        distribution = {}
        for i, card_type in enumerate(available_types):
            count = target_count // len(available_types)
            if i < target_count % len(available_types):
                count += 1
            percentage = (count / target_count) * 100
            distribution[card_type] = f"{percentage:.0f}%"
        
        return ", ".join([f"{k}: {v}" for k, v in distribution.items()])
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # AsyncClient from ollama doesn't need explicit closing
        pass
