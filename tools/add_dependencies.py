from typing import List
from langchain_core.tools import tool
import subprocess
from logger_config import get_logger

logger = get_logger("add_dependencies")

@tool
def add_dependencies(dependencies: List[str]) -> str:
    """
    Install the given Python packages into the environment.

    Parameters:
        dependencies (List[str]):
            A list of Python package names to install. Each name must match the 
            corresponding package name on PyPI.

    Returns:
        str:
            A message indicating success or failure.
    """
    logger.info(f"Installing dependencies: {', '.join(dependencies)}")
    
    try:
        subprocess.check_call(
            ["uv", "add"] + dependencies,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        success_msg = "Successfully installed dependencies: " + ", ".join(dependencies)
        logger.info(success_msg)
        return success_msg
    
    except subprocess.CalledProcessError as e:
        error_msg = (
            "Dependency installation failed.\n"
            f"Exit code: {e.returncode}\n"
            f"Error: {e.stderr or 'No error output.'}"
        )
        logger.error(error_msg)
        return error_msg
    
    except Exception as e:
        error_msg = f"Unexpected error while installing dependencies: {e}"
        logger.error(error_msg)
        return error_msg 
