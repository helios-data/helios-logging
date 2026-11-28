from helios.config import load_pydantic_config
from src.helios_pydantic_config import Config
import logging

config = load_pydantic_config(Config)

if config.logging.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)