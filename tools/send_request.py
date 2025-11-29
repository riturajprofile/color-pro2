from langchain_core.tools import tool
import requests
import json
from typing import Any, Dict, Optional
from logger_config import get_logger

logger = get_logger("post_request")

@tool
def post_request(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Any:
    """
    Send an HTTP POST request to the given URL with the provided payload.

    This function is designed for LangGraph applications, where it can be wrapped
    as a Tool or used inside a Runnable to call external APIs, webhooks, or backend
    services during graph execution.
    REMEMBER: This a blocking function so it may take a while to return. Wait for the response.
    Args:
        url (str): The endpoint to send the POST request to.
        payload (Dict[str, Any]): The JSON-serializable request body.
        headers (Optional[Dict[str, str]]): Optional HTTP headers to include
            in the request. If omitted, a default JSON header is applied.

    Returns:
        Any: The response body. If the server returns JSON, a parsed dict is
        returned. Otherwise, the raw text response is returned.

    Raises:
        requests.HTTPError: If the server responds with an unsuccessful status.
        requests.RequestException: For network-related errors.
    """
    headers = headers or {"Content-Type": "application/json"}
    try:
        # Log request details with clear separator
        logger.info("="*80)
        logger.info("POST REQUEST")
        logger.info(f"URL: {url}")
        logger.info(f"Headers: {json.dumps(headers, indent=2)}")
        logger.info("Payload (JSON):")
        for line in json.dumps(payload, indent=2).split('\n'):
            logger.info(f"  {line}")
        logger.info("-"*80)
        
        response = requests.post(url, json=payload, headers=headers)

        # Raise on 4xx/5xx
        response.raise_for_status()

        logger.info(f"Response Status: {response.status_code} {response.reason}")
        
        # Try to return JSON, fallback to raw text
        data = response.json()
        delay = data.get("delay", 0)
        delay = delay if isinstance(delay, (int, float)) else 0
        correct = data.get("correct")
        message = data.get("message", "")
        next_url = data.get("url", "")
        
        logger.info(f"Answer Correct: {correct}")
        logger.info(f"Time Elapsed: {delay}s")
        if message:
            logger.info(f"Server Message: {message}")
        if next_url:
            logger.info(f"Next URL: {next_url}")
        
        logger.info("Full Response (JSON):")
        for line in json.dumps(data, indent=2).split('\n'):
            logger.info(f"  {line}")
        logger.info("="*80)
        
        # Process response according to quiz logic
        if not correct and delay < 180:
            del data["url"]
        if delay >= 180:
            data = {
                "url": data.get("url")
            }
        
        return data
        
    except requests.HTTPError as e:
        # Extract server's error response
        err_resp = e.response
        
        logger.error("="*80)
        logger.error(f"HTTP ERROR: {e.response.status_code} {e.response.reason}")
        logger.error(f"URL: {url}")

        try:
            err_data = err_resp.json()
            logger.error("Error Response (JSON):")
            for line in json.dumps(err_data, indent=2).split('\n'):
                logger.error(f"  {line}")
        except ValueError:
            err_data = err_resp.text
            logger.error(f"Error Response (Text): {err_data}")
        
        logger.error("="*80)
        return err_data

    except Exception as e:
        logger.error("="*80)
        logger.error(f"UNEXPECTED ERROR during POST request")
        logger.error(f"URL: {url}")
        logger.error(f"Error: {str(e)}")
        logger.error("="*80)
        return str(e)
