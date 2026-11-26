Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "            INVENTARIO DE HARDWARE Y SOFTWARE             " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Sistema Operativo y Nombre de Equipo
$os = Get-CimInstance Win32_OperatingSystem
Write-Host "--- INFORMACION GENERAL ---" -ForegroundColor Yellow
Write-Host "Equipo:         $env:COMPUTERNAME"
Write-Host "Sistema Op:     $($os.Caption) ($($os.OSArchitecture))"
Write-Host "Version OS:     $($os.Version) (Build $($os.BuildNumber))"
Write-Host ""

# 2. Placa Madre (Motherboard) y BIOS
$mobo = Get-CimInstance Win32_BaseBoard -ErrorAction SilentlyContinue
$bios = Get-CimInstance Win32_BIOS -ErrorAction SilentlyContinue
Write-Host "--- PLACA MADRE Y BIOS ---" -ForegroundColor Yellow
Write-Host "Fabricante:     $($mobo.Manufacturer)"
Write-Host "Modelo:         $($mobo.Product)"
Write-Host "Version BIOS:   $($bios.SMBIOSBIOSVersion)"
Write-Host ""

# 3. Procesador (CPU)
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
Write-Host "--- PROCESADOR (CPU) ---" -ForegroundColor Yellow
Write-Host "Modelo:         $($cpu.Name)"
Write-Host "Nucleos/Hilos:  $($cpu.NumberOfCores) Nucleos Fisicos / $($cpu.NumberOfLogicalProcessors) Hilos"
Write-Host "Frecuencia:     $($cpu.MaxClockSpeed) MHz"
Write-Host ""

# 4. Memoria RAM (Detalle por modulo)
$ramModulos = Get-CimInstance Win32_PhysicalMemory -ErrorAction SilentlyContinue
$ramTotalBytes = ($ramModulos | Measure-Object -Property Capacity -Sum).Sum
$ramTotalGB = [math]::Round($ramTotalBytes / 1GB, 2)

Write-Host "--- MEMORIA RAM (Total: $ramTotalGB GB) ---" -ForegroundColor Yellow
$slot = 1
foreach ($m in $ramModulos) {
    $gb = [math]::Round($m.Capacity / 1GB, 2)
    Write-Host "  Modulo $slot`: $gb GB @ $($m.Speed) MHz ($($m.Manufacturer) - Slot: $($m.DeviceLocator))"
    $slot++
}
Write-Host ""

# 5. Tarjeta Grafica (GPU)
Write-Host "--- TARJETA GRAFICA (GPU) ---" -ForegroundColor Yellow
$gpus = Get-CimInstance Win32_VideoController
foreach ($gpu in $gpus) {
    $vramGB = [math]::Round($gpu.AdapterRAM / 1GB, 2)
    Write-Host "  GPU: $($gpu.Name) (VRAM: $vramGB GB - Resolucion: $($gpu.CurrentHorizontalResolution)x$($gpu.CurrentVerticalResolution))"
}
Write-Host ""

# 6. Almacenamiento (Discos fisicos y particiones)
Write-Host "--- UNIDADES DE ALMACENAMIENTO ---" -ForegroundColor Yellow
$discosFisicos = Get-CimInstance Win32_DiskDrive -ErrorAction SilentlyContinue
foreach ($d in $discosFisicos) {
    $sizeGB = [math]::Round($d.Size / 1GB, 2)
    Write-Host "  Disco Fisico: $($d.Model) ($sizeGB GB) - Interfaz: $($d.InterfaceType)"
}

Write-Host ""
Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 } | ForEach-Object {
    $libreGB = [math]::Round($_.FreeSpace / 1GB, 2)
    $totalGB = [math]::Round($_.Size / 1GB, 2)
    Write-Host "  Unidad $($_.DeviceID) Libre: $libreGB GB de $totalGB GB"
}
Write-Host ""

# 7. Adaptadores de Red (Wi-Fi / Ethernet)
Write-Host "--- ADAPTADORES DE RED ---" -ForegroundColor Yellow
Get-CimInstance Win32_NetworkAdapter | Where-Object { $_.PhysicalAdapter -and $_.NetConnectionStatus -eq 2 } | ForEach-Object {
    Write-Host "  Red: $($_.Name) (MAC: $($_.MACAddress))"
}
Write-Host ""

# 8. Muestra de Software Instalado
Write-Host "--- SOFTWARE INSTALADO (Resumen) ---" -ForegroundColor Yellow
$apps = Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*, 
                         HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName } | 
        Select-Object DisplayName, DisplayVersion | 
        Sort-Object DisplayName

$apps | Select-Object -First 10 | ForEach-Object {
    Write-Host "  - $($_.DisplayName) [$($_.DisplayVersion)]"
}

Write-Host "..."
Write-Host "Total de aplicaciones registradas: $($apps.Count)" -ForegroundColor Cyan
Write-Host ""