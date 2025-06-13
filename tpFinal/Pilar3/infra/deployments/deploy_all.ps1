# PowerShell script para aplicar todos los YAML de Kubernetes
$ErrorActionPreference = 'Stop'

Write-Host '🚀 Aplicando manifiestos de Kubernetes...'
kubectl apply -f "$PSScriptRoot\backend.yaml"
kubectl apply -f "$PSScriptRoot\coordinator.yaml"
kubectl apply -f "$PSScriptRoot\frontend.yaml"
kubectl apply -f "$PSScriptRoot\split.yaml"
kubectl apply -f "$PSScriptRoot\joiner.yaml"
kubectl apply -f "$PSScriptRoot\pool.yaml"
kubectl apply -f "$PSScriptRoot\worker_mock.yaml"
kubectl apply -f "$PSScriptRoot\worker_real.yaml"
kubectl apply -f "$PSScriptRoot\worker-mock-hpa.yaml"