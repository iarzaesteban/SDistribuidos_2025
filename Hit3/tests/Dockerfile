FROM python:3.9

WORKDIR /app

COPY ./tests/connections_tests.py tests/connections_tests.py
COPY ./server/server_tcp.py server/server_tcp.py

RUN pip install pytest

CMD ["pytest", "tests/connections_tests.py"]