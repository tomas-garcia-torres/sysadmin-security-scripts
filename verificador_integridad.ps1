param (
    [string]$RutaArchivo
)

if ([string]::IsNullOrWhitespace($RutaArchivo)) {
    $RutaArchivo = Read-Host "Arrastre o ingrese la ruta completa del archivo"
}

# Limpiar prefijo de invocacion '&', comillas simples y comillas dobles al arrastrar desde Windows
$RutaLimpia = $RutaArchivo.Trim()
if ($RutaLimpia.StartsWith("&")) {
    $RutaLimpia = $RutaLimpia.Substring(1).Trim()
}
$RutaLimpia = $RutaLimpia.Trim("'").Trim('"')

if (-not (Test-Path -Path $RutaLimpia)) {
    Write-Host "[Error] La ruta ingresada no existe: $RutaLimpia" -ForegroundColor Red
    exit
}

if (Test-Path -Path $RutaLimpia -PathType Container) {
    Write-Host "[Aviso] Debe especificar un archivo individual, no una carpeta." -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "            CALCULO DE INTEGRIDAD DE ARCHIVOS             " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

$info = Get-Item $RutaLimpia
Write-Host "Archivo:   $($info.Name)" -ForegroundColor Yellow
Write-Host "Tamanio:   $([math]::Round($info.Length / 1MB, 2)) MB" -ForegroundColor Yellow
Write-Host "Ubicacion: $($info.FullName)" -ForegroundColor Gray
Write-Host ""

Write-Host "Calculando Hashes cryptographicos..." -ForegroundColor Gray

$sha256 = (Get-FileHash -Path $RutaLimpia -Algorithm SHA256).Hash
$md5    = (Get-FileHash -Path $RutaLimpia -Algorithm MD5).Hash

Write-Host "SHA-256: $sha256" -ForegroundColor Green
Write-Host "MD5:     $md5" -ForegroundColor Cyan
Write-Host ""