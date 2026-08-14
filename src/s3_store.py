import boto3
import json
import logging

from typing import Callable, Iterable, List, Optional
from src.config import VERBOSE

logger = logging.getLogger(__name__)


def make_s3_store(
    bucket: str,
    region: str,
    endpoint_url: Optional[str] = None,
) -> Callable[[str, List[dict]], None]:
    """Return a `store_func(key: str, batch: List[dict]) -> None` that writes to S3.

    Args:
        bucket: S3 bucket name.
        region: AWS region name.
        endpoint_url: Optional S3 endpoint URL (useful for MinIO/tests).

    Raises:
        ValueError: if bucket cannot be determined.
    """

    s3_client = boto3.client("s3", region_name=region, endpoint_url=endpoint_url)

    def _store(key: str, batch: List[dict]) -> None:
        if not batch:
            return

        # Build JSONL content
        try:
            lines = [json.dumps(item, ensure_ascii=False) for item in batch]
            body = "\n".join(lines) + "\n"
        except Exception as e:  # pragma: no cover - defensive
            logger.exception("Failed to serialize batch for S3: %s", e)
            return

        try:
            s3_client.put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"), ContentType="application/x-ndjson")
            if VERBOSE: logger.info("Wrote %d records to s3://%s/%s", len(batch), bucket, key)
        except Exception as e:  # pragma: no cover - defensive
            logger.exception("Unexpected error writing to S3: %s", e)

    return _store
