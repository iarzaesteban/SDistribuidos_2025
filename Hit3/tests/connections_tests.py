import socket
import time
import threading
import pytest
import subprocess

SERVER_HOST = 'servidor_tcp_h3'
SERVER_PORT = 12345


def connect_and_send_message(client_name, message):
    """Función auxiliar para conectarse al servidor y enviar mensajes."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        client_socket.sendall(client_name.encode())
        time.sleep(0.2)
        client_socket.sendall(message.encode())
        return client_socket.recv(1024).decode()


def test_connect_and_send_message():
    """Test para enviar un mensaje al servidor y verificar la respuesta."""
    client_name = "test_client"
    message = "Hello Server"
    response = connect_and_send_message(client_name, message)
    assert response == f"Hola {client_name} desde el servidor!"
    