# FinancePilot AI — Backend Dockerfile (skeleton)
# No application entrypoint exists yet; this builds the environment only.

FROM python:3.11-slim

WORKDIR /app

# System deps (kept minimal; extend as needed once pandas/etc. are pinned)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# TODO: replace once app/main.py exists
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "-c", "print('Backend skeleton — no app entrypoint yet')"]
