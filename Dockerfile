FROM python:3.13-slim AS python-builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    protobuf-compiler \
    libprotobuf-dev \
    && rm -rf /var/lib/apt/lists/*  

COPY pyproject.toml uv.lock* ./

# Copy SDK and build it
COPY helios-python-sdk/ ./helios-python-sdk/
COPY falcon-protos/ ./falcon-protos/
RUN uv sync --frozen --no-install-project

# Copy source
COPY src/ ./src/

RUN mkdir -p src/generated && \
    uv run protoc \
    -I=falcon-protos \
    --python_betterproto2_out=src/generated \
    $(find falcon-protos -name "*.proto")

RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 5050

ENTRYPOINT ["/entrypoint.sh"]