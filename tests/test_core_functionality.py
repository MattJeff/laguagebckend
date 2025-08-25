#!/usr/bin/env python3
"""
Core Functionality Test Suite
Tests the most critical endpoints with simplified payloads
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
TIMEOUT = 25

def test_word_analysis_simple():
    """Test word analysis with simple word"""
    payload = {
        "word": "cat",
        "context": "The cat is sleeping.",
        "langue_output": "fr",
        "userLevel": "A1"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/words/analyze",
        json=payload,
        timeout=TIMEOUT
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Word analysis successful")
        print(f"   Word: {data.get('word', 'N/A')}")
        print(f"   Translation: {data.get('translation', 'N/A')}")
        print(f"   Difficulty: {data.get('difficulty', 'N/A')}")
        return True
    else:
        print(f"❌ Word analysis failed: {response.text}")
        return False

def test_flashcard_generation_minimal():
    """Test flashcard generation with minimal data"""
    payload = {
        "words": [
            {
                "text": "dog",
                "translation": "chien",
                "context": "I have a dog.",
                "masteryLevel": "NEW"
            }
        ],
        "sessionConfig": {
            "types": ["classic"],
            "count": 1,
            "userLevel": "A1",
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
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Flashcard generation successful")
        print(f"   Cards generated: {len(data.get('cards', []))}")
        print(f"   Session ID: {data.get('sessionId', 'N/A')}")
        if data.get('cards'):
            card = data['cards'][0]
            print(f"   Sample question: {card.get('question', 'N/A')[:50]}...")
        return True
    else:
        print(f"❌ Flashcard generation failed: {response.text}")
        return False

def test_simple_test_creation():
    """Test simple test creation"""
    payload = {
        "userWords": ["hello", "cat", "dog"],
        "testType": "vocabulary_review",
        "targetLevel": "A1",
        "questionCount": 2
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/tests/create",
        json=payload,
        timeout=TIMEOUT
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Test creation successful")
        print(f"   Questions generated: {len(data.get('questions', []))}")
        print(f"   Estimated time: {data.get('estimatedTime', 'N/A')}")
        return True
    else:
        print(f"❌ Test creation failed: {response.text}")
        return False

def test_basic_recommendations():
    """Test basic recommendations"""
    payload = {
        "userProgress": {
            "totalWords": 50,
            "masteredWords": 30,
            "weakAreas": ["verbs"],
            "averageAccuracy": 0.75
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/recommendations/get",
        json=payload,
        timeout=TIMEOUT
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Recommendations successful")
        print(f"   Recommendations: {len(data.get('recommendations', []))}")
        return True
    else:
        print(f"❌ Recommendations failed: {response.text}")
        return False

def run_all_tests():
    """Run all core functionality tests"""
    print("🧪 Running Core Functionality Tests\n")
    
    # Check server health first
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not healthy, aborting tests")
            return
        print("✅ Server is healthy\n")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return
    
    tests = [
        ("Word Analysis", test_word_analysis_simple),
        ("Flashcard Generation", test_flashcard_generation_minimal),
        ("Test Creation", test_simple_test_creation),
        ("Recommendations", test_basic_recommendations)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"🔍 Testing {test_name}...")
        try:
            start_time = time.time()
            success = test_func()
            end_time = time.time()
            duration = end_time - start_time
            results.append((test_name, success, duration))
            print(f"   Duration: {duration:.2f}s\n")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}\n")
            results.append((test_name, False, 0))
    
    # Summary
    print("📊 Test Summary:")
    print("-" * 50)
    passed = 0
    for test_name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20} {status:<8} ({duration:.2f}s)")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All core functionality tests passed!")
    else:
        print("⚠️  Some tests failed - check logs above")

if __name__ == "__main__":
    run_all_tests()
