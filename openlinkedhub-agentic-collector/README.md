# OpenLinkedHub Agentic Collector

OpenLinkedHub Agentic Collector is a production-ready reference implementation for an hourly, tag-driven open data harvesting platform focused on Vietnam's digital transformation. It combines Scrapy spiders, an orchestrating agent, FastAPI for serving normalized records, and persistence in PostgreSQL or SQLite.

## Key features

- **Agentic orchestration** that plans and executes jobs per portal/tag with retries and run reporting.
- **Multi-source collection** from:
  - [data.gov.vn](https://data.gov.vn) (national CKAN)
  - [opendata.danang.gov.vn](https://opendata.danang.gov.vn) (local CKAN)
  - [opendata.mic.gov.vn](https://opendata.mic.gov.vn)
  - [World Bank open API](https://api.worldbank.org/v2/)
- **Tag-first discovery** on every portal with normalization of provinces, indicators, and values.
- **Unified storage** using SQLAlchemy, with optional MinIO raw export integration hooks.
- **FastAPI OpenAPI service** exposing `/api/records`, `/api/health`, and `/api/meta/tags`.
- **Scheduling** via cron-friendly shell entrypoint and an Airflow DAG running hourly.
- **Exports** to JSONL and CSV for downstream processing.
- **Testing** suite covering selector logic and API responses.

## Architecture overview

```text
+----------------+        +------------------------+
| Cron / Airflow | -----> | Agent Orchestrator     |
+----------------+        | - Plans tag jobs       |
                          | - Runs Scrapy spiders  |
                          | - Emits run metadata   |
                          +-----------+------------+
                                      |
                                      v
                           +----------+-----------+
                           | Scrapy Collectors    |
                           |  - CKAN (data.gov.vn)|
                           |  - MIC portal        |
                           |  - World Bank API    |
                           +----------+-----------+
                                      |
                         +------------+--------------+
                         | Pipelines (validation,    |
                         | normalization, database,  |
                         | exports)                  |
                         +------------+--------------+
                                      |
                     +----------------+----------------+
                     | PostgreSQL / SQLite (records)   |
                     +----------------+----------------+
                                      |
                              +-------+-------+
                              | FastAPI API   |
                              +---------------+
```

## Getting started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (for containerized deployment)
- Git

### Clone & setup environment

```bash
git clone https://github.com/your-org/openlinkedhub-agentic-collector.git
cd openlinkedhub-agentic-collector
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Database initialization

By default the application uses SQLite at `data/collector.db`. To use PostgreSQL, set `DATABASE_URL` in `.env` to something like `postgresql+psycopg2://user:password@host:5432/dbname` and run `alembic` or the schema from `db/schema.sql`.

### Running locally

1. **API**

   ```bash
   make run
   # visit http://localhost:8000/docs for OpenAPI explorer
   ```

2. **Manual crawl**

   ```bash
   make crawl
   # Exports appear under exports/, database populated under data/
   ```

3. **Tests**

   ```bash
   make test
   ```

### Docker Compose deployment

```bash
docker-compose up --build
```

Services:

- `db`: PostgreSQL 15
- `minio`: Optional object storage for raw exports
- `api`: FastAPI service (port 8000)
- `airflow`: Scheduler with DAG `olh_agentic_collector`

### Scheduling

- **Cron**: add `0 * * * * /path/to/repo/agent/scheduler/run_hourly.sh`
- **Airflow**: mount repo into `/opt/olh`, enable DAG shipped under `agent/scheduler/airflow/dags/olh_collector_dag.py`

## Configuration

All configs live under `agent/config/`:

- `tags.yaml`: list of tags to crawl hourly.
- `sources.ckan.yaml`: CKAN base URLs.
- `sources.mic.yaml`: listing selectors for MIC portal.
- `sources.worldbank.yaml`: tag → indicator mappings for World Bank API.

Adjust tags or add new portals without code changes.

## API usage

### Health

```bash
curl http://localhost:8000/api/health
```

### Records

```
GET /api/records?indicator=internet&limit=20&offset=0
```

Response:

```json
{
  "total": 1,
  "limit": 20,
  "offset": 0,
  "items": [
    {
      "id": "worldbank:IT.NET.USER.ZS:2022",
      "source": "https://api.worldbank.org",
      "dataset": "Individuals using the Internet (% of population)",
      "resource_id": "IT.NET.USER.ZS",
      "tags": ["internet"],
      "indicator": "internet",
      "province": null,
      "province_code": null,
      "year": "2022",
      "date": null,
      "value": 75.5,
      "raw": { "value": 75.5 },
      "fetched_at": "2024-03-08T10:00:00Z"
    }
  ]
}
```

### Tags metadata

```bash
curl http://localhost:8000/api/meta/tags
```

## Directory layout

See the scaffold in the repository root for full structure, including spiders, orchestrator, configs, API, and tests.

## Airflow DAG

The DAG `olh_agentic_collector` schedules hourly and runs collectors in the order `worldbank → ckan → mic → finalize`. Customize environment variables via `.env` mounted into the container.

## Release & changelog

- First stable release tagged `v1.0.0` (see `CHANGELOG.md`).

## Contributing

Please read `CONTRIBUTING.md` for development workflow, coding style, and submission guidelines. Issues and pull requests are welcome.

## License

MIT License – see `LICENSE`.
