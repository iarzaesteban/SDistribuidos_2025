FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY server/server_app ./app

EXPOSE 8000

CMD ["uvicorn", "server.server_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
