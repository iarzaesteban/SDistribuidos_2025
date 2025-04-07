# Explicacion de programa

![alt text](<tp2sd2025.drawio (1).png>)
## Cliente

El cliente va a realizar una solicitud (HTTP GET/POST) para comunicarse con el servidor.
Los parametros son enviados en json, enviando la imagen de dockerhub que puede resolver la tarea, el tipo de tarea, los parametros de la misma y las credenciales para conectarse con la imagen en la nube.

```bash
curl -X POST "http://localhost:8000/getRemoteTask/" \
     -H "Content-Type: application/json" \
     -d '{
  "imagen_docker": "iarzaesteban94/sdistribuidos2025:latest",
  "calculo": "suma",
  "parametros": {"a": 10, "b": 20, "c": 5},
  "datos_adicionales": {"descripcion": "Suma de 3 valores"},
  "credenciales": {
    "usuario": "iarzaesteban94",
    "password": "'$(echo -n "<access_token>"º | base64)'"
  }
}'
```

## Servidor

Creamos un servidor HTTP que reciba las solicitudes del cliente, para cada solicitud veriifica si la iamgen docker ya esta descargada, si no esta hace un pull desde docker hub, si no le puede hacer pull la intenta crear localmente y subirla.
Luego levanta el contenedor con esa imagen (el servicio tarea), le pasa los parametros de la tarea, espera la respuesta del servicio, detiene el contenedor temporal y le devuelve el resultado al cliente.

Entre las tecnologias que usamos encontramos:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import docker
import requests
import time
import uuid
import base64
import subprocess
import os
```
1. FastAPI: framework para construir APIs RESTful
2. Docker SDK para Python: manejar imágenes y contenedores desde el código.
3. requests: para hacer request HTTP desde el servidor al contenedor.
4. uuid: generar nombres únicos para los contenedores.
5. base64: decodifica contraseñas encriptadas.
6. subprocess: construir o subir imágenes Docker si es necesario.

### Para levantar el contenedor temporal

```python
nombre_contenedor = f"task_container_{uuid.uuid4()}"
container = client.containers.run(
    image=imagen_docker,
    detach=True,
    remove=True,
    network="app_network",
    name=nombre_contenedor,
    ports={f"{TASK_PORT}/tcp": None},
    volumes={os.path.abspath("./logs"): {'bind': '/app/logs', 'mode': 'rw'}}
)
```

Se crea un contenedor temporal en base a la imagen recibida del cliente, a este se le asigna una red para cominarse con el contenedor desde el servidor, y luego se monta el volumen de logs.
Para ver si el servicio esta listo se chequea si el endpoint /status/ del contenedor responde, intento 5 veces y si no responde lo apago y devuelvo error.
Si esta listo, llama al endpoint /ejecutarTarea/ dentro del contenedor, pasándole los parámetros que llegaron del cliente.

Cuando termina de resolver la tarea, apaga el contenedor, y si la respuesta es correcta devuelve el resultado al cliente.


## Servicio tarea

Es pequenio servidor web (FAST API) expone un endpoint 'status' que informa si esta listo para recibir tareas, y un endpoint 'ejecutarTarea' que ejecuta la operacion enviada por el cliente. Este servicio esta contenido en una imagen docker que procesa calculos en base a lo enviado desde el cliente(pasando por el servidor).

```python
from fastapi import FastAPI
from pydantic import BaseModel
from utils.json_logger import get_json_logger

app = FastAPI()
logger = get_json_logger("task_service", "logs/task_service.log.json")
```

Tiene un FastApi para armar los endpoints y un logger para loguear en formato json, para ir dejando registro de las solicitudes.

Se define un modelo de entrada, que basicamente es con que formato espera los datos el endpoint /ejecutarTarea/, que recibe las variables con sus valores y la operacion a realizar. 

```python
class TareaRequest(BaseModel):
    parametros: dict
    calculo: str
```

El endpoint definido 'status' sirve para saber si el contenedor esta levantado y andando, para evitar ejecutar la tarea sin que el contenedor este levantado.

### Endpoint ejecutarTarea

Cuando llega una solicitud, extrae los datos JSON y loguea lo pedido. Luego ejecuta la tarea solicitada suma/promedio/multiplicacion y si pide otra tarea no existente da error y guarda un log con eso.
Si esta ok, devuelve un json con la respuesta del calculo. Si algo falla (por ejemplo, un tipo de dato incorrecto), atrapa la excepción y devuelve un mensaje de error.