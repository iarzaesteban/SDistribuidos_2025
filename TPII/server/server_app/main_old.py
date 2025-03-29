from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import docker
import requests
import time
import uuid 
import base64

app = FastAPI()
client = docker.from_env()

TASK_PORT = 5000

class TaskRequest(BaseModel):
    imagen_docker: str
    parametros: dict
    calculo: str
    datos_adicionales: dict = None
    credenciales: dict = None 

@app.post("/getRemoteTask/")
def ejecutar_tarea_remota(payload: TaskRequest):
    """
    Recibe una solicitud para ejecutar una tarea remota con una imagen Docker específica.
    """
    imagen_docker = payload.imagen_docker
    parametros = payload.parametros
    calculo = payload.calculo
    credenciales = payload.credenciales

    try:
        # Si hay credenciales, nos autenticamos en Docker Hub
        if credenciales:
            username = credenciales.get("usuario")
            password_encoded = credenciales.get("password")
            password = base64.b64decode(password_encoded).decode()
            
            client.login(username=username, password=password)
            print(f"Autenticado en Docker Hub como {username}")

        # Descargamos la imagen desde Docker Hub si no está disponible localmente
        try:
            client.images.get(imagen_docker)
            print(f"Imagen '{imagen_docker}' encontrada localmente.")
        except docker.errors.ImageNotFound:
            print(f"Descargando imagen '{imagen_docker}' desde Docker Hub...")
            client.images.pull(imagen_docker)

        # Levantamos el contenedor con la imagen enviada por el cliente, asignamos el nombre de la red, 
        # aignamos un nombre de contenedor único y asignamos un puerto de forma aleatoria
        container = client.containers.run(
            image=imagen_docker,
            detach=True,
            remove=True,
            network="app_network",
            name=f"task_container_{uuid.uuid4()}",
            ports={f"{TASK_PORT}/tcp": None}
        )

        # Esperamos 5 segundos a que el servicio esté disponible
        time.sleep(5)
        # Nos aseguramos que la info está actualizada
        container.reload()  
        task_service_ip = container.attrs['NetworkSettings']['Networks']['app_network']['IPAddress']

        # Enviamos los parámetros a la tarea dentro del contenedor
        url = f"http://{task_service_ip}:{TASK_PORT}/status/"
        max_retries = 5
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    break  # La API está lista
            except requests.exceptions.ConnectionError:
                time.sleep(1)  # Esperar antes de reintentar
                retries += 1

        if retries == max_retries:
            container.stop()
            return {"error": "Timeout esperando a que el servicio esté disponible"}
        url = f"http://{task_service_ip}:{TASK_PORT}/ejecutarTarea/"
        response = requests.post(url, json={"parametros": parametros, "calculo": calculo})
        
        # Detenemos el contenedor después de obtener la respuesta
        container.stop()

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Error en el servicio de tareas.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar la tarea: {str(e)}")
