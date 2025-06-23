#!/bin/bash

set -e

project="blockchainsd2025"

# Definición de microservicios
services=(
    "redis::redis:7.2-alpine:true"
    "rabbitmq::rabbitmq:3-management:true"
    "nct:Pilar2/coordinador:deploy/Dockerfile:false"
    "mover:Pilar2/exchanger:deploy/Dockerfile:false"
    "validator:Pilar2/validator:deploy/Dockerfile:false"
    "pool:Pilar2/pool:deploy/Dockerfile:false"
    "worker-mock-1:Pilar2/worker_mock:deploy/Dockerfile:false"
    "worker-mock-2:Pilar2/worker_mock:deploy/Dockerfile:false"
    "worker-mock-3:Pilar2/worker_mock:deploy/Dockerfile:false"
    "worker-real:Pilar2/worker-real:Dockerfile:false"
    "frontend:pilar3-test-k8s/frontend:Dockerfile:false"
)

echo "Autenticando Docker con GCloud..."
gcloud auth configure-docker

for service in "${services[@]}"; do
    IFS=":" read -r name path df skipBuild <<< "$service"

    if [ "$skipBuild" = "true" ]; then
        echo "Skipping build for image: $name (usará imagen pública)"
        continue
    fi

    imageName="gcr.io/$project/$name:latest"

    echo -e "\nProcesando imagen: $name"

    # Validación extra: chequea si path está vacío
    if [ -z "$path" ]; then
        echo "El path para $name está vacío. Saltando..."
        continue
    fi

    docker build -t "$name" -f "$path/$df" "$path"
    docker tag "$name" "$imageName"
    docker push "$imageName"
done
