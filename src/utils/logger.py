import logging
import sys
from src.config import AppConfig

def setup_logging():
    """Setup logging configuration"""

    # Create logs directory
    log_dir = AppConfig.PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    
    if logging.getLogger().handlers:
        return
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, AppConfig.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding='utf-8'),
            logging.StreamHandler(sys.stderr)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"✅ Logging initialized - Level: {AppConfig.LOG_LEVEL} - Log dir: {log_dir}")

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)

# Auto setup
setup_logging()