#!/usr/bin/env python3
"""
Simple Metrics Sender for OpenTelemetry Collector
Sends the below metrics via OTLP HTTP protocol: 
 - http_requests_total: Counter for total HTTP requests
 - http_request_duration_seconds: Histogram for request durations
 - cpu_usage_percent: Observable gauge for CPU usage
Requires: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
"""

import os
import time
import random
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource

def main():
    # Get endpoint from environment or use default
    #Service Type: ClusterIP without ingress and port-forwarding
    #endpoint = os.getenv("OTEL_ENDPOINT", "http://localhost:4318/v1/metrics")
    # Service Type: LoadBalancer
    #endpoint = os.getenv("OTEL_ENDPOINT", "http://9.223.17.201:4318/v1/metrics")
    #Service Type: ClusterIP with ingress manifest
    endpoint = os.getenv("OTEL_ENDPOINT", "http://demo123.swedencentral.cloudapp.azure.com/collector/v1/metrics")
    
    print("=" * 50)
    print("OpenTelemetry Metrics Sender")
    print("=" * 50)
    print(f"Endpoint: {endpoint}")
    print("Starting in 2 seconds...")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    time.sleep(2)
    
    # Create resource with service information
    resource = Resource.create({
        "service.name": "external-metrics-app",
        "service.version": "1.0.0",
        "deployment.environment": "testing"
    })
    
    # Create OTLP exporter
    exporter = OTLPMetricExporter(
        endpoint=endpoint,
        timeout=10
    )
    
    # Create metric reader
    reader = PeriodicExportingMetricReader(
        exporter=exporter,
        export_interval_millis=5000  # Export every 5 seconds
    )
    
    # Create meter provider
    provider = MeterProvider(
        resource=resource,
        metric_readers=[reader]
    )
    
    # Set global meter provider
    metrics.set_meter_provider(provider)
    
    # Get meter
    meter = metrics.get_meter("external-app-meter", "1.0.0")
    
    # Create instruments
    request_counter = meter.create_counter(
        name="http_requests_total",
        description="Total number of HTTP requests",
        unit="1"
    )
    
    request_duration = meter.create_histogram(
        name="http_request_duration_seconds",
        description="HTTP request duration in seconds",
        unit="s"
    )
    
    # Callback for gauge (CPU usage simulation)
    def get_cpu_usage(options):
        usage = 20.0 + random.random() * 60.0
        yield metrics.Observation(usage, {})
    
    cpu_gauge = meter.create_observable_gauge(
        name="cpu_usage_percent",
        callbacks=[get_cpu_usage],
        description="CPU usage percentage",
        unit="%"
    )
    
    print("\n✓ Metrics application started successfully!")
    print("✓ Sending metrics every 5 seconds...\n")
    
    request_count = 0
    
    try:
        while True:
            # Increment request counter
            request_count += 1
            request_counter.add(1, {
                "method": "GET",
                "status_code": "200",
                "endpoint": "/api/data"
            })
            
            # Record request duration
            duration = 0.1 + random.random() * 0.5
            request_duration.record(duration, {
                "method": "GET",
                "route": "/api/data"
            })
            
            print(f"📊 [{time.strftime('%H:%M:%S')}] Sent metrics: requests={request_count}, duration={duration:.3f}s")
            
            # Wait before next iteration
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n✓ Shutting down...")
        provider.shutdown()
        print("✓ Metrics sender stopped")

if __name__ == "__main__":
    main()