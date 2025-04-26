import logging
from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggingHandler, LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource
from app.config import settings


def setup_logging():
    if not settings.otel_enabled:
        return

    resource = Resource.create({
        "service.name": settings.otel_service_name,
    })

    logger_provider = LoggerProvider(resource=resource)
    _logs.set_logger_provider(logger_provider)

    otlp_exporter = OTLPLogExporter(endpoint=settings.otel_exporter_otlp_endpoint)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))

    handler = LoggingHandler(logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)
