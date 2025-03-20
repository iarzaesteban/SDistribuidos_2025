import socket
import threading
import os
import json
import time
import logging
from logging.handlers import RotatingFileHandler

NODE_NAME = os.getenv('NODE_NAME')
LISTEN_HOST = os.getenv('LISTEN_HOST')
LISTEN_PORT = int(os.getenv('LISTEN_PORT'))

# Configuración de logs
class NodeNameFilter(logging.Filter):
    def filter(self, record):
        record.NODE_NAME = NODE_NAME
        return True

log_file = f"logs/output.log"
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
logging.getLogger().addFilter(NodeNameFilter())

# Registros de nodos C en memoria
registry = []
# Lista para guardar las conexiones de los nodos C (no utilizada actualmente)
connections = []

INSCRIPTIONS_PATH = "/app/logs/inscriptions.json"

def save_registry_to_file():
    try:
        with open(INSCRIPTIONS_PATH, "w") as f:
            json.dump(registry, f, indent=4)
        logging.info(f"Registro actualizado guardado en '{INSCRIPTIONS_PATH}'")
    except Exception as e:
        logging.error(f"Error al guardar el registro en el archivo: {e}")



def handle_connection(conn, addr):
    global registry, connections

    data = conn.recv(1024).decode()
    if data:
        node_info = json.loads(data)
        if node_info not in registry:
            registry.append(node_info)
            logging.info(f"[NODE D] Registrando nodo: {node_info}")
            print(f"[NODE D] Registrando nodo: {node_info}")
            # Guardamos el registro en un archivo JSON
            save_registry_to_file()
        
        # Enviamos la lista actualizada directamente al nodo que se conecta
        conn.sendall(json.dumps(registry).encode())
        conn.close()

        # Notificamos a todos los nodos registrados sobre el nuevo nodo
        broadcast_registry()

def broadcast_registry():
    global registry

    # Enviamos la lista de nodos a todos los nodos registrados
    for node in registry:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((node["ip"], node["port"]))
                s.sendall(json.dumps(registry).encode())
                logging.info(f"Enviamos lista actualizada a {node}")
                print(f"Enviamos lista actualizada a {node}")
        except Exception as e:
            logging.error(f"No se pudo enviar la actualización a {node}: {e}")
            print(f"No se pudo enviar la actualización a {node}: {e}")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((LISTEN_HOST, LISTEN_PORT))
        server_socket.listen()
        logging.info(f"[NODE D] Registro de contactos escuchando en {LISTEN_HOST}:{LISTEN_PORT}")
        print(f"[NODE D] Registro de contactos escuchando en {LISTEN_HOST}:{LISTEN_PORT}")
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_connection, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
