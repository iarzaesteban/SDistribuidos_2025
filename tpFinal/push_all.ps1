# PowerShell script actualizado para microservicios ubicados en tpFinal/
$ErrorActionPreference = 'Stop'

Write-Host '🔐 Autenticando Docker con GCloud...'
gcloud auth configure-docker

Write-Host '📦 Procesando imagen: backend'
$contextPath = Join-Path $PSScriptRoot "backend"
docker build -t backend $contextPath
docker tag backend gcr.io/blockchainsd2025/backend:latest
docker push gcr.io/blockchainsd2025/backend:latest

Write-Host '📦 Procesando imagen: coordinator'
$contextPath = Join-Path $PSScriptRoot "coordinator"
docker build -t coordinator $contextPath
docker tag coordinator gcr.io/blockchainsd2025/coordinator:latest
docker push gcr.io/blockchainsd2025/coordinator:latest

Write-Host '📦 Procesando imagen: frontend'
$contextPath = Join-Path $PSScriptRoot "frontend"
docker build -t frontend $contextPath
docker tag frontend gcr.io/blockchainsd2025/frontend:latest
docker push gcr.io/blockchainsd2025/frontend:latest

Write-Host '📦 Procesando imagen: split'
$contextPath = Join-Path $PSScriptRoot "split"
docker build -t split $contextPath
docker tag split gcr.io/blockchainsd2025/split:latest
docker push gcr.io/blockchainsd2025/split:latest

Write-Host '📦 Procesando imagen: joiner'
$contextPath = Join-Path $PSScriptRoot "joiner"
docker build -t joiner $contextPath
docker tag joiner gcr.io/blockchainsd2025/joiner:latest
docker push gcr.io/blockchainsd2025/joiner:latest

Write-Host '📦 Procesando imagen: pool'
$contextPath = Join-Path $PSScriptRoot "pool"
docker build -t pool $contextPath
docker tag pool gcr.io/blockchainsd2025/pool:latest
docker push gcr.io/blockchainsd2025/pool:latest

Write-Host '📦 Procesando imagen: worker_mock'
$contextPath = Join-Path $PSScriptRoot "worker_mock"
docker build -t worker_mock $contextPath
docker tag worker_mock gcr.io/blockchainsd2025/worker_mock:latest
docker push gcr.io/blockchainsd2025/worker_mock:latest

Write-Host '📦 Procesando imagen: worker_real'
$contextPath = Join-Path $PSScriptRoot "worker_real"
docker build -t worker_real $contextPath
docker tag worker_real gcr.io/blockchainsd2025/worker_real:latest
docker push gcr.io/blockchainsd2025/worker_real:latest

Write-Host '🔄 Reiniciando deployments...'
kubectl rollout restart deployment backend
kubectl rollout restart deployment coordinator
kubectl rollout restart deployment split
kubectl rollout restart deployment joiner
kubectl rollout restart deployment pool
kubectl rollout restart deployment worker-mock
kubectl rollout restart deployment worker-real
