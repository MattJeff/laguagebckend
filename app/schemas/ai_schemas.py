from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class WordAnalysisRequest(BaseModel):
    word: str
    context: str
    langue_output: str = "fr"
    userLevel: Optional[str] = None  # A1, A2, B1, B2, C1, C2


class WordAnalysisResponse(BaseModel):
    word: str
    translation: str
    definition: str
    difficulty: str  # A1, A2, B1, B2, C1, C2
    cefr_level: str
    context_analysis: str
    usage_examples: List[str]
    synonyms: List[str]
    etymology: Optional[str] = None
    error: Optional[str] = None


# === NEW: Auto-Translation Endpoint ===

class UnknownWordData(BaseModel):
    text: str
    context: str
    translation: str = ""  # Empty = AI will translate
    masteryLevel: str = "NEW"


class TranslationConfig(BaseModel):
    sourceLanguage: str = "en"
    targetLanguage: str = "fr"
    userLevel: str = "B1"


class WordTranslationRequest(BaseModel):
    word: UnknownWordData
    config: TranslationConfig


class WordTranslationResponse(BaseModel):
    word: str
    translation: str
    alternativeTranslations: Optional[List[str]] = None
    contextTranslation: str
    definition: str
    difficulty: str
    cefr_level: str
    contextAnalysis: Dict[str, str]
    learningData: Dict[str, Any]
    flashcardSuggestion: Dict[str, Any]
    error: Optional[str] = None


class WordData(BaseModel):
    text: str
    context: Optional[str] = None
    translation: Optional[str] = None
    definition: Optional[str] = None
    masteryLevel: str = "NEW"  # NEW, LEARNING, FAMILIAR, MASTERED


class SessionConfig(BaseModel):
    types: List[str] = ["classic", "contextual", "audio", "speed"]
    difficulty: str = "adaptive"
    count: int = 10
    userLevel: str = "A2"
    isPremium: bool = False
    
    # 🌍 Multilingual Support
    sourceLanguage: str = "en"      # Language being learned
    targetLanguage: str = "fr"      # Native language
    learningDirection: str = "en->fr"  # Learning direction


class FlashcardGenerateRequest(BaseModel):
    words: List[WordData]
    sessionConfig: SessionConfig


class AudioMetadata(BaseModel):
    accent: str = "american"
    speed: str = "normal"
    gender: str = "female"


class FlashcardQuestion(BaseModel):
    id: str
    wordId: str
    type: str  # classic, contextual, audio, speed
    subType: str  # translation_to_native, translation_to_target, fill_in_blank, etc.
    question: str
    answer: str
    options: Optional[List[str]] = None
    hints: Optional[List[str]] = None
    explanation: Optional[str] = None
    difficulty: str  # easy, medium, hard
    timeLimit: int  # milliseconds
    points: int = 10
    
    # 🌍 Multilingual Support
    questionLanguage: Optional[str] = None  # Language of the question
    answerLanguage: Optional[str] = None    # Language of the answer
    
    # Contextual specific
    context: Optional[str] = None
    originalContext: Optional[str] = None
    contextExplanation: Optional[str] = None
    contextTranslation: Optional[str] = None  # Translation of context
    
    # Audio specific
    audioUrl: Optional[str] = None
    phonetic: Optional[str] = None
    audioMetadata: Optional[AudioMetadata] = None
    
    # Speed specific
    showTime: Optional[int] = None  # milliseconds
    responseTime: Optional[int] = None  # milliseconds
    speedBonus: Optional[bool] = None


class DifficultyMix(BaseModel):
    easy: int
    medium: int
    hard: int


class SessionMetadata(BaseModel):
    totalCards: int
    estimatedTime: int  # seconds
    difficultyMix: DifficultyMix


class FlashcardGenerateResponse(BaseModel):
    sessionId: str
    cards: List[FlashcardQuestion]
    metadata: SessionMetadata
    error: Optional[str] = None


class TestGenerateRequest(BaseModel):
    userWords: List[str]
    testType: str = "vocabulary_review"
    targetLevel: str = "A2"  # A1, A2, B1, B2, C1, C2
    questionCount: int = 10


class TestQuestion(BaseModel):
    id: str
    type: str  # multiple_choice, fill_blank, context_completion
    question: str
    answer: str
    options: List[str]
    difficulty: str  # A1, A2, B1, B2, C1, C2
    explanation: Optional[str] = None


class TestGenerateResponse(BaseModel):
    questions: List[TestQuestion]
    estimatedTime: int  # in seconds
    error: Optional[str] = None


class UserProgress(BaseModel):
    totalWords: int
    masteredWords: int
    weakAreas: List[str]
    averageAccuracy: float


class RecommendationsRequest(BaseModel):
    userProgress: UserProgress


class Recommendation(BaseModel):
    type: str  # word_to_learn, exercise_type, review_session
    content: str
    priority: str  # high, medium, low
    reason: str


class RecommendationsResponse(BaseModel):
    recommendations: List[Recommendation]
    error: Optional[str] = None
