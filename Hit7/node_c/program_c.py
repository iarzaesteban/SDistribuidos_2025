import socket
import threading
import time
import os
import json
import logging
from logging.handlers import RotatingFileHandler

NODE_NAME = os.getenv("NODE_NAME")
if not NODE_NAME:
    NODE_NAME = "nodes_c"

D_HOST = os.getenv("D_HOST")
D_PORT = int(os.getenv("D_PORT"))

# Configuración de logs
class NodeNameFilter(logging.Filter):
    def filter(self, record):
        record.NODE_NAME = NODE_NAME
        return True

log_dir = f"logs/{NODE_NAME}"
os.makedirs(log_dir, exist_ok=True)

log_file = f"{log_dir}/output.log"
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

HOST = socket.gethostbyname(socket.gethostname())

with socket.socket() as temp_sock:
    temp_sock.bind(('0.0.0.0', 0))
    PORT = temp_sock.getsockname()[1]

def register_with_d():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((D_HOST, D_PORT))
            # Agregamos un timestamp al registro para saber cuándo se conectó el nodo
            node_info = {
                "node_name": NODE_NAME,
                "ip": HOST,
                "port": PORT,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            message = json.dumps(node_info)
            s.sendall(message.encode())
            time.sleep(0.5)
            response = s.recv(1024).decode()
            if response:
                logging.info(f"RECIBIMOS LAS LISTAS DE NODOS C {json.loads(response)}")
                print(f"RECIBIMOS LAS LISTAS DE NODOS C {json.loads(response)}")
                return json.loads(response)
            else:
                logging.warning("[NODE C] No se recibió respuesta de node_d")
                return []
        except Exception as e:
            logging.error(f"No se pudo conectar con el nodo D {D_HOST}:{D_PORT}: {e}")
            return []

def greet_peers(peers):
    for peer in peers:
        if peer["node_name"] != NODE_NAME:
            try:
                logging.info(f"Vamos a mandarle un mensaje a {peer}")
                print(f"Vamos a mandarle un mensaje a {peer}")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((peer["ip"], peer["port"]))
                    message = {"node": NODE_NAME, "message": f"Hola {peer['node_name']} desde {NODE_NAME}"}
                    s.sendall(json.dumps(message).encode())
            except ConnectionRefusedError:
                logging.error(f"No se pudo conectar con {peer}")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('0.0.0.0', PORT))
        server_socket.listen()
        logging.info(f"[{NODE_NAME}] Escuchando en {HOST}:{PORT}")
        print(f"[{NODE_NAME}] Escuchando en {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            data = conn.recv(1024).decode()
            if data:
                logging.info(f"[{NODE_NAME}] Mensaje recibido: {data}")
                print(f"[{NODE_NAME}] Mensaje recibido: {data}")

if __name__ == "__main__":
    threading.Thread(target=start_server).start()
    time.sleep(2)

    peers = register_with_d()
    greet_peers(peers)
