# from opentelemetry import trace
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
# from app.config import settings


# def setup_telemetry():
#     provider = TracerProvider()
#     exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
#     provider.add_span_processor(BatchSpanProcessor(exporter))
#     trace.set_tracer_provider(provider)
#     FastAPIInstrumentor().instrument()
#     SQLAlchemyInstrumentor().instrument()
