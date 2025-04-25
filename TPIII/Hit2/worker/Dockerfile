FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY worker.py .
CMD ["python", "worker.py", "input_2.png", "output_2.png"]

