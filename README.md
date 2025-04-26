# prayog-api
Prayog is an experimentation system, which you can run as a service to conduct experiments.

prayog-api exposes the experimentation libraries from prayog-core through the REST interface.

## Services

1. FastAPI application (port 8000)
2. Cassandra database (port 9042)
3. OpenTelemetry Collector
4. Prometheus (port 9090)
5. Grafana (port 3000)
6. Jaeger (port 16686)

## Setup

1. Install Poetry: `pip install poetry`
2. Install dependencies: `poetry install`
3. Copy .env.example to .env and adjust if needed
4. Run with Docker: `docker-compose up --build`

## Endpoints

- FastAPI: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Jaeger UI: http://localhost:16686