import logging
import os
from datetime import datetime
from pathlib import Path

# Create logs and data directories
PROJECT_ROOT = Path(__file__).parent
LOGS_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "data"
DOWNLOADS_DIR = DATA_DIR / "downloads"
AUDIO_DIR = DATA_DIR / "audio"
CODE_WORKSPACE_DIR = DATA_DIR / "workspace"

# Create all necessary directories
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
DOWNLOADS_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)
CODE_WORKSPACE_DIR.mkdir(exist_ok=True)

# Configure logging
LOG_FILE = LOGS_DIR / "log.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create logger
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a'),
        logging.StreamHandler()  # Also print to console
    ]
)

logger = logging.getLogger("TDS-Agent")

# Log startup
logger.info("="*80)
logger.info(f"TDS Agent Started - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info(f"Project Root: {PROJECT_ROOT}")
logger.info(f"Logs Directory: {LOGS_DIR}")
logger.info(f"Data Directory: {DATA_DIR}")
logger.info(f"Downloads Directory: {DOWNLOADS_DIR}")
logger.info(f"Audio Directory: {AUDIO_DIR}")
logger.info(f"Code Workspace: {CODE_WORKSPACE_DIR}")
logger.info("="*80)

def get_logger(name: str = None):
    """Get a logger instance for a specific module."""
    if name:
        return logging.getLogger(f"TDS-Agent.{name}")
    return logger

def log_task_start(task_url: str, task_number: int = None):
    """Log the start of a new task/quiz question."""
    logger.info("")
    logger.info("╔" + "═"*78 + "╗")
    if task_number:
        logger.info(f"║ NEW TASK #{task_number:<70} ║")
    else:
        logger.info(f"║ NEW TASK{'':<70} ║")
    logger.info("╠" + "═"*78 + "╣")
    logger.info(f"║ URL: {task_url:<71} ║")
    logger.info(f"║ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<69} ║")
    logger.info("╚" + "═"*78 + "╝")
    logger.info("")

def log_task_end(success: bool = True, message: str = ""):
    """Log the end of a task."""
    logger.info("")
    logger.info("╔" + "═"*78 + "╗")
    if success:
        logger.info(f"║ TASK COMPLETED ✓{'':<63} ║")
    else:
        logger.info(f"║ TASK FAILED ✗{'':<66} ║")
    if message:
        logger.info(f"║ {message:<75} ║")
    logger.info(f"║ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<69} ║")
    logger.info("╚" + "═"*78 + "╝")
    logger.info("")
