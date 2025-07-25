# Infrastructure Monitoring & Client Setup

A comprehensive monitoring and observability stack with distributed client configuration for production environments.

## Overview

This repository contains a complete infrastructure monitoring solution built with modern observability tools and designed for distributed client-server architecture.

### Architecture

- **Server-side Monitoring Stack**: Centralized monitoring with Prometheus, Grafana, Loki, Tempo, and Alertmanager
- **Client-side Collection**: Distributed metrics and logs collection using OpenTelemetry and Promtail
- **Remote Data Ingestion**: Direct client-to-server data streaming via Prometheus remote write and Loki push APIs

## Components

### Monitoring Server (`/monitoring`)
- **Prometheus**: Metrics storage and querying
- **Grafana**: Visualization and dashboards
- **Loki**: Log aggregation and search
- **Alertmanager**: Alert routing and management
<!-- - **Tempo**: Distributed tracing -->

### Client Setup (`/client`)
- **OpenTelemetry Collector**: Metrics collection and forwarding
- **Promtail**: Log shipping to Loki
- **System Monitoring**: Node exporter, cAdvisor, and custom exporters
- **Application Monitoring**: Custom metrics endpoints