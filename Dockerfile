# ==============================================================================
# LLM Analysis - Autonomous Quiz Solver Agent
# ==============================================================================
# This Dockerfile builds a production-ready container with:
# - Python 3.12 runtime
# - Playwright (for web scraping with JavaScript rendering)
# - Tesseract OCR (for image text extraction)
# - UV package manager (for fast dependency management)
# - All project dependencies (LangGraph, LangChain, Groq, Gemini, etc.)
# - Organized file structure (data/downloads, data/audio, data/workspace, logs)
#
# Capabilities:
# - 7 specialized tools (web scraping, code execution, file download, HTTP POST,
#   dependency installation, audio transcription, image analysis)
# - Autonomous multi-step quiz solving
# - Audio transcription via Groq Whisper
# - Image OCR via Tesseract
# - Data analysis (filtering, ML, geo-spatial, network analysis)
# - Comprehensive logging to logs/log.log
# ==============================================================================

FROM python:3.12-slim

# --- System deps required by Playwright browsers and Tesseract OCR ---
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates curl unzip \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 \
    libgtk-3-0 libgbm1 libasound2 libxcomposite1 libxdamage1 libxrandr2 \
    libxfixes3 libpango-1.0-0 libcairo2 \
    tesseract-ocr tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# --- Install uv package manager ---
RUN pip install uv

# --- Copy app to container ---
WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY . .

# Create necessary directories for data storage and logging
RUN mkdir -p data/downloads data/audio data/workspace logs

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# --- Install project dependencies using uv ---
RUN uv sync --frozen

# --- Install Playwright Chromium browser ---
RUN uv run playwright install chromium --with-deps

# HuggingFace Spaces exposes port 7860
EXPOSE 7860

# --- Run your FastAPI app ---
CMD ["uv", "run", "main.py"]
