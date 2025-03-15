import socket
import time

SERVER_HOST = 'servidor_tcp_h2'
SERVER_PORT = 12345
RETRY_INTERVAL = 5  # Tiempo entre intentos de reconexión
MESSAGE_INTERVAL = 5  # Tiempo entre cada mensaje enviado

def start_client():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                print(f"Intentando conectar con {SERVER_HOST}:{SERVER_PORT}...")
                client_socket.connect((SERVER_HOST, SERVER_PORT))
                print("Conexión establecida con el servidor.")

                while True:
                    try:
                        # Enviar mensaje al servidor cada 5 segundos
                        message = "Hola Servidor B!"
                        client_socket.sendall(message.encode())
                        print(f"Mensaje enviado: {message}")

                        # Recibir respuesta del servidor
                        response = client_socket.recv(1024).decode()
                        print(f"Respuesta del servidor B: {response}")

                        # Esperar antes de enviar otro mensaje
                        time.sleep(MESSAGE_INTERVAL)
                    
                    except (ConnectionResetError, socket.error):
                        print("Conexión perdida con el servidor. Intentando reconectar...")
                        break  # Salir del bucle interno para intentar reconectar

        except (ConnectionRefusedError, socket.error) as e:
            print(f"No se pudo conectar: {e}. Reintentando en {RETRY_INTERVAL} segundos...")
            time.sleep(RETRY_INTERVAL)  # Espera antes de intentar nuevamente

if __name__ == "__main__":
    start_client()
