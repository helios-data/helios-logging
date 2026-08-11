# helios-logging

A simple service for cloud storage of telemetry data in Helios.

# Running in Helios-Launcher

Required ENV:
    - S3_BUCKET
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY

Optional ENV:
    - AWS_REGION (Default: "us-east-1")
    - S3_KEY_PREFIX (Default: "")
    - S3_ENDPOINT_URL (Default: None)
    - VERBOSE (Default: Unset)