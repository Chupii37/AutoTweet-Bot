import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = None, log_level: str = None):
    """Setup logger with file and console handlers"""
    
    logger = logging.getLogger(name or __name__)
    
    if log_level is None:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    logger.setLevel(getattr(logging, log_level))
    
    if logger.handlers:
        return logger
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    logs_dir = Path(__file__).parent.parent.parent / 'storage' / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()
