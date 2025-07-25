# Monitoring Setup (Both Monitoring and Client's Server)

## Overview

This repository provides a monitoring setup with instructions for both the monitoring server and the client server, enabling the collection and visualization of system metrics.

## Structure

### Monitoring

- **Node Exporter** : Scrape metrics from the system itself
- **CAdvisor** : Scrape metris from each running container
- **OpenTelemetry Collector** : Collects all the metrics from itself and from each client connected 
- **Prometheus** : Processes all the metrics 
- **Promtail** : Groups logs from all containers into one 
- **Loki** : Receives and processes the logs from promtail and the system ifself 
- **Tempo** : Processes all the traces
- **Grafana** : Visualization tool

### Client

- **Node Exporter** : Scrape metrics from the system itself
- **CAdvisor** : Scrape metris from each running container
- **OpenTelemetry Collector** : Collects all the metrics from itself and sends to the monitoring server 
- **Promtail** : Groups logs from all containers into one and sends to the monitoring server
- **Additional services** : Needed to expose metrics from certain services (Only present in some docker compose)

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
- **Tempo**: Distributed tracing
- **Alertmanager**: Alert routing and management

### Client Setup (`/client`)
- **OpenTelemetry Collector**: Metrics collection and forwarding
- **Promtail**: Log shipping to Loki
- **System Monitoring**: Node exporter, cAdvisor, and custom exporters
- **Application Monitoring**: Custom metrics endpoints