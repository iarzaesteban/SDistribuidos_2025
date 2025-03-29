from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import docker
import requests
import time
import uuid
import base64
import subprocess

app = FastAPI()
client = docker.from_env()

TASK_PORT = 5000

class TaskRequest(BaseModel):
    imagen_docker: str
    parametros: dict
    calculo: str
    datos_adicionales: dict = None
    credenciales: dict = None

def docker_image_exists_locally(image_name: str) -> bool:
    """Verifica si una imagen Docker existe localmente."""
    try:
        client.images.get(image_name)
        return True
    except docker.errors.ImageNotFound:
        return False

def pull_docker_image(image_name: str, username: str = None, password: str = None):
    """Intenta hacer pull de una imagen de Docker Hub."""
    try:
        if username and password:
            print(f"Logueando en Docker Hub como {username}...")
            client.login(username=username, password=password)
        print(f"Descargando imagen '{image_name}' desde Docker Hub...")
        client.images.pull(image_name)
        print(f"Imagen '{image_name}' descargada con éxito de Docker Hub.")
    except docker.errors.APIError as e:
        print(f"No se pudo descargar la imagen '{image_name}': {e}")
        return False
    return True

def build_and_push_image(image_name: str, username: str, password: str):
    """Construye la imagen localmente y la sube a Docker Hub."""
    try:
        # Extraer nombre y tag de la imagen
        repo, tag = image_name.split(":") if ":" in image_name else (image_name, "latest")
        full_image_name = f"{username}/{repo}:{tag}"
        
        print(f"Construyendo imagen '{full_image_name}'...")
        subprocess.run(["docker", "build", "-t", full_image_name, "./server/task_service"], check=True)
        
        print(f"Logueando en Docker Hub como {username}...")
        subprocess.run(["docker", "login", "-u", username, "--password-stdin"], input=password.encode(), check=True)
        
        print(f"Pushing imagen '{full_image_name}' a Docker Hub...")
        subprocess.run(["docker", "push", full_image_name], check=True)
        return full_image_name
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error al construir o subir la imagen: {str(e)}")

@app.post("/getRemoteTask/")
def ejecutar_tarea_remota(payload: TaskRequest):
    """Recibe una solicitud para ejecutar una tarea remota con una imagen Docker específica."""
    imagen_docker = payload.imagen_docker
    parametros = payload.parametros
    calculo = payload.calculo
    credenciales = payload.credenciales
    
    username, password = None, None
    if credenciales:
        print(f"entro a credenciales {credenciales}")
        username = credenciales.get("usuario")
        password_encoded = credenciales.get("password")
        password = base64.b64decode(password_encoded).decode()
    
    # Verificamos si la imagen está disponible localmente
    if not docker_image_exists_locally(imagen_docker):
        print(f"Imagen '{imagen_docker}' no encontrada localmente.")
        if not pull_docker_image(imagen_docker, username, password):
            print(f"Construyendo imagen localmente porque no está en Docker Hub...")
            imagen_docker = build_and_push_image(imagen_docker, username, password)
    
    # Ejecutamos el contenedor
    container = client.containers.run(
        image=imagen_docker,
        detach=True,
        remove=True,
        network="app_network",
        name=f"task_container_{uuid.uuid4()}",
        ports={f"{TASK_PORT}/tcp": None}
    )
    
    time.sleep(5)
    container.reload()
    task_service_ip = container.attrs['NetworkSettings']['Networks']['app_network']['IPAddress']
    
    url = f"http://{task_service_ip}:{TASK_PORT}/status/"
    for _ in range(5):
        try:
            if requests.get(url).status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        container.stop()
        return {"error": "Timeout esperando al servicio"}
    
    url = f"http://{task_service_ip}:{TASK_PORT}/ejecutarTarea/"
    response = requests.post(url, json={"parametros": parametros, "calculo": calculo})
    
    container.stop()
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail="Error en el servicio de tareas.")
