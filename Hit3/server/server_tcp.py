import socket
import threading

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 12345

clients = {}

def handle_client(conn, addr):
    try:
        # Recibimos el nombre del cliente
        client_name = conn.recv(1024).decode()
        clients[conn] = client_name

        print(f"'{client_name}': se ha conectado desde {addr}")

        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            print(f"Mensaje de {client_name}: {data}")
            conn.sendall(f"Hola {client_name} desde el servidor!".encode())
    
    except (ConnectionResetError, socket.error):
        print(f"El cliente '{clients[conn]}' se ha desconectado abruptamente.")

    finally:
        client_name = clients.pop(conn, 'Cliente desconocido')
        print(f"El cliente '{client_name}' se ha desconectado.")
        conn.close()


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen()
        print(f"Servidor TCP escuchando en {SERVER_HOST}:{SERVER_PORT}...")

        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == "__main__":
    start_server()
