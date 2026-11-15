from pydantic import BaseModel, Field
from enum import Enum

class S3(BaseModel):
    s3_bucket: str
    access_key_id: str
    secret_access_key: str
    region: str = "us-east-1"
    s3_key_prefix: str = ""
    s3_endpoint_url: str = ""

class AggregatorType(Enum):
    STRING = "string"
    BYTE = "byte"

class Aggregator(BaseModel):
    type: AggregatorType = AggregatorType.STRING
    max_buffer_size: int = 100
    store_interval_ms: int = 5000
    store_interval_max_size: int = 1000

class Subscription(BaseModel):
    event_name: str
    event_address: str = "*"
    aggregator: Aggregator = Field(default_factory=Aggregator)

class Logging(BaseModel):
    verbose: bool = False

class Config(BaseModel):
    s3: S3
    subscriptions: list[Subscription] = Field(default_factory=list)
    logging: Logging = Field(default_factory=Logging)