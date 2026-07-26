import threading
import logging
from typing import Callable, List, Optional

DEFAULT_STORE_INTERVAL_MS = 1000
DEFAULT_STORE_INTERVAL_MAX_SIZE = 1000

logger = logging.getLogger(__name__)

class Aggregator:
    def __init__(
        self,
        store_interval_ms: int = DEFAULT_STORE_INTERVAL_MS,
        store_interval_max_size: int = DEFAULT_STORE_INTERVAL_MAX_SIZE,
        store_func: Optional[Callable[[List[dict]], None]] = None,
    ):
        """Thread-safe aggregator that flushes when either the buffer reaches
        `store_interval_max_size` or every `store_interval_ms` milliseconds.

        If the timer elapses and there is no data, the store is skipped and the
        timer continues.

        Args:
            store_interval_ms: flush interval in milliseconds
            store_interval_max_size: flush when buffer reaches this size
            store_func: callable to persist a list of dicts; defaults to a no-op
        """
        self.store_interval_ms = store_interval_ms
        self.store_interval_max_size = store_interval_max_size
        self._store_func = store_func or (lambda batch: None)

        self._lock = threading.Lock()
        self._buffer: List[dict] = []

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the background timer thread. Safe to call multiple times."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_timer_loop, daemon=True)
        self._thread.start()

    def stop(self, flush: bool = True, timeout: Optional[float] = None) -> None:
        """Stop the background thread. Optionally flush remaining data."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
        if flush:
            self._flush()

    def store_dictionary(self, data: dict) -> None:
        """Add a dictionary to the buffer. Flush immediately if max size reached."""
        with self._lock:
            self._buffer.append(data)
            size = len(self._buffer)
        if size >= self.store_interval_max_size:
            # Flush outside lock to avoid blocking producers on store IO
            self._flush()

    def _run_timer_loop(self) -> None:
        """Background loop that wakes every interval and flushes if there's data.

        If there's no data when the interval elapses, skip storing and continue.
        """
        interval = max(0.001, self.store_interval_ms / 1000.0)
        while not self._stop_event.is_set():
            # Wait for either stop signal or the interval to elapse
            self._stop_event.wait(timeout=interval)
            if self._stop_event.is_set():
                break
            # On interval tick, flush only if there's data
            with self._lock:
                has_data = len(self._buffer) > 0
            if has_data:
                self._flush()

    def _flush(self) -> None:
        """Flush the buffer by calling the configured store function.

        The buffer copy is made under lock and the actual store is performed
        outside the lock to avoid blocking producers.
        """
        with self._lock:
            if not self._buffer:
                return
            batch = list(self._buffer)
            self._buffer.clear()

        try:
            self._store_func(batch)
        except Exception as e:
            logger.exception("Error storing batch of telemetry data:", e)
            pass
