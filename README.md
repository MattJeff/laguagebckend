# 🤖 Backend IA Multilingue pour Flashcards

Un service backend basé sur FastAPI qui fournit la génération de flashcards multilingues alimentée par l'IA, l'analyse de mots et les recommandations d'apprentissage utilisant MLX-LM (Meta Llama 3.1 8B Instruct).

## 🏗️ Architecture

**Approche Stateless:**
- **Extension**: Gère TOUT le stockage de données (Chrome Storage + IndexedDB)
- **Backend**: Fournit UNIQUEMENT les services IA (analyse, génération, traduction)
- **Avantages**: Fonctionnalité hors ligne, confidentialité, performance, simplicité

## 🚀 Fonctionnalités

- **Analyse de Mots**: Analyse des mots anglais avec traductions françaises et informations contextuelles
- **Génération de Flashcards**: Création de flashcards intelligentes et adaptatives basées sur le niveau de maîtrise
- **Création de Tests**: Génération de tests de vocabulaire avec questions à choix multiples
- **Recommandations d'Apprentissage**: Suggestions personnalisées basées sur les progrès de l'utilisateur
- **Support Multilingue**: Actuellement EN ↔ FR avec architecture extensible
- **Traduction Automatique**: IA traduit automatiquement les mots inconnus
- **Traitement IA Local**: Utilise MLX-LM pour l'inférence IA privée et hors ligne

## 📋 Documentation Complète des Endpoints

### 🏥 Endpoints de Santé

#### `GET /`
**Description**: Informations générales sur l'API

**Réponse**:
```json
{
  "message": "Multilingual AI Flashcard Backend",
  "version": "2.0.0",
  "ai_engine": "MLX-LM",
  "endpoints": [
    "/api/v1/words/analyze",
    "/api/v1/words/translate-and-analyze",
    "/api/v1/flashcards/generate",
    "/api/v1/tests/create",
    "/api/v1/recommendations/get"
  ]
}
```

#### `GET /health`
**Description**: Vérification de l'état du serveur

**Réponse**:
```json
{
  "status": "healthy",
  "ai_engine": "MLX-LM",
  "timestamp": "2025-01-19T23:46:09"
}
```

---

### 🔍 Analyse de Mots

#### `POST /api/v1/words/analyze`
**Description**: Analyse un mot anglais avec contexte pour les apprenants français

**Input attendu**:
```json
{
  "word": "sophisticated",
  "context": "She has sophisticated taste in art.",
  "langue_output": "fr",
  "userLevel": "B2"
}
```

**Paramètres**:
- `word` (string, requis): Le mot à analyser
- `context` (string, requis): Phrase contenant le mot
- `langue_output` (string, optionnel): Langue de sortie ("fr" par défaut)
- `userLevel` (string, optionnel): Niveau CECR ("A2" par défaut)

**Output attendu**:
```json
{
  "word": "sophisticated",
  "translation": "sophistiqué, raffiné",
  "definition": "Having great knowledge or experience; refined",
  "difficulty": "B2",
  "cefr_level": "B2",
  "context_analysis": "Dans ce contexte, 'sophisticated' décrit un goût raffiné et développé",
  "usage_examples": [
    "She has sophisticated manners.",
    "This is a sophisticated analysis."
  ],
  "synonyms": ["refined", "cultured", "elegant"],
  "etymology": "Du latin 'sophisticatus'"
}
```

---

### 🔄 Traduction et Analyse Automatique

#### `POST /api/v1/words/translate-and-analyze`
**Description**: Traduit automatiquement un mot inconnu et fournit une analyse complète

**Input attendu**:
```json
{
  "word": {
    "text": "serendipity",
    "context": "Finding this job was pure serendipity.",
    "translation": "",
    "masteryLevel": "NEW"
  },
  "config": {
    "sourceLanguage": "en",
    "targetLanguage": "fr",
    "userLevel": "B2"
  }
}
```

