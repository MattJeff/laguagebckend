from __future__ import annotations

"""Netflix English Learner AI Service using MLX-LM for local Llama inference."""
from typing import Any, Dict, List, Optional
import json
import re
from mlx_lm import load, generate
from app.core.config import settings


class MLXAIService:
    """AI Service using MLX-LM for local Llama inference"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
        self._load_model()
    
    def _load_model(self):
        """Load MLX model and tokenizer"""
        try:
            self.model, self.tokenizer = load(self.model_name)
            print(f"✅ MLX Model loaded: {self.model_name}")
        except Exception as e:
            print(f"❌ Failed to load MLX model: {e}")
            self.model = None
            self.tokenizer = None
    
    def _generate_response(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate response using MLX-LM"""
        if not self.model or not self.tokenizer:
            raise Exception("MLX model not loaded")
        
        # Use chat template if available
        if hasattr(self.tokenizer, "apply_chat_template") and self.tokenizer.chat_template:
            messages = [
                {"role": "system", "content": "Tu es un assistant IA qui répond uniquement en JSON valide."},
                {"role": "user", "content": prompt},
            ]
            llama_prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            llama_prompt = prompt
        
        try:
            response = generate(
                self.model,
                self.tokenizer,
                prompt=llama_prompt,
                verbose=False,
                max_tokens=max_tokens,
            )
            return response
        except Exception as e:
            raise Exception(f"MLX generation failed: {e}")
    
    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Extract and parse JSON from LLM response"""
        # Clean response from chat tokens and artifacts
        cleaned = re.sub(r'<\|[^\|]*\|>', '', response)  # Remove chat tokens
        cleaned = re.sub(r'assistant\s*\{', '{', cleaned)  # Remove "assistant" before JSON
        cleaned = re.sub(r'```json\s*', '', cleaned)  # Remove markdown json blocks
        cleaned = re.sub(r'```\s*', '', cleaned)  # Remove markdown blocks
        
        # Find all JSON objects and parse them one by one
        brace_level = 0
        start_idx = None
        
        for i, ch in enumerate(cleaned):
            if ch == '{':
                if brace_level == 0:
                    start_idx = i
                brace_level += 1
            elif ch == '}':
                brace_level -= 1
                if brace_level == 0 and start_idx is not None:
                    # Found complete JSON object
                    json_candidate = cleaned[start_idx:i + 1]
                    try:
                        result = json.loads(json_candidate)
                        return result  # Return the first valid JSON
                    except json.JSONDecodeError:
                        # Continue to next JSON object
                        continue
        
        raise Exception("No valid JSON object found in LLM response")
    
    async def analyze_word(self, word: str, context: str, langue_output: str = "fr", user_level: str = "A2") -> Dict:
        """Analyze a word using MLX-LM for French learners"""
        
        # 📊 Log input data
        input_data = {
            "word": word,
            "context": context,
            "langue_output": langue_output,
            "user_level": user_level
        }
        print(f"\n🔍 ANALYZE INPUT:")
        print(f"📥 {json.dumps(input_data, indent=2, ensure_ascii=False)}")
        
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
- ContextualMeaning catégorise le rôle sémantique

Ne retourne AUCUN autre texte que le JSON.
"""
        
        try:
            response = self._generate_response(prompt, max_tokens=1024)
            result = self._extract_json(response)
            
            # 📊 Log output data
            print(f"\n🔍 ANALYZE OUTPUT:")
            print(f"📤 {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            return result
        except Exception as e:
            logger.error(f"Word analysis failed: {e}")
            # Fallback response
            fallback_result = {
                "word": word,
                "translation": "Traduction automatique",
                "definition": f"Définition de '{word}' non disponible",
                "difficulty": user_level or "A2",
                "cefr_level": user_level or "A2",
                "context_analysis": f"Analyse contextuelle de '{word}' dans: {context}",
                "usage_examples": [f"Exemple d'usage de '{word}'"],
                "synonyms": ["synonyme1", "synonyme2"],
                "etymology": f"Étymologie de '{word}' non disponible",
                "error": f"Erreur d'analyse: {str(e)}"
            }
            
            # 📊 Log fallback output
            print(f"\n🔍 ANALYZE OUTPUT (FALLBACK):")
            print(f"📤 {json.dumps(fallback_result, indent=2, ensure_ascii=False)}")
            
            return fallback_result
    
    async def translate_and_analyze_word(self, word: str, context: str, source_lang: str, target_lang: str, user_level: str, mastery_level: str) -> Dict:
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
            response = self._generate_response(prompt, max_tokens=1200)
            result = self._extract_json(response)
            return result
        except Exception as e:
            # Fallback response
            return {
                "word": word,
                "translation": "traduction automatique",
                "alternativeTranslations": [],
                "contextTranslation": f"Traduction de: {context}",
                "definition": "Définition non disponible",
                "difficulty": "medium",
                "cefr_level": user_level,
                "contextAnalysis": {
                    "originalSentence": context,
                    "translatedSentence": "Traduction non disponible",
                    "grammarNotes": "Analyse non disponible",
                    "usage": "Usage contextuel non disponible"
                },
                "learningData": {
                    "synonyms": [],
                    "relatedWords": [],
                    "commonPhrases": []
                },
                "flashcardSuggestion": {
                    "question": f"Que signifie '{word}'?",
                    "answer": "traduction automatique",
                    "options": ["traduction automatique", "option2", "option3", "option4"],
                    "hint": "Mot à traduire",
                    "explanation": "Traduction automatique générée"
                },
                "error": f"Erreur de traduction: {str(e)}"
            }
    
    async def generate_flashcards(self, words_data: List[Dict], session_config: Dict) -> Dict:
        """Generate intelligent flashcards using MLX-LM with multilingual support"""
        
        # 📊 Log input data
        input_data = {
            "words_data": words_data,
            "session_config": session_config
        }
        print(f"\n🎴 FLASHCARD GENERATION INPUT:")
        print(f"📥 {json.dumps(input_data, indent=2, ensure_ascii=False)}")
        
        # Extract configuration with proper handling
        available_types = session_config.get('types', ['classic', 'contextual'])
        user_level = session_config.get('userLevel', 'A2')
        is_premium = session_config.get('isPremium', False)
        difficulty = session_config.get('difficulty', 'adaptive')
        
        # 🎯 Card count limiting
        requested_count = session_config.get('count', 10)
        target_count = min(requested_count, len(words_data))
        selected_words = words_data[:target_count]
        
        # 🌍 Multilingual Support
        source_lang = session_config.get('sourceLanguage', 'en')
        target_lang = session_config.get('targetLanguage', 'fr')
        learning_direction = session_config.get('learningDirection', 'en->fr')
        
        words_list = "\n".join([
            f"- {w['text']}: {w.get('translation', 'N/A')} (maîtrise: {w.get('masteryLevel', 'NEW')})"
            for w in selected_words
        ])
        
        # 🌍 Language-specific schema and prompts
        lang_config = self._get_language_config(source_lang, target_lang, learning_direction)
        
        schema = {
            "sessionId": "session_id_généré",
            "cards": [
                {
                    "id": "card_1",
                    "wordId": "word_hello",
                    "type": "classic|contextual|audio|speed",
                    "subType": "translation_to_native|translation_to_target|fill_in_blank|etc",
                    "question": "Texte de la question",
                    "answer": "Réponse correcte",
                    "options": ["correct", "distracteur1", "distracteur2", "distracteur3"],
                    "hints": ["indice 1", "indice 2"],
                    "explanation": "Explication de la réponse",
                    "difficulty": "easy|medium|hard",
                    "timeLimit": 15000,
                    "points": 10,
                    "questionLanguage": f"{lang_config['question_lang']}",
                    "answerLanguage": f"{lang_config['answer_lang']}",
                    "contextTranslation": "Traduction du contexte si applicable"
                }
            ],
            "metadata": {
                "totalCards": 5,
                "estimatedTime": 180,
                "difficultyMix": {"easy": 3, "medium": 2, "hard": 0}
            }
        }
        
        prompt = self._build_multilingual_prompt(
            words_list, available_types, user_level, is_premium, target_count,
            source_lang, target_lang, learning_direction, lang_config, schema, difficulty
        )
        
        try:
            response = self._generate_response(prompt, max_tokens=2048)
            result = self._extract_json(response)
            
            # 📊 Log AI output data
            print(f"\n🎴 FLASHCARD GENERATION OUTPUT (AI):")
            print(f"📤 {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            return result
        except Exception as e:
            logger.error(f"Flashcard generation failed: {e}")
            # 🎯 Enhanced fallback with proper type distribution and difficulty
            fallback_cards = []
            type_cycle = self._create_type_cycle(available_types, target_count)
            
            for i, word_data in enumerate(selected_words):
                card_type = type_cycle[i]
                card_difficulty = self._determine_card_difficulty(difficulty, user_level, i, target_count)
                
                card = self._generate_fallback_card(
                    word_data, f"card_{i+1}", card_type, card_difficulty,
                    source_lang, target_lang, learning_direction
                )
                fallback_cards.append(card)
            
            # Calculate difficulty distribution
            difficulty_count = {"easy": 0, "medium": 0, "hard": 0}
            for card in fallback_cards:
                card_diff = card.get('difficulty', 'easy')
                difficulty_count[card_diff] += 1
            
            total_time = sum(card.get('timeLimit', 15000) for card in fallback_cards) // 1000
            
            fallback_result = {
                "sessionId": f"session_{uuid.uuid4().hex[:8]}",
                "cards": fallback_cards,
                "metadata": {
                    "totalCards": len(fallback_cards),
                    "estimatedTime": total_time,
                    "difficultyMix": difficulty_count
                },
                "error": None
            }
            
            # 📊 Log fallback output data
            print(f"\n🎴 FLASHCARD GENERATION OUTPUT (FALLBACK):")
            print(f"📤 {json.dumps(fallback_result, indent=2, ensure_ascii=False)}")
            
            return fallback_result
    
    async def create_test(self, user_words: List[str], test_type: str, target_level: str, question_count: int) -> Dict:
        """Create adaptive language test using MLX-LM"""
        
        # Limit question count for performance
        actual_count = min(question_count, len(user_words), 3)
        selected_words = user_words[:actual_count]
        
        prompt = f"""Create {actual_count} test questions for words: {', '.join(selected_words)}
Target level: {target_level}
Test type: {test_type}

Return JSON with this structure:
{{
  "questions": [
    {{
      "id": "q1",
      "type": "multiple_choice",
      "question": "Question text",
      "answer": "Correct answer",
      "options": ["correct", "wrong1", "wrong2", "wrong3"],
      "difficulty": "{target_level}",
      "explanation": "Why this is correct"
    }}
  ],
  "estimatedTime": 90
}}"""

        try:
            response = self._generate_response(prompt, max_tokens=1024)
            result = self._extract_json(response)
            return result
        except Exception as e:
            logger.error(f"Test creation failed: {e}")
            # Simple fallback for performance
            questions = []
            for i, word in enumerate(selected_words):
                questions.append({
                    "id": f"q{i+1}",
                    "type": "multiple_choice",
                    "question": f"What does '{word}' mean?",
                    "answer": "Basic translation",
                    "options": ["Basic translation", "Option 2", "Option 3", "Option 4"],
                    "difficulty": target_level,
                    "explanation": "Simple test question"
                })
            
            return {
                "questions": questions,
                "estimatedTime": len(questions) * 30,
                "error": None
            }
    
    async def generate_recommendations(self, user_progress: Dict) -> Dict:
        """Generate personalized recommendations using MLX-LM"""
        
        # Quick fallback for better performance
        total_words = user_progress.get('totalWords', 0)
        mastered = user_progress.get('masteredWords', 0)
        weak_areas = user_progress.get('weakAreas', [])
        accuracy = user_progress.get('averageAccuracy', 0.0)
        
        recommendations = []
        
        if accuracy < 0.7:
            recommendations.append({
                "type": "practice_focus",
                "content": "Focus on reviewing basic vocabulary to improve accuracy",
                "priority": "high"
            })
        
        if weak_areas:
            recommendations = [
            {
                "type": "weak_areas",
                "content": f"Focus on: {', '.join(weak_areas[:2]) if weak_areas else 'vocabulary expansion'}",
                "priority": "medium",
                "reason": "Based on your performance patterns"
            },
            {
                "type": "review_session", 
                "content": f"Review session recommended ({total_words - mastered} words to practice)",
                "priority": "high" if accuracy < 0.7 else "low",
                "reason": f"Your accuracy is {accuracy:.1%}, improvement needed" if accuracy < 0.7 else "Maintenance review"
            }
        ]
        
        if total_words > 0 and mastered / total_words < 0.5:
            recommendations.append({
                "type": "mastery",
                "content": "Spend more time reviewing learned words to improve retention",
                "priority": "medium",
                "reason": f"Only {mastered}/{total_words} words mastered"
            })
        
        return {
            "recommendations": recommendations[:3]  # Limit to 3 recommendations
        }
    
    def _get_language_config(self, source_lang: str, target_lang: str, learning_direction: str) -> Dict:
        """Get language configuration for multilingual support"""
        
        # Language name mappings
        lang_names = {
            'en': {'name': 'anglais', 'native': 'English'},
            'fr': {'name': 'français', 'native': 'Français'},
            'it': {'name': 'italien', 'native': 'Italiano'},
            'es': {'name': 'espagnol', 'native': 'Español'},
            'de': {'name': 'allemand', 'native': 'Deutsch'}
        }
        
        if learning_direction == "en->fr":
            return {
                'question_lang': 'en',  # Changed to English for contextual cards
                'answer_lang': 'en',    # Changed to English for contextual cards
                'interface_lang': 'fr',
                'source_name': lang_names.get(source_lang, {}).get('name', source_lang),
                'target_name': lang_names.get(target_lang, {}).get('name', target_lang),
                'question_template': "Complete the sentence: '{context}'",
                'context_template': "Complete the sentence",
                'explanation_lang': 'fr'
            }
        elif learning_direction == "fr->en":
            return {
                'question_lang': 'en',
                'answer_lang': 'en',
                'interface_lang': 'en',
                'source_name': lang_names.get(source_lang, {}).get('native', source_lang),
                'target_name': lang_names.get(target_lang, {}).get('native', target_lang),
                'question_template': "How do you say '{word}' in English?",
                'context_template': "Complete this {source_name} sentence",
                'explanation_lang': 'en'
            }
        else:
            # Default fallback
            return {
                'question_lang': target_lang,
                'answer_lang': target_lang,
                'interface_lang': target_lang,
                'source_name': source_lang,
                'target_name': target_lang,
                'question_template': "What does '{word}' mean?",
                'context_template': "Complete this sentence",
                'explanation_lang': target_lang
            }
    
    def _get_card_type_prompt(self, card_type: str, learning_direction: str) -> str:
        """Get specific prompt instructions for each card type"""
        
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
        """Prompt for classic translation cards"""
        if learning_direction == "en->fr":
            return """
TYPE: CLASSIC - Traduction simple
- Question: "Que signifie '[mot]' ?"
- Réponse: traduction française
- Options: [traduction correcte, distracteur1, distracteur2, distracteur3] en français
- questionLanguage: "fr", answerLanguage: "fr"
- Explication en français
"""
        elif learning_direction == "fr->en":
            return """
TYPE: CLASSIC - Simple translation
- Question: "How do you say '[mot]' in English?"
- Answer: English translation
- Options: [correct translation, distractor1, distractor2, distractor3] in English
- questionLanguage: "en", answerLanguage: "en"
- Explanation in English
"""
        else:
            return "TYPE: CLASSIC - Basic translation card"
    
    def _get_contextual_prompt(self, learning_direction: str) -> str:
        """Prompt for contextual completion cards"""
        if learning_direction == "en->fr":
            return """
TYPE: CONTEXTUAL - Complétion de phrase
- Question: "Complete the sentence: '[phrase avec _____]'"
- OBLIGATOIRE: La question DOIT contenir _____ à la place du mot cible
- Réponse: le mot anglais original
- Options: [mot correct, distracteur1, distracteur2, distracteur3] TOUS EN ANGLAIS
- questionLanguage: "en", answerLanguage: "en"
- contextTranslation: traduction française de la phrase complète

EXEMPLES CORRECTS:
Question: "Complete the sentence: 'The movie was _____'"
Answer: "brainless"

Question: "Complete the sentence: 'I couldn't see her _____ in the crowd'"
Answer: "face"

IMPORTANT: TOUJOURS mettre _____ dans la question !
"""
        else:
            return """
TYPE: CONTEXTUAL - Sentence completion
- USE the exact context provided (do NOT invent)
- Question: "Complete the sentence: '[context with _____]'"
- Answer: original word
- Options: [correct word, distractor1, distractor2, distractor3] in original language
"""
    
    def _get_audio_prompt(self, learning_direction: str) -> str:
        """Prompt for audio pronunciation cards"""
        return """
TYPE: AUDIO - Pronunciation focus
- Question: "Listen and identify the word" (audio simulation)
- Focus on phonetically similar distractors
- Include pronunciation hints
"""
    
    def _get_speed_prompt(self, learning_direction: str) -> str:
        """Prompt for speed challenge cards"""
        return """
TYPE: SPEED - Quick recognition
- Shorter time limits
- Simple, clear questions
- Focus on instant recognition
"""
    
    def _build_multilingual_prompt(self, words_list: str, available_types: List[str], 
                                 user_level: str, is_premium: bool, target_count: int,
                                 source_lang: str, target_lang: str, learning_direction: str,
                                 lang_config: Dict, schema: Dict, difficulty: str = "adaptive") -> str:
        """Build multilingual prompt for flashcard generation"""
        
        # Get type-specific instructions
        type_instructions = []
        for card_type in available_types:
            type_instructions.append(self._get_card_type_prompt(card_type, learning_direction))
        
        difficulty_instruction = self._get_difficulty_instruction(difficulty, user_level)
        type_distribution = self._calculate_type_distribution(available_types, target_count)
        
        return f"""
Crée EXACTEMENT {target_count} flashcards pour apprenant niveau {user_level} qui apprend {source_lang}->{target_lang}.

Mots à traiter:
{words_list}

TYPES DE CARTES À GÉNÉRER:
{chr(10).join(type_instructions)}

CONFIGURATION:
- Répartition: {type_distribution}
- Difficulté: {difficulty} {difficulty_instruction}

SCHÉMA JSON OBLIGATOIRE:
{json.dumps(schema, indent=2, ensure_ascii=False)}

RÈGLES GÉNÉRALES:
- Respecte EXACTEMENT le type demandé pour chaque carte
- N'invente JAMAIS de contextes pour les cartes contextuelles
- Utilise les contextes fournis tels quels
- Distracteurs intelligents: mots similaires, même champ sémantique, erreurs communes

Réponds UNIQUEMENT en JSON valide.
"""
    
    def _generate_fallback_card(self, word_data: Dict, card_id: str, card_type: str, 
                                  card_difficulty: str, source_lang: str, target_lang: str, 
                                  learning_direction: str) -> Dict:
        """Generate multilingual fallback card when AI fails"""
        
        word_text = word_data.get('text', 'word')
        translation = word_data.get('translation')
        context = word_data.get('context', '')
        
        # Generate basic translation if none provided
        if not translation:
            if learning_direction == "en->fr":
                # Basic English to French translations
                basic_translations = {
                    "seeing": "voir/rencontrer",
                    "country": "pays",
                    "behind": "derrière", 
                    "tear": "déchirer",
                    "motto": "devise",
                    "every": "chaque",
                    "fantasy": "fantaisie",
                    "friend": "ami",
                    "don't": "ne pas",
                    "kinsman": "parent"
                }
                translation = basic_translations.get(word_text.lower(), f"traduction de {word_text}")
            else:
                translation = f"translation of {word_text}"
        
        lang_config = self._get_language_config(source_lang, target_lang, learning_direction)
        
        if learning_direction == "en->fr":
            # French learning English
            question = f"Que signifie '{word_text}' ?"
            answer = translation
            options = [translation, "option1", "option2", "option3"]
            explanation = f"'{word_text}' signifie '{translation}' en français."
            question_lang = "fr"
            answer_lang = "fr"
        elif learning_direction == "fr->en":
            # English learning French
            question = f"How do you say '{translation}' in English?"
            answer = word_text
            options = [word_text, "option1", "option2", "option3"]
            explanation = f"'{translation}' means '{word_text}' in English."
            question_lang = "en"
            answer_lang = "en"
        else:
            # Default fallback
            question = f"What does '{word_text}' mean?"
            answer = translation
            options = [translation, "option1", "option2", "option3"]
            explanation = f"'{word_text}' means '{translation}'."
            question_lang = target_lang
            answer_lang = target_lang
        
        # Set difficulty and timing based on card_difficulty parameter
        if card_difficulty == "easy":
            time_limit = 20000
            points = 10
        elif card_difficulty == "medium":
            time_limit = 15000
            points = 15
        else:  # hard
            time_limit = 10000
            points = 20
        
        # Adjust for card type
        if card_type == "speed":
            time_limit = max(5000, time_limit - 5000)
            points += 5
        elif card_type == "audio":
            time_limit += 5000
            points += 5

        card = {
            "id": card_id,
            "wordId": f"word_{word_text}",
            "type": card_type,
            "subType": "translation_to_native" if learning_direction.endswith("->fr") else "translation_to_target",
            "question": question,
            "answer": answer,
            "options": options,
            "hints": ["Indice contextuel"],
            "explanation": explanation,
            "difficulty": card_difficulty,
            "timeLimit": time_limit,
            "points": points,
            "questionLanguage": question_lang,
            "answerLanguage": answer_lang
        }
        
        # Add type-specific fields
        if card_type == "contextual" and context:
            if learning_direction == "en->fr":
                card.update({
                    "context": context.replace(word_text, "_____"),
                    "originalContext": context,
                    "contextExplanation": f"Dans ce contexte, '{word_text}' signifie '{translation}'",
                    "contextTranslation": f"Traduction: {context}"
                })
            else:
                card.update({
                    "context": context.replace(word_text, "_____"),
                    "originalContext": context,
                    "contextExplanation": f"In this context, '{word_text}' means '{translation}'",
                    "contextTranslation": f"Translation: {context}"
                })
        
        return card
    
    def _create_type_cycle(self, available_types: List[str], target_count: int) -> List[str]:
        """Create a cycle of card types for the requested count"""
        if not available_types:
            return ["classic"] * target_count
        
        cycle = []
        for i in range(target_count):
            cycle.append(available_types[i % len(available_types)])
        return cycle
    
    def _determine_card_difficulty(self, difficulty_setting: str, user_level: str, card_index: int, total_cards: int) -> str:
        """Determine individual card difficulty based on settings"""
        if difficulty_setting == "easy":
            return "easy"
        elif difficulty_setting == "hard":
            return "hard"
        elif difficulty_setting == "adaptive":
            # Adaptive based on user level and position
            if user_level in ["A1", "A2"]:
                return "easy" if card_index < total_cards * 0.7 else "medium"
            elif user_level in ["B1", "B2"]:
                if card_index < total_cards * 0.4:
                    return "easy"
                elif card_index < total_cards * 0.8:
                    return "medium"
                else:
                    return "hard"
            else:  # C1, C2
                return "medium" if card_index < total_cards * 0.5 else "hard"
        else:  # medium or default
            return "medium"
    
    def _get_difficulty_instruction(self, difficulty: str, user_level: str) -> str:
        """Get difficulty-specific instructions for AI"""
        if difficulty == "easy":
            return "(Questions simples, plus d'indices, vocabulaire de base)"
        elif difficulty == "hard":
            return "(Questions complexes, moins d'indices, vocabulaire avancé)"
        elif difficulty == "adaptive":
            return f"(Adapté au niveau {user_level}: mélange progressif de difficultés)"
        else:
            return "(Difficulté équilibrée)"
    
    def _calculate_type_distribution(self, available_types: List[str], target_count: int) -> str:
        """Calculate and format type distribution"""
        if not available_types:
            return "classic: 100%"
        
        base_count = target_count // len(available_types)
        remainder = target_count % len(available_types)
        
        distribution = []
        for i, card_type in enumerate(available_types):
            count = base_count + (1 if i < remainder else 0)
            percentage = round((count / target_count) * 100)
            distribution.append(f"{card_type}: {count} ({percentage}%)")
        
        return ", ".join(distribution)


# Singleton instance
mlx_ai_service = MLXAIService()
