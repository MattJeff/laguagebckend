"""Groq API Service for fast, free AI inference."""
import json
from typing import Dict, List, Any
from groq import AsyncGroq
import httpx
from app.core.config import settings


class GroqService:
    """AI Service using Groq API for fast, free inference"""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.client = AsyncGroq(api_key=self.api_key)
        self.fallback_model = settings.GROQ_FALLBACK_MODEL
        self.base_url = "https://api.groq.com/openai/v1"
    
    def get_engine_name(self) -> str:
        """Return the engine name for health checks"""
        return "Groq"
    
    async def _generate_completion(self, prompt: str, system_prompt: str = "") -> str:
        """Generate completion using Groq API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 8000,
            "temperature": 0.3
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise Exception(f"Groq API failed: {str(e)}")
    
    async def analyze_word(self, word: str, context: str, langue_output: str = "fr", user_level: str = "A2") -> Dict[str, Any]:
        """Analyze a word using Groq for French learners"""
        
        level_guidance = ""
        if user_level:
            level_guidance = f"Adapte la complexité pour un apprenant de niveau {user_level}."
        
        schema = {
            "word": word,
            "translation": "Traduction française contextuelle",
            "definition": "Définition claire et simple",
            "difficulty": "A1|A2|B1|B2|C1|C2",
            "cefr_level": "A1|A2|B1|B2|C1|C2",
            "context_analysis": "Analyse du mot dans ce contexte",
            "usage_examples": ["Exemple 1", "Exemple 2"],
            "synonyms": ["synonyme1", "synonyme2"],
            "etymology": "Origine du mot (optionnel)"
        }
        
        prompt = f"""
Analyse le mot anglais "{word}" dans ce contexte : "{context}" pour des apprenants {langue_output}.
{level_guidance}

Produis un objet JSON conforme au schéma suivant. Toutes les clés doivent être renseignées.

SCHÉMA:
{json.dumps(schema, indent=2, ensure_ascii=False)}

RÈGLES:
- Traduction contextuelle précise pour francophones
- Définition en anglais simple pour apprenants
- Difficulté selon CEFR (A1=basique, C2=avancé)
- 3 synonymes utiles de difficulté similaire
- Exemples montrant différents contextes d'usage

Ne retourne AUCUN autre texte que le JSON.
"""
        
        try:
            response = await self._generate_completion(prompt, "")
            # Try to parse JSON
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # Fallback response
            return {
                "word": word,
                "translation": "Traduction automatique",
                "definition": f"Définition de '{word}' non disponible",
                "difficulty": user_level or "A2",
                "cefr_level": user_level or "A2",
                "context_analysis": f"Analyse contextuelle de '{word}' dans: {context}",
                "usage_examples": [f"Exemple d'usage de '{word}'"],
                "synonyms": ["synonyme1", "synonyme2"],
                "etymology": f"Étymologie de '{word}' non disponible"
            }
    
    async def translate_and_analyze_word(self, word: str, context: str, source_lang: str, 
                                       target_lang: str, user_level: str, mastery_level: str) -> Dict[str, Any]:
        """AI auto-translates unknown word and provides complete analysis"""
        
        schema = {
            "word": word,
            "translation": "Traduction principale",
            "alternativeTranslations": ["traduction1", "traduction2"],
            "contextTranslation": "Phrase traduite complète",
            "definition": "Définition claire",
            "difficulty": "A1|A2|B1|B2|C1|C2",
            "cefr_level": "A1|A2|B1|B2|C1|C2",
            "contextAnalysis": {
                "originalSentence": context,
                "translatedSentence": "Phrase traduite",
                "grammarNotes": "Notes grammaticales",
                "usage": "Usage contextuel"
            },
            "learningData": {
                "synonyms": ["synonym1", "synonym2"],
                "relatedWords": ["mot1", "mot2"],
                "commonPhrases": ["phrase1", "phrase2"]
            },
            "flashcardSuggestion": {
                "question": "Question suggérée",
                "answer": "Réponse",
                "options": ["option1", "option2", "option3", "option4"],
                "hint": "Indice utile",
                "explanation": "Explication pédagogique"
            }
        }
        
        prompt = f"""