**Paramètres**:
- `word.text` (string): Mot à traduire
- `word.context` (string): Contexte d'usage
- `word.translation` (string): Vide pour traduction automatique
- `word.masteryLevel` (string): "NEW", "LEARNING", "FAMILIAR", "MASTERED"
- `config.sourceLanguage` (string): Langue source
- `config.targetLanguage` (string): Langue cible
- `config.userLevel` (string): Niveau CECR

**Output attendu**:
```json
{
  "word": "serendipity",
  "translation": "sérendipité, heureux hasard",
  "alternativeTranslations": ["coïncidence heureuse", "découverte fortuite"],
  "contextTranslation": "Trouver ce travail était un pur hasard heureux.",
  "definition": "The occurrence of events by chance in a happy way",
  "difficulty": "C1",
  "cefr_level": "C1",
  "contextAnalysis": {
    "originalSentence": "Finding this job was pure serendipity.",
    "translatedSentence": "Trouver ce travail était un pur hasard heureux.",
    "grammarNotes": "Nom indénombrable, souvent précédé de 'pure'",
    "usage": "Utilisé pour décrire des découvertes heureuses inattendues"
  },
  "learningData": {
    "synonyms": ["chance", "fortune", "luck"],
    "relatedWords": ["coincidence", "fate", "destiny"],
    "commonPhrases": ["pure serendipity", "by serendipity"]
  },
  "flashcardSuggestion": {
    "question": "Que signifie 'serendipity' ?",
    "answer": "sérendipité, heureux hasard",
    "options": ["sérendipité", "malchance", "routine", "planification"],
    "hint": "Découverte heureuse par hasard",
    "explanation": "La sérendipité désigne une découverte inattendue et heureuse"
  }
}
```

---

### 🎴 Génération de Flashcards

#### `POST /api/v1/flashcards/generate`
**Description**: Génère des flashcards intelligentes et adaptatives

**Input attendu**:
```json
{
  "words": [
    {
      "text": "hello",
      "translation": "bonjour",
      "context": "Hello, how are you?",
      "masteryLevel": "NEW"
    },
    {
      "text": "goodbye",
      "translation": "au revoir",
      "context": "Goodbye, see you tomorrow!",
      "masteryLevel": "LEARNING"
    }
  ],
  "sessionConfig": {
    "types": ["classic", "contextual"],
    "count": 5,
    "userLevel": "A2",
    "isPremium": false,
    "sourceLanguage": "en",
    "targetLanguage": "fr",
    "learningDirection": "en->fr"
  }
}
```

**Paramètres**:
- `words` (array): Liste des mots à inclure
  - `text` (string): Le mot
  - `translation` (string): Traduction
  - `context` (string, optionnel): Contexte d'usage
  - `masteryLevel` (string): Niveau de maîtrise
- `sessionConfig` (object): Configuration de la session
  - `types` (array): Types de cartes ["classic", "contextual", "audio", "speed"]
  - `count` (number): Nombre de cartes à générer
  - `userLevel` (string): Niveau CECR
  - `isPremium` (boolean): Utilisateur premium
  - `sourceLanguage` (string): Langue source
  - `targetLanguage` (string): Langue cible
  - `learningDirection` (string): Direction d'apprentissage

**Output attendu**:
```json
{
  "sessionId": "session_12345",
  "cards": [
    {
      "id": "card_1",
      "wordId": "word_hello",
      "type": "classic",
      "subType": "translation_to_native",
      "question": "Que signifie 'hello' en français ?",
      "answer": "bonjour",
      "options": ["bonjour", "bonsoir", "salut", "au revoir"],
      "hints": ["Salutation du matin"],
      "explanation": "'Hello' se traduit par 'bonjour' en français",
      "difficulty": "easy",
      "timeLimit": 15000,
      "points": 10,
      "questionLanguage": "fr",
      "answerLanguage": "fr"
    }
  ],
  "metadata": {
    "totalCards": 2,
    "estimatedTime": 60,
    "difficultyMix": {
      "easy": 1,
      "medium": 1,
      "hard": 0
    }
  }
}
```

---

### 📝 Création de Tests

#### `POST /api/v1/tests/create`
**Description**: Crée des tests de vocabulaire adaptatifs

**Input attendu**:
```json
{
  "userWords": ["hello", "goodbye", "thank you", "please"],
  "testType": "vocabulary_review",
  "targetLevel": "A2",
  "questionCount": 5
}
```

**Paramètres**:
- `userWords` (array): Liste des mots à tester
- `testType` (string): Type de test
- `targetLevel` (string): Niveau CECR cible
- `questionCount` (number): Nombre de questions

**Output attendu**:
```json
{
  "questions": [
    {
      "id": "q1",
      "type": "multiple_choice",
      "question": "Que signifie 'hello' en français ?",
      "answer": "traduction",
      "options": ["traduction", "autre mot", "faux ami", "synonyme"],
      "difficulty": "A2",
      "points": 10,
      "explanation": "'hello' se traduit par 'traduction' en français"
    }
  ],
  "estimatedTime": 135,
  "totalPoints": 30
}
```

---

### 💡 Recommandations d'Apprentissage

#### `POST /api/v1/recommendations/get`
**Description**: Génère des recommandations personnalisées

**Input attendu**:
```json
{
  "userProgress": {
    "totalWords": 150,
    "masteredWords": 75,
    "weakAreas": ["verbs", "formal_vocabulary"],
    "averageAccuracy": 0.82
  }
}
```

**Paramètres**:
- `userProgress` (object): Progrès de l'utilisateur
  - `totalWords` (number): Nombre total de mots
  - `masteredWords` (number): Mots maîtrisés
  - `weakAreas` (array): Domaines faibles
  - `averageAccuracy` (number): Précision moyenne (0-1)

**Output attendu**:
```json
{
  "recommendations": [
    {
      "type": "weak_areas",
      "content": "Practice more with: verbs, formal_vocabulary",
      "priority": "medium"
    },
    {
      "type": "mastery",
      "content": "Spend more time reviewing learned words to improve retention",
      "priority": "medium"
    }
  ]
}
```

---

### 🏥 Endpoints de Santé Spécialisés

#### `GET /api/v1/words/health`
```json
{"status": "healthy", "service": "word_analysis", "ai_engine": "MLX-LM"}
```

#### `GET /api/v1/flashcards/health`
```json
{"status": "healthy", "service": "flashcard_generation", "ai_engine": "MLX-LM"}
```

#### `GET /api/v1/tests/health`
```json
{"status": "healthy", "service": "test_creation", "ai_engine": "MLX-LM"}
```

#### `GET /api/v1/recommendations/health`
```json
{"status": "healthy", "service": "recommendations", "ai_engine": "MLX-LM"}
```

---

## 🛠️ Installation et Configuration

### Prérequis
- Python 3.11+
- MLX-LM (Meta Llama 3.1 8B Instruct 4bit)

### Installation

```bash
# 1. Cloner le repository
git clone <repository-url>
cd backendFlashacrd

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate     # Sur Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le serveur
python main.py
```

Le serveur démarre sur `http://localhost:8000`

### Stack Technique
- **FastAPI**: Framework web moderne et rapide
- **MLX-LM**: Framework d'apprentissage automatique d'Apple pour l'inférence LLM efficace
- **Pydantic**: Validation de données et gestion des paramètres
- **Uvicorn**: Serveur ASGI pour FastAPI

## 🧪 Tests

```bash
# Tests complets avec pytest
source venv/bin/activate
python -m pytest tests/test_endpoints.py -v

# Tests de fonctionnalité core (plus rapides)
python tests/test_core_functionality.py

# Test de santé de l'API
curl http://localhost:8000/health

# Test d'analyse de mot
curl -X POST http://localhost:8000/api/v1/words/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "word": "sophisticated",
    "context": "She has sophisticated taste.",
    "langue_output": "fr",
    "userLevel": "B2"
  }'
```

