import asyncio
import logging
import sys

from helios.generated.helios.cots import (
    AprsPacket, TelemetryPacket, NmeaSentence, LandingPrediction
)

from contextlib import AsyncExitStack
from helios import HeliosClient
from src.aggregator import StringAggregator
from src.s3_store import make_s3_string_store
from src.processor import process_events_str
from src.config import config, VERBOSE
from src.helios_pydantic_config import SupportedEvent

logger = logging.getLogger(__name__)

# Maps event type to the packet type
# Add an entry to here and the config for new events
PACKET_TYPES: dict[SupportedEvent, type] = {
    SupportedEvent.TELEMETRY: TelemetryPacket,
    SupportedEvent.APRS: AprsPacket,
    SupportedEvent.GROUND_POSITION: NmeaSentence,
    SupportedEvent.LANDING_PREDICTION: LandingPrediction,
}


async def main() -> None:
    if VERBOSE: logger.info("Starting logging task with verbose output.")

    if not config.subscriptions:
        logger.info("No subscriptions configured. Exiting")
        sys.exit(1)

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

    aggregators: list[StringAggregator] = []
    for sub in config.subscriptions:
        aggregator = StringAggregator(
            store_func=s3_store_func,
            type_name=sub.event_name.value,
            key_prefix=config.s3.s3_key_prefix,
            maximum_buffer_size=sub.aggregator.max_buffer_size,
            store_interval_ms=sub.aggregator.store_interval_ms,
            store_interval_max_size=sub.aggregator.store_interval_max_size,
        )
        aggregators.append(aggregator)

    if VERBOSE:
        logger.info("Starting %d configured subscriptions.", len(config.subscriptions))

    for aggregator in aggregators:
        aggregator.start()

    try:
        async with AsyncExitStack() as stack:
            tasks = []
            for sub, aggregator in zip(config.subscriptions, aggregators):
                packet_type = PACKET_TYPES[sub.event_name]
                events = await stack.enter_async_context(
                    helios_client.subscribe_event(
                        address=sub.event_address,
                        event_name=sub.event_name.value,
                    )
                )
                if VERBOSE:
                    logger.info("Subscribed to event_name=%r address=%r", sub.event_name.value, sub.event_address)

                tasks.append(process_events_str(events, aggregator, packet_type))

            await asyncio.gather(*tasks)
    finally:
        for aggregator in aggregators:
            aggregator.stop()

if __name__ == "__main__":
    asyncio.run(main())