FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama using official method
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create startup script using official Ollama approach
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Set port\n\
APP_PORT=${PORT:-8000}\n\
echo "Starting on port: $APP_PORT"\n\
\n\
# Start Ollama server\n\
echo "Starting Ollama server..."\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
\n\
# Wait for Ollama to be ready\n\
echo "Waiting for Ollama..."\n\
while ! curl -s http://localhost:11434/api/version >/dev/null 2>&1; do\n\
    sleep 1\n\
done\n\
echo "Ollama is ready!"\n\
\n\
# Pull model\n\
echo "Pulling model..."\n\
ollama pull qwen2.5:7b\n\
\n\
# Start FastAPI\n\
echo "Starting FastAPI..."\n\
exec uvicorn main:app --host 0.0.0.0 --port "$APP_PORT"\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE 8000 11434

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the startup script
CMD ["/app/start.sh"]
