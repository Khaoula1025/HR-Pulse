# HR-Pulse

AI-powered job analysis platform.

## Quickstart

```bash
# 1. Copy and fill env
cp .env.example .env

# 2. Provision infrastructure
cd infrastructure/terraform
terraform init
terraform apply

# 3. Ingest data
cd ../../backend
uv run python scripts/train_model.py
uv run python scripts/ingest.py

# 4. Run locally
docker compose up --build
```

## Services

| Service   | URL                    |
|-----------|------------------------|
| API docs  | http://localhost:8000/docs |
| Frontend  | http://localhost:8501  |
| Jaeger UI | http://localhost:16686 |
