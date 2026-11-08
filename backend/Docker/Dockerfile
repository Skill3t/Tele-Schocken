FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="/app/backend/.venv/bin:$PATH"

RUN pip install --no-cache-dir "poetry>=2,<3"

WORKDIR /app

COPY app/backend/pyproject.toml app/backend/poetry.lock ./backend/

WORKDIR /app/backend

RUN poetry install --only main --no-interaction --no-ansi --no-root

COPY app/backend/ ./
# Eigenen Benutzer und Gruppe erstellen
RUN groupadd --system teleschocken \
    && useradd --system \
       --gid teleschocken \
       --home-dir /app \
       --no-create-home \
       --shell /usr/sbin/nologin \
       teleschocken \
    && chown -R teleschocken:teleschocken /app \
    && id teleschocken \
    && grep '^teleschocken:' /etc/passwd

# Ab hier läuft die Anwendung ohne Root-Rechte
USER teleschocken

EXPOSE 8000

# python:slim enthält kein curl, daher Healthcheck über die Python-Standardbibliothek
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=4)"]

CMD ["poetry", "run", "gunicorn", "-k", "gevent", "-w", "1", "-b", "0.0.0.0:8000", "teleschocken:app"]