FROM python:3.11-slim

WORKDIR /app

# Copiamos el archivo de requirements e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el script del worker
COPY worker.py .

CMD ["python", "-u", "worker.py"]

