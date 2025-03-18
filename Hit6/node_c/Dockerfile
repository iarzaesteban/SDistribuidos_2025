FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install python-dotenv

ENV PYTHONUNBUFFERED=1

CMD ["python", "program_c.py"]
