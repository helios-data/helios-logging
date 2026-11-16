from config import Config
from helios.config import load_pydantic_config
import logging
import os

# For now, keep the old structure to not have breaking changes
# The newer structure supports better features, which requires a refactor
# Those can be done in a separate PR. This introduces the minimum to validate.
config = load_pydantic_config(Config)

# === GLOBAL
VERBOSE: bool = config.logging.verbose
logging.basicConfig(level=logging.INFO)

# === S3 CREDENTIALS
S3_BUCKET = config.s3.s3_bucket
S3_KEY_PREFIX = config.s3.s3_key_prefix
S3_REGION = config.s3.region
S3_ENDPOINT_URL = config.s3.s3_endpoint_url

# === AGGREGATOR
# Maximum number of failed uploads to keep for retry.
DEFAULT_MAXIMUM_BUFFER_SIZE = int(os.environ.get("MAXIMUM_BUFFER_SIZE", 100))
# Default interval (in milliseconds) between automatic flushes.
DEFAULT_STORE_INTERVAL_MS = int(os.environ.get("STORE_INTERVAL_MS", 5000))
# Maximum number of items to flush in a single batch. If the buffer exceeds this size, it will flush immediately.
DEFAULT_STORE_INTERVAL_MAX_SIZE = int(os.environ.get("STORE_INTERVAL_MAX_SIZE", 1000))