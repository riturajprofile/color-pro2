# LLM Analysis - Autonomous Quiz Solver Agent

An intelligent, autonomous agent built with LangGraph and LangChain that solves data-related quizzes involving web scraping, data processing, analysis, and visualization tasks. The system uses Google's Gemini 2.5 Flash model to orchestrate tool usage and make decisions.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Tools & Capabilities](#tools--capabilities)
- [Docker Deployment](#docker-deployment)
- [How It Works](#how-it-works)
- [License](#license)

## 🔍 Overview

This project was developed for the TDS (Tools in Data Science) course project, where the objective is to build an application that can autonomously solve multi-step quiz tasks involving:

- **Data sourcing**: Scraping websites, calling APIs, downloading files, transcribing audio
- **Data preparation**: Cleaning text, PDFs, audio transcripts, and various data formats
- **Data analysis**: Filtering, aggregating, statistical analysis, ML models
- **Data visualization**: Generating charts, narratives, and presentations

The system receives quiz URLs via a REST API, navigates through multiple quiz pages, solves each task using LLM-powered reasoning and specialized tools, and submits answers back to the evaluation server.

## 🏗️ Architecture

The project uses a LangGraph state machine architecture with the following components:

```
┌─────────────┐
│   FastAPI   │ ← Receives POST requests with quiz URLs
│   Server    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Agent    │ ← LangGraph orchestrator with Gemini 2.5 Flash
│    (LLM)    │
└──────┬──────┘
       │
       ├────────────┬────────────┬─────────────┬──────────────┐
       ▼            ▼            ▼             ▼              ▼
  [Scraper]   [Downloader]  [Code Exec]  [POST Req]   [Add Deps]
```

### Key Components:

- **FastAPI Server**: Entry point for receiving quiz requests
- **LangGraph Agent**: Orchestrates the solving process using state machine logic
- **Gemini 2.5 Flash**: LLM for reasoning and decision-making
- **Tool Suite**: Five specialized tools for different operations

## ✨ Features

- ✅ **Autonomous multi-step problem solving**: Chains together multiple quiz pages automatically
- ✅ **Dynamic JavaScript rendering**: Uses Playwright for client-side rendered pages
- ✅ **Code generation & execution**: Writes and runs Python code for data analysis
- ✅ **Audio transcription**: Converts audio instructions to text using Groq's Whisper API
- ✅ **Image processing**: OCR text extraction from images using Tesseract
- ✅ **Flexible data handling**: Downloads and processes files (PDFs, CSVs, images, audio, etc.)
- ✅ **Statistical & ML analysis**: Filtering, aggregating, statistical tests, ML models
- ✅ **Geo-spatial & network analysis**: Supports geopandas, networkx, and spatial operations
- ✅ **Self-installing dependencies**: Automatically adds required Python packages on-demand
- ✅ **Comprehensive logging**: All actions logged to `logs/log.log` with timestamps
- ✅ **Organized file storage**: Structured directories for downloads, audio, workspace, and logs
- ✅ **Task tracking**: Visual task separators in logs for easy debugging
- ✅ **Robust error handling**: Retries failed attempts within time limits
- ✅ **Docker containerization**: Production-ready for HuggingFace Spaces or any cloud platform
- ✅ Rate limiting: Respects API quotas with exponential backoff

## 📁 Project Structure

```
LLM-Analysis-TDS-Project-2/
├── agent.py                # LangGraph state machine & orchestration
├── main.py                 # FastAPI server with /solve endpoint
├── pyproject.toml          # Project dependencies & configuration
├── Dockerfile              # Container image with Playwright
├── .env                    # Environment variables (not in repo)
├── tools/
│   ├── __init__.py
│   ├── web_scraper.py       # Playwright-based HTML renderer
│   ├── run_code.py          # Python code executor
│   ├── download_file.py     # File downloader  
│   ├── send_request.py      # HTTP POST tool
│   ├── add_dependencies.py  # Package installer
│   ├── audio_transcriber.py # Audio transcription with Groq Whisper
│   └── image_analyzer.py    # Image processing with OCR
├── data/
│   ├── downloads/           # Downloaded files (CSV, PDF, etc.)
│   ├── audio/               # Audio files for transcription
│   └── workspace/           # Code execution workspace
├── logs/
│   └── log.log              # Comprehensive activity log
├── logger_config.py         # Centralized logging configuration
└── README.md
```

## 📦 Installation

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/riturajprofile/LLM-Analysis-TDS-Project-2.git
cd LLM-Analysis-TDS-Project-2
```

### Step 2: Install Dependencies

#### Option A: Using `uv` (Recommended)

Ensure you have uv installed, then sync the project:

```bash
# Install uv if you haven't already  
pip install uv

# Sync dependencies  
uv sync
uv run playwright install chromium
```

Start the FastAPI server:
```bash
uv run main.py
```

The server will start at `http://0.0.0.0:7860`.

#### Option B: Using `pip`

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# Install Playwright browsers
playwright install chromium
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Your credentials from the Google Form submission
EMAIL=your.email@example.com
SECRET=your_secret_string

# Google Gemini API Key
GOOGLE_API_KEY=your_gemini_api_key_here

# Groq API Key (for audio transcription with Whisper)
GROQ_API_KEY=your_groq_api_key_here

# Note: Image OCR uses Tesseract (included in Docker, no API key needed)
```

### Getting API Keys

**Gemini API Key** (Required):
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy it to your `.env` file

**Groq API Key** (Optional - for audio transcription):
1. Visit [Groq Console](https://console.groq.com/keys)
2. Create a new API key
3. Copy it to your `.env` file

## 🚀 Usage

### Local Development

Start the FastAPI server:

```bash
# If using uv
uv run main.py

# If using standard Python
python main.py
```

The server will start on `http://0.0.0.0:7860`

### Testing the Endpoint

Send a POST request to test your setup:

```bash
curl -X POST http://localhost:7860/solve \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example-quiz.com",
    "secret": "your_secret_string"
  }'
```

Expected response:

```json
{
  "status": "ok"
}
```

The agent will run in the background and solve the quiz chain autonomously.

## 🌐 API Endpoints

### `POST /solve`

Receives quiz tasks and triggers the autonomous agent.

**Request Body:**

```json
{
  "url": "https://example.com/quiz-123",
  "secret": "your_secret_string"
}
```

**Responses:**

| Status Code | Description                    |
| ----------- | ------------------------------ |
| `200`       | Secret verified, agent started |
| `400`       | Invalid JSON payload           |
| `403`       | Invalid secret                 |

### `GET /healthz`

Health check endpoint for monitoring.

**Response:**

```json
{
  "status": "ok",
  "uptime_seconds": 3600
}
```

## 🛠️ Tools & Capabilities

The agent has access to the following tools:

### 1. **Web Scraper** (`get_rendered_html`)

- Uses Playwright to render JavaScript-heavy pages
- Waits for network idle before extracting content
- Returns fully rendered HTML for parsing

### 2. **File Downloader** (`download_file`)

- Downloads files (PDFs, CSVs, images, audio, etc.) from direct URLs
- Saves files to `LLMFiles/` directory
- Returns the saved filename

### 3. **Code Executor** (`run_code`)

- Executes arbitrary Python code in an isolated subprocess
- Returns stdout, stderr, and exit code
- Useful for data processing, analysis, and visualization

### 4. **POST Request** (`post_request`)

- Sends JSON payloads to submission endpoints
- Includes automatic error handling and response parsing
- Prevents resubmission if answer is incorrect and time limit exceeded

### 5. **Dependency Installer** (`add_dependencies`)

- Dynamically installs Python packages as needed
- Uses `uv add` for fast package resolution
- Enables the agent to adapt to different task requirements

### 6. **Audio Transcriber** (`transcribe_audio`)

- Transcribes audio files or URLs using Groq's Whisper API (whisper-large-v3-turbo)
- Supports multiple audio formats (mp3, wav, m4a, webm, opus, etc.)
- Auto-detects language or accepts language parameter
- Downloads audio to `data/audio/` directory
- Useful for quizzes with audio instructions
- Uses verbose JSON response format for detailed transcription

### 7. **Image Analyzer** (`analyze_image`)

- Analyzes images from URLs or local files
- **OCR**: Extracts text from images using Tesseract
- **Metadata**: Gets image properties (size, format, dimensions)
- **Describe**: Provides detailed image analysis
- Supports multiple formats (png, jpg, jpeg, gif, bmp, tiff, webp)
- Downloads images to `data/downloads/` directory
- Useful for quizzes with visual data or text in images

## 🐳 Docker Deployment

### Build the Image

```bash
docker build -t llm-analysis-agent .
```

### Run the Container

```bash
docker run -p 7860:7860 \
  -e EMAIL="your.email@example.com" \
  -e SECRET="your_secret_string" \
  -e GOOGLE_API_KEY="your_api_key" \
  llm-analysis-agent
```

### Deploy to HuggingFace Spaces

1. Create a new Space with Docker SDK
2. Push this repository to your Space
3. Add secrets in Space settings:
   - `EMAIL`
   - `SECRET`
   - `GOOGLE_API_KEY`
4. The Space will automatically build and deploy

## 🧠 How It Works

### 1. Request Reception

- FastAPI receives a POST request with quiz URL
- Validates the secret against environment variables
- Returns 200 OK and starts the agent in the background

### 2. Agent Initialization

- LangGraph creates a state machine with two nodes: `agent` and `tools`
- The initial state contains the quiz URL as a user message

### 3. Task Loop

The agent follows this loop:

```
┌─────────────────────────────────────────┐
│ 1. LLM analyzes current state           │
│    - Reads quiz page instructions       │
│    - Plans tool usage                   │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│ 2. Tool execution                       │
│    - Scrapes page / downloads files     │
│    - Runs analysis code                 │
│    - Submits answer                     │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│ 3. Response evaluation                  │
│    - Checks if answer is correct        │
│    - Extracts next quiz URL (if exists) │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│ 4. Decision                             │
│    - If new URL exists: Loop to step 1  │
│    - If no URL: Return "END"            │
└─────────────────────────────────────────┘
```

### 4. State Management

- All messages (user, assistant, tool) are stored in state
- The LLM uses full history to make informed decisions
- Recursion limit set to 5000 to handle long quiz chains

### 5. Completion

- Agent returns "END" when no new URL is provided
- Background task completes
- Logs indicate success or failure

## 📝 Key Design Decisions

1. **LangGraph over Sequential Execution**: Allows flexible routing and complex decision-making
2. **Background Processing**: Prevents HTTP timeouts for long-running quiz chains
3. **Tool Modularity**: Each tool is independent and can be tested/debugged separately
4. **Rate Limiting**: Prevents API quota exhaustion (9 req/min for Gemini)
5. **Code Execution**: Dynamically generates and runs Python for complex data tasks
6. **Playwright for Scraping**: Handles JavaScript-rendered pages that `requests` cannot
7. **uv for Dependencies**: Fast package resolution and installation

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Author**: Rituraj  
**Course**: Tools in Data Science (TDS)  
**Repository**: [GitHub](https://github.com/riturajprofile/LLM-Analysis-TDS-Project-2)

For questions or issues, please open an issue on the GitHub repository.