Traduis et analyse le mot "{word}" de {source_lang} vers {target_lang}.
Contexte: "{context}"
Niveau utilisateur: {user_level}
Niveau maîtrise: {mastery_level}

Produis un objet JSON complet conforme au schéma suivant:

SCHÉMA:
{json.dumps(schema, indent=2, ensure_ascii=False)}

RÈGLES:
- Traduis le mot dans le contexte donné
- Traduis aussi la phrase complète
- Adapte la complexité au niveau {user_level}
- Fournis des exemples d'usage pertinents
- Suggère une question de flashcard adaptée

Ne retourne AUCUN autre texte que le JSON.
"""
        
        try:
            response = await self._generate_completion(prompt, "")
            result = json.loads(response)
            
            # Validate and fix None values
            if result.get("word") is None:
                result["word"] = word
            if result.get("translation") is None:
                result["translation"] = f"Traduction de {word}"
            if result.get("definition") is None:
                result["definition"] = f"Définition de {word}"
            if result.get("difficulty") is None:
                result["difficulty"] = user_level or "A2"
            if result.get("cefr_level") is None:
                result["cefr_level"] = user_level or "A2"
            
            # Fix nested objects
            if result.get("contextAnalysis") is None:
                result["contextAnalysis"] = {}
            if result.get("learningData") is None:
                result["learningData"] = {}
            if result.get("flashcardSuggestion") is None:
                result["flashcardSuggestion"] = {}
            
            return result
        except Exception as e:
            # Fallback response
            return {
                "word": word,
                "translation": f"Traduction de {word}",
                "alternativeTranslations": [f"Alt traduction {word}"],
                "contextTranslation": f"Traduction du contexte: {context}",
                "definition": f"Définition de {word}",
                "difficulty": user_level or "A2",
                "cefr_level": user_level or "A2",
                "contextAnalysis": {
                    "originalSentence": context,
                    "translatedSentence": f"Traduction de: {context}",
                    "grammarNotes": "Notes grammaticales non disponibles",
                    "usage": "Usage contextuel"
                },
                "learningData": {
                    "synonyms": ["synonyme1", "synonyme2"],
                    "relatedWords": ["mot1", "mot2"],
                    "commonPhrases": ["phrase1", "phrase2"]
                },
                "flashcardSuggestion": {
                    "question": f"Que signifie '{word}' ?",
                    "answer": f"Traduction de {word}",
                    "options": ["option1", "option2", "option3", "option4"],
                    "hint": f"Indice pour {word}",
                    "explanation": f"Explication pour {word}"
                }
            }
    
    def _get_basic_translation(self, word: str) -> str:
        """Basic translations for common words"""
        translations = {
            "she": "elle", "he": "il", "you": "tu/vous", "I": "je", "we": "nous", "they": "ils/elles",
            "hello": "bonjour", "goodbye": "au revoir", "yes": "oui", "no": "non", "please": "s'il vous plaît",
            "thank": "merci", "sorry": "désolé", "house": "maison", "car": "voiture", "book": "livre",
            "water": "eau", "food": "nourriture", "time": "temps", "day": "jour", "night": "nuit",
            "good": "bon", "bad": "mauvais", "big": "grand", "small": "petit", "new": "nouveau",
            "old": "vieux", "hot": "chaud", "cold": "froid", "happy": "heureux", "sad": "triste",
            "love": "amour", "hate": "haine", "work": "travail", "play": "jouer", "eat": "manger",
            "drink": "boire", "sleep": "dormir", "walk": "marcher", "run": "courir", "stop": "arrêter",
            "go": "aller", "come": "venir", "see": "voir", "hear": "entendre", "speak": "parler",
            "duet": "duo", "courthouse": "tribunal", "grunting": "grognement"
        }
        return translations.get(word.lower(), f"traduction de {word}")
    
    def _get_contextual_distractors(self, answer: str) -> List[str]:
        """Generate contextual distractors for fill-in-blank questions"""
        # Contextual distractors based on word type and context
        common_distractors = {
            "think": ["believe", "know", "feel"],
            "arm": ["hand", "leg", "foot"],
            "decaf": ["regular", "strong", "black"],
            "of": ["from", "with", "by"],
            "don't": ["can't", "won't", "shouldn't"],
            "motto": ["slogan", "phrase", "saying"],
            "tiger": ["lion", "leopard", "panther"],
            "tear": ["rip", "break", "cut"],
            "bored": ["tired", "excited", "happy"],
            "hello": ["goodbye", "thanks", "sorry"],
            "world": ["planet", "earth", "globe"],
            "love": ["hate", "like", "enjoy"],
            "book": ["magazine", "newspaper", "novel"],
            "water": ["juice", "milk", "coffee"],
            "groaning": ["moaning", "crying", "shouting"],
            "brainless": ["mindless", "thoughtless", "careless"],
            "fantasy": ["reality", "dream", "story"],
            "applause": ["silence", "booing", "cheering"]
        }
        
        if answer.lower() in common_distractors:
            return common_distractors[answer.lower()]
        else:
            # Better generic distractors based on word length and type
            if len(answer) <= 4:
                return ["word", "item", "thing"]
            elif answer.endswith("ing"):
                return ["running", "walking", "talking"]
            elif answer.endswith("ed"):
                return ["played", "worked", "lived"]
            else:
                return ["something", "anything", "nothing"]

    def _get_distractor_option(self, word: str, index: int) -> str:
        """Generate realistic distractor options"""
        distractors = [
            ["famille", "ami", "maison", "temps"],
            ["bonjour", "merci", "eau", "livre"], 
            ["grand", "petit", "bon", "nouveau"],
            ["aller", "voir", "manger", "parler"]
        ]
        return distractors[index-1][hash(word) % 4]
    
    def _fix_json_syntax(self, json_str: str) -> str:
        """Fix common JSON syntax errors from Groq responses"""
        import re
        
        # Remove trailing commas before closing brackets/braces
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix missing commas between objects in arrays
        json_str = re.sub(r'}\s*{', r'},{', json_str)
        
        # Fix missing commas between array elements
        json_str = re.sub(r']\s*\[', r'],[', json_str)
        
        # Fix missing commas after closing braces/brackets when followed by quotes
        json_str = re.sub(r'}\s*"', r'},"', json_str)
        json_str = re.sub(r']\s*"', r'],"', json_str)
        
        # Fix missing commas after string values when followed by quotes
        json_str = re.sub(r'"\s*"([^"]*)":', r'","\1":', json_str)
        
        # Fix malformed structure - remove orphaned values and fix property order
        lines = json_str.split('\n')
        fixed_lines = []
        in_object = False
        in_array = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Track object/array state
            if '{' in line:
                in_object = True
            if '}' in line:
                in_object = False
            if '[' in line:
                in_array = True
            if ']' in line:
                in_array = False
                
            # Skip orphaned values (strings not part of key-value pairs)
            if in_object and '"' in line and ':' not in line and not line.endswith(',') and not line.endswith('{') and not line.endswith('}'):
                continue
                
            fixed_lines.append(line)
        
        json_str = '\n'.join(fixed_lines)
        
        # Final cleanup - ensure proper comma placement
        json_str = re.sub(r'"\s*\n\s*"', '",\n"', json_str)
        json_str = re.sub(r'}\s*\n\s*"', '},\n"', json_str)
        json_str = re.sub(r']\s*\n\s*"', '],\n"', json_str)
        
        return json_str
    
    def _rebuild_json_structure(self, json_str: str, target_count: int = 5) -> str:
        """Rebuild JSON structure from scrambled Groq response"""
        import re
        
        # Extract session ID
        session_id_match = re.search(r'"sessionId":\s*"([^"]*)"', json_str)
        session_id = session_id_match.group(1) if session_id_match else "session_generated"
        
        # Extract individual card properties using regex
        cards = []
        
        # Find all card IDs to determine how many cards we have
        card_ids = re.findall(r'"id":\s*"(card_\d+)"', json_str)
        print(f"[DEBUG] Found card IDs in JSON: {card_ids}")
        print(f"[DEBUG] Expected {target_count} cards, found {len(card_ids)} card IDs")
        
        for card_id in card_ids:
            card = {"id": card_id}
            
            # Extract properties for this card by finding patterns near the card ID
            # This is a more robust approach for scrambled JSON
            
            # Find wordId
            wordid_pattern = rf'(?:.*{re.escape(card_id)}.*?"wordId":\s*"([^"]*)")|(?:"wordId":\s*"([^"]*)".*?{re.escape(card_id)})'
            wordid_match = re.search(wordid_pattern, json_str, re.DOTALL)
            if wordid_match:
                card["wordId"] = wordid_match.group(1) or wordid_match.group(2)
            
            # Extract question
            question_pattern = rf'(?:.*{re.escape(card_id)}.*?"question":\s*"([^"]*)")|(?:"question":\s*"([^"]*)".*?{re.escape(card_id)})'
            question_match = re.search(question_pattern, json_str, re.DOTALL)
            if question_match:
                card["question"] = question_match.group(1) or question_match.group(2)
            
            # Extract answer
            answer_pattern = rf'(?:.*{re.escape(card_id)}.*?"answer":\s*"([^"]*)")|(?:"answer":\s*"([^"]*)".*?{re.escape(card_id)})'
            answer_match = re.search(answer_pattern, json_str, re.DOTALL)
            if answer_match:
                card["answer"] = answer_match.group(1) or answer_match.group(2)
            
            # Extract options array
            options_pattern = rf'(?:.*{re.escape(card_id)}.*?"options":\s*\[([^\]]*)\])|(?:"options":\s*\[([^\]]*)\].*?{re.escape(card_id)})'
            options_match = re.search(options_pattern, json_str, re.DOTALL)
            if options_match:
                options_str = options_match.group(1) or options_match.group(2)
                # Parse options
                options = re.findall(r'"([^"]*)"', options_str)
                card["options"] = options[:4]  # Limit to 4 options
            
            # Set default values
            card.setdefault("type", "contextual")
            card.setdefault("subType", "fill_in_blank")
            card.setdefault("hints", [])
            card.setdefault("explanation", "")
            card.setdefault("difficulty", "medium")
            card.setdefault("timeLimit", 15000)
            card.setdefault("points", 10)
            card.setdefault("questionLanguage", "en")
            card.setdefault("answerLanguage", "en")
            card.setdefault("contextTranslation", "")
            
            # Only add card if it has essential fields
            if "question" in card and "answer" in card:
                cards.append(card)
                print(f"[DEBUG] Rebuilt card: {card['id']} - {card.get('question', 'No question')[:50]}...")
        
        rebuilt_json = {
            "sessionId": session_id,
            "cards": cards,
            "metadata": {
                "totalCards": len(cards),
                "estimatedTime": len(cards) * 15,
                "difficultyMix": {"easy": len(cards), "medium": 0, "hard": 0}
            }
        }
        
        print(f"[DEBUG] Successfully rebuilt {len(cards)} cards from scrambled JSON")
        print(f"[DEBUG] Expected {target_count} cards, got {len(cards)} cards")
        if len(cards) < target_count:
            print(f"[DEBUG] Missing {target_count - len(cards)} cards - Groq may have generated incomplete JSON")
        return json.dumps(rebuilt_json, ensure_ascii=False)

    async def generate_flashcards(self, words_data: List[Dict], session_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate flashcards using Groq with same interface as MLX"""
        
        # Extract configuration
        available_types = session_config.get('types', ['classic', 'contextual'])
        user_level = session_config.get('userLevel', 'A2')
        requested_count = session_config.get('count', 10)
        target_count = min(requested_count, len(words_data))
        selected_words = words_data[:target_count]
        
        source_lang = session_config.get('sourceLanguage', 'en')
        target_lang = session_config.get('targetLanguage', 'fr')
        
        words_list = "\n".join([
            f"- {w['text']}: {w.get('translation') or 'À traduire'} (maîtrise: {w.get('masteryLevel', 'NEW')})"
            for w in selected_words
        ])
        
        schema = {
            "sessionId": "session_id_généré",
            "cards": [
                {
                    "id": "card_1",
                    "wordId": "word_hello",
                    "type": "classic|contextual|audio|speed",
                    "subType": "translation_to_native|translation_to_target|fill_in_blank",
                    "question": "Texte de la question",
                    "answer": "Réponse correcte",
                    "options": ["correct", "distracteur1", "distracteur2", "distracteur3"],
                    "hints": ["indice 1", "indice 2"],
                    "explanation": "Explication de la réponse",
                    "difficulty": "easy|medium|hard",
                    "timeLimit": 15000,
                    "points": 10,
                    "questionLanguage": source_lang,
                    "answerLanguage": target_lang
                }
            ],
            "metadata": {
                "totalCards": target_count,
                "estimatedTime": target_count * 15,
                "difficultyMix": {"easy": 0, "medium": 0, "hard": 0}
            }
        }
        
        # Determine which type to generate
        card_type = available_types[0] if len(available_types) == 1 else "classic"
        
        if card_type == "contextual":
            prompt = f"""Generate exactly {target_count} contextual flashcards. MUST generate ALL {target_count} cards.

Words: {', '.join([w['text'] for w in selected_words])}

JSON format - generate card_1, card_2, card_3, card_4, card_5:
{{
  "sessionId": "session_123",
  "cards": [
    {{"id": "card_1", "wordId": "{selected_words[0]['text']}", "type": "contextual", "subType": "fill_in_blank", "question": "Complete: 'The _____ was amazing'", "answer": "{selected_words[0]['text']}", "options": ["{selected_words[0]['text']}", "option2", "option3", "option4"], "hints": [], "explanation": "", "difficulty": "easy", "timeLimit": 15000, "points": 10, "questionLanguage": "en", "answerLanguage": "en", "contextTranslation": ""}},
    {{"id": "card_2", "wordId": "{selected_words[1]['text'] if len(selected_words) > 1 else 'word2'}", "type": "contextual", "subType": "fill_in_blank", "question": "Complete: 'I need _____'", "answer": "{selected_words[1]['text'] if len(selected_words) > 1 else 'word2'}", "options": ["{selected_words[1]['text'] if len(selected_words) > 1 else 'word2'}", "option2", "option3", "option4"], "hints": [], "explanation": "", "difficulty": "easy", "timeLimit": 15000, "points": 10, "questionLanguage": "en", "answerLanguage": "en", "contextTranslation": ""}},
    {{"id": "card_3", "wordId": "{selected_words[2]['text'] if len(selected_words) > 2 else 'word3'}", "type": "contextual", "subType": "fill_in_blank", "question": "Complete: 'The _____ is important'", "answer": "{selected_words[2]['text'] if len(selected_words) > 2 else 'word3'}", "options": ["{selected_words[2]['text'] if len(selected_words) > 2 else 'word3'}", "option2", "option3", "option4"], "hints": [], "explanation": "", "difficulty": "easy", "timeLimit": 15000, "points": 10, "questionLanguage": "en", "answerLanguage": "en", "contextTranslation": ""}},
    {{"id": "card_4", "wordId": "{selected_words[3]['text'] if len(selected_words) > 3 else 'word4'}", "type": "contextual", "subType": "fill_in_blank", "question": "Complete: 'We found _____'", "answer": "{selected_words[3]['text'] if len(selected_words) > 3 else 'word4'}", "options": ["{selected_words[3]['text'] if len(selected_words) > 3 else 'word4'}", "option2", "option3", "option4"], "hints": [], "explanation": "", "difficulty": "easy", "timeLimit": 15000, "points": 10, "questionLanguage": "en", "answerLanguage": "en", "contextTranslation": ""}},
    {{"id": "card_5", "wordId": "{selected_words[4]['text'] if len(selected_words) > 4 else 'word5'}", "type": "contextual", "subType": "fill_in_blank", "question": "Complete: 'They use _____'", "answer": "{selected_words[4]['text'] if len(selected_words) > 4 else 'word5'}", "options": ["{selected_words[4]['text'] if len(selected_words) > 4 else 'word5'}", "option2", "option3", "option4"], "hints": [], "explanation": "", "difficulty": "easy", "timeLimit": 15000, "points": 10, "questionLanguage": "en", "answerLanguage": "en", "contextTranslation": ""}}
  ],
  "metadata": {{"totalCards": {target_count}, "estimatedTime": {target_count * 15}, "difficultyMix": {{"easy": {target_count}, "medium": 0, "hard": 0}}}}
}}

IMPORTANT: Generate ALL {target_count} cards. Do not stop at 3."""
        else:
            prompt = f"""
Génère {target_count} flashcards CLASSIC pour l'apprentissage {source_lang} → {target_lang}.
Niveau utilisateur: {user_level}

Words: {', '.join([w['text'] for w in selected_words])}
Type: classic translation cards
Source: English → French

Return ONLY valid JSON with this exact structure:
{{
  "sessionId": "session_123",
  "cards": [
    {{
      "id": "card_1",
      "wordId": "word_hello",
      "type": "classic",
      "subType": "translation_to_target",
      "question": "Que signifie 'hello' ?",
      "answer": "bonjour",
      "options": ["bonjour", "salut", "bonsoir", "bonne nuit"],
      "hints": ["greeting"],
      "explanation": "Common greeting",
      "difficulty": "easy",
      "timeLimit": 15000,
      "points": 10,
      "questionLanguage": "en",
      "answerLanguage": "fr"
    }}
  ],
  "metadata": {{
    "totalCards": {target_count},
    "estimatedTime": {target_count * 15},
    "difficultyMix": {{"easy": {target_count}, "medium": 0, "hard": 0}}
  }}
}}

NO explanatory text. ONLY JSON."""
        
        try:
            print(f"[DEBUG] Sending prompt to Groq: {prompt[:200]}...")
            response = await self._generate_completion(prompt, "")
            print(f"[DEBUG] Groq RAW response: {response}")
            print(f"[DEBUG] Attempting to parse JSON...")
            
            # Extract JSON from response if it contains explanatory text
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                # Extract JSON from markdown code block
                start = response_clean.find('{')
                end = response_clean.rfind('}') + 1
                if start != -1 and end > start:
                    response_clean = response_clean[start:end]
            elif response_clean.startswith('{'):
                # Find the end of JSON object
                end = response_clean.rfind('}') + 1
                if end > 0:
                    response_clean = response_clean[:end]
            else:
                # Try to find JSON object in the response
                start = response_clean.find('{')
                end = response_clean.rfind('}') + 1
                if start != -1 and end > start:
                    response_clean = response_clean[start:end]
            
            print(f"[DEBUG] Raw extracted JSON: {response_clean[:500]}...")
            
            # Try to rebuild JSON from scrambled structure
            if '"cards"' in response_clean and '"sessionId"' in response_clean:
                response_clean = self._rebuild_json_structure(response_clean, target_count)
            
            # Fix common JSON syntax errors
            response_clean = self._fix_json_syntax(response_clean)
            
            print(f"[DEBUG] Cleaned JSON: {response_clean[:500]}...")
            result = json.loads(response_clean)
            print(f"[DEBUG] Groq parsed successfully: {result}")
            
            # Validate and fix None values in cards
            if "cards" in result and isinstance(result["cards"], list):
                # Update metadata with actual card count
                actual_count = len(result["cards"])
                result["metadata"]["totalCards"] = actual_count
                result["metadata"]["estimatedTime"] = actual_count * 15
                
                for i, card in enumerate(result["cards"]):
                    if not isinstance(card, dict):
                        continue
                        
                    # Fix None answer
                    if card.get("answer") is None or card.get("answer") == "":
                        word_text = card.get("wordId", f"word_{i+1}").replace("word_", "")
                        card["answer"] = f"Réponse pour {word_text}" if word_text else f"Réponse {i+1}"
                    
                    # Fix None question
                    if card.get("question") is None or card.get("question") == "":
                        word_text = card.get("wordId", f"word_{i+1}").replace("word_", "")
                        card["question"] = f"Que signifie '{word_text}' ?" if word_text else f"Question {i+1}"
                    
                    # Fix None options with better distractors
                    if card.get("options") is None or not isinstance(card.get("options"), list) or len(card.get("options", [])) == 0:
                        answer = card.get("answer", "")
                        if card.get("type") == "contextual":
                            distractors = self._get_contextual_distractors(answer)
                            options = [answer] + distractors[:3]
                            # Randomize order so answer isn't always first
                            import random
                            random.shuffle(options)
                            card["options"] = options
                        else:
                            card["options"] = [
                                card.get("answer", f"Réponse {i+1}"),
                                "Option incorrecte 1",
                                "Option incorrecte 2", 
                                "Option incorrecte 3"
                            ]
                    else:
                        # Replace generic options with better distractors
                        if any("option" in str(opt).lower() or "incorrecte" in str(opt).lower() for opt in card.get("options", [])):
                            answer = card.get("answer", "")
                            if card.get("type") == "contextual":
                                distractors = self._get_contextual_distractors(answer)
                                options = [answer] + distractors[:3]
                                # Randomize order so answer isn't always first
                                import random
                                random.shuffle(options)
                                card["options"] = options
                        else:
                            # Fix individual None values in options and ensure 4 options
                            options = card["options"]
                            for j in range(len(options)):
                                if options[j] is None or options[j] == "":
                                    options[j] = f"Option {j+1}"
                            
                            # Ensure we have exactly 4 options
                            while len(options) < 4:
                                options.append(f"Option {len(options)+1}")
                            card["options"] = options[:4]  # Limit to 4 options
                    
                    # Fix other None values
                    if card.get("hints") is None:
                        card["hints"] = []
                    if card.get("explanation") is None:
                        card["explanation"] = ""
                    if card.get("difficulty") is None:
                        card["difficulty"] = "easy"
                    
                    # Force contextual type if requested
                    if "contextual" in available_types and len(available_types) == 1:
                        card["type"] = "contextual"
                        if not ("_____" in card.get("question", "")):
                            word_text = card.get("wordId", f"word_{i+1}").replace("word_", "")
                            card["question"] = f"Complete the sentence: 'The {word_text} was _____'"
                            card["answer"] = word_text
                            card["questionLanguage"] = "en"
                            card["answerLanguage"] = "en"
            
            return result
        except Exception as e:
            print(f"[ERROR] Groq failed: {str(e)}")
            print(f"[ERROR] Exception type: {type(e).__name__}")
            print(f"[ERROR] Full traceback:")
            import traceback
            traceback.print_exc()
            print(f"[FALLBACK] Using fallback generation...")
            # Fallback response matching MLX format
            import uuid
            fallback_cards = []
            
            for i, word in enumerate(selected_words):
                # Determine card type for fallback
                if "contextual" in available_types and len(available_types) == 1:
                    card = {
                        "id": f"card_{i+1}",
                        "wordId": f"word_{word['text'].lower()}",
                        "type": "contextual",
                        "subType": "fill_in_blank",
                        "question": f"Complete the sentence: 'The {word['text']} was _____'",
                        "answer": word['text'],
                        "options": [
                            word['text'],
                            "Option incorrecte 1",
                            "Option incorrecte 2", 
                            "Option incorrecte 3"
                        ],
                        "hints": [f"Think about the context", f"What word fits logically?"],
                        "explanation": f"The word '{word['text']}' completes this sentence naturally.",
                        "difficulty": "easy",
                        "timeLimit": 15000,
                        "points": 10,
                        "questionLanguage": "en",
                        "answerLanguage": "en",
                        "contextTranslation": f"La phrase complète traduite avec {word.get('translation', word['text'])}"
                    }
                else:
                    card = {
                        "id": f"card_{i+1}",
                        "wordId": f"word_{word['text'].lower()}",
                        "type": "classic",
                        "subType": "translation_to_native",
                        "question": f"Que signifie '{word['text']}' ?",
                        "answer": word.get('translation') or self._get_basic_translation(word['text']),
                        "options": [
                            word.get('translation') or self._get_basic_translation(word['text']),
                            self._get_distractor_option(word['text'], 1),
                            self._get_distractor_option(word['text'], 2), 
                            self._get_distractor_option(word['text'], 3)
                        ],
                        "hints": [f"Indice pour {word['text']}"],
                        "explanation": f"Explication pour {word['text']}",
                        "difficulty": "easy",
                        "timeLimit": 15000,
                        "points": 10,
                        "questionLanguage": source_lang,
                        "answerLanguage": target_lang
                    }
                fallback_cards.append(card)
            
            print(f"[FALLBACK] Generated {len(fallback_cards)} fallback cards")
            return {
                "sessionId": str(uuid.uuid4()),
                "cards": fallback_cards,
                "metadata": {
                    "totalCards": len(fallback_cards),
                    "estimatedTime": len(fallback_cards) * 15,
                    "difficultyMix": {"easy": len(fallback_cards), "medium": 0, "hard": 0}
                },
                "error": None,
                "fallback": True,
                "source": "fallback"
            }
