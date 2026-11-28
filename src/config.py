import sys

from loguru import logger

from helios.config import load_pydantic_config
from src.helios_pydantic_config import Config

config = load_pydantic_config(Config)

logger.remove()

logging_level = "DEBUG" if config.logging.verbose else "INFO"

logger.add(
    sys.stderr,
    level=logging_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}"
)