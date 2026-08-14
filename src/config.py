import logging
import os

# === GLOBAL
VERBOSE: bool = os.getenv("VERBOSE", "") != ""
logging.basicConfig(level=logging.INFO)

# === S3 CREDENTIALS
S3_BUCKET = os.environ.get("S3_BUCKET", "")
S3_KEY_PREFIX = os.environ.get("S3_KEY_PREFIX", "")
S3_REGION = os.environ.get("AWS_REGION", "us-east-1")
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL")

# === AGGREGATOR
# Maximum number of failed uploads to keep for retry.
DEFAULT_MAXIMUM_BUFFER_SIZE = int(os.environ.get("MAXIMUM_BUFFER_SIZE", 100))
# Default interval (in milliseconds) between automatic flushes.
DEFAULT_STORE_INTERVAL_MS = int(os.environ.get("STORE_INTERVAL_MS", 5000))
# Maximum number of items to flush in a single batch. If the buffer exceeds this size, it will flush immediately.
DEFAULT_STORE_INTERVAL_MAX_SIZE = int(os.environ.get("STORE_INTERVAL_MAX_SIZE", 1000))