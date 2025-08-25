FROM python:3.11-slim

WORKDIR /app

# Install system dependencies + debugging tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    procps \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create startup script that installs Ollama at runtime
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Set port with explicit handling\n\
if [ -z "$PORT" ] || [ "$PORT" = "" ]; then\n\
    APP_PORT=8000\n\
    echo "PORT not set, using default: 8000"\n\
else\n\
    APP_PORT="$PORT"\n\
    echo "Using PORT from environment: $APP_PORT"\n\
fi\n\
\n\
# Install Ollama first\n\
echo "Installing Ollama..."\n\
curl -fsSL https://ollama.ai/install.sh | sh\n\
\n\
# Start Ollama server in background\n\
echo "Starting Ollama server..."\n\
nohup ollama serve > /tmp/ollama.log 2>&1 &\n\
OLLAMA_PID=$!\n\
echo "Ollama PID: $OLLAMA_PID"\n\
\n\
# Wait for Ollama to be ready\n\
echo "Waiting for Ollama to be ready..."\n\
for i in {1..30}; do\n\
    if curl -s http://localhost:11434/api/version >/dev/null 2>&1; then\n\
        echo "Ollama is ready!"\n\
        break\n\
    fi\n\
    echo "Waiting for Ollama... ($i/30)"\n\
    sleep 2\n\
done\n\
\n\
# Pull smaller model in background\n\
{\n\
    echo "Pulling Llama 3.2 3B model (lighter)..."\n\
    ollama pull llama3.2:3b || echo "Model pull failed, will retry later"\n\
    echo "Model setup complete!"\n\
} &\n\
\n\
# Start FastAPI\n\
echo "Starting FastAPI application on port $APP_PORT..."\n\
exec uvicorn main:app --host 0.0.0.0 --port "$APP_PORT"\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Health check with shorter startup time since FastAPI starts immediately
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the startup script
CMD ["/app/start.sh"]
