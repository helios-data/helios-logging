import asyncio
import logging
import os
import sys

from helios import HeliosClient
from src.aggregator import Aggregator
from src.s3_store import make_s3_store
from src.processor import process_telemetry, process_aprs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VERBOSE: bool = os.getenv("VERBOSE", "") != ""

async def main() -> None:
    if VERBOSE: logger.info("Starting logging task with verbose output.")

    helios_client = HeliosClient(
        core_address="Helios",
        core_port=5000,
        node_uri="Helios.FALCON.Logging",
    )

    try:
        await helios_client.connect()
        logger.info("Connected to Helios core")
    except Exception as e:
        logger.error(f"Fatal error in logging task: {e}", exc_info=True)
        sys.exit(1)

    S3_BUCKET = os.environ.get("S3_BUCKET")
    S3_KEY_PREFIX = os.environ.get("S3_KEY_PREFIX", "")
    S3_REGION = os.environ.get("AWS_REGION", "us-east-1")
    S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL")

    telemetry_store = make_s3_store(type_name="telemetry", bucket=S3_BUCKET, key_prefix=S3_KEY_PREFIX, region=S3_REGION, endpoint_url=S3_ENDPOINT_URL)
    aprs_store = make_s3_store(type_name="aprs", bucket=S3_BUCKET, key_prefix=S3_KEY_PREFIX, region=S3_REGION, endpoint_url=S3_ENDPOINT_URL)

    telemetry_aggregator = Aggregator(store_func=telemetry_store)
    aprs_aggregator = Aggregator(store_func=aprs_store)

    if VERBOSE: logger.info("Starting telemetry subscription and processing loop.")

    telemetry_aggregator.start()
    aprs_aggregator.start()

    async with helios_client.subscribe_event(address="*", event_name="telemetry") as telemetry_events:
        async with helios_client.subscribe_event(address="*", event_name="aprs") as aprs_events:
            await asyncio.gather(
                process_telemetry(telemetry_events, telemetry_aggregator),
                process_aprs(aprs_events, aprs_aggregator),
            )

    telemetry_aggregator.stop()
    aprs_aggregator.stop()

if __name__ == "__main__":
    asyncio.run(main())