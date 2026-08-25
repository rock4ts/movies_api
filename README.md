# Movies API — Online Movie Theater

FastAPI service for an online movie theater platform. It serves film, genre, and person data from Elasticsearch with Redis caching for client applications.

Part of the [Yandex Practicum](https://practicum.yandex.ru/) diploma project (sprint 2).

## What it does

The service is the **read-optimized API layer** for the catalog: it queries Elasticsearch indexes populated by the ETL pipeline from the admin panel database and caches responses in Redis.

**REST API** (`/v1/`) returns catalog data as JSON:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/films/` | Paginated list with optional genre filter and rating sort |
| `GET` | `/v1/films/search` | Full-text search by film title |
| `GET` | `/v1/films/<uuid>` | Single film with genres and cast/crew (access-controlled; see below) |
| `GET` | `/v1/genres/` | List of all genres |
| `GET` | `/v1/genres/<uuid>` | Single genre by ID |
| `GET` | `/v1/persons/search` | Full-text search by person name |
| `GET` | `/v1/persons/<uuid>` | Single person by ID |
| `GET` | `/v1/persons/<uuid>/films` | Films linked to a person |

List and search endpoints accept pagination query parameters: `page_size` (default 50, max 100) and `page_number` (default 1). Film list also supports `sort` (`imdb_rating`, `-imdb_rating`) and `genre` (genre UUID).

### Film detail access control

`GET /v1/films/<uuid>` checks each film's `access_label` (`free`, `premium`, or `vip`) against the caller's allowed labels:

- **No JWT** (or a token without `access_labels`): only films with the `free` label are returned.
- **With JWT**: the `access_labels` claim in the access token lists which tiers the user may view. A film is returned only when its label is included in that list.
- **Superuser**: tokens with `is_superuser=true` may access films with any label.

Requests for a film the caller is not allowed to view return `403` with `film access error`. Other endpoints are not restricted by access labels.

## Data sources

The service reads catalog data from three Elasticsearch indexes:

- **movies** — films and TV shows with rating, genres, and people
- **genres** — genre name and description
- **persons** — actors, directors, and writers

Indexes and documents are created and updated by the ETL service.

## Tech stack

- Python 3.12, FastAPI
- Elasticsearch 8.x
- Redis
- Gunicorn + Uvicorn workers (production)
- Sentry error reporting (optional)
- Multiprocess-safe structured JSON file logging
- [uv](https://docs.astral.sh/uv/) for local dependency management

Optional integration with an external auth service via RS256 JWT. Access tokens are verified with the public key from `PUBLIC_KEY_PATH`. Send the token in the `Authorization: Bearer <token>` header on film detail requests when access beyond `free` content is required.

## Environment variables

Copy `.env.example` to `.env` and adjust values for your environment.

Key settings: `REDIS_HOST`, `ELASTIC_HOST`, `PUBLIC_KEY_PATH`, `CACHE_TTL`, index names (`FILM_INDEX`, `GENRE_INDEX`, `PERSON_INDEX`).

Logging and Sentry settings:

| Variable | Description |
|----------|-------------|
| `LOG_FILE_PATH` | Enable structured file logging and set the active JSON log path; unset to keep console-only logging |
| `LOG_MAX_BYTES` | Rotate the active log after this many bytes (default: 10 MiB) |
| `LOG_BACKUP_COUNT` | Number of rotated files retained (default: 7) |
| `SENTRY_ENABLED` | Report unhandled errors to Sentry when `true` and `SENTRY_DSN` is set |
| `SENTRY_DSN` | Sentry DSN; leave empty to keep Sentry off |
| `SENTRY_ENVIRONMENT` | Sentry environment tag (for example, `development`) |
| `SENTRY_RELEASE` | Optional release identifier |

## Logging and ELK

Console logging remains enabled for `docker compose logs`. When `LOG_FILE_PATH` is set, the service also writes one JSON object per line through a multiprocess-safe rotating handler. Events include timestamp, level, logger, message, process ID, and exception details.

The portfolio Compose stack sets `LOG_FILE_PATH=/var/log/movies-api/app.json`, mounts that directory as a named volume, and has Filebeat forward it through Logstash to daily `movies-api-YYYY.MM.dd` indexes in the logging Elasticsearch cluster. Search the events in Kibana at `http://localhost/logs/`.

## Error reporting (Sentry)

Unhandled exceptions are sent to Sentry when `SENTRY_ENABLED=true` and `SENTRY_DSN` is set. Expected `HTTPException` responses are ignored. Authorization headers, cookies, and request bodies are stripped; events are tagged with `service=movies-api`. Sentry performance tracing stays off.

The portfolio production stack uses a self-hosted Sentry at `http://sentry.localhost/`. Copy the **movies-api** project DSN from the UI, replace only the host with `sentry-api:9000`, and keep the project ID from that DSN. Tests set `SENTRY_ENABLED=false`.

## Getting started

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Copy `.env.example` to `.env` and adjust Redis, Elasticsearch, and JWT public key paths.
3. Place the auth service public key at the path configured in `PUBLIC_KEY_PATH` (default: `./certs/jwt-public.pem`).
4. Start Redis and Elasticsearch, then ensure indexes exist and catalog data is loaded.
5. Sync dependencies (including the `dev` group):
   ```bash
   uv sync --group dev
   ```

Run the service:

```bash
set -a && source .env && set +a; uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

OpenAPI docs: http://127.0.0.1:8000/docs

## Running tests

Sentry unit tests do not need Docker:

```bash
uv run pytest tests/test_sentry.py
```

Functional tests exercise the live API against Elasticsearch and Redis. Default connection settings in `tests/functional/settings.py` match the ports published by `docker-compose.tests.yml`:

| Service | Host | Port |
|---------|------|------|
| API | `127.0.0.1` | `8001` |
| Elasticsearch | `127.0.0.1` | `9201` |
| Redis | `127.0.0.1` | `6378` |

### Test stack (Docker)

1. JWT keys for the test stack live in `tests/docker/certs/` (included in the repo). Compose mounts the public key into the API container; pytest reads the private key from the same directory to sign tokens. The stack loads `.env.tests` with Docker network hostnames for Redis and Elasticsearch.

2. Start Redis, Elasticsearch, and the API:
   ```bash
   docker compose -f docker-compose.tests.yml up --build -d
   ```

3. Run the full suite from the `movies_api` directory:
   ```bash
   uv run pytest tests/functional -c tests/functional/pytest.ini
   ```

4. Stop the stack when finished:
   ```bash
   docker compose -f docker-compose.tests.yml down
   ```

### Run a subset

```bash
uv run pytest tests/functional/testunits/films -c tests/functional/pytest.ini
uv run pytest tests/functional/testunits/genres -c tests/functional/pytest.ini
uv run pytest tests/functional/testunits/persons -c tests/functional/pytest.ini
```

Override host or port via environment variables accepted by `tests/functional/settings.py` (for example, `ELASTIC_PORT`, `REDIS_PORT`, `SERVICE_PORT`).

## Code quality (PEP pipeline)

Install development-only tooling and enable hooks from the `movies_api` directory:

```bash
uv sync --group dev
uv run pre-commit install
```

Run checks manually:

```bash
uv run ruff format --check .
uv run ruff check .
```

Auto-format and apply safe lint fixes:

```bash
uv run ruff check --fix .
uv run ruff format .
```

## Updating dependencies

`pyproject.toml` is the source of truth for local development. After changing dependencies, export them for Docker builds:

```bash
uv export --format requirements-txt --no-dev --no-hashes -o requirements.txt
uv export --format requirements-txt --only-dev --no-hashes -o requirements-dev.txt
```
