#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

docker build -t gcr.io/alert-parsec-456902-u3/sobel-worker:latest ./worker
docker push gcr.io/alert-parsec-456902-u3/sobel-worker:latest

docker build -t gcr.io/alert-parsec-456902-u3/sobel-backend:latest ./backend
docker push gcr.io/alert-parsec-456902-u3/sobel-backend:latest

docker build -t gcr.io/alert-parsec-456902-u3/sobel-frontend:latest ./frontend
docker push gcr.io/alert-parsec-456902-u3/sobel-frontend:latest


Write-Host "🔄 Borrando recursos anteriores..."

$paths = @(
    "k8s_actualizados/redis-deployment.yaml",
    "k8s_actualizados/redis-service.yaml",
    "k8s_actualizados/rabbitmq-deployment.yaml",
    "k8s_actualizados/rabbitmq-service.yaml",
    "k8s_actualizados/backend-deployment.yaml",
    "k8s_actualizados/backend-service.yaml",
    "k8s_actualizados/backend-service-external.yaml",
    "k8s_actualizados/frontend-deployment.yaml",
    "k8s_actualizados/frontend-service.yaml",
    "k8s_actualizados/nginx-deployment.yaml",
    "k8s_actualizados/nginx-service.yaml",
    "k8s_actualizados/worker-deployment.yaml"
    "k8s_actualizados/worker-hpa.yaml"
)

foreach ($path in $paths) {
    kubectl delete -f $path --ignore-not-found
}

Write-Host "🚀 Aplicando recursos nuevamente..."

foreach ($path in $paths) {
    kubectl apply -f $path
}

make restart

Write-Host "✅ Todo levantado de nuevo correctamente."
