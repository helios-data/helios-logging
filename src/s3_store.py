"""S3 JSONL store helper.

Provides a factory that returns a callable suitable for passing as the
`store_func` to `Aggregator`. The returned function writes a batch of
dictionaries to S3 as a JSONL file named using the convention
`<type>-<timestamp>.jsonl`.

Environment variables used:
- `S3_BUCKET` (required unless `bucket` param is provided)
- `AWS_REGION` (optional)
- `S3_ENDPOINT_URL` (optional, for custom S3-compatible endpoints)

AWS credentials are read by boto3 using its normal credential resolution
chain (environment variables, config files, instance profile, etc.).
"""
from __future__ import annotations

import boto3
import json
import logging
import os
from typing import Callable, Iterable, List, Optional
from src.config import VERBOSE

logger = logging.getLogger(__name__)


def make_s3_store(
    bucket: Optional[str] = None,
    region: Optional[str] = None,
    endpoint_url: Optional[str] = None,
) -> Callable[[str, List[dict]], None]:
    """Return a `store_func(key: str, batch: List[dict]) -> None` that writes to S3.

    The returned function accepts the full S3 object `key` and a batch of
    dictionaries to write as JSONL. This moves filename/key generation out of
    the S3 helper so callers (for example `Aggregator`) can decide naming.

    Args:
        bucket: S3 bucket name. If not provided, read from `S3_BUCKET` env var.
        region: AWS region name. If not provided, read from `AWS_REGION` env var.
        endpoint_url: Optional S3 endpoint URL (useful for MinIO/tests).

    Raises:
        ValueError: if bucket cannot be determined.
    """
    bucket = bucket or os.environ.get("S3_BUCKET")
    if not bucket:
        raise ValueError("S3 bucket must be provided via `bucket` or S3_BUCKET env var")
    region = region or os.environ.get("AWS_REGION")
    endpoint_url = endpoint_url or os.environ.get("S3_ENDPOINT_URL")

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
