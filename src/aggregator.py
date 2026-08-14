import threading
import logging
import time
from typing import Callable, List, Optional, Tuple
from src.config import DEFAULT_MAXIMUM_BUFFER_SIZE, DEFAULT_STORE_INTERVAL_MAX_SIZE, DEFAULT_STORE_INTERVAL_MS, VERBOSE

logger = logging.getLogger(__name__)

class Aggregator:
    def __init__(
        self,
        store_func: Callable[[str, List[dict]], None],
        type_name: str,
        key_prefix: str = "",
        maximum_buffer_size: int = DEFAULT_MAXIMUM_BUFFER_SIZE,
        store_interval_ms: int = DEFAULT_STORE_INTERVAL_MS,
        store_interval_max_size: int = DEFAULT_STORE_INTERVAL_MAX_SIZE,
    ):
        """Thread-safe aggregator.

        Flushes when either:
        - The buffer reaches `store_interval_max_size`
        - `store_interval_ms` milliseconds have passed since the last flush

        If the timer expires while the buffer is empty, no store occurs,
        but the timer continues from that point.
        """
        self.maximum_buffer_size = maximum_buffer_size
        self.store_interval_ms = store_interval_ms
        self.store_interval_max_size = store_interval_max_size
        self._store_func = store_func or (lambda key, batch: None)

        # Naming for generated object keys
        self._type_name = type_name
        self._key_prefix = key_prefix or ""
        if self._key_prefix and not self._key_prefix.endswith("/"):
            self._key_prefix = self._key_prefix + "/"

        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)

        # Primary buffer of incoming dictionaries waiting to be flushed.
        self._buffer: List[dict] = []

        # Retry buffer holds tuples of (key, batch) for failed uploads.
        # Acts as a FIFO queue with a maximum size of MAXIMUM_BUFFER_SIZE.
        self._retry_buffer: List[Tuple[str, List[dict]]] = []

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Time of the last flush.
        self._last_flush = time.monotonic()

    def start(self) -> None:
        """Start the background timer thread. Safe to call multiple times."""
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()

        with self._lock:
            self._last_flush = time.monotonic()

        self._thread = threading.Thread(
            target=self._run_timer_loop,
            daemon=True,
        )
        self._thread.start()

    def stop(
        self,
        flush: bool = True,
        timeout: Optional[float] = None,
    ) -> None:
        """Stop the background thread. Optionally flush remaining data."""

        self._stop_event.set()

        # Wake the timer immediately if it is waiting.
        with self._condition:
            self._condition.notify_all()

        if self._thread:
            self._thread.join(timeout=timeout)

        if flush:
            self._flush()

    def store_dictionary(self, data: dict) -> None:
        """Add a dictionary to the buffer.

        If the buffer reaches the maximum size, flush immediately.
        """

        should_flush = False

        with self._condition:
            self._buffer.append(data)

            if len(self._buffer) >= self.store_interval_max_size:
                should_flush = True

                # Wake the timer thread. It will notice that the buffer
                # is full, although we also flush below.
                self._condition.notify_all()

        if should_flush:
            self._flush()

    def _run_timer_loop(self) -> None:
        """Flush whenever the interval since the last flush expires."""

        interval = max(
            0.001,
            self.store_interval_ms / 1000.0,
        )

        while not self._stop_event.is_set():

            with self._condition:
                # Calculate how much time remains until the next flush.
                elapsed = time.monotonic() - self._last_flush
                remaining = interval - elapsed

                if remaining > 0:
                    self._condition.wait(timeout=remaining)

                if self._stop_event.is_set():
                    break

                # The interval has elapsed.
                has_data = bool(self._buffer)

            if has_data:
                self._flush()
            else:
                # No data, but this still counts as the timer point.
                with self._lock:
                    self._last_flush = time.monotonic()

    def _flush(self) -> None:
        """Flush the current buffer."""

        with self._lock:
            if not self._buffer:
                if VERBOSE:
                    logger.info("[Flush] Buffer is empty; skipping store.")

                # Reset timer even though there was nothing to store.
                self._last_flush = time.monotonic()
                return

            batch = list(self._buffer)
            self._buffer.clear()

            # The flush happened from the aggregator's perspective here.
            self._last_flush = time.monotonic()

        # Prepare key for the current batch
        timestamp_ms = int(time.time() * 1000)
        current_key = f"{self._key_prefix}{self._type_name}-{timestamp_ms}.jsonl"

        # First, try to upload any queued failed items (oldest first).
        # Make a local copy and clear the retry buffer; if any upload fails,
        # re-queue the remaining items plus the current batch.
        with self._lock:
            local_retry = list(self._retry_buffer)
            self._retry_buffer.clear()

        # Upload retry items one-by-one; on first failure requeue remaining + current batch.
        for idx, (key, retry_batch) in enumerate(local_retry):
            try:
                self._store_func(key, retry_batch)
            except Exception:
                logger.exception("Error storing queued batch %s", key)

                remaining = local_retry[idx:]
                remaining.append((current_key, batch))

                with self._lock:
                    for k, b in remaining:
                        self._enqueue_retry(k, b)

                return

        # All retry items succeeded; upload the current batch.
        try:
            self._store_func(current_key, batch)
            if VERBOSE:
                logger.info(f"[Flush] Stored batch of {len(batch)} items.")
        except Exception:
            logger.exception("Error storing current batch %s", current_key)
            with self._lock:
                self._enqueue_retry(current_key, batch)
            return

    def _enqueue_retry(self, key: str, batch: List[dict]) -> None:
        """Append (key, batch) to the retry buffer, dropping oldest if full.

        Caller must hold `self._lock`.
        """
        # Drop oldest items if we're at capacity before appending.
        while len(self._retry_buffer) >= self.maximum_buffer_size:
            self._retry_buffer.pop(0)

        self._retry_buffer.append((key, batch))