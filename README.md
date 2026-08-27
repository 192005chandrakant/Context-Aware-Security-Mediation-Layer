# CASML — Context-Aware Security Middleware Layer

CASML is a production-quality research prototype that protects tool-using LLM agents against indirect prompt injection and related unauthorized actions.

All privileged tool execution must pass through CASML.

## Project Structure

```
casml/
├── backend/                  # FastAPI Application & CASML Pipeline
│   ├── app/
│   │   ├── main.py           # Entry point
│   │   ├── api/              # API Routes
│   │   ├── core/             # Database & Config settings
│   │   ├── contracts/        # Shared Pydantic models (integration layer)
│   │   ├── agent/            # Agent interface / simulator
│   │   ├── casml/            # Security pipeline modules
│   │   ├── tools/            # Tool registry & Mock tools
│   │   ├── sandbox/          # Sandboxed execution environment
│   │   └── models/           # SQLAlchemy DB models
│   └── tests/                # Pytest suite
│
├── frontend/                 # React + TypeScript + Vite + Tailwind CSS Dashboard
│
├── dataset/                  # Datasets of benign & attack samples
│   ├── attacks/
│   ├── benign/
│   └── metadata/
│
├── experiments/              # Research experiments outputs
│   ├── raw/
│   └── processed/
│
├── configs/                  # Configurable security thresholds & policies
│   ├── models.yaml
│   ├── risk.yaml
│   ├── policies.yaml
│   └── tools.yaml
│
├── docker-compose.yml        # Development environment services
├── .env.example              # Template for environment variables
└── README.md                 # Setup & usage instructions
```

## Setup & Run Local Environment

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (uv or virtualenv recommended)
- Node.js 20+

### Setup Environment

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Start the database service:
   ```bash
   docker-compose up -d postgres
   ```

### Backend Setup

1. Install Python dependencies:
   ```bash
   cd backend
   pip install -e ".[dev]"
   ```

2. Run Alembic migrations (if DB is running):
   ```bash
   alembic upgrade head
   ```

3. Start backend development server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Install Node dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start frontend development server:
   ```bash
   npm run dev
   ```

## Running Tests

### Backend Tests
Runs all unit, integration, and security invariant tests:
```bash
cd backend
pytest tests/ -v
```

### Security Regression Tests
Proves that tool requests without authorization are rejected and external content cannot bypass the pipeline:
```bash
pytest tests/security/ -v
```
