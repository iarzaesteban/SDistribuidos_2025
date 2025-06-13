# PowerShell script para aplicar todos los servicios de Kubernetes
$ErrorActionPreference = 'Stop'

Write-Host '🌐 Aplicando servicios de Kubernetes...'

kubectl apply -f "$PSScriptRoot\backend_service.yaml"
kubectl apply -f "$PSScriptRoot\coordinator_service.yaml"
kubectl apply -f "$PSScriptRoot\frontend_service.yaml"
kubectl apply -f "$PSScriptRoot\joiner_service.yaml"
kubectl apply -f "$PSScriptRoot\split_service.yaml"
kubectl apply -f "$PSScriptRoot\worker-mock_service.yaml"