## 🔄 Intégration avec Extension Chrome

L'extension s'intègre avec ce backend via un client API simple :

```javascript
// Exemple de client API pour l'extension
class FlashcardAIClient {
    constructor() {
        this.baseURL = 'http://localhost:8000';
    }

    async analyzeWord(word, context, userLevel = 'A2') {
        const response = await fetch(`${this.baseURL}/api/v1/words/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                word, 
                context, 
                langue_output: 'fr',
                userLevel 
            })
        });
        return response.json();
    }

    async translateAndAnalyze(wordData, config) {
        const response = await fetch(`${this.baseURL}/api/v1/words/translate-and-analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ word: wordData, config })
        });
        return response.json();
    }

    async generateFlashcards(words, sessionConfig) {
        const response = await fetch(`${this.baseURL}/api/v1/flashcards/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ words, sessionConfig })
        });
        return response.json();
    }

    async getRecommendations(userProgress) {
        const response = await fetch(`${this.baseURL}/api/v1/recommendations/get`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userProgress })
        });
        return response.json();
    }
}
```

## 📊 Flux de Travail

1. **Utilisateur clique sur un mot** → Extension sauvegarde localement immédiatement
2. **Processus en arrière-plan** → Extension appelle l'API pour l'analyse IA
3. **Enrichissement IA** → Backend traite avec MLX-LM
4. **Mise à jour locale** → Extension met à jour les données locales avec les résultats IA
5. **Génération de flashcards** → À la demande via API quand l'utilisateur étudie

## 🏗️ Architecture du Système

```
┌─────────────────┐    HTTP/JSON    ┌──────────────────┐
│                 │ ──────────────► │                  │
│  Extension      │                 │  Backend FastAPI │
│  Chrome         │ ◄────────────── │                  │
│                 │                 │                  │
├─────────────────┤                 ├──────────────────┤
│ • Chrome Storage│                 │ • MLX-LM Service │
│ • IndexedDB     │                 │ • Word Analysis  │
│ • UI/UX         │                 │ • Flashcards Gen │
│ • Gamification │                 │ • Recommendations│
│ • User State    │                 │ • Stateless API  │
└─────────────────┘                 └──────────────────┘
```

## 📈 Performance

- **Analyse de mots**: ~13s (traitement IA local)
- **Génération de flashcards**: ~18s (génération adaptative)
- **Tests simples**: ~3s (logique optimisée)
- **Recommandations**: ~1s (algorithme rapide)
- **Endpoints de santé**: <100ms

## 🚀 Déploiement

### Développement
```bash
python main.py
# Serveur sur http://localhost:8000
```

### Production
```bash
# Avec Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Avec Docker
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Configuration Production
- **CORS**: Configurer les origines appropriées pour l'extension
- **SSL/TLS**: Certificats pour HTTPS
- **Monitoring**: Logs et métriques de performance
- **Rate Limiting**: Protection contre l'abus d'API

## 🔒 Sécurité et Confidentialité

- ✅ **Traitement IA local**: Aucune donnée envoyée à des services externes
- ✅ **Validation stricte**: Pydantic valide toutes les entrées
- ✅ **Gestion d'erreurs**: Fallbacks robustes pour tous les endpoints
- ✅ **CORS configuré**: Accès sécurisé depuis l'extension Chrome
- ✅ **Stateless**: Aucune donnée utilisateur stockée sur le backend

## 🎯 Cas d'Usage

### Pour les Développeurs d'Extensions
- Backend prêt à l'emploi pour fonctionnalités IA
- API REST simple et bien documentée
- Réponses JSON structurées et prévisibles

### Pour les Apprenants de Langues
- Analyse contextuelle intelligente des mots
- Flashcards adaptées au niveau de l'utilisateur
- Recommandations personnalisées d'apprentissage

### Pour les Éducateurs
- Outils d'évaluation automatisés
- Génération de contenu pédagogique
- Suivi des progrès d'apprentissage
# Force Railway redeploy
