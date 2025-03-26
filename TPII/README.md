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

O desde un powershell:
```bash
Invoke-WebRequest -Uri "http://localhost:8000/getRemoteTask/" `
  -Method POST `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{"imagen_docker": "tasks_image:latest", "calculo": "suma", "parametros": {"a": 10, "b": 20, "c": 5}, "datos_adicionales": {"descripcion": "Suma de 3 valores"}}'
```

La respuesta a esto sería la suma de a + b + c. En la terminal deberiamos ver algo como:

{"resultado":35}%

Para hacer pruebas automatizadas:
```bash
make test_docker
```