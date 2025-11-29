from langchain_core.tools import tool
import requests
import os
from logger_config import get_logger, DOWNLOADS_DIR

logger = get_logger("download_file")

@tool
def download_file(url: str, filename: str) -> str:
    """
    Download a file from a URL and save it with the given filename
    in the downloads directory (data/downloads/).

    Args:
        url (str): Direct URL to the file.
        filename (str): The filename to save the downloaded content as.

    Returns:
        str: Relative path to the saved file from project root.
    """
    try:
        logger.info(f"Downloading file from URL: {url}")
        logger.info(f"Target filename: {filename}")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filepath = DOWNLOADS_DIR / filename
        
        with open(filepath, "wb") as f:
            total_size = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)
        
        logger.info(f"Download complete: {filename} ({total_size} bytes)")
        logger.info(f"Saved to: {filepath}")
        
        # Return relative path from downloads directory
        return str(filepath.relative_to(filepath.parent.parent.parent))
        
    except Exception as e:
        error_msg = f"Error downloading file: {str(e)}"
        logger.error(error_msg)
        return error_msg
