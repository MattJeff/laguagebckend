FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
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
# Debug environment variables\n\
echo "PORT environment variable: [$PORT]"\n\
echo "All environment variables:"\n\
env | grep -E "(PORT|RAILWAY)" || echo "No PORT/RAILWAY vars found"\n\
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
# Start FastAPI first to pass healthcheck\n\
echo "Starting FastAPI application on port $APP_PORT..."\n\
uvicorn main:app --host 0.0.0.0 --port "$APP_PORT" &\n\
FASTAPI_PID=$!\n\
\n\
# Install and setup Ollama in background\n\
{\n\
    echo "Installing Ollama..."\n\
    curl -fsSL https://ollama.ai/install.sh | sh\n\
    \n\
    echo "Starting Ollama server..."\n\
    ollama serve &\n\
    OLLAMA_PID=$!\n\
    \n\
    echo "Waiting for Ollama to be ready..."\n\
    sleep 15\n\
    \n\
    echo "Pulling Llama model (this may take a few minutes)..."\n\
    ollama pull llama3.1:8b || echo "Model pull failed, will retry later"\n\
    \n\
    echo "Ollama setup complete!"\n\
} &\n\
\n\
# Wait for FastAPI process\n\
wait $FASTAPI_PID\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Health check with shorter startup time since FastAPI starts immediately
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the startup script
CMD ["/app/start.sh"]
