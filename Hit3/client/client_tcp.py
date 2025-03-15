import socket
import time
import uuid

SERVER_HOST = 'servidor_tcp_h3'
SERVER_PORT = 12345
RETRY_INTERVAL = 5  # Tiempo entre intentos de reconexión
MESSAGE_INTERVAL = 5  # Tiempo entre cada mensaje enviado

CLIENT_NAME = f"Cliente-{uuid.uuid4().hex[:5]}"

def start_client():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                print(f"Intentando conectar con {SERVER_HOST}:{SERVER_PORT}...")
                client_socket.connect((SERVER_HOST, SERVER_PORT))
                print("Conexión establecida con el servidor.")
                #Enviamos nombre cliente al server
                client_socket.sendall(CLIENT_NAME.encode())
                time.sleep(0.2)
                while True:
                    try:
                        # Enviar mensaje al servidor cada 5 segundos
                        message = f"Hola desde {CLIENT_NAME}!"
                        client_socket.sendall(message.encode())
                        print(f"Mensaje enviado: {message}")

                        # Recibir respuesta del servidor
                        response = client_socket.recv(1024).decode()
                        if not response:
                            raise ConnectionResetError("Servidor desconectado abruptamente.")

                        print(f"Respuesta del servidor: {response}")

                        # Esperar antes de enviar otro mensaje
                        time.sleep(MESSAGE_INTERVAL)
                    
                    except (ConnectionResetError, socket.error):
                        print("Conexión perdida con el servidor. Intentando reconectar...")
                        break

        except (ConnectionResetError, socket.error) as e:
            print(f"No se pudo conectar con el servidor. Error: {e}.")
            print(f"Reintentando en {RETRY_INTERVAL} segundos...")
            time.sleep(RETRY_INTERVAL)

if __name__ == "__main__":
    start_client()
