# Customer Data Pipeline

A Dockerized backend assessment project with three services: a Flask mock data server, a FastAPI ingestion service, and PostgreSQL for storage. The pipeline fetches paginated customer data from Flask, stages it with `dlt`, upserts it into PostgreSQL, and exposes read APIs from the database.

## Architecture

```text
mock-server/data/customers.json
            |
            v
    Flask Mock Server
      GET /api/customers
      GET /api/customers/{id}
            |
            v
   FastAPI Pipeline Service
      POST /api/ingest
      GET /api/customers
      GET /api/customers/{id}
            |
            v
        PostgreSQL
   public.customers_staging
   public.customers
```

## Tech Stack

- Python 3.11
- Flask
- FastAPI
- PostgreSQL 15
- SQLAlchemy 2
- dlt
- Docker Compose

## Project Structure

```text
.
|-- docker-compose.yml
|-- README.md
|-- mock-server
|   |-- app.py
|   |-- data
|   |   `-- customers.json
|   |-- Dockerfile
|   `-- requirements.txt
`-- pipeline-service
    |-- config.py
    |-- database.py
    |-- Dockerfile
    |-- main.py
    |-- models
    |   |-- __init__.py
    |   `-- customer.py
    |-- requirements.txt
    |-- routes
    |   |-- __init__.py
    |   |-- customers.py
    |   `-- ingest.py
    `-- services
        |-- __init__.py
        `-- ingestion.py
```

## Services

### 1. PostgreSQL

- Runs on port `5432`
- Database: `customer_db`
- Stores the final `customers` table

### 2. Flask Mock Server

- Runs on port `5000`
- Loads customer data from `mock-server/data/customers.json`
- Exposes paginated customer APIs

Endpoints:

- `GET /api/health`
- `GET /api/customers?page=1&limit=10`
- `GET /api/customers/{customer_id}`

### 3. FastAPI Pipeline Service

- Runs on port `8000`
- Creates the `customers` table on startup
- Fetches all paginated customer data from Flask
- Uses `dlt` to stage data into `customers_staging`
- Performs parameterized upserts into `customers`

Endpoints:

- `GET /api/health`
- `GET /api/health/db`
- `POST /api/ingest`
- `GET /api/customers?page=1&limit=10`
- `GET /api/customers/{customer_id}`

## How To Run

Start all services:

```bash
docker compose up --build -d
```

Check running containers:

```bash
docker compose ps
```

## How To Test

### Flask mock server

Health check:

```bash
curl http://localhost:5000/api/health
```

Paginated customers:

```bash
curl "http://localhost:5000/api/customers?page=1&limit=5"
```

Single customer:

```bash
curl http://localhost:5000/api/customers/C001
```

Missing customer:

```bash
curl http://localhost:5000/api/customers/FAKE
```

### FastAPI pipeline service

Service health:

```bash
curl http://localhost:8000/api/health
```

Database health:

```bash
curl http://localhost:8000/api/health/db
```

Run ingestion:

```bash
curl -X POST http://localhost:8000/api/ingest
```

Expected response:

```json
{"status":"success","records_processed":30}
```

List customers from PostgreSQL:

```bash
curl "http://localhost:8000/api/customers?page=1&limit=5"
```

Get one customer from PostgreSQL:

```bash
curl http://localhost:8000/api/customers/C001
```

Missing customer from PostgreSQL:

```bash
curl http://localhost:8000/api/customers/FAKE
```

## Database Schema

The `customers` table is defined in `pipeline-service/models/customer.py` with the following columns:

- `customer_id` `VARCHAR(50)` primary key
- `first_name` `VARCHAR(100)` not null
- `last_name` `VARCHAR(100)` not null
- `email` `VARCHAR(255)` not null
- `phone` `VARCHAR(20)`
- `address` `TEXT`
- `date_of_birth` `DATE`
- `account_balance` `DECIMAL(15, 2)`
- `created_at` `TIMESTAMP`

## Useful Commands

Stop the stack:

```bash
docker compose down
```

Stop and remove the Postgres volume:

```bash
docker compose down -v
```

Rebuild only the pipeline service:

```bash
docker compose up -d --build pipeline-service
```

View service logs:

```bash
docker compose logs -f mock-server
docker compose logs -f pipeline-service
docker compose logs -f postgres
```

## Troubleshooting

If PostgreSQL fails to start because port `5432` is already in use, stop the local process using that port or change the host-side port mapping in `docker-compose.yml`.

If ingestion fails after experimenting with schema changes, reset the local database volume and start again:

```bash
docker compose down -v
docker compose up --build -d
```
