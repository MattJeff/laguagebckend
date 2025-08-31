"""Groq API Service for fast, free AI inference."""
from typing import Dict, Any, List
import json
import httpx
from app.core.config import settings


class GroqService:
    """AI Service using Groq API for fast, free inference"""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.fallback_model = settings.GROQ_FALLBACK_MODEL
        self.base_url = "https://api.groq.com/openai/v1"
    
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
            "max_tokens": 500,
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
Analyse le mot anglais "{word}" dans ce contexte : "{context}" pour des apprenants français.
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
    
    def _get_distractor_option(self, word: str, index: int) -> str:
        """Generate realistic distractor options"""
        distractors = [
            ["famille", "ami", "maison", "temps"],
            ["bonjour", "merci", "eau", "livre"], 
            ["grand", "petit", "bon", "nouveau"],
            ["aller", "voir", "manger", "parler"]
        ]
        return distractors[index-1][hash(word) % 4]

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
            prompt = f"""
Génère {target_count} flashcards CONTEXTUAL pour l'apprentissage {source_lang} → {target_lang}.
Niveau utilisateur: {user_level}

MOTS À TRAITER:
{words_list}

TYPE: CONTEXTUAL UNIQUEMENT - Complétion de phrase
- Question: "Complete the sentence: 'phrase avec _____'"
- OBLIGATOIRE: La question DOIT contenir _____ à la place du mot cible
- Answer: le mot anglais original
- Options: [mot correct, distracteur1, distracteur2, distracteur3] TOUS EN ANGLAIS
- type: "contextual"
- questionLanguage: "en"
- answerLanguage: "en"
- contextTranslation: traduction française de la phrase complète

EXEMPLES:
Question: "Complete the sentence: 'I couldn't see her _____ in the crowd'"
Answer: "face"
Options: ["face", "hand", "voice", "smile"]
contextTranslation: "Je ne pouvais pas voir son visage dans la foule"

SCHÉMA:
{json.dumps(schema, indent=2, ensure_ascii=False)}

RÈGLES:
- TOUTES les cartes type="contextual"
- Questions avec _____ OBLIGATOIRE
- Answer en anglais
- questionLanguage="en", answerLanguage="en"
- Aucun champ null

RETOURNE UNIQUEMENT LE JSON VALIDE.
"""
        else:
            prompt = f"""
Génère {target_count} flashcards CLASSIC pour l'apprentissage {source_lang} → {target_lang}.
Niveau utilisateur: {user_level}

MOTS À TRAITER:
{words_list}

TYPE: CLASSIC UNIQUEMENT - Traduction simple
- Question: "Que signifie 'word' en français ?"
- Answer: traduction française
- Options: [traduction correcte, distracteur1, distracteur2, distracteur3]
- type: "classic"
- questionLanguage: "en"
- answerLanguage: "fr"

SCHÉMA:
{json.dumps(schema, indent=2, ensure_ascii=False)}

RÈGLES:
- TOUTES les cartes type="classic"
- Questions de traduction directe
- Answer en français
- questionLanguage="en", answerLanguage="fr"
- Aucun champ null

RETOURNE UNIQUEMENT LE JSON VALIDE.
"""
        
        try:
            print(f"[DEBUG] Sending prompt to Groq: {prompt[:200]}...")
            response = await self._generate_completion(prompt, "")
            print(f"[DEBUG] Groq response: {response[:500]}...")
            result = json.loads(response)
            
            # Validate and fix None values in cards
            if "cards" in result and isinstance(result["cards"], list):
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
                    
                    # Fix None options
                    if card.get("options") is None or not isinstance(card.get("options"), list) or len(card.get("options", [])) == 0:
                        card["options"] = [
                            card.get("answer", f"Réponse {i+1}"),
                            "Option incorrecte 1",
                            "Option incorrecte 2", 
                            "Option incorrecte 3"
                        ]
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
                        card["hints"] = [f"Indice pour carte {i+1}"]
                    if card.get("explanation") is None:
                        card["explanation"] = f"Explication pour carte {i+1}"
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
            
            return {
                "sessionId": f"session_{uuid.uuid4().hex[:8]}",
                "cards": fallback_cards,
                "metadata": {
                    "totalCards": len(fallback_cards),
                    "estimatedTime": len(fallback_cards) * 15,
                    "difficultyMix": {"easy": len(fallback_cards), "medium": 0, "hard": 0}
                },
                "error": None
            }
