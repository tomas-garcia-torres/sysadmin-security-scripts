import socket
from concurrent.futures import ThreadPoolExecutor

PUERTOS_CONOCIDOS = {
    21: "FTP - Transferencia de archivos (Inseguro)",
    22: "SSH - Administracion remota segura",
    23: "Telnet - Administracion remota en texto plano (Inseguro)",
    25: "SMTP - Envio de correo electronico",
    53: "DNS - Resolucion de nombres de dominio",
    80: "HTTP - Trafico web no cifrado",
    110: "POP3 - Recepcion de correo electronico",
    135: "RPC - Llamada a procedimiento remoto (Windows)",
    139: "NetBIOS - Comparticion de archivos e impresoras en red local",
    143: "IMAP - Acceso a correo electronico",
    443: "HTTPS - Trafico web cifrado (SSL/TLS)",
    445: "SMB - Comparticion de archivos y carpetas en Windows",
    1433: "MSSQL - Base de datos Microsoft SQL Server",
    3306: "MySQL - Base de datos MySQL / MariaDB",
    3389: "RDP - Escritorio remoto de Windows",
    8080: "HTTP-Proxy / Servidor web secundario",
    8443: "HTTPS Alt - Panel de administracion web secundario"
}

def escanear_puerto(ip, puerto):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.5)
    resultado = sock.connect_ex((ip, puerto))
    sock.close()
    if resultado == 0:
        desc = PUERTOS_CONOCIDOS.get(puerto, "Servicio personalizado o desconocido")
        return puerto, desc
    return None

def main():
    target = input("Ingrese la IP a auditar (ej. 192.168.1.1 o 127.0.0.1): ").strip()
    if not target:
        target = "127.0.0.1"
        
    print(f"\n[+] Escaneando puertos abiertos en {target}...\n")
    print(f"{'PUERTO':<10} | {'ESTADO':<10} | {'DESCRIPCION Y USO'}")
    print("-" * 75)
    
    puertos_abiertos = 0
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(escanear_puerto, target, p) for p in PUERTOS_CONOCIDOS.keys()]
        for future in futures:
            res = future.result()
            if res:
                puerto, desc = res
                print(f"{puerto:<10} | {'ABIERTO':<10} | {desc}")
                puertos_abiertos += 1
                
    print("-" * 75)
    print(f"Resumen: {puertos_abiertos} puertos abiertos detectados en {target}.\n")

if __name__ == "__main__":
    main()