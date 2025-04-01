# SDistribuidos_2025

# Proyecto Docker con Tareas Remotas

Este proyecto permite ejecutar tareas remotas dentro de contenedores Docker a través de un servidor API REST en FastAPI. El servidor interactúa con imágenes Docker, descarga o utiliza imágenes locales, y ejecuta tareas definidas por el cliente.

## Requisitos

- Docker
- Docker Compose
- Python 3.8+
- Dependencias de Python en `requirements.txt` (FastAPI, docker, requests, etc.)

## Estructura del Proyecto

El proyecto contiene las siguientes imágenes Docker:

1. **Servidor (`server_image`)**: Una imagen que contiene el servidor API en FastAPI, que maneja la solicitud y ejecución de tareas remotas.
2. **Tareas (`server_tasks_image`)**: Una imagen que contiene las tareas específicas que se ejecutan dentro de contenedores Docker, las cuales pueden ser definidas por el cliente.

## Comandos de Docker

Puedes usar los siguientes comandos para interactuar con el proyecto:

### Utilizar y probar los servidores

Para levantar entorno asegurarno de estar en el directorio TPII y ejecutamos:

```bash
make build_server_image
```

```bash
make build_server_tasks_image
```

```bash
make up_server
```

Para hacer pruebas de performance(guarda las metricas en tests/resultados_real.json):

```bash
make test_real
```

Le pegamos al servidor con curl simulando un cliente. Abrimos otra terminal y ejecutamos:

En linux:

```bash
curl -X POST "http://localhost:8000/getRemoteTask/" -H "Content-Type: application/json" -d '{
  "imagen_docker": "task_service:latest",
  "calculo": "suma",
  "parametros": {"a": 10, "b": 20, "c": 5},
  "datos_adicionales": {"descripcion": "Suma de 3 valores"}
}'
```

Con credenciales  
En linux:

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

O desde un powershell:

```bash
Invoke-WebRequest -Uri "http://localhost:8000/getRemoteTask/" `
  -Method POST `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{"imagen_docker": "tasks_image:latest", "calculo": "suma", "parametros": {"a": 10, "b": 20, "c": 5}, "datos_adicionales": {"descripcion": "Suma de 3 valores"}}'
```

Con credenciales  
En powershell:
```bash
.\ejecutar_tarea.ps1
```

La respuesta a esto sería la suma de a + b + c. En la terminal deberiamos ver algo como:

{"resultado":35}%

Para hacer pruebas automatizadas:

```bash
make test_docker
```

## 🧪 CI automático con GitHub Actions

![CI](https://github.com/iarzaesteban/SDistribuidos_2025/actions/workflows/ci.yml/badge.svg?branch=practico_II)

Este proyecto incluye un pipeline de **CI** en GitHub Actions que:

- 📦 Instala dependencias desde `requirements.txt`
- ✅ Ejecuta pruebas automatizadas con `pytest`
- 🧪 Mockea el cliente Docker para evitar fallas por imágenes ausentes

Los tests están ubicados en la carpeta `tests/` y se ejecutan automáticamente al hacer `push` o `pull_request` sobre la rama `practico_II`.

## Configuaración para Docker Hub

1- Crear cuenta en Docker Hub
2- Crear un access token para que en vez de hacer el login le facilitemos el usuario y en el password el token
3- Crear repo en Docker Hub
4- En el Dockerfile recordar instalar el cliente docker "apt-get install -y docker.io"
5- En el docker-compose-yml recordar montar el socket de Docker:
volumes:

- /var/run/docker.sock:/var/run/docker.sock

En el curl del cliente en el parámetro imagen_docker configurar de la siguiente manera:
<nombre_usuario>/<nombre_repo_dockerHub>:latest

Luego en el parámetro credenciales configurarlo de la siguiente manera:
{
"usuario": "<nombre_usuario>",
"password": "'$(echo -n "<access_token>" | base64)'"
}

Para la materia Sistemas distribuidos creamos una cuenta en Docker Hub y un repo, las credenciales son:
repo: sdistribuidos2025
usuario: iarzaesteban94
password: º

º --Solicitarlo al administrador--


## 🧪 Verificar estado del servicio de tareas (`/status/`)

---

### 🌐 Verificar remotamente (Docker Hub)

Si se subio la imagen a Docker Hub (`iarzaesteban94/sdistribuidos2025:latest`), podés testear el estado del contenedor directamente desde el registro remoto con:

```powershell
.\test_task_service_status.ps1
```

```linux
./test_task_status_linux.sh
```

Este script:

1. Baja la imagen desde Docker Hub (si no la tenés local).
2. La ejecuta con el puerto 5000.
3. Consulta el endpoint `/status/`.
4. Muestra la respuesta.
5. Y apaga el contenedor.

También deberías ver una respuesta como:

```
Respuesta del servicio:
status      : Its running
status_code : 200
```