import logging

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.metrics import get_meter_provider, set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from redis import Redis


def setup_instrumentation(app=None, engine=None, service_name="py-instrument"):
    """Setup OpenTelemetry instrumentation for tracing, logging, and metrics.
    
    Args:
        app: Optional FastAPI app to instrument
        engine: Optional SQLAlchemy engine (async or sync) to instrument.
                For async engines, pass the async engine and it will be handled automatically.
        service_name: Service name for OpenTelemetry resource attributes
    """
    
    # Create Resource with service name
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
    })
    
    # Logging setup
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)
    exporter = ConsoleLogExporter()
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    
    # Get the root logger and set its level
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)  # Set to NOTSET to capture all log levels
    
    # Create and add the OpenTelemetry handler
    otel_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logger.addHandler(otel_handler)

    # Tracing setup
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)

    console_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    span_processor = BatchSpanProcessor(console_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Metrics setup
    exporter = ConsoleMetricExporter()
    reader = PeriodicExportingMetricReader(exporter)
    meter_provider = MeterProvider(metric_readers=[reader], resource=resource)
    set_meter_provider(meter_provider)
    meter = get_meter_provider().get_meter(__name__)

    # Instrumentation setup
    if app:
        FastAPIInstrumentor.instrument_app(app)
    RedisInstrumentor().instrument()
    
    # SQLAlchemy instrumentation - for async engines, pass engine.sync_engine
    if engine:
        # Check if it's an async engine
        if hasattr(engine, 'sync_engine'):
            # Async engine - pass sync_engine
            SQLAlchemyInstrumentor().instrument(
                engine=engine.sync_engine,
                enable_commenter=True,
                commenter_options={},
                tracer_provider=trace.get_tracer_provider()
            )
        else:
            # Sync engine - pass directly
            SQLAlchemyInstrumentor().instrument(
                engine=engine,
                enable_commenter=True,
                commenter_options={},
                tracer_provider=trace.get_tracer_provider()
            )
    else:
        # No engine provided - instrument globally (may not work for async)
        SQLAlchemyInstrumentor().instrument(
            enable_commenter=True,
            commenter_options={},
            tracer_provider=trace.get_tracer_provider()
        )
    
    AsyncPGInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
    LoggingInstrumentor().instrument()

    return tracer, meter, logger


def get_redis_client():
    """Get Redis client instance."""
    return Redis(host="localhost", port=6379)

