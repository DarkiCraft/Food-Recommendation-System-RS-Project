FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Required to compile some Python dependencies (e.g., psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# init.py nukes/resets the DB, seeds data, and retrains — only when RUN_INIT=1 (e.g. in backend/.env).
# One-off: docker compose run --rm -e RUN_INIT=1 backend
#     or: docker compose run --rm backend python init.py
CMD ["/bin/sh", "-c", "if [ \"${RUN_INIT:-0}\" = \"1\" ]; then python init.py; fi && exec fastapi dev main.py --host 0.0.0.0 --port 8000"]
