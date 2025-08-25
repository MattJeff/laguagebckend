import ollama
import json
from typing import Dict, List, Optional
from app.core.config import settings


class AIService:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.OLLAMA_MODEL

    async def analyze_word(self, word: str, context: str, langue_output: str = "fr", user_level: str = None) -> Dict:
        """Analyze a word using Llama for French learners with contextual intelligence"""
        
        level_guidance = ""
        if user_level:
            level_guidance = f"Adapt explanation complexity for {user_level} level learner."
        
        prompt = f"""
        Analyze the English word "{word}" in context: "{context}" for French learners.
        {level_guidance}
        
        Provide a JSON response with this EXACT structure:
        {{
            "translation": "French translation (contextual)",
            "definition": "Clear English definition",
            "difficulty": "A1|A2|B1|B2|C1|C2",
            "partOfSpeech": "noun|verb|adjective|adverb|etc",
            "synonyms": ["synonym1", "synonym2", "synonym3"],
            "examples": [
                "Example sentence 1 with {word}",
                "Example sentence 2 with {word}"
            ],
            "pronunciation": "/IPA notation/",
            "frequency": "very_common|common|uncommon|rare",
            "contextualMeaning": "greeting_formal|action_past|emotion_positive|etc"
        }}
        
        Rules:
        - Translation must be contextually accurate for French speakers
        - Definition in simple English appropriate for language learners
        - Difficulty follows CEFR levels (A1=basic, C2=advanced)
        - Provide 3 useful synonyms of similar difficulty
        - Examples show different contexts and usage patterns
        - ContextualMeaning categorizes the word's semantic role
        
        Respond ONLY with valid JSON.
        """
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.3}
            )
            
            # Parse the JSON response
            result = json.loads(response['message']['content'])
            return result
            
        except Exception as e:
            # Fallback response if AI fails
            return {
                "translation": "traduction",
                "definition": f"Definition for {word}",
                "difficulty": "A2",
                "partOfSpeech": "unknown",
                "synonyms": [],
                "examples": [f"Example with {word}"],
                "pronunciation": f"/{word}/",
                "frequency": "common",
                "contextualMeaning": "general",
                "error": str(e)
            }

    async def generate_flashcards(self, words_data: List[Dict], session_config: Dict) -> Dict:
        """Generate 4 types of intelligent flashcards with adaptive selection"""
        from app.services.flashcard_generator import flashcard_generator
        import uuid
        
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        cards = []
        difficulty_count = {"easy": 0, "medium": 0, "hard": 0}
        
        # Extract session configuration
        available_types = session_config.get('types', ['classic', 'contextual'])
        user_level = session_config.get('userLevel', 'A2')
        is_premium = session_config.get('isPremium', False)
        target_count = session_config.get('count', 10)
        
        # Generate cards for each word
        for i, word_data in enumerate(words_data[:target_count]):
            card_id = f"card_{i+1}"
            mastery_level = word_data.get('masteryLevel', 'NEW')
            
            # Select appropriate card type
            card_type = flashcard_generator.select_card_type(
                mastery_level, available_types, is_premium
            )
            
            # Generate card based on type
            if card_type == "classic":
                card = flashcard_generator.generate_classic_card(word_data, card_id, user_level)
            elif card_type == "contextual":
                card = flashcard_generator.generate_contextual_card(word_data, card_id, user_level)
            elif card_type == "audio" and is_premium:
                card = flashcard_generator.generate_audio_card(word_data, card_id, user_level)
            elif card_type == "speed" and is_premium:
                card = flashcard_generator.generate_speed_card(word_data, card_id, user_level)
            else:
                # Fallback to classic if premium type requested but not available
                card = flashcard_generator.generate_classic_card(word_data, card_id, user_level)
            
            cards.append(card)
            difficulty_count[card.get('difficulty', 'medium')] += 1
        
        # Calculate estimated time
        total_time = sum(card.get('timeLimit', 15000) for card in cards) // 1000
        
        return {
            "sessionId": session_id,
            "cards": cards,
            "metadata": {
                "totalCards": len(cards),
                "estimatedTime": total_time,
                "difficultyMix": {
                    "easy": difficulty_count.get("easy", 0),
                    "medium": difficulty_count.get("medium", 0),
                    "hard": difficulty_count.get("hard", 0)
                }
            }
        }

    async def generate_test_questions(self, user_words: List[str], test_type: str = "vocabulary_review", target_level: str = "A2", question_count: int = 10) -> Dict:
        """Generate adaptive test questions with CEFR level targeting"""
        
        words_list = "\n".join([f"- {word}" for word in user_words])
        
        prompt = f"""
        Create an adaptive {test_type} test for French learners at {target_level} level.
        Use these English words from the user's vocabulary:
        {words_list}
        
        Generate {question_count} questions with this EXACT structure:
        {{
            "questions": [
                {{
                    "id": "q1",
                    "type": "multiple_choice|fill_blank|context_completion",
                    "question": "Question text (in French for translations)",
                    "answer": "Correct answer",
                    "options": ["correct", "distractor1", "distractor2", "distractor3"],
                    "difficulty": "A1|A2|B1|B2|C1|C2",
                    "explanation": "Brief explanation in French"
                }}
            ],
            "estimatedTime": 300
        }}
        
        Question Types:
        - multiple_choice: "Que signifie 'hello' ?" with 4 options
        - fill_blank: "Complete: Hello, ___ are you?" 
        - context_completion: "In 'Hello world', 'hello' is a ___"
        
        Rules:
        - Target {target_level} difficulty level
        - Create intelligent distractors (similar words, common mistakes)
        - Progressive difficulty within the test
        - Questions in French for translation exercises
        - Explanations help learning, not just correction
        - Estimate 30 seconds per question
        
        Respond ONLY with valid JSON.
        """
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.4}
            )
            
            result = json.loads(response['message']['content'])
            return result
            
        except Exception as e:
            # Fallback test
            questions = []
            for i, word in enumerate(user_words[:question_count]):
                questions.append({
                    "id": f"q{i+1}",
                    "type": "multiple_choice",
                    "question": f"Que signifie '{word}' ?",
                    "answer": "traduction",
                    "options": ["traduction", "option1", "option2", "option3"],
                    "difficulty": target_level,
                    "explanation": f"'{word}' signifie 'traduction'"
                })
            
            return {
                "questions": questions,
                "estimatedTime": question_count * 30,
                "error": str(e)
            }

    async def generate_recommendations(self, user_progress: Dict) -> Dict:
        """Generate personalized learning recommendations based on user progress"""
        
        progress_summary = f"""
        Total words: {user_progress.get('totalWords', 0)}
        Mastered words: {user_progress.get('masteredWords', 0)}
        Weak areas: {', '.join(user_progress.get('weakAreas', []))}
        Average accuracy: {user_progress.get('averageAccuracy', 0)}%
        """
        
        prompt = f"""
        Analyze this French learner's progress and provide personalized recommendations:
        {progress_summary}
        
        Generate a JSON response with this EXACT structure:
        {{
            "recommendations": [
                {{
                    "type": "word_to_learn|exercise_type|review_session",
                    "content": "Specific recommendation text",
                    "priority": "high|medium|low",
                    "reason": "Why this recommendation is important"
                }}
            ]
        }}
        
        Recommendation Types:
        - word_to_learn: Suggest specific vocabulary to focus on
        - exercise_type: Recommend specific practice methods
        - review_session: Suggest review patterns or timing
        
        Rules:
        - Identify learning gaps from weak areas
        - Prioritize based on accuracy and mastery levels
        - Provide actionable, specific recommendations
        - Focus on areas that will improve overall progress
        - Maximum 5 recommendations, ordered by priority
        
        Respond ONLY with valid JSON.
        """
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.3}
            )
            
            result = json.loads(response['message']['content'])
            return result
            
        except Exception as e:
            # Fallback recommendations
            return {
                "recommendations": [
                    {
                        "type": "review_session",
                        "content": "Practice your weakest words daily for 10 minutes",
                        "priority": "high",
                        "reason": "Regular review improves retention"
                    }
                ],
                "error": str(e)
            }


# Singleton instance
ai_service = AIService()
