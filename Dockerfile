# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY apps/frontend/package*.json ./
RUN npm ci
COPY apps/frontend/ ./
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# Stage 2: Final Unified Image
FROM python:3.12-slim

# Prevent prompts during apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Install Node.js, Supervisor, Postgres, Redis, Wget, and curl
RUN apt-get update && apt-get install -y curl supervisor postgresql postgresql-contrib redis-server wget zstd && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Ollama and Pre-pull the Qwen2 model
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install Qdrant
RUN wget https://github.com/qdrant/qdrant/releases/download/v1.8.4/qdrant-x86_64-unknown-linux-gnu.tar.gz && \
    tar -xzf qdrant-x86_64-unknown-linux-gnu.tar.gz && \
    mv qdrant /usr/local/bin/ && \
    rm qdrant-x86_64-unknown-linux-gnu.tar.gz



# Setup Poetry
RUN pip install poetry==1.8.2
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Setup Backend
WORKDIR /app/api
COPY apps/api/pyproject.toml apps/api/poetry.lock* ./
RUN poetry install --no-root --without dev
COPY apps/api/ ./

# Setup Frontend from builder
WORKDIR /app/frontend
COPY --from=frontend-builder /app/frontend/public ./public
COPY --from=frontend-builder /app/frontend/.next/standalone ./
COPY --from=frontend-builder /app/frontend/.next/static ./.next/static

# Setup Supervisor and Entrypoint
WORKDIR /app
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Expose API (8000), Frontend (3000), Postgres (5432), Redis (6379), Qdrant (6333), Ollama (11434)
EXPOSE 3000 8000 5432 6379 6333 11434

# Start everything via entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
