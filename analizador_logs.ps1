Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         ANALIZADOR DE EVENTOS Y LOGS DE SEGURIDAD        " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[+] Analizando eventos de Seguridad y Sistema (ultimas 24hs)..." -ForegroundColor Gray
Write-Host ""

# Eventos de login fallido (Event ID 4625)
$loginsFallidos = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625; StartTime=(Get-Date).AddDays(-1)} -ErrorAction SilentlyContinue

Write-Host "--- INTENTOS FALLIDOS DE INICIO DE SESION (Event ID 4625) ---" -ForegroundColor Yellow
if ($loginsFallidos) {
    Write-Host "⚠️ Alerta: Se detectaron $($loginsFallidos.Count) intentos fallidos de login." -ForegroundColor Red
    $loginsFallidos | Select-Object -First 5 | ForEach-Object {
        Write-Host "  Fecha: $($_.TimeCreated) | Usuario: $($_.Properties[5].Value)"
    }
} else {
    Write-Host "[OK] Sin registros de fallos de inicio de sesion recientes." -ForegroundColor Green
}

Write-Host ""
# Eventos de errores criticos del sistema (Kernel-Power 41 / Event 6008)
Write-Host "--- ERRORES CRITICOS DE SISTEMA (Ultimas 24hs) ---" -ForegroundColor Yellow
$erroresCriticos = Get-WinEvent -FilterHashtable @{LogName='System'; Id=41,6008; StartTime=(Get-Date).AddDays(-1)} -ErrorAction SilentlyContinue

if ($erroresCriticos) {
    Write-Host "⚠️ Se registraron apagos inesperados o fallos de energia:" -ForegroundColor Red
    $erroresCriticos | Select-Object -First 5 | ForEach-Object {
        Write-Host "  [$($_.TimeCreated)] ID: $($_.Id) | Origen: $($_.ProviderName)"
    }
} else {
    Write-Host "[OK] Sin apagones o reinicios criticos detectados en el sistema." -ForegroundColor Green
}

Write-Host ""