import asyncio
import logging
import sys

from src.generated import TelemetryPacket
from helios.generated.helios.transport import AprsPacket

# Temp protos
from src.generated_temp.helios.transport import NmeaSentence
from src.generated_temp import LandingPrediction

from contextlib import AsyncExitStack
from helios import HeliosClient
from src.aggregator import StringAggregator
from src.s3_store import make_s3_string_store
from src.processor import process_events_str
from src.config import config, VERBOSE

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

    s3_store_func = make_s3_string_store(
        bucket=config.s3.s3_bucket, 
        region=config.s3.region, 
        aws_access_key_id=config.s3.access_key_id, 
        aws_secret_access_key=config.s3.secret_access_key,
        endpoint_url=config.s3.s3_endpoint_url,
    )

    telemetry_aggregator = StringAggregator(store_func=s3_store_func, type_name="telemetry", key_prefix="pydantic")
    aprs_aggregator = StringAggregator(store_func=s3_store_func, type_name="aprs", key_prefix="pydantic")
    nmea_aggregator = StringAggregator(store_func=s3_store_func, type_name="nmea", key_prefix="pydantic")
    landing_prediction_aggregator = StringAggregator(store_func=s3_store_func, type_name="landing_prediction", key_prefix="pydantic")

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
            process_events_str(telemetry_events, telemetry_aggregator, TelemetryPacket),
            process_events_str(aprs_events, aprs_aggregator, AprsPacket),
            process_events_str(nmea_events, nmea_aggregator, NmeaSentence),
            process_events_str(landing_prediction_events, landing_prediction_aggregator, LandingPrediction),
        )   

    telemetry_aggregator.stop()
    aprs_aggregator.stop()
    nmea_aggregator.stop()
    landing_prediction_aggregator.stop()

if __name__ == "__main__":
    asyncio.run(main())