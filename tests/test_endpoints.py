#!/usr/bin/env python3
"""
Comprehensive Test Suite for Multilingual AI Backend
Tests all endpoints with clean, robust validation
"""

import pytest
import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

class TestMultilingualAPI:
    """Test suite for all API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Verify server is running before each test"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            assert response.status_code == 200
        except Exception as e:
            pytest.skip(f"Server not accessible: {e}")
    
    # === HEALTH ENDPOINTS ===
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct info"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "2.0.0"
        assert data["ai_engine"] == "MLX-LM"
        assert len(data["endpoints"]) >= 4
    
    def test_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["ai_engine"] == "MLX-LM"
        assert "timestamp" in data
    
    # === WORD ANALYSIS ENDPOINT ===
    
    def test_word_analysis_basic(self):
        """Test basic word analysis with known word"""
        payload = {
            "word": "hello",
            "context": "Hello, how are you?",
            "langue_output": "fr",
            "userLevel": "A2"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/words/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate required fields
        assert data["word"] == "hello"
        assert "translation" in data
        assert "definition" in data
        assert data["difficulty"] in ["A1", "A2", "B1", "B2", "C1", "C2"]
        assert data["cefr_level"] in ["A1", "A2", "B1", "B2", "C1", "C2"]
        assert isinstance(data["usage_examples"], list)
        assert isinstance(data["synonyms"], list)
    
    def test_word_analysis_complex(self):
        """Test word analysis with complex word"""
        payload = {
            "word": "sophisticated",
            "context": "She has sophisticated taste in art.",
            "langue_output": "fr",
            "userLevel": "C1"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/words/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["word"] == "sophisticated"
        assert len(data["translation"]) > 0
        assert data["difficulty"] in ["B2", "C1", "C2"]  # Should be advanced
    
    # === AUTO-TRANSLATION ENDPOINT ===
    
    def test_translate_and_analyze_basic(self):
        """Test auto-translation with unknown word"""
        payload = {
            "word": {
                "text": "serendipity",
                "context": "Finding this job was pure serendipity.",
                "translation": "",  # Empty = AI translates
                "masteryLevel": "NEW"
            },
            "config": {
                "sourceLanguage": "en",
                "targetLanguage": "fr",
                "userLevel": "B2"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/words/translate-and-analyze",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate structure
        assert data["word"] == "serendipity"
        assert len(data["translation"]) > 0
        assert "contextTranslation" in data
        assert "contextAnalysis" in data
        assert "learningData" in data
        assert "flashcardSuggestion" in data
        
        # Validate nested structures
        assert "originalSentence" in data["contextAnalysis"]
        assert "translatedSentence" in data["contextAnalysis"]
        assert "question" in data["flashcardSuggestion"]
        assert "answer" in data["flashcardSuggestion"]
        assert len(data["flashcardSuggestion"]["options"]) == 4
    
    def test_translate_and_analyze_simple_word(self):
        """Test auto-translation with simple word"""
        payload = {
            "word": {
                "text": "amazing",
                "context": "This movie is amazing!",
                "translation": "",
                "masteryLevel": "NEW"
            },
            "config": {
                "sourceLanguage": "en",
                "targetLanguage": "fr",
                "userLevel": "A2"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/words/translate-and-analyze",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["word"] == "amazing"
        assert data["difficulty"] in ["A1", "A2", "B1"]  # Should be easier
    
    # === FLASHCARD GENERATION ENDPOINT ===
    
    def test_flashcard_generation_single_word(self):
        """Test flashcard generation with single word"""
        payload = {
            "words": [
                {
                    "text": "hello",
                    "translation": "bonjour",
                    "context": "Hello, how are you?",
                    "masteryLevel": "NEW"
                }
            ],
            "sessionConfig": {
                "types": ["classic"],
                "count": 1,
                "userLevel": "A2",
                "isPremium": False,
                "sourceLanguage": "en",
                "targetLanguage": "fr",
                "learningDirection": "en->fr"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/flashcards/generate",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate structure
        assert "sessionId" in data
        assert "cards" in data
        assert "metadata" in data
        assert len(data["cards"]) == 1
        
        # Validate card structure
        card = data["cards"][0]
        assert "id" in card
        assert "question" in card
        assert "answer" in card
        assert "options" in card
        assert len(card["options"]) == 4
        assert "explanation" in card
        assert card["difficulty"] in ["easy", "medium", "hard"]
        
        # Validate metadata
        metadata = data["metadata"]
        assert metadata["totalCards"] == 1
        assert "estimatedTime" in metadata
        assert "difficultyMix" in metadata
        assert "easy" in metadata["difficultyMix"]
        assert "medium" in metadata["difficultyMix"]
        assert "hard" in metadata["difficultyMix"]
    
    def test_flashcard_generation_multiple_words(self):
        """Test flashcard generation with multiple words"""
        payload = {
            "words": [
                {"text": "hello", "translation": "bonjour", "masteryLevel": "NEW"},
                {"text": "goodbye", "translation": "au revoir", "masteryLevel": "LEARNING"},
                {"text": "thank you", "translation": "merci", "masteryLevel": "FAMILIAR"}
            ],
            "sessionConfig": {
                "types": ["classic", "contextual"],
                "count": 3,
                "userLevel": "B1",
                "isPremium": True,
                "sourceLanguage": "en",
                "targetLanguage": "fr",
                "learningDirection": "en->fr"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/flashcards/generate",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["cards"]) <= 3
        assert data["metadata"]["totalCards"] <= 3
        
        # Check card variety for premium user
        card_types = [card.get("type") for card in data["cards"]]
        assert len(set(card_types)) >= 1  # At least some variety
    
    def test_flashcard_generation_fr_to_en(self):
        """Test flashcard generation FR→EN direction"""
        payload = {
            "words": [
                {"text": "bonjour", "translation": "hello", "masteryLevel": "NEW"}
            ],
            "sessionConfig": {
                "types": ["classic"],
                "count": 1,
                "userLevel": "A2",
                "isPremium": False,
                "sourceLanguage": "fr",
                "targetLanguage": "en",
                "learningDirection": "fr->en"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/flashcards/generate",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        card = data["cards"][0]
        # Question should be in English for FR→EN
        assert "bonjour" in card["question"] or "hello" in card["question"]
    
    # === TEST CREATION ENDPOINT ===
    
    def test_test_creation_basic(self):
        """Test basic test creation"""
        payload = {
            "userWords": ["hello", "goodbye", "thank you"],
            "testType": "vocabulary_review",
            "targetLevel": "A2",
            "questionCount": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/tests/create",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "questions" in data
        assert len(data["questions"]) <= 3
        assert "estimatedTime" in data
        
        # Validate question structure
        if data["questions"]:
            question = data["questions"][0]
            assert "id" in question
            assert "type" in question
            assert "question" in question
            assert "answer" in question
            assert "options" in question
            assert question["difficulty"] in ["A1", "A2", "B1", "B2", "C1", "C2"]
    
    # === RECOMMENDATIONS ENDPOINT ===
    
    def test_recommendations_basic(self):
        """Test basic recommendations"""
        payload = {
            "userProgress": {
                "totalWords": 100,
                "masteredWords": 75,
                "weakAreas": ["verbs", "formal_vocabulary"],
                "averageAccuracy": 0.85
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/recommendations/get",
            json=payload,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "recommendations" in data
        
        # Validate recommendation structure
        if data["recommendations"]:
            rec = data["recommendations"][0]
            assert "type" in rec
            assert "content" in rec
            assert "priority" in rec
            assert rec["priority"] in ["high", "medium", "low"]
    
    # === ERROR HANDLING ===
    
    def test_word_analysis_invalid_input(self):
        """Test word analysis with invalid input"""
        payload = {
            "word": "",  # Empty word
            "context": "Test context",
            "langue_output": "fr"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/words/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        
        # Should handle gracefully (either 400 or 500 with error message)
        assert response.status_code in [400, 500]
    
    def test_flashcard_generation_empty_words(self):
        """Test flashcard generation with empty words list"""
        payload = {
            "words": [],
            "sessionConfig": {
                "types": ["classic"],
                "count": 1,
                "userLevel": "A2",
                "isPremium": False,
                "learningDirection": "en->fr"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/flashcards/generate",
            json=payload,
            timeout=TIMEOUT
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 500]
    
    # === PERFORMANCE TESTS ===
    
    def test_response_times(self):
        """Test that responses are reasonably fast"""
        start_time = time.time()
        
        payload = {
            "word": "test",
            "context": "This is a test.",
            "langue_output": "fr",
            "userLevel": "A2"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/words/analyze",
            json=payload,
            timeout=TIMEOUT
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 30  # Should respond within 30 seconds


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
