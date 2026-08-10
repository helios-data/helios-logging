import logging

from src.aggregator import Aggregator
from src.generated import TelemetryPacket
from src.formatter import format_landing_prediction, format_nmea_sentence, format_telemetry_packet, format_aprs_packet
from helios.generated.helios.transport import AprsPacket

# Temp protos
from src.generated_temp.helios.transport import NmeaSentence
from src.generated_temp import LandingPrediction

logger = logging.getLogger(__name__)

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

async def process_nmea(events, aggregator: Aggregator) -> None:
    async for event in events:
        if not event.data: continue

        try:
            nmea = NmeaSentence().parse(event.data)
            nmea = format_nmea_sentence(nmea)
            aggregator.store_dictionary(nmea)

        except Exception as e:
            logger.error("Error processing NMEA event: %s", e, exc_info=True)

async def process_landing_prediction(events, aggregator: Aggregator) -> None:
    async for event in events:
        if not event.data: continue

        try:
            landing_prediction = LandingPrediction().parse(event.data)
            landing_prediction = format_landing_prediction(landing_prediction)
            aggregator.store_dictionary(landing_prediction)

        except Exception as e:
            logger.error("Error processing landing prediction event: %s", e, exc_info=True)