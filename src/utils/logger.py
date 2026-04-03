import logging
import sys
from pathlib import Path
from typing import Optional

from .config import get_config

_logger: Optional[logging.Logger] = None

def setup_logger() -> logging.Logger:
    global _logger
    
    if _logger is not None:
        return _logger
    
    log_level = get_config("log.level", "INFO")
    log_file = get_config("log.file", "./data/logs/zzzai.log")
    
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    _logger = logging.getLogger("ZZZAI")
    _logger.setLevel(getattr(logging, log_level.upper()))
    
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)
    
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)
    
    return _logger

def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger
