# Script para ejecutar llama-server en modo router para desarrollo (CONEXION-MODELOS.md §6)

$llamaServerPath = "C:\Users\Max\AppData\Local\Microsoft\WinGet\Packages\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\llama-server.exe"
$modelsDir = "$env:APPDATA\IslandAgent\models"
$port = 8080
$hostIp = "127.0.0.1"
$apiKey = "dev-llama-key"

Write-Host "Iniciando llama-server en modo router..." -ForegroundColor Cyan
Write-Host "Directorio de modelos: $modelsDir"
Write-Host "Escuchando en: http://${hostIp}:${port}"

& $llamaServerPath `
  --models-dir $modelsDir `
  --models-max 1 `
  -c 8192 `
  -ngl 99 `
  --host $hostIp `
  --port $port `
  --api-key $apiKey

