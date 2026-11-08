# --- Build-Stage: Abhängigkeiten mit Poetry in /app/backend/.venv installieren ---
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_OPTIONS_NO_PIP=true \
    POETRY_NO_INTERACTION=1

RUN pip install --no-cache-dir "poetry>=2,<3"

WORKDIR /app/backend

COPY app/backend/pyproject.toml app/backend/poetry.lock ./

RUN poetry install --only main --no-ansi --no-root


# --- Runtime-Stage: nur Python, .venv und Anwendungscode (ohne Poetry/pip) ---
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/backend/.venv/bin:$PATH"

# Sicherheitsupdates des Basis-Images einspielen und pip/setuptools entfernen,
# da sie zur Laufzeit nicht benötigt werden
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip uninstall -y pip setuptools wheel

# Eigenen Benutzer und Gruppe erstellen
RUN groupadd --system teleschocken \
    && useradd --system \
       --gid teleschocken \
       --home-dir /app \
       --no-create-home \
       --shell /usr/sbin/nologin \
       teleschocken

WORKDIR /app/backend

COPY --chown=teleschocken:teleschocken app/backend/ ./
# Nach dem Code kopieren, damit ein evtl. lokales .venv nicht drüberkopiert wird;
# .venv muss am gleichen Pfad liegen wie in der Build-Stage (Shebangs der Skripte)
COPY --from=builder --chown=teleschocken:teleschocken /app/backend/.venv ./.venv

# Ab hier läuft die Anwendung ohne Root-Rechte
USER teleschocken

EXPOSE 8000

# python:slim enthält kein curl, daher Healthcheck über die Python-Standardbibliothek
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=4)"]

CMD ["gunicorn", "-k", "gevent", "-w", "1", "-b", "0.0.0.0:8000", "teleschocken:app"]
