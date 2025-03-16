import socket
import time
import pytest

SERVER_HOST = 'server'
SERVER_PORT = 12345

def test_server_response():
    """Prueba que el servidor responde correctamente."""
    time.sleep(2)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        client_socket.sendall("Hola Servidor B!".encode())
        response = client_socket.recv(1024).decode()
        assert response == "Hola Cliente A, conexión establecida!"

def test_server_response_failed():
    """Prueba que el servidor NO responde correctamente."""
    time.sleep(2)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        client_socket.sendall("Hola Servidor B!".encode())
        response = client_socket.recv(1024).decode()
        assert response == "Hola Cliente A, conexión establecida!"