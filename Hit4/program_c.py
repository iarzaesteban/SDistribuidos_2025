import socket
import threading
import time
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

NODE_NAME = os.getenv('NODE_NAME')
LISTEN_HOST = os.getenv('LISTEN_HOST')
LISTEN_PORT = int(os.getenv('LISTEN_PORT'))
PEER_HOST = os.getenv('PEER_HOST')
PEER_PORT = int(os.getenv('PEER_PORT'))

RETRY_INTERVAL = 5  # Tiempo entre intentos de reconexión
MESSAGE_INTERVAL = 5  # Tiempo entre cada mensaje enviado
SECONDS_TO_AWAIT_SERVER_START = 2



# Configuramos de logs
class NodeNameFilter(logging.Filter):
    def filter(self, record):
        # Inyectamos NODE_NAME en cada log
        record.NODE_NAME = NODE_NAME
        return True
    
log_file = f"logs/output.log"
# Como estamos en prueba no queremos que los logs supere los 500MB
log_handler = RotatingFileHandler(
    log_file, 
    maxBytes=500 * 1024 * 1024,  
    backupCount=2,
    encoding="utf-8"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s, [%(levelname)s], [%(NODE_NAME)s], [%(filename)s]: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    handlers=[log_handler]
)
# Agregamos el filtro personalizado para NODE_NAME
logging.getLogger().addFilter(NodeNameFilter())

def handle_connection(conn, addr):
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            logging.info(f"[{NODE_NAME}] Mensaje recibido: {data}")
            conn.sendall(f"Hola desde {NODE_NAME}!".encode())
    finally:
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((LISTEN_HOST, LISTEN_PORT))
        server_socket.listen()
        logging.info(f"[{NODE_NAME}] Escuchando en {LISTEN_HOST}:{LISTEN_PORT}...")
        
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_connection, args=(conn, addr)).start()

def start_client():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                logging.info(f"[{NODE_NAME}] Intentando conectar con {PEER_HOST}:{PEER_PORT}...")
                client_socket.connect((PEER_HOST, PEER_PORT))
                message = f"Hola desde {NODE_NAME}!"
                client_socket.sendall(message.encode())
                response = client_socket.recv(1024).decode()
                logging.info(f"[{NODE_NAME}] Respuesta recibida: {response}")
                time.sleep(MESSAGE_INTERVAL)
        except:
            logging.error(f"[{NODE_NAME}] Error de conexión. Reintentando en 5 segundos...")
            time.sleep(RETRY_INTERVAL)

if __name__ == "__main__":
    threading.Thread(target=start_server).start()
    time.sleep(SECONDS_TO_AWAIT_SERVER_START)
    start_client()
