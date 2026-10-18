from src.aggregator import StringAggregator

from typing import Any, Protocol
from collections.abc import AsyncIterable
from dataclasses import asdict
from collections.abc import AsyncIterable

import json
import logging

logger = logging.getLogger(__name__)


class Parsable(Protocol):
    def parse(self, data: bytes) -> Any: ...

async def process_events_str(
    events: AsyncIterable[Any],
    aggregator: StringAggregator,
    packet_type: type[Parsable],
    *,
    min_data_length: int = 1,
) -> None:
    async for event in events:
        if not event.data or len(event.data) < min_data_length:
            continue

        try:
            packet = packet_type().parse(event.data)
            packet_str = json.dumps(asdict(packet))
            aggregator.store_str(packet_str)

        except EOFError as e:
            logger.error("Skipping malformed packet: %s", e)

        except Exception as e:
            logger.error("Error processing event: %s", e, exc_info=True)
