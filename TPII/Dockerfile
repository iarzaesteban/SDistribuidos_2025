FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y docker.io
COPY server/server_app ./app
COPY utils ./utils
EXPOSE 8000
CMD ["uvicorn", "server.server_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
