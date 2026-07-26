DEFAULT_STORE_INTERVAL_MS = 1000
DEFAULT_STORE_INTERVAL_MAX_SIZE = 200

class Aggregator:
    def __init__(self, store_interval_ms: int = DEFAULT_STORE_INTERVAL_MS, store_interval_max_size: int = DEFAULT_STORE_INTERVAL_MAX_SIZE):
        self.store_interval_ms = store_interval_ms
        self.store_interval_max_size = store_interval_max_size
        self.data_buffer = []
        self.last_store_time = None

    def store_dictionary(self, data: dict):
        self.data_buffer.append(data)
        if len(self.data_buffer) >= self.store_interval_max_size:
            self._store_data()

    def _store_data(self):
        # Implement your logic to store the data here
        pass