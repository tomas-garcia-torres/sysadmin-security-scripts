Write-Host "==========================================================================================" -ForegroundColor Cyan
Write-Host "                AUDITORIA DE REDES Y CIFRADO WI-FI COMPLETA (PS)                          " -ForegroundColor Cyan
Write-Host "==========================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Escaneando el espectro radioelectrico en tiempo real..." -ForegroundColor Gray

# Forzar captura en formato de texto estándar de la consola de Windows
$salida = netsh wlan show networks mode=bssid | Out-String

if ([string]::IsNullOrWhitespace($salida) -or $salida -match "no hay ninguna interfaz") {
    Write-Host "❌ No se encontro una interfaz Wi-Fi activa." -ForegroundColor Red
    exit
}

$lineas = $salida -split "`r`n"

Write-Host ("{0,-20} | {1,-18} | {2,-6} | {3,-8} | {4,-15} | {5,-8} | {6}" -f "SSID (RED)", "BSSID (MAC ANTENA)", "CANAL", "SENAL", "AUTENTICACION", "CIFRADO", "EVALUACION") -ForegroundColor Yellow
Write-Host ("-" * 107)

$ssidActual = ""
$autenticacion = "Desconocida"
$cifrado = "Desconocido"
$bssidMAC = ""
$canal = "N/A"
$senal = "N/A"
$totalSSID = 0
$totalBSSID = 0
$ssidsVistos = @{}

foreach ($linea in $lineas) {
    $l = $linea.Trim()

    # 1. Capturar SSID
    if ($l -match "^SSID \d+\s*:\s*(.*)$") {
        $ssidActual = $matches[1].Trim()
        if ([string]::IsNullOrWhitespace($ssidActual)) { $ssidActual = "<SSID Oculto>" }
    }
    # 2. Capturar Autenticación
    elseif ($l -match "Autenticac|Authentication") {
        $autenticacion = ($l -split ":")[1].Trim()
    }
    # 3. Capturar Cifrado
    elseif ($l -match "Cifrado|Encryption") {
        $cifrado = ($l -split ":")[1].Trim()
    }
    # 4. Capturar BSSID / MAC Antena
    elseif ($l -match "^BSSID \d+\s*:\s*(.*)$") {
        $bssidMAC = $matches[1].Trim()
        $totalBSSID++
    }
    # 5. Capturar Señal (Tolerante a 'Señal' con ñ y '%' explícito)
    elseif ($l -match "Se.al|Signal|Percent|%") {
        if ($l -match "(\d+)\s*%") {
            $senal = "$($matches[1])%"
        }
    }
    # 6. Capturar Canal e imprimir fila al completar el bloque
    elseif ($l -match "Canal|Channel") {
        if ($l -match ":\s*(\d+)") {
            $canal = $matches[1]
        }

        if ($ssidActual -ne "" -and $bssidMAC -ne "") {
            $evaluacion = "Revisa manual"
            if ($autenticacion -match "Abierta|Open") { $evaluacion = "CRITICO: Red Abierta" }
            elseif ($autenticacion -match "WPA3") { $evaluacion = "EXCELENTE: WPA3" }
            elseif ($autenticacion -match "WPA2") { $evaluacion = "ACEPTABLE: WPA2-PSK" }
            elseif ($autenticacion -match "WEP") { $evaluacion = "INSEGURO: WEP" }
            elseif ($autenticacion -match "WPA") { $evaluacion = "DEBIL: WPAv1" }

            if (-not $ssidsVistos.ContainsKey($ssidActual)) {
                $ssidsVistos[$ssidActual] = $true
                $totalSSID++
                $ssidMostrar = $ssidActual
            } else {
                $ssidMostrar = "  +-- (Nodo Mesh)"
            }

            $ssidCorta = if ($ssidMostrar.Length -gt 19) { $ssidMostrar.Substring(0, 19) } else { $ssidMostrar }

            $fmt = "{0,-20} | {1,-18} | {2,-6} | {3,-8} | {4,-15} | {5,-8} | {6}"
            Write-Host ($fmt -f $ssidCorta, $bssidMAC, $canal, $senal, $autenticacion, $cifrado, $evaluacion)
            
            # Reiniciar valores temporales de la antena
            $bssidMAC = ""
            $senal = "N/A"
            $canal = "N/A"
        }
    }
}

Write-Host ("-" * 107)
Write-Host "Resumen: $totalSSID redes (SSID) y $totalBSSID antenas/nodos (BSSID) detectados." -ForegroundColor Cyan