from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import docker
import requests
import time
import uuid
import base64
import subprocess
import os

from utils.json_logger import get_json_logger

app = FastAPI()
client = docker.from_env()

TASK_PORT = 5000

# Logger configurado
logger = get_json_logger("servidor", "logs/servidor.log.json")

class TaskRequest(BaseModel):
    imagen_docker: str
    parametros: dict
    calculo: str
    datos_adicionales: dict = None
    credenciales: dict = None

def docker_image_exists_locally(image_name: str) -> bool:
    try:
        client.images.get(image_name)
        return True
    except docker.errors.ImageNotFound:
        return False

def pull_docker_image(image_name: str, username: str = None, password: str = None):
    try:
        if username and password:
            logger.info(f"Logueando en Docker Hub como {username}...")
            client.login(username=username, password=password)
        logger.info(f"Descargando imagen '{image_name}' desde Docker Hub...")
        client.images.pull(image_name)
        logger.info(f"Imagen '{image_name}' descargada con éxito.")
    except docker.errors.APIError as e:
        logger.error(f"No se pudo descargar la imagen '{image_name}': {e}")
        return False
    return True

def build_and_push_image(image_name: str, username: str, password: str):
    try:
        repo, tag = image_name.split(":") if ":" in image_name else (image_name, "latest")
        full_image_name = f"{username}/{repo}:{tag}"

        logger.info(f"Construyendo imagen '{full_image_name}'...")
        subprocess.run(["docker", "build", "-t", full_image_name, "./server/task_service"], check=True)

        logger.info(f"Logueando en Docker Hub como {username}...")
        subprocess.run(["docker", "login", "-u", username, "--password-stdin"], input=password.encode(), check=True)

        logger.info(f"Subiendo imagen '{full_image_name}' a Docker Hub...")
        subprocess.run(["docker", "push", full_image_name], check=True)

        return full_image_name
    except subprocess.CalledProcessError as e:
        logger.exception("Error al construir o subir la imagen")
        raise HTTPException(status_code=500, detail=f"Error al construir o subir la imagen: {str(e)}")

@app.post("/getRemoteTask/")
def ejecutar_tarea_remota(payload: TaskRequest):
    imagen_docker = payload.imagen_docker
    parametros = payload.parametros
    calculo = payload.calculo
    credenciales = payload.credenciales

    username, password = None, None
    if credenciales:
        logger.info(f"Recibidas credenciales para el usuario: {credenciales.get('usuario')}")
        username = credenciales.get("usuario")
        password_encoded = credenciales.get("password")
        password = base64.b64decode(password_encoded).decode()

    if not docker_image_exists_locally(imagen_docker):
        logger.info(f"Imagen '{imagen_docker}' no encontrada localmente.")
        if not pull_docker_image(imagen_docker, username, password):
            logger.info(f"Construyendo imagen localmente porque no está en Docker Hub...")
            imagen_docker = build_and_push_image(imagen_docker, username, password)

    nombre_contenedor = f"task_container_{uuid.uuid4()}"
    logger.info(f"Iniciando contenedor '{nombre_contenedor}' con imagen '{imagen_docker}'")

    container = client.containers.run(
        image=imagen_docker,
        detach=True,
        remove=True,
        network="app_network",
        name=nombre_contenedor,
        ports={f"{TASK_PORT}/tcp": None},
        volumes={
            os.path.abspath("./logs"): {
                'bind': '/app/logs', 'mode': 'rw'
            }
        }
    )

    time.sleep(5)
    container.reload()
    task_service_ip = container.attrs['NetworkSettings']['Networks']['app_network']['IPAddress']
    logger.info(f"Contenedor iniciado. IP: {task_service_ip}")

    url_status = f"http://{task_service_ip}:{TASK_PORT}/status/"
    for _ in range(5):
        try:
            if requests.get(url_status).status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        container.stop()
        logger.error("Timeout esperando al servicio de tarea")
        return {"error": "Timeout esperando al servicio"}

    url = f"http://{task_service_ip}:{TASK_PORT}/ejecutarTarea/"
    response = requests.post(url, json={"parametros": parametros, "calculo": calculo})

    container.stop()
    logger.info(f"Contenedor detenido: {nombre_contenedor}")

    if response.status_code == 200:
        logger.info("Tarea ejecutada con éxito")
        return response.json()
    
    logger.error(f"Error en la tarea: código {response.status_code}")
    raise HTTPException(status_code=response.status_code, detail="Error en el servicio de tareas.")
