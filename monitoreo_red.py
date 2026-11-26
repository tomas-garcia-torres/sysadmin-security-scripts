import os
import re
import subprocess
import time
import json
import socket
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURACIÓN ---
RANGO_IP = "192.168.68"  # Ajustá si tu red usa 192.168.68. u otro rango Deco
INTERVALO_ESCANEO = 45
ARCHIVO_CONOCIDOS = "dispositivos_conocidos.json"

def cargar_conocidos():
    if os.path.exists(ARCHIVO_CONOCIDOS):
        try:
            with open(ARCHIVO_CONOCIDOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f" Error al leer {ARCHIVO_CONOCIDOS}: {e}")
    return {"AA-BB-CC-DD-EE-FF": "Router Principal"}

def guardar_conocidos(conocidos):
    try:
        with open(ARCHIVO_CONOCIDOS, "w", encoding="utf-8") as f:
            json.dump(conocidos, f, indent=4, ensure_ascii=False)
        print(f"  ✔ Lista actualizada y guardada en '{ARCHIVO_CONOCIDOS}'.")
    except Exception as e:
        print(f" Error al guardar en {ARCHIVO_CONOCIDOS}: {e}")

def obtener_nombre_host(ip):
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except (socket.herror, socket.gaierror, TimeoutError):
        return "Desconocido / No resuelto"

def ip_a_tupla(ip_str):
    try:
        return tuple(map(int, ip_str.split('.')))
    except ValueError:
        return (0, 0, 0, 0)

def _ping_host(ip):
    """Lanza un ping de 80ms a una IP específica (silencioso)."""
    subprocess.run(f"ping -n 1 -w 80 {ip}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def barrido_completo_subred():
    """Fuerza la respuesta de las 254 IPs en paralelo usando 50 hilos."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Escaneando subred completa ({RANGO_IP}1 a 254)...")
    ips = [f"{RANGO_IP}{i}" for i in range(1, 255)]
    with ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(_ping_host, ips)

def obtener_dispositivos_arp():
    resultado = subprocess.run(["arp", "-a"], capture_output=True, text=True, errors='ignore')
    lineas = resultado.stdout.splitlines()
    
    dispositivos = []
    patron = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+([0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2})')

    for linea in lineas:
        coincidencia = patron.search(linea)
        if coincidencia:
            ip = coincidencia.group(1)
            mac = coincidencia.group(2).lower().replace(":", "-")
            
            if not ip.startswith("224.") and not ip.endswith(".255") and mac != "ff-ff-ff-ff-ff-ff":
                dispositivos.append({'ip': ip, 'mac': mac})
                
    return dispositivos

def mostrar_resumen_dispositivos(equipos, conocidos):
    conocidos_lista = []
    desconocidos_lista = []

    for dev in equipos:
        ip = dev['ip']
        mac = dev['mac']

        if mac in conocidos:
            dev['nombre'] = conocidos[mac]
            conocidos_lista.append(dev)
        else:
            dev['hostname'] = obtener_nombre_host(ip)
            desconocidos_lista.append(dev)

    conocidos_lista.sort(key=lambda x: ip_a_tupla(x['ip']))
    desconocidos_lista.sort(key=lambda x: ip_a_tupla(x['ip']))

    print("\n" + "="*85)
    print(f"   RESUMEN DE DISPOSITIVOS DETECTADOS ({len(equipos)} ENCONTRADOS)")
    print("="*85)
    print(f"{'ESTADO':<15} | {'NOMBRE / ALIAS':<25} | {'DIRECCIÓN IP':<15} | {'DIRECCIÓN MAC'}")
    print("-" * 85)

    if conocidos_lista:
        print(" -- DISPOSITIVOS CONOCIDOS --")
        for dev in conocidos_lista:
            print(f" CONOCIDO     | {dev['nombre'][:24]:<25} | {dev['ip']:<15} | {dev['mac']}")

    if desconocidos_lista:
        if conocidos_lista:
            print("-" * 85)
        print(" -- DISPOSITIVOS DESCONOCIDOS --")
        for dev in desconocidos_lista:
            print(f" DESCONOCIDO  | {dev['hostname'][:24]:<25} | {dev['ip']:<15} | {dev['mac']}")

    print("="*85 + "\n")
    return desconocidos_lista

def monitorear():
    print("==================================================")
    print("   MONITOR DE RED DECO (DESCUBRIMIENTO MULTIHILO)")
    print("==================================================")
    
    conocidos = cargar_conocidos()
    print(f"Rango configurado: {RANGO_IP}1-254")
    print(f"Dispositivos conocidos registrados: {len(conocidos)}\n")

    try:
        while True:
            # Forzar barrido activo multihilo
            barrido_completo_subred()
            equipos_detectados = obtener_dispositivos_arp()
            
            desconocidos = mostrar_resumen_dispositivos(equipos_detectados, conocidos)
            
            if desconocidos:
                print(f"  [!] Se encontraron {len(desconocidos)} dispositivos no registrados.")
                for dev in desconocidos:
                    ip = dev['ip']
                    mac = dev['mac']
                    hostname = dev['hostname']

                    print(f"\n  --> Revisando dispositivo: IP {ip} | MAC {mac} ({hostname})")
                    opcion = input("      ¿Deseas agregar este dispositivo a la lista de conocidos? (s/n): ").strip().lower()

                    if opcion == 's':
                        alias = input(f"      Ingresa un nombre/alias [{hostname}]: ").strip()
                        if not alias:
                            alias = hostname if hostname != "Desconocido / No resuelto" else f"Equipo_{ip}"
                        
                        conocidos[mac] = alias
                        guardar_conocidos(conocidos)
                    else:
                        print("      - Dispositivo omitido.")

            print(f"\nPróximo escaneo en {INTERVALO_ESCANEO} segundos... (Presiona Ctrl+C para salir)\n")
            time.sleep(INTERVALO_ESCANEO)

    except KeyboardInterrupt:
        print("\n[!] Monitoreo detenido por el usuario.")

if __name__ == "__main__":
    monitorear()