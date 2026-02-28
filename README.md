# HR-Pulse 🚀

> Automated job offer analysis platform powered by Azure AI, FastAPI, and Next.js.

HR-Pulse helps recruiters analyze job offers, extract key skills using NLP, and predict competitive salary ranges using machine learning.

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        CLIENT                           │
│                    Next.js (port 3000)                  │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP /api/*
┌───────────────────────▼─────────────────────────────────┐
│                      BACKEND                            │
│                  FastAPI (port 8000)                    │
│         Auth │ Jobs │ Predictor │ OpenTelemetry         │
└──────┬────────────────┬────────────────────┬────────────┘
       │                │                    │
┌──────▼──────┐ ┌───────▼───────┐ ┌─────────▼──────────┐
│  Azure SQL  │ │  Azure AI     │ │  Jaeger (port 16686)│
│  Database   │ │  Language/NER │ │  Traces & Monitoring│
└─────────────┘ └───────────────┘ └────────────────────┘
```

---

## 📁 Project Structure

```
hr-pulse/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           ├── auth.py
│   │   │           ├── jobs.py
│   │   │           └── predictor.py
│   │   ├── core/               # Config & settings
│   │   ├── db/                 # SQLAlchemy session & base
│   │   ├── models/             # ORM models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/
│   │   │   ├── ner_service.py          # Azure AI NER
│   │   │   └── predictor_service.py    # ML salary prediction
│   │   ├── telemetry/          # OpenTelemetry setup
│   │   └── main.py
│   ├── data/
│   │   └── raw/jobs.csv
│   ├── ml/                     # Training notebooks & scripts
│   ├── models/
│   │   ├── salary_model.pkl
│   │   └── model_random_forest.pkl
│   ├── scripts/                # Ingestion & preprocessing
│   ├── tests/
│   │   └── test_core.py
│   └── Dockerfile
├── frontend/
│   ├── src/app/
│   │   ├── jobs/page.tsx
│   │   ├── predict/page.tsx
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── next.config.js
│   ├── Dockerfile
│   └── package.json
├── infrastructure/
│   └── terraform/
│       ├── main.tf             # Azure SQL + AI Language provisioning
│       └── docker.tf           # Docker provider for local orchestration
├── .env                        # Environment variables (not committed)
├── docker-compose.yml
├── pyproject.toml              # Python dependencies (uv)
└── uv.lock
```

---

## ⚙️ Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [uv](https://docs.astral.sh/uv/) — Python package manager
- [Node.js 20+](https://nodejs.org/)
- [Terraform](https://www.terraform.io/) — for infrastructure provisioning
- Azure account with access to your Resource Group

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Khaoula1025/HR-Pulse.git
cd hr-pulse
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your Azure credentials:

```env
DATABASE_URL=mssql+pyodbc://<user>:<password>@sql-server-hr-pulse-2026.database.windows.net/db-khaoula?driver=ODBC+Driver+18+for+SQL+Server
AZURE_LANGUAGE_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
AZURE_LANGUAGE_KEY=<your-key>
SECRET_KEY=<your-jwt-secret>
MODEL_PATH=models/salary_model.pkl
```

### 3. Launch with Docker Compose

```bash
docker compose up --build
```

| Service  | URL |
|----------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/docs |
| Jaeger UI | http://localhost:16686 |

---

## 🏗️ Infrastructure (Terraform)

### Provision Azure resources

```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

This creates:
- Azure SQL Database (serverless, auto-pause after 15 min)
- Azure AI Language service for NER extraction

### Launch containers with Terraform Docker provider

```bash
# From the same terraform folder
terraform apply
```

---

## 🤖 Data Pipeline

### 1. Preprocess and ingest jobs data

```bash
uv run python backend/scripts/preprocessing.py
uv run python backend/scripts/ingest.py
```

### 2. Run NER extraction (Azure AI)

```bash
uv run python backend/scripts/Ner_extraction.py
```

### 3. Train salary prediction model

```bash
uv run python backend/scripts/train_model.py
```

---

## 🧪 Tests & Code Quality

### Run linting

```bash
uv run ruff check backend/
# Auto-fix:
uv run ruff check backend/ --fix
```

### Run unit tests

```bash
uv run pytest backend/tests/ -v
```

Tests cover:
- Salary parsing (`$137K-$171K` → `154000.0`)
- ML feature construction
- FastAPI endpoints (mocked DB)
- Salary prediction (mocked model)

---

## ⚡ CI/CD Pipeline (GitHub Actions)

Every push triggers 3 sequential jobs:

```
lint ──► test ──► docker-build
```

| Job | Tool | Purpose |
|-----|------|---------|
| Lint | Ruff | Enforce Python code standards |
| Test | Pytest | Run unit tests |
| Docker Build | Docker | Verify images build without errors |

---

## 📊 Observability (OpenTelemetry + Jaeger)

The backend is fully instrumented with OpenTelemetry:

- **FastAPI routes** — auto-traced (latency, errors)
- **SQL queries** — auto-traced via SQLAlchemy instrumentation
- **Azure AI calls** — manual spans with response time tracking
- **500 errors** — visible directly in Jaeger UI

Open Jaeger at **http://localhost:16686** and select `hr-pulse-backend` to visualize traces.

---

## 🔒 Security

- No secrets committed to git — all credentials via `.env`
- JWT authentication on all protected endpoints
- `.env` is listed in `.gitignore`

---

## 👤 Author

**Khaoula** — HR-Pulse Project 2026