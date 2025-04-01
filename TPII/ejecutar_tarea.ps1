# archivo: ejecutar_tarea.ps1

$accessToken = "<>"  # Reemplazá esto por tu token real
$encodedToken = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($accessToken))

$body = @{
    imagen_docker = "iarzaesteban94/sdistribuidos2025:latest"
    calculo = "suma"
    parametros = @{
        a = 10
        b = 20
        c = 5
    }
    datos_adicionales = @{
        descripcion = "Suma de 3 valores"
    }
    credenciales = @{
        usuario = "iarzaesteban94"
        password = $encodedToken
    }
} | ConvertTo-Json -Depth 5

$response = Invoke-WebRequest -Uri "http://localhost:8000/getRemoteTask/" `
  -Method POST `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body $body

$response.Content
