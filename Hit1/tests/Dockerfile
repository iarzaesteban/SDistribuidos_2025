FROM python:3.9

WORKDIR /app

COPY connections_tests.py .

RUN pip install pytest

CMD ["pytest", "connections_tests.py"]
