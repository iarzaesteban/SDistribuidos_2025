import socket
import threading
import os
import json
import time
import logging
import datetime
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

# Registros de nodos C para ventanas de tiempo
current_registry = []  # Nodos activos en la ventana actual
next_registry = []     # Nodos registrados para la siguiente ventana

def save_current_registry_to_file():
    # Si no hay nodos registrados en la ventana actual, no se crea el archivo.
    if not current_registry:
        logging.info("No hay registros en la ventana actual. No se crea archivo.")
        return

    window_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    file_path = f"/app/logs/inscriptions_{window_time}.json"
    try:
        with open(file_path, "w") as f:
            json.dump(current_registry, f, indent=4)
        logging.info(f"Registro de ventana guardado en '{file_path}'")
    except Exception as e:
        logging.error(f"Error al guardar el registro de ventana: {e}")


def window_rotation_loop():
    global current_registry, next_registry
    while True:
        now = datetime.datetime.now()
        # Calcula los segundos restantes hasta el inicio del próximo minuto
        seconds_to_sleep = 60 - now.second
        time.sleep(seconds_to_sleep)
        # Al alcanzar el límite, guarda la ventana actual
        save_current_registry_to_file()
        # Rota: los nodos de next_registry se vuelven la ventana actual
        current_registry = next_registry
        next_registry = []
        logging.info("Ventana rotada: la siguiente ventana se asigna a la actual.")

def handle_connection(conn, addr):
    global current_registry, next_registry
    data = conn.recv(1024).decode()
    if data:
        node_info = json.loads(data)
        # Se asigna el nodo a la siguiente ventana (sin duplicados)
        if node_info not in next_registry:
            next_registry.append(node_info)
            logging.info(f"[NODE D] Registrando nodo para la ventana futura: {node_info}")
            print(f"[NODE D] Registrando nodo para la ventana futura: {node_info}")
        # Se envía como respuesta la unión de los nodos de ambas ventanas
        response_registry = current_registry + next_registry
        conn.sendall(json.dumps(response_registry).encode())
        conn.close()
        # Se notifica (broadcast) a todos los nodos registrados
        broadcast_registry()

def broadcast_registry():
    global current_registry, next_registry
    all_nodes = current_registry + next_registry
    for node in all_nodes:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((node["ip"], node["port"]))
                s.sendall(json.dumps(all_nodes).encode())
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
    # Inicia el hilo para la rotación de ventanas
    rotation_thread = threading.Thread(target=window_rotation_loop, daemon=True)
    rotation_thread.start()
    # Inicia el servidor
    start_server()
