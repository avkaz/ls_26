# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (Playwright will install browser deps with --with-deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Install Python deps
# If you have requirements.txt it will use it, otherwise installs a minimal set for your code.
RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then \
    pip install -r requirements.txt; \
    else \
    pip install \
    streamlit \
    python-dotenv \
    loguru \
    openai \
    pydantic \
    selectolax \
    playwright \
    pytest; \
    fi

# Install Playwright browser (Chromium) + OS deps
RUN python -m playwright install --with-deps chromium

# Streamlit defaults
EXPOSE 8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501

# Run the app
CMD ["streamlit", "run", "app.py"]
