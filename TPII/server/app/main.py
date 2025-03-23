import docker
import time
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
client = docker.from_env()

DOCKER_IMAGE = "server-task_service:latest"

class TaskRequest(BaseModel):
    task_name: str
    task_params: dict

def start_task_container():
    """Levanta el contenedor task_service temporalmente y devuelve su puerto."""
    try:
        # Verificar si la imagen existe
        try:
            client.images.get(DOCKER_IMAGE)
        except docker.errors.ImageNotFound:
            return {"error": f"La imagen {DOCKER_IMAGE} no existe en el sistema."}

        print("[INFO] Creando el contenedor task_service...")
        task_service_port = 5000

        # Crear y ejecutar el contenedor
        container = client.containers.run(
            DOCKER_IMAGE,
            command="python task_service.py",
            detach=True,
            remove=True,
            ports={"5000/tcp": 5000},
            network="app_network",
            name="task_service"
        )
        print(f"[INFO] Contenedor {container.id} iniciado.")

        container.reload()
        task_service_port = container.attrs['NetworkSettings']['Ports']['5000/tcp'][0]['HostPort']
        task_service_ip = container.attrs['NetworkSettings']['Networks']['app_network']['IPAddress']
        print(f"[INFO] task_service disponible en la IP {task_service_ip}")

        print(f"[INFO] task_service disponible en el puerto {task_service_port}")

        # Esperar a que el servicio de tareas esté disponible
        task_service_url = f"http://{task_service_ip}:5000/executeTask"
        for _ in range(10):  # Esperamos un máximo de 10 segundos
            try:
                response = requests.get(f"http://{task_service_ip}:5000/")
                if response.status_code == 200:
                    print("[INFO] task_service está listo.")
                    break
            except requests.exceptions.ConnectionError:
                print("[INFO] Esperando a que task_service arranque...")
                time.sleep(1)

        return container, task_service_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/getRemoteTask")
def get_remote_task(task: TaskRequest):
    try:
        container, task_service_url = start_task_container()

        # Enviar petición al contenedor
        response = requests.post(task_service_url, json=task.dict())

        # Detener y eliminar el contenedor después de la ejecución
        #container.stop()

        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
