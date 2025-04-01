# Nombre de la imagen y contenedor
$imageName = "iarzaesteban94/sdistribuidos2025:latest"
$containerName = "test_task_remote"
$localPort = 5006
$containerPort = 5000

Write-Host "Verificando si el puerto $localPort está libre..."
$portInUse = (Get-NetTCPConnection -LocalPort $localPort -ErrorAction SilentlyContinue)
if ($portInUse) {
    Write-Host "❌ El puerto $localPort ya está en uso. Por favor, liberalo o usa otro puerto."
    exit 1
}

Write-Host "Levantando contenedor '$containerName' en el puerto $localPort..."
docker run -d --rm -p ${localPort}:${containerPort} --name $containerName $imageName

Start-Sleep -Seconds 5

Write-Host "Consultando http://localhost:$localPort/status/"
try {
    $response = Invoke-RestMethod -Uri "http://localhost:$localPort/status/" -Method GET
    Write-Host "`nRespuesta del servicio:"
    $response | Format-List
} catch {
    Write-Host "No se pudo contactar con el servicio en el puerto $localPort."
}

Write-Host "Deteniendo contenedor..."
docker stop $containerName | Out-Null