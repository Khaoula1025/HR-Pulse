FROM python:3.12-slim

# Install uv
RUN pip install uv

WORKDIR /app

COPY pyproject.toml .
RUN uv sync --no-dev

COPY . .

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]