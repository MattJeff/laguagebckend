# Déploiement sur Railway

## 🚀 Déploiement rapide

1. **Fork/Clone ce repo** sur votre GitHub
2. **Connectez Railway** à votre repo GitHub
3. **Configurez les variables d'environnement** (voir ci-dessous)
4. **Déployez** - Railway détectera automatiquement le Dockerfile

## 📋 Variables d'environnement à configurer sur Railway

```bash
# Obligatoires
ENVIRONMENT=production
AI_SERVICE=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Sécurité
API_KEY=votre-cle-api-securisee
ALLOWED_ORIGINS=https://votre-domaine-frontend.com

# Optionnelles
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

## ⚙️ Configuration Railway

1. **Allez sur** [railway.app](https://railway.app)
2. **Connectez votre GitHub**
3. **New Project** → **Deploy from GitHub repo**
4. **Sélectionnez** votre repo
5. **Variables** → Ajoutez les variables ci-dessus
6. **Deploy**

## 🔧 Spécifications recommandées

- **RAM** : Minimum 4GB (pour Llama 3.1 8B)
- **CPU** : 2+ vCPUs recommandés
- **Stockage** : ~8GB (modèle + app)
- **Temps de démarrage** : ~2-3 minutes (téléchargement du modèle)

## 🏥 Health Check

L'application expose plusieurs endpoints de santé :

- `GET /health` - Santé générale
- `GET /api/v1/words/health` - Service d'analyse de mots
- `GET /api/v1/flashcards/health` - Service de flashcards

## 📊 Monitoring

Railway fournit automatiquement :
- **Logs** en temps réel
- **Métriques** CPU/RAM
- **Uptime** monitoring

## 🔍 Troubleshooting

### Erreur de mémoire
- Augmentez la RAM à 6GB+ sur Railway
- Ou utilisez un modèle plus petit : `llama3.1:7b-instruct-q4_0`

### Timeout au démarrage
- Le premier démarrage prend 2-3 minutes (téléchargement Llama)
- Railway attend jusqu'à 10 minutes par défaut

### Erreur Ollama
- Vérifiez que `OLLAMA_BASE_URL=http://localhost:11434`
- Vérifiez les logs Railway pour les erreurs Ollama

## 🌐 URL de production

Une fois déployé, Railway vous donnera une URL comme :
`https://votre-app-production-12345.up.railway.app`

Utilisez cette URL dans votre extension Chrome !

## 💰 Coûts estimés

- **Gratuit** : 500h/mois (largement suffisant pour tester)
- **Payant** : ~$5-10/mois selon l'usage
- **RAM 4GB** recommandée pour performance optimale
