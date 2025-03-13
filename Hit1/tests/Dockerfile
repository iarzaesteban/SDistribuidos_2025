FROM python:3.9

RUN pip install pytest

WORKDIR /app

COPY . .

CMD ["pytest", "connections_tests.py"]
