# Script para ejecutar y ver el proyecto Gem completo en funcionamiento

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       Iniciando Gem y Servicios          " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 0. Asegurar nivel de integridad Medium y desbloquear ejecutables para evitar bloqueo MIC (0xC0000142) y dialogos de seguridad
$env:SEE_MASK_NOZONECHECKS = 1
$nativeExe = "$PSScriptRoot\src-tauri\target\debug\island-agent.exe"
$debugDir = "$PSScriptRoot\src-tauri\target\debug"
Unblock-File -Path "$PSScriptRoot\start_project.ps1", "$PSScriptRoot\run_llama_dev.ps1", $nativeExe -ErrorAction SilentlyContinue
& icacls.exe $nativeExe /setintegritylevel M /Q | Out-Null
& icacls.exe "$debugDir\*.dll" /setintegritylevel M /Q | Out-Null

# Limpiar rutas conflictivas de MinGW antiguo (Haskell 2016) del PATH actual
$winlibs = "C:\Users\Max\AppData\Local\Microsoft\WinGet\Packages\BrechtSanders.WinLibs.POSIX.UCRT.LLVM_Microsoft.Winget.Source_8wekyb3d8bbwe\mingw64\bin"
$cleanPath = ($env:PATH -split ';' | Where-Object { $_ -notlike '*Haskell*' }) -join ';'
if (Test-Path $winlibs) {
    $env:PATH = "$winlibs;$cleanPath"
} else {
    $env:PATH = $cleanPath
}

# 1. Iniciar llama-server en modo router (puerto 8080)
$conn8080 = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue
if (-not $conn8080) {
    Write-Host "[1/4] Levantando llama-server con modelos Qwen 3.5 9B y Gemma 4 E4B..." -ForegroundColor Green
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\run_llama_dev.ps1`"" -WindowStyle Minimized
} else {
    Write-Host "[1/4] llama-server ya se encuentra activo en el puerto 8080." -ForegroundColor Green
}

# 2. Iniciar el Backend FastAPI (puerto 8765)
$conn8765 = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue
if (-not $conn8765) {
    Write-Host "[2/4] Levantando Backend FastAPI (SQLite + Migraciones + Router + Chat)..." -ForegroundColor Green
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -Command `"Set-Location '$PSScriptRoot'; `$env:PYTHONPATH='backend'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8765`"" -WindowStyle Hidden
} else {
    Write-Host "[2/4] Backend FastAPI ya se encuentra activo en el puerto 8765." -ForegroundColor Green
}

# 3. Iniciar Servidor Web Local para el Frontend (puerto 3000)
$conn3000 = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if (-not $conn3000) {
    Write-Host "[3/4] Iniciando servidor de recursos Frontend (puerto 3000)..." -ForegroundColor Green
    $frontendDir = Join-Path $PSScriptRoot "frontend"
    Start-Process -FilePath "python" -ArgumentList "-m http.server 3000 --directory `"$frontendDir`"" -WindowStyle Hidden
} else {
    Write-Host "[3/4] Servidor Frontend ya se encuentra activo en el puerto 3000." -ForegroundColor Green
}

# Esperar a que el servidor del frontend (puerto 3000) este escuchando antes de abrir Tauri
Write-Host "Verificando disponibilidad de puerto 3000..." -ForegroundColor Yellow
for ($i = 0; $i -lt 15; $i++) {
    if (Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue) {
        break
    }
    Start-Sleep -Milliseconds 400
}

# 4. Iniciar la Isla Nativa en el Escritorio (Tauri)
Stop-Process -Name "island-agent" -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500

if (Test-Path $nativeExe) {
    Write-Host "[4/4] Levantando Isla Dinamica de Escritorio (Tauri Native Window)..." -ForegroundColor Green
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $nativeExe
    $psi.WorkingDirectory = $debugDir
    $psi.UseShellExecute = $false
    [System.Diagnostics.Process]::Start($psi) | Out-Null
} else {
    Write-Host "[ERROR] No se encontro el binario nativo en: $nativeExe" -ForegroundColor Red
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "¡Gem esta corriendo en tu escritorio!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
