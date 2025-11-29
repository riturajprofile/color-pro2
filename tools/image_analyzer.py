from langchain_core.tools import tool
import os
import requests
from typing import Optional, Dict, Any
from logger_config import get_logger, DOWNLOADS_DIR

logger = get_logger("image_analyzer")

@tool
def analyze_image(image_source: str, operation: str = "ocr", language: str = "eng") -> str:
    """
    Analyze images from a file path or URL using various operations.
    
    This tool handles image processing for quiz tasks including OCR (text extraction),
    metadata extraction, and basic image analysis. Supports both local files and remote URLs.
    
    Parameters
    ----------
    image_source : str
        Either a local file path (e.g., "data/downloads/image.png") or a URL to an image file.
        Supported formats: png, jpg, jpeg, gif, bmp, tiff, webp
    operation : str
        The operation to perform on the image. Options:
        - "ocr": Extract text from image (default)
        - "metadata": Get image properties (size, format, mode, etc.)
        - "describe": Basic image analysis (colors, dimensions)
    language : str
        Language code for OCR (default: "eng" for English).
        Other options: "fra" (French), "deu" (German), "spa" (Spanish), etc.
    
    Returns
    -------
    str
        The result of the image operation (extracted text, metadata, or description).
    
    Examples
    --------
    >>> analyze_image("https://example.com/document.png", operation="ocr")
    >>> analyze_image("data/downloads/chart.jpg", operation="metadata")
    >>> analyze_image("data/downloads/screenshot.png", operation="describe")
    """
    try:
        from PIL import Image
        import pytesseract
        from io import BytesIO
        
        logger.info(f"Image analysis requested for: {image_source}")
        logger.info(f"Operation: {operation}, Language: {language}")
        
        # Handle URL downloads
        if image_source.startswith("http://") or image_source.startswith("https://"):
            logger.info(f"Downloading image from URL: {image_source}")
            response = requests.get(image_source, stream=True)
            response.raise_for_status()
            
            # Extract filename from URL or use default
            filename = image_source.split("/")[-1].split("?")[0]
            if not any(filename.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']):
                filename = "image.png"
            
            local_path = DOWNLOADS_DIR / filename
            
            total_size = 0
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            logger.info(f"Image downloaded: {filename} ({total_size} bytes)")
            logger.info(f"Saved to: {local_path}")
            image_source = str(local_path)
        
        # Verify file exists
        if not os.path.exists(image_source):
            error_msg = f"Image file not found at {image_source}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        # Open image
        logger.info(f"Opening image: {image_source}")
        img = Image.open(image_source)
        
        # Perform requested operation
        if operation == "ocr":
            logger.info(f"Performing OCR with language: {language}")
            text = pytesseract.image_to_string(img, lang=language)
            logger.info(f"OCR complete: {len(text)} characters extracted")
            logger.info(f"Preview: {text[:200]}..." if len(text) > 200 else f"Full text: {text}")
            return text.strip()
        
        elif operation == "metadata":
            logger.info("Extracting image metadata")
            metadata = {
                "format": img.format,
                "mode": img.mode,
                "size": f"{img.size[0]}x{img.size[1]}",
                "width": img.size[0],
                "height": img.size[1],
                "file_size": os.path.getsize(image_source)
            }
            
            # Add EXIF data if available
            if hasattr(img, '_getexif') and img._getexif():
                metadata["has_exif"] = True
            
            result = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
            logger.info(f"Metadata extracted: {metadata}")
            return result
        
        elif operation == "describe":
            logger.info("Describing image")
            description = f"""Image Description:
- Format: {img.format}
- Size: {img.size[0]}x{img.size[1]} pixels
- Mode: {img.mode}
- File Size: {os.path.getsize(image_source)} bytes
- Aspect Ratio: {img.size[0]/img.size[1]:.2f}
"""
            logger.info("Description complete")
            return description
        
        else:
            error_msg = f"Unknown operation: {operation}. Use 'ocr', 'metadata', or 'describe'"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
    except ImportError:
        error_msg = "Required libraries not installed. Use 'add_dependencies' tool to install 'pillow' and 'pytesseract' packages first."
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Error analyzing image: {str(e)}"
        logger.error(error_msg)
        return error_msg
