FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY task_service.py .
COPY utils/ ./utils/ 

CMD ["uvicorn", "task_service:app", "--host", "0.0.0.0", "--port", "5000"]

