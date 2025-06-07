FROM python:3.10-slim

WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY deploy/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY utils ./utils

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8989"]
