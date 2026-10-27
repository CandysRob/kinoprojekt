# Django backend arenduseks (docker-compose.yml teenus "backend")
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.12 /uv /uvx /bin/

# Virtuaalkeskkond on väljaspool /app kausta, et koodi kaardistamine seda ei peidaks
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-install-project

COPY . .

EXPOSE 8000
CMD ["uv", "run", "--frozen", "python", "manage.py", "runserver", "0.0.0.0:8000"]
