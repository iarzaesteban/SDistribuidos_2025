$logPath = "logs/cliente.log.json"
$requestBody = @{
    imagen_docker = "tasks_image:latest"
    calculo = "suma"
    parametros = @{ a = 10; b = 20; c = 5 }
    datos_adicionales = @{ descripcion = "Suma de 3 valores" }
} | ConvertTo-Json -Depth 5

$response = Invoke-WebRequest -Uri "http://localhost:8000/getRemoteTask/" `
    -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body $requestBody

# Construimos un objeto de log
$logEntry = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    componente = "cliente"
    evento = "ejecutar_tarea"
    parametros_enviados = $requestBody | ConvertFrom-Json
    respuesta = ($response.Content | ConvertFrom-Json)
}

# Convertimos a JSON y lo guardamos (apendeamos)
$logJson = $logEntry | ConvertTo-Json -Depth 5

# Creamos archivo si no existe
if (!(Test-Path $logPath)) {
    New-Item -ItemType File -Path $logPath -Force | Out-Null
    Add-Content $logPath "["
} else {
    # Si ya hay contenido, sacamos el cierre del array anterior
    (Get-Content $logPath -Raw) -replace '\]\s*$', ',' | Set-Content $logPath
}

# Agregamos nueva entrada
Add-Content $logPath $logJson

# Cerramos el array de JSON nuevamente
Add-Content $logPath "]"

# Mostrar en pantalla también
$response.Content | ConvertFrom-Json | Format-List
