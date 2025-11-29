from langchain_core.tools import tool
import os
import requests
from typing import Optional
from logger_config import get_logger, AUDIO_DIR

logger = get_logger("audio_transcriber")

@tool
def transcribe_audio(audio_source: str, language: Optional[str] = None) -> str:
    """
    Transcribe audio from a file path or URL using Groq's Whisper API.
    
    This tool handles audio transcription for quiz instructions or other audio content.
    It supports both local files and remote URLs.
    
    Parameters
    ----------
    audio_source : str
        Either a local file path (e.g., "data/audio/audio.mp3") or a URL to an audio file.
        Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
    language : Optional[str]
        ISO-639-1 language code (e.g., "en" for English, "es" for Spanish).
        If None, the model will auto-detect the language.
    
    Returns
    -------
    str
        The transcribed text from the audio file.
    
    Examples
    --------
    >>> transcribe_audio("https://example.com/instructions.mp3")
    >>> transcribe_audio("data/audio/quiz_audio.wav", language="en")
    """
    try:
        from groq import Groq
        from dotenv import load_dotenv
        load_dotenv()
        
        logger.info(f"Transcription requested for: {audio_source}")
        if language:
            logger.info(f"Language specified: {language}")
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Handle URL downloads
        if audio_source.startswith("http://") or audio_source.startswith("https://"):
            logger.info(f"Downloading audio from URL: {audio_source}")
            response = requests.get(audio_source, stream=True)
            response.raise_for_status()
            
            # Extract filename from URL or use default
            filename = audio_source.split("/")[-1].split("?")[0]
            if not any(filename.endswith(ext) for ext in ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']):
                filename = "audio.m4a"
            
            local_path = AUDIO_DIR / filename
            
            total_size = 0
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            logger.info(f"Audio downloaded: {filename} ({total_size} bytes)")
            logger.info(f"Saved to: {local_path}")
            audio_source = str(local_path)
        
        # Verify file exists
        if not os.path.exists(audio_source):
            error_msg = f"Audio file not found at {audio_source}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        # Get filename for Groq API
        filename = os.path.basename(audio_source)
        
        # Transcribe using Groq's Whisper API
        logger.info(f"Starting transcription: {filename}")
        logger.info(f"Model: whisper-large-v3-turbo")
        
        with open(audio_source, "rb") as file:
            transcription_params = {
                "file": (filename, file.read()),
                "model": "whisper-large-v3-turbo",
                "temperature": 0,
                "response_format": "verbose_json",
            }
            
            if language:
                transcription_params["language"] = language
            
            transcription = client.audio.transcriptions.create(**transcription_params)
        
        result = transcription.text
        logger.info(f"Transcription complete: {len(result)} characters")
        logger.info(f"Preview: {result[:100]}..." if len(result) > 100 else f"Full text: {result}")
        
        return result
        
    except ImportError:
        error_msg = "Groq library not installed. Use 'add_dependencies' tool to install 'groq' package first."
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Error transcribing audio: {str(e)}"
        logger.error(error_msg)
        return error_msg
