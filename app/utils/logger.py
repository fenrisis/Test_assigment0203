import logging
import sys
from datetime import datetime

logger = logging.getLogger("chat_app")
logger.setLevel(logging.INFO)


formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


file_handler = logging.FileHandler(f"logs/chat_app_{datetime.now().strftime('%Y%m%d')}.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

__all__ = ["logger"]
