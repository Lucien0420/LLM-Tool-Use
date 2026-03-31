# Runtime image for CLI tools (Ollama / cloud LLM via env).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install package (README required by pyproject metadata)
COPY pyproject.toml README.md ./
COPY app ./app
COPY main.py ./
COPY scripts ./scripts
COPY samples ./samples

RUN pip install --upgrade pip && pip install -e .

# Default: show loaded settings (override when running extract scripts)
CMD ["python", "main.py"]
