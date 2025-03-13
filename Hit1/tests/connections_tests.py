import socket
import threading
import pytest
from server.server_tcp import start_server

@pytest.fixture
def server():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

def test_server_response(server):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(("127.0.0.1", 12345))
        client_socket.sendall("Hola Servidor B!".encode())
        response = client_socket.recv(1024).decode()
        assert response == "Hola Cliente A, conexión establecida!"