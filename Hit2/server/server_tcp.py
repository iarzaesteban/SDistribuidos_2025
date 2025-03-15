import socket

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 12345

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen()
        print(f"Servidor TCP esperando conexiones en {SERVER_HOST}:{SERVER_PORT}...")

        while True:
            conn, addr = server_socket.accept()
            print(f"Conexión establecida desde {addr}")

            with conn:
                while True:
                    data = conn.recv(1024).decode()
                    if not data:
                        print(f"Cliente {addr} desconectado.")
                        break  # Salir del bucle y esperar nueva conexión

                    print(f"Mensaje recibido: {data}")
                    conn.sendall("Hola Cliente A, conexión establecida!".encode())

if __name__ == "__main__":
    start_server()
