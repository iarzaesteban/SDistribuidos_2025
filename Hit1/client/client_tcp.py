import socket
SERVER_HOST = 'servidor_tcp_h1'
SERVER_PORT = 12345

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        client_socket.sendall("Hola Servidor B!".encode())
        response = client_socket.recv(1024).decode()
        print(f"Respuesta del servidor B: {response}")

if __name__ == "__main__":
    start_client()
