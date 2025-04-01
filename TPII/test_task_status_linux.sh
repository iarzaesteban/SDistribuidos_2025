#!/bin/bash

IMAGE_NAME="iarzaesteban94/sdistribuidos2025:latest"
CONTAINER_NAME="task_status_remote"
LOCAL_PORT=5005
CONTAINER_PORT=5000

echo "Verificando si el puerto $LOCAL_PORT está libre..."
if lsof -i :$LOCAL_PORT >/dev/null; then
    echo "❌ El puerto $LOCAL_PORT ya está en uso. Elegí otro o liberalo."
    exit 1
fi

echo "Levantando contenedor '$CONTAINER_NAME' en el puerto $LOCAL_PORT..."
docker run -d --rm -p ${LOCAL_PORT}:${CONTAINER_PORT} --name $CONTAINER_NAME $IMAGE_NAME

echo "Esperando a que el servicio arranque..."
sleep 5

echo "Consultando http://localhost:$LOCAL_PORT/status/"
STATUS=$(curl -s http://localhost:$LOCAL_PORT/status/)

if [ -n "$STATUS" ]; then
    echo -e "\nRespuesta del servicio:"
    echo "$STATUS"
else
    echo "No se pudo contactar con el servicio."
fi

echo "Deteniendo contenedor..."
docker stop $CONTAINER_NAME > /dev/null