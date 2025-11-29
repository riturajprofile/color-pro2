from google import genai
import subprocess
from langchain_core.tools import tool
from dotenv import load_dotenv
import os
from google.genai import types
from logger_config import get_logger, CODE_WORKSPACE_DIR, PROJECT_ROOT

load_dotenv()
client = genai.Client()
logger = get_logger("run_code")

def strip_code_fences(code: str) -> str:
    code = code.strip()
    # Remove ```python ... ``` or ``` ... ```
    if code.startswith("```"):
        # remove first line (```python or ```)
        code = code.split("\n", 1)[1]
    if code.endswith("```"):
        code = code.rsplit("\n", 1)[0]
    return code.strip()

@tool
def run_code(code: str) -> dict:
    """
    Executes a Python code 
    This tool:
      1. Takes in python code as input
      3. Writes code into a temporary .py file in the workspace
      4. Executes the file from project root (so data/ paths work)
      5. Returns its output

    Parameters
    ----------
    code : str
        Python source code to execute.

    Returns
    -------
    dict
        {
            "stdout": <program output>,
            "stderr": <errors if any>,
            "return_code": <exit code>
        }
    """
    try:
        logger.info("Code execution requested")
        logger.info(f"Code length: {len(code)} characters")
        
        filename = "runner.py"
        filepath = CODE_WORKSPACE_DIR / filename
       
        logger.info(f"Writing code to: {filepath}")
        with open(filepath, "w") as f:
            f.write(code)
        
        logger.info("Executing code with 'uv run' from project root...")
        logger.info(f"Working directory: {PROJECT_ROOT}")
        
        # Run from project root so data/ paths work correctly
        proc = subprocess.Popen(
            ["uv", "run", str(filepath.relative_to(PROJECT_ROOT))],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(PROJECT_ROOT)  # Run from project root
        )
        stdout, stderr = proc.communicate()

        logger.info(f"Execution complete. Return code: {proc.returncode}")
        if stdout:
            logger.info(f"STDOUT ({len(stdout)} chars): {stdout[:200]}..." if len(stdout) > 200 else f"STDOUT: {stdout}")
        if stderr:
            logger.warning(f"STDERR: {stderr[:200]}..." if len(stderr) > 200 else f"STDERR: {stderr}")
        
        return {
            "stdout": stdout,
            "stderr": stderr,
            "return_code": proc.returncode
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Code execution failed: {error_msg}")
        return {
            "stdout": "",
            "stderr": error_msg,
            "return_code": -1
        }
