# ProductIQ — AI-Driven Product Feedback Intelligence & Developer Workflow Platform

ProductIQ is an enterprise-grade AI application that ingests raw customer feedback, automatically classifies taxonomy (feedback type, category, subcategory, bug category, severity, priority, impact area, recommended action), detects duplicate candidate feedback, generates structured developer roadmaps with actionable task breakdowns, tracks developer workflow progress, and sends resolution notifications when issue fixes are verified.

---

## Architecture Overview

```text
React + TypeScript + Vite + Tailwind (Nginx / Port 80)
             │
             ▼ REST API Requests
FastAPI Application (Uvicorn / Port 8000)
             │
             ├──► Ollama llama3.1 LLM (Local / Port 11434)
             │      └── JSONParser & TaxonomyValidator (Strict Self-Correction)
             │
             ├──► DecisionEngine & DuplicateDetector (Vector Similarity)
             │
             ├──► RoadmapAgent & TaskWorkflowService (Deterministic Progress)
             │
             └──► PostgreSQL 16 Database (Alembic Migrations)
```

---

## Key Features

- **Automated Feedback Classification**: Analyzes raw customer input via local `llama3.1` into rigid hierarchical taxonomies.
- **Strict Taxonomy Validation**: Self-correcting AI output validation against `app/taxonomy/taxonomy.json`.
- **Vector Duplicate Detection**: Calculates semantic text similarity against existing candidate feedback items.
- **Automated Roadmap Generation**: Creates structured product roadmaps complete with effort estimates and acceptance criteria tasks.
- **Deterministic Task Workflow Engine**: Enforces valid progress (0–100%) and state transition rules (`Open` → `In Progress` → `Testing` → `Resolved` → `Closed`).
- **Resolution Alert System**: Recalculates roadmap progress and emits single resolution notifications when all tasks reach 100%.
- **Enterprise SaaS Dashboard**: Modern dark-themed React + Tailwind CSS dashboard with real-time server analytics and unread notification polling.

---

## Technology Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn, Pydantic 2.x, Loguru
- **Database**: PostgreSQL 16, SQLAlchemy 2.x, Alembic, Psycopg 3
- **AI / LLM**: Ollama (`llama3.1` model, local execution)
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS v4, Axios, React Router 6, Lucide React, Nginx
- **Containerization**: Docker, Docker Compose

---

## System Requirements

- **Python**: 3.11+
- **Node.js**: 20+ (with npm 10+)
- **Ollama**: Installed locally with `llama3.1` model pulled
- **PostgreSQL**: 16+ (or Docker Compose container)
- **Docker**: 24+ with Docker Compose v2+

---

## Quick Start — Local Development

### 1. Prerequisites & Ollama Setup

Ensure Ollama is running and pull the `llama3.1` model:

```bash
ollama serve
ollama pull llama3.1
```

### 2. Backend Setup

```bash
# Clone and navigate to project root
cd f:\productiq

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Run database migrations (or SQLite in-memory fallback will run automatically)
alembic upgrade head

# Run backend development server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install frontend dependencies
npm install

# Run Vite dev server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## Production Deployment with Docker Compose

ProductIQ can be built and deployed as containerized production services:

```bash
# Build containers
docker compose build

# Start services in detached mode
docker compose up -d

# Check status of running services
docker compose ps
```

Services exposed:
- **Frontend UI (Nginx)**: `http://localhost:80`
- **FastAPI REST API**: `http://localhost:8000/api/v1`
- **PostgreSQL Database**: `localhost:5432`

---

## Environment Variables Configuration

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | Environment mode (`development`, `testing`, `production`) |
| `DATABASE_URL` | `postgresql+psycopg://...` | PostgreSQL connection URL |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama service endpoint |
| `OLLAMA_MODEL` | `llama3.1` | Target LLM model name |
| `OLLAMA_TIMEOUT` | `120.0` | Execution timeout in seconds |
| `CORS_ORIGINS` | `http://localhost:5173...` | Allowed CORS origins (comma separated) |
| `LOG_LEVEL` | `INFO` | Loguru logging level |
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000/api/v1` | Frontend API client base URL |

---

## Testing & Verification

### Run Backend Unit & Integration Tests

```bash
# Run pytest test suite (100 tests)
python -m pytest -q
```

### Run Frontend Production Build Check

```bash
cd frontend
npm run build
```

---

## API Documentation

When the backend server is running, visit:
- **Swagger Interactive Documentation**: `http://127.0.0.1:8000/docs`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

Key Endpoints:
- `GET /api/v1/health`
- `POST /api/v1/feedback`
- `GET /api/v1/feedback`
- `GET /api/v1/feedback/{id}`
- `PATCH /api/v1/feedback/{id}/status`
- `GET /api/v1/roadmaps`
- `GET /api/v1/roadmaps/{id}`
- `PATCH /api/v1/roadmaps/{id}`
- `GET /api/v1/tasks/{id}`
- `PATCH /api/v1/tasks/{id}`
- `GET /api/v1/notifications`
- `PATCH /api/v1/notifications/{id}/read`
- `GET /api/v1/dashboard/summary`

---

## Troubleshooting Guide

- **Ollama Timeout or Model Error**: Ensure `ollama list` shows `llama3.1`. Increase `OLLAMA_TIMEOUT=180.0` in `.env` if hardware is constrained.
- **PostgreSQL Connection Timeout**: ProductIQ's `get_db()` automatically falls back to an in-memory SQLite engine if PostgreSQL is unreachable. For production PostgreSQL, verify container health via `docker compose logs postgres`.
- **CORS Errors**: Ensure the frontend port is included in the `CORS_ORIGINS` environment variable in `.env`.
