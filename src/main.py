import asyncio
import logging
import os
import sys

from contextlib import AsyncExitStack
from helios import HeliosClient
from src.aggregator import Aggregator
from src.s3_store import make_s3_store
from src.processor import process_telemetry, process_aprs, process_nmea, process_landing_prediction
from src.config import S3_BUCKET, S3_ENDPOINT_URL, S3_KEY_PREFIX, S3_REGION, VERBOSE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    s3_store_func = make_s3_store(bucket=S3_BUCKET, region=S3_REGION, endpoint_url=S3_ENDPOINT_URL)

    telemetry_aggregator = Aggregator(store_func=s3_store_func, type_name="telemetry", key_prefix=S3_KEY_PREFIX)
    aprs_aggregator = Aggregator(store_func=s3_store_func, type_name="aprs", key_prefix=S3_KEY_PREFIX)
    nmea_aggregator = Aggregator(store_func=s3_store_func, type_name="nmea", key_prefix=S3_KEY_PREFIX)
    landing_prediction_aggregator = Aggregator(store_func=s3_store_func, type_name="landing_prediction", key_prefix=S3_KEY_PREFIX)

    if VERBOSE: logger.info("Starting telemetry subscription and processing loop.")

    telemetry_aggregator.start()
    aprs_aggregator.start()
    nmea_aggregator.start()
    landing_prediction_aggregator.start()

    async with AsyncExitStack() as stack:
        telemetry_events = await stack.enter_async_context(helios_client.subscribe_event(address="*", event_name="telemetry"))
        aprs_events = await stack.enter_async_context(helios_client.subscribe_event(address="*", event_name="aprs"))
        nmea_events = await stack.enter_async_context(helios_client.subscribe_event(address="*", event_name="ground_position"))
        landing_prediction_events = await stack.enter_async_context(helios_client.subscribe_event(address="*", event_name="landing_prediction"))

        await asyncio.gather(
            process_telemetry(telemetry_events, telemetry_aggregator),
            process_aprs(aprs_events, aprs_aggregator),
            process_nmea(nmea_events, nmea_aggregator),
            process_landing_prediction(landing_prediction_events, landing_prediction_aggregator),
        )   

    telemetry_aggregator.stop()
    aprs_aggregator.stop()
    nmea_aggregator.stop()
    landing_prediction_aggregator.stop()

if __name__ == "__main__":
    asyncio.run(main())