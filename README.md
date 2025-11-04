# py-instrument

A FastAPI application demonstrating OpenTelemetry instrumentation for observability (tracing, logging, and metrics). This project showcases how to instrument a Python application with OpenTelemetry to monitor FastAPI requests, SQLAlchemy database queries, Redis operations, HTTPX client calls, and application logging.

## Features

- **OpenTelemetry Integration**: Comprehensive instrumentation for distributed tracing, logging, and metrics
- **FastAPI Instrumentation**: Automatic tracing of HTTP requests and responses
- **SQLAlchemy Instrumentation**: Tracing of database queries (supports both async and sync engines)
- **Redis Instrumentation**: Automatic tracing of Redis operations
- **HTTPX Client Instrumentation**: Tracing of outgoing HTTP requests
- **Structured Logging**: OpenTelemetry-integrated logging with console export
- **OTLP Export**: Traces exported to OTLP collector (gRPC) for visualization in tools like Jaeger or Grafana

## Prerequisites

- Python 3.12+
- Docker and Docker Compose (for PostgreSQL and Redis)
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd py-instrument
```

2. Install dependencies using uv:
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

## Setup

1. Start PostgreSQL and Redis services using Docker Compose:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432 (user: `postgres`, password: `postgres`, database: `myapp`)
- Redis on port 6379

2. (Optional) Start an OTLP collector to receive traces. You can use Jaeger or any OTLP-compatible backend. The application is configured to send traces to `http://localhost:4317`.

## Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Or with uv:
```bash
uv run uvicorn main:app --reload
```

The application will be available at `http://localhost:8000`.

## API Endpoints

### `GET /`
Simple root endpoint that demonstrates Redis operations and manual span creation.

### `GET /db-test`
Tests async PostgreSQL database connectivity and queries.

### `GET /httpx-test`
Demonstrates HTTPX client instrumentation by making an external HTTP request.

### `GET /logging-test`
Tests OpenTelemetry logging integration.

### `GET /favorites?username=<username>`
Retrieves user favorites from Redis, demonstrating Redis instrumentation and span attributes.

## Architecture

The project consists of two main modules:

- **`main.py`**: FastAPI application with various endpoints demonstrating different instrumentation scenarios
- **`instrument.py`**: OpenTelemetry setup and configuration module

### Instrumentation Coverage

- **FastAPI**: Automatic request/response tracing
- **SQLAlchemy**: Database query tracing with SQL commenter support
- **AsyncPG**: PostgreSQL async driver instrumentation
- **Redis**: Redis operation tracing
- **HTTPX**: Outgoing HTTP request tracing
- **Python Logging**: Structured logging with OpenTelemetry integration

### Trace Export

Traces are exported via OTLP (gRPC) to `http://localhost:4317`. To visualize traces, you can:

1. Use [Jaeger](https://www.jaeger.io/) with OTLP receiver
2. Use [Grafana Tempo](https://grafana.com/docs/tempo/)
3. Use any OTLP-compatible backend

## Project Structure

```
py-instrument/
├── main.py              # FastAPI application
├── instrument.py        # OpenTelemetry instrumentation setup
├── pyproject.toml       # Project dependencies and configuration
├── docker-compose.yml   # PostgreSQL and Redis services
└── README.md           # This file
```

## Development

The project uses:
- **FastAPI** for the web framework
- **SQLAlchemy** with async support for database operations
- **Redis** for caching
- **HTTPX** for HTTP client operations
- **OpenTelemetry** for observability
