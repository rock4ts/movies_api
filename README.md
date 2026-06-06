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
| `GET` | `/v1/films/<uuid>` | Single film with genres and cast/crew |
| `GET` | `/v1/genres/` | List of all genres |
| `GET` | `/v1/genres/<uuid>` | Single genre by ID |
| `GET` | `/v1/persons/search` | Full-text search by person name |
| `GET` | `/v1/persons/<uuid>` | Single person by ID |
| `GET` | `/v1/persons/<uuid>/films` | Films linked to a person |

List and search endpoints accept pagination query parameters: `page_size` (default 50, max 100) and `page_number` (default 1). Film list also supports `sort` (`imdb_rating`, `-imdb_rating`) and `genre` (genre UUID).

## Data sources

Catalog data lives in three Elasticsearch indexes (see `elasticsearch/indexes/`):

- **movies** — films and TV shows with rating, genres, and people
- **genres** — genre name and description
- **persons** — actors, directors, and writers

Indexes are created by `elastic-init` and filled by the `movies-etl` service from the admin panel PostgreSQL database.

## Tech stack

- Python 3.12, FastAPI
- Elasticsearch 8.x
- Redis
- Gunicorn + Uvicorn workers (production)
- [uv](https://docs.astral.sh/uv/) for local dependency management

Optional integration with an external auth service via RS256 JWT. Access tokens are verified with the public key from `PUBLIC_KEY_PATH`.

## Local development

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Configure `.env.local` for local Redis and Elasticsearch (for example, `REDIS_HOST=127.0.0.1`, `ELASTIC_HOST=127.0.0.1`, `DEBUG=True`, `CACHE_TTL=300`). Place the auth service public key at `certs/jwt-public.pem` and set `PUBLIC_KEY_PATH=certs/jwt-public.pem` (this is the default when the variable is omitted).
3. Start Redis and Elasticsearch locally (or run the dev stack from repo root).
4. Ensure indexes exist and catalog data is loaded (`just elastic-init`, then `just etl-local` or the ETL container).
5. Sync dependencies and start the dev server:
   ```bash
   uv sync
   set -a && source .env.local && set +a; uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

From repo root, you can also start the full development stack:

```bash
just dev
```

API: http://127.0.0.1:8000/v1/films/  
OpenAPI docs: http://127.0.0.1:8000/docs

## Containerized run

Containerized runs are orchestrated from repo root:

- Development stack: `docker-compose.dev.yml`

The `movies-api` service runs in the development stack with Redis, Elasticsearch, nginx, and `movies-etl`. Ensure env files for dependent services are in place as well (`admin_panel/.env`, `movies_etl/.env`, and repo-root `.env` for PostgreSQL).

Copy `.env.example` to `.env` and use Docker network hostnames (`REDIS_HOST=redis`, `ELASTIC_HOST=elastic-db`). Mount the JWT public key into the container and point `PUBLIC_KEY_PATH` at it (for example, `/run/secrets/jwt/jwt-public.pem` as in `.env.example`). You can tune cache expiration with `CACHE_TTL` (seconds):

```bash
cp movies_api/.env.example movies_api/.env
```

Run development stack:

```bash
docker compose -f docker-compose.dev.yml up --build -d
```

The API is exposed through nginx at `/api`:

API: http://127.0.0.1/api/v1/films/  
OpenAPI docs: http://127.0.0.1/api/docs

## Running tests

Functional tests exercise the live API against Elasticsearch and Redis. Default connection settings in `tests/functional/settings.py` match the ports published by `docker-compose.tests.yml`:

| Service | Host | Port |
|---------|------|------|
| API | `127.0.0.1` | `8001` |
| Elasticsearch | `127.0.0.1` | `9201` |
| Redis | `127.0.0.1` | `6378` |

### Test stack (Docker)

1. Create `.env` for the API container (Docker network hostnames):
   ```bash
   cp .env.example .env
   ```
   Set `ELASTIC_HOST=elastic-db` — the Elasticsearch service name in `docker-compose.tests.yml`. Ensure `PUBLIC_KEY_PATH=/run/secrets/jwt/jwt-public.pem` (the default from `.env.example`); `docker-compose.tests.yml` mounts `./certs/jwt-public.pem` to that path.

   For JWT-related functional tests, also place the matching private key at `certs/jwt-private.pem` (used by the test suite to sign tokens).

2. Start Redis, Elasticsearch, and the API:
   ```bash
   docker compose -f docker-compose.tests.yml up --build -d
   ```

3. Run the full suite from the repo root:
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

## Updating dependencies

`pyproject.toml` is the source of truth for local development. After changing dependencies, export them for Docker builds:

```bash
uv export --format requirements-txt --no-hashes > requirements.txt
```
