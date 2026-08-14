# helios-logging

A simple service for cloud storage of telemetry data in Helios.

# Running in Helios-Launcher

## Required ENV

### AWS

- S3_BUCKET
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY

## Option ENV

### AWS:

- AWS_REGION (Default: "us-east-1")
- S3_KEY_PREFIX (Default: "")
- S3_ENDPOINT_URL (Default: None)

### Aggregation

- MAXIMUM_BUFFER_SIZE (Default: 100)
- STORE_INTERVAL_MS (Default: 5000)
- STORE_INTERVAL_MAX_SIZE (Default: 1000)

### Logging

- VERBOSE (Default: Unset)
