from helios.config import load_pydantic_config
from src.helios_pydantic_config import Config
import logging

# For now, keep the old structure to not have breaking changes
# The newer structure supports better features, which requires a refactor
# Those can be done in a separate PR. This introduces the minimum to validate.
config = load_pydantic_config(Config)

VERBOSE: bool = config.logging.verbose
logging.basicConfig(level=logging.INFO)