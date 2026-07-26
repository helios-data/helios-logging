import asyncio
import logging
import os
import sys

from helios import HeliosClient
from helios.generated.helios.transport import AprsPacket
from aggregator import Aggregator
from generated import TelemetryPacket
from formatter import format_aprs_packet, format_telemetry_packet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VERBOSE: bool = os.getenv("VERBOSE", "") != ""

async def process_telemetry(events, aggregator: Aggregator) -> None:
    async for event in events:
        if not event.data or len(event.data) < 15: continue

        try:
            telemetry = TelemetryPacket().parse(event.data)
            telemetry = format_telemetry_packet(telemetry)
            aggregator.store_dictionary(telemetry)

        except EOFError as e:
            logger.error(f"Skipping malformed packet: {e}")
        except Exception as e:
            logger.error(f"Error processing telemetry event: {e}", exc_info=True)

async def process_aprs(events, aggregator: Aggregator) -> None:
    async for event in events:
        if not event.data: continue

        try:
            aprs = AprsPacket().parse(event.data)
            
            if aprs.position is None:
                logger.warning("No position in APRS packet from %s", aprs.source)
                continue

            aprs = format_aprs_packet(aprs)
            aggregator.store_dictionary(aprs)

        except Exception as e:
            logger.error("Error processing APRS event: %s", e, exc_info=True)

async def main() -> None:
    helios_client = HeliosClient(
        core_address="Helios",
        core_port=5000,
        node_uri="Helios.FALCON.Dashboard",
    )

    try:
        await helios_client.connect()
        logger.info("Connected to Helios core")
    except Exception as e:
        logger.error(f"Fatal error in dashboard task: {e}", exc_info=True)
        sys.exit(1)

    telemetry_aggregator = Aggregator()
    aprs_aggregator = Aggregator()

    async with helios_client.subscribe_event(address="Helios.FALCON.Telemetry", event_name="telemetry") as telemetry_events:
        async with helios_client.subscribe_event(address="Helios.Services.TeleGPS", event_name="aprs") as aprs_events:
            await asyncio.gather(
                process_telemetry(telemetry_events, telemetry_aggregator),
                process_aprs(aprs_events, aprs_aggregator),
            )

if __name__ == "__main__":
    asyncio.run(main())