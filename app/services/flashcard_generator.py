import random
import uuid
from typing import Dict, List, Optional
from app.core.config import settings


class FlashcardGenerator:
    """Advanced flashcard generation with 4 types and intelligent distractors"""
    
    def __init__(self):
        self.base_audio_url = "https://api.netflix-english-learner.com/audio"
    
    def select_card_type(self, mastery_level: str, available_types: List[str], is_premium: bool) -> str:
        """Select appropriate card type based on mastery level and premium status"""
        
        # Filter premium types if not premium user
        if not is_premium:
            available_types = [t for t in available_types if t in ["classic", "contextual"]]
        
        # Adaptive selection based on mastery
        if mastery_level == "NEW":
            return "classic" if "classic" in available_types else available_types[0]
        elif mastery_level == "LEARNING":
            return "contextual" if "contextual" in available_types else available_types[0]
        elif mastery_level == "FAMILIAR":
            return "audio" if "audio" in available_types else "contextual"
        else:  # MASTERED
            return "speed" if "speed" in available_types else "audio"
    
    def generate_classic_card(self, word_data: Dict, card_id: str, user_level: str) -> Dict:
        """Generate classic translation flashcard (FREE)"""
        
        # Select subtype based on user level
        subtypes = ["translation_to_french", "french_to_english", "definition_match", "synonym_match"]
        subtype = random.choice(subtypes[:2])  # Focus on translation for beginners
        
        if subtype == "translation_to_french":
            question = f"Que signifie '{word_data['text']}' ?"
            answer = word_data.get('translation', 'traduction')
            distractors = self._generate_translation_distractors(answer, user_level)
        elif subtype == "french_to_english":
            question = f"Comment dit-on '{word_data.get('translation', 'traduction')}' en anglais ?"
            answer = word_data['text']
            distractors = self._generate_english_distractors(answer, user_level)
        elif subtype == "definition_match":
            question = word_data.get('definition', f"Definition of {word_data['text']}")
            answer = word_data['text']
            distractors = self._generate_word_distractors(answer, user_level)
        else:  # synonym_match
            question = f"Quel est un synonyme de '{word_data['text']}' ?"
            answer = "synonym"  # Would need synonym data
            distractors = ["option1", "option2", "option3"]
        
        options = [answer] + distractors[:3]
        random.shuffle(options)
        
        return {
            "id": card_id,
            "wordId": f"word_{word_data['text']}",
            "type": "classic",
            "subType": subtype,
            "question": question,
            "answer": answer,
            "options": options,
            "hints": [f"C'est un mot de niveau {user_level}"],
            "explanation": f"'{word_data['text']}' signifie '{word_data.get('translation', 'traduction')}'",
            "difficulty": self._map_level_to_difficulty(user_level),
            "timeLimit": 15000,
            "points": 10
        }
    
    def generate_contextual_card(self, word_data: Dict, card_id: str, user_level: str) -> Dict:
        """Generate contextual flashcard with fill-in-blank (RECOMMENDED)"""
        
        context = word_data.get('context', f"Example with {word_data['text']}")
        word = word_data['text']
        
        # Create fill-in-blank from context
        if word.lower() in context.lower():
            blank_context = context.replace(word, "_____", 1)
        else:
            blank_context = f"_____, how are you today?"
            context = f"{word}, how are you today?"
        
        subtypes = ["fill_in_blank", "context_completion", "situation_match"]
        subtype = random.choice(subtypes)
        
        if subtype == "fill_in_blank":
            question = f"Complétez la phrase : '{blank_context}'"
            answer = word
            distractors = self._generate_contextual_distractors(word, context, user_level)
        elif subtype == "context_completion":
            question = f"Dans cette situation : '{context}', quel mot convient le mieux ?"
            answer = word
            distractors = self._generate_situational_distractors(word, user_level)
        else:  # situation_match
            question = f"Quelle situation correspond à '{word}' ?"
            answer = "Saluer quelqu'un"
            distractors = ["Dire au revoir", "Remercier", "S'excuser"]
        
        options = [answer] + distractors[:3]
        random.shuffle(options)
        
        return {
            "id": card_id,
            "wordId": f"word_{word_data['text']}",
            "type": "contextual",
            "subType": subtype,
            "question": question,
            "answer": answer,
            "options": options,
            "context": blank_context,
            "originalContext": context,
            "contextExplanation": f"Dans cette situation, on utilise '{word}' pour {self._get_context_explanation(word)}",
            "difficulty": self._map_level_to_difficulty(user_level),
            "timeLimit": 20000,
            "points": 15
        }
    
    def generate_audio_card(self, word_data: Dict, card_id: str, user_level: str) -> Dict:
        """Generate audio pronunciation flashcard (PREMIUM)"""
        
        word = word_data['text']
        subtypes = ["pronunciation_recognition", "listen_translate", "accent_identification", "speed_variation"]
        subtype = random.choice(subtypes[:2])  # Focus on main audio features
        
        if subtype == "pronunciation_recognition":
            question = "Écoutez et choisissez la bonne traduction"
            answer = word_data.get('translation', 'traduction')
            distractors = self._generate_translation_distractors(answer, user_level)
        else:  # listen_translate
            question = "Écoutez et écrivez ce que vous entendez"
            answer = word
            distractors = self._generate_phonetic_distractors(word, user_level)
        
        options = [answer] + distractors[:3]
        random.shuffle(options)
        
        return {
            "id": card_id,
            "wordId": f"word_{word_data['text']}",
            "type": "audio",
            "subType": subtype,
            "question": question,
            "answer": answer,
            "options": options,
            "audioUrl": f"{self.base_audio_url}/{word}_native.mp3",
            "phonetic": f"/{word}/",  # Would need real IPA
            "audioMetadata": {
                "accent": "american",
                "speed": "normal",
                "gender": random.choice(["male", "female"])
            },
            "difficulty": self._map_level_to_difficulty(user_level),
            "timeLimit": 25000,
            "points": 20
        }
    
    def generate_speed_card(self, word_data: Dict, card_id: str, user_level: str) -> Dict:
        """Generate speed flashcard for rapid practice (PREMIUM)"""
        
        word = word_data['text']
        subtypes = ["rapid_translation", "flash_memory", "speed_chain", "rapid_fire"]
        subtype = random.choice(subtypes[:2])
        
        if subtype == "rapid_translation":
            question = word
            answer = word_data.get('translation', 'traduction')
            show_time = 2000
            response_time = 3000
        else:  # flash_memory
            question = f"Mémorisez: {word} = {word_data.get('translation', 'traduction')}"
            answer = word_data.get('translation', 'traduction')
            show_time = 3000
            response_time = 2000
        
        return {
            "id": card_id,
            "wordId": f"word_{word_data['text']}",
            "type": "speed",
            "subType": subtype,
            "question": question,
            "answer": answer,
            "showTime": show_time,
            "responseTime": response_time,
            "difficulty": "hard",
            "timeLimit": show_time + response_time,
            "points": 50,
            "speedBonus": True
        }
    
    def _generate_translation_distractors(self, correct_answer: str, user_level: str) -> List[str]:
        """Generate intelligent French translation distractors"""
        # Common French words that could confuse learners
        common_distractors = {
            "bonjour": ["bonsoir", "au revoir", "salut"],
            "au revoir": ["bonjour", "à bientôt", "merci"],
            "merci": ["pardon", "s'il vous plaît", "de rien"],
            "oui": ["non", "peut-être", "bien sûr"],
            "non": ["oui", "jamais", "pas du tout"]
        }
        
        if correct_answer.lower() in common_distractors:
            return common_distractors[correct_answer.lower()]
        
        # Fallback distractors
        return ["option1", "option2", "option3"]
    
    def _generate_english_distractors(self, correct_answer: str, user_level: str) -> List[str]:
        """Generate intelligent English word distractors"""
        common_distractors = {
            "hello": ["goodbye", "thanks", "sorry"],
            "goodbye": ["hello", "welcome", "please"],
            "thank you": ["excuse me", "you're welcome", "sorry"],
            "yes": ["no", "maybe", "sure"],
            "no": ["yes", "never", "not at all"]
        }
        
        if correct_answer.lower() in common_distractors:
            return common_distractors[correct_answer.lower()]
        
        return ["word1", "word2", "word3"]
    
    def _generate_contextual_distractors(self, word: str, context: str, user_level: str) -> List[str]:
        """Generate contextual distractors based on situation"""
        if "hello" in word.lower():
            return ["goodbye", "thanks", "sorry"]
        elif "thank" in word.lower():
            return ["hello", "goodbye", "excuse me"]
        else:
            return ["option1", "option2", "option3"]
    
    def _generate_situational_distractors(self, word: str, user_level: str) -> List[str]:
        """Generate situation-based distractors"""
        return ["situation1", "situation2", "situation3"]
    
    def _generate_phonetic_distractors(self, word: str, user_level: str) -> List[str]:
        """Generate phonetically similar word distractors"""
        phonetic_similar = {
            "hello": ["halo", "hollow", "hero"],
            "goodbye": ["good buy", "good by", "good bye"],
            "thank": ["think", "thick", "thunk"]
        }
        
        if word.lower() in phonetic_similar:
            return phonetic_similar[word.lower()]
        
        return ["sound1", "sound2", "sound3"]
    
    def _generate_word_distractors(self, word: str, user_level: str) -> List[str]:
        """Generate word-level distractors"""
        return ["word1", "word2", "word3"]
    
    def _map_level_to_difficulty(self, user_level: str) -> str:
        """Map CEFR level to difficulty"""
        mapping = {
            "A1": "easy",
            "A2": "easy", 
            "B1": "medium",
            "B2": "medium",
            "C1": "hard",
            "C2": "hard"
        }
        return mapping.get(user_level, "medium")
    
    def _get_context_explanation(self, word: str) -> str:
        """Get contextual explanation for word usage"""
        explanations = {
            "hello": "saluer quelqu'un",
            "goodbye": "dire au revoir",
            "thank": "remercier",
            "sorry": "s'excuser"
        }
        return explanations.get(word.lower(), "communiquer")


# Singleton instance
flashcard_generator = FlashcardGenerator()
