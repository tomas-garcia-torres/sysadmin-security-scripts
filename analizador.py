import os
import sys
import psutil
import subprocess
import ctypes
import shutil
import re
from datetime import datetime, timedelta

def es_administrador():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def revisar_almacenamiento():
    print("\n[+] 1. REVISANDO ESPACIO EN DISCO...")
    particiones = psutil.disk_partitions()
    for particion in particiones:
        try:
            uso = psutil.disk_usage(particion.mountpoint)
            print(f"  - Disco {particion.device} ({particion.opts}):")
            print(f"    Total: {uso.total / (1024**3):.2f} GB")
            print(f"    Usado: {uso.percent}%")
            if uso.percent > 85:
                print("    ⚠️ ¡ALERTA! El disco está casi lleno. Podría causar lentitud.")
        except PermissionError:
            continue

def revisar_y_limpiar_archivos_basura():
    print("\n[+] 2. ESCANEANDO ARCHIVOS BASURA Y TEMPORALES...")
    
    rutas_basura = [
        os.environ.get('TEMP'),                                 
        os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp'), 
        os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Prefetch'), 
        os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Logs')      
    ]
    
    archivos_a_borrar = []
    espacio_total_basura = 0

    for ruta in rutas_basura:
        if not ruta or not os.path.exists(ruta):
            continue
        try:
            for root, dirs, files in os.walk(ruta):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        espacio_total_basura += os.path.getsize(fp)
                        archivos_a_borrar.append(fp)
                    except (PermissionError, FileNotFoundError):
                        continue
        except (PermissionError, FileNotFoundError):
            continue

    print(f"  - Archivos basura detectados: {len(archivos_a_borrar)}")
    print(f"  - Espacio total estimado a recuperar: {espacio_total_basura / (1024**2):.2f} MB")
    
    if archivos_a_borrar:
        respuesta = input("\n  ¿Deseas eliminar estos archivos basura ahora mismo? (s/n): ").strip().lower()
        if respuesta == 's':
            print("  [!] Eliminando archivos... Por favor, espera.")
            eliminados = 0
            errores = 0
            for archivo in archivos_a_borrar:
                try:
                    os.remove(archivo)
                    eliminados += 1
                except:
                    errores += 1
            print(f"  ✔ ¡Limpieza completada! Se borraron {eliminados} archivos.")
            if errores > 0:
                print(f"  (Nota: {errores} archivos no se pudieron borrar porque Windows los está usando ahora mismo).")
        else:
            print("  - Operación cancelada. No se borró ningún archivo.")
    else:
        print("  - No se encontraron archivos temporales para eliminar.")

def analizar_uso_programas():
    print("\n[+] 3. ANALIZANDO PROGRAMAS POCO USADOS (HISTORIAL DE MENÚ DE INICIO)...")
    
    rutas_inicio = [
        os.path.join(os.environ.get('ProgramData', 'C:\\ProgramData'), 'Microsoft\\Windows\\Start Menu\\Programs'),
        os.path.join(os.environ.get('AppData', ''), 'Microsoft\\Windows\\Start Menu\\Programs')
    ]
    
    programas_antiguos = []
    limite_tiempo = datetime.now() - timedelta(days=90) 

    palabras_criticas = [
        "windows", "system32", "microsoft", "powershell", "cmd", "administrative tools", 
        "herramientas administrativas", "seguridad", "defender", "driver", "nvidia", "intel", "amd"
    ]

    for ruta in rutas_inicio:
        if not os.path.exists(ruta):
            continue
        for root, dirs, files in os.walk(ruta):
            for f in files:
                if f.endswith('.lnk'): 
                    fp = os.path.join(root, f)
                    try:
                        fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(fp))
                        if fecha_modificacion < limite_tiempo:
                            nombre_app = f.replace('.lnk', '')
                            
                            ruta_baja = fp.lower()
                            nombre_bajo = nombre_app.lower()
                            
                            if any(critico in nombre_bajo or critico in ruta_baja for critico in palabras_criticas):
                                puedo_borrar = "No"
                            else:
                                puedo_borrar = "Sí"
                                
                            programas_antiguos.append((nombre_app, fecha_modificacion, puedo_borrar))
                    except (PermissionError, FileNotFoundError):
                        continue

    vistos = set()
    programas_filtrados = []
    for app, fecha, puedo in programas_antiguos:
        if app not in vistos:
            vistos.add(app)
            programas_filtrados.append((app, fecha, puedo))

    programas_filtrados = sorted(programas_filtrados, key=lambda x: x[1])

    if programas_filtrados:
        print("  - Los siguientes programas no muestran actividad reciente (Últimos 3 meses):")
        print(f"    {'-'*80}")
        print(f"    {'PROGRAMA':<35} | {'ÚLTIMO USO':<15} | {'¿PUEDO BORRAR?'}")
        print(f"    {'-'*80}")
        for app, fecha, puedo in programas_filtrados[:20]: 
            nombre_corto = app if len(app) <= 33 else app[:30] + "..."
            fecha_str = fecha.strftime('%Y-%m-%d')
            print(f"    {nombre_corto:<35} | {fecha_str:<15} | {puedo}")
        print(f"    {'-'*80}")
    else:
        print("  - Todos tus programas principales muestran actividad reciente.")

def revisar_y_ejecutar_actualizaciones():
    print("\n[+] 4. REVISANDO ACTUALIZACIONES DE SOFTWARE (WINGET)...")
    try:
        print("  - Buscando versiones nuevas pendientes... (esto puede tomar unos segundos)")
        resultado = subprocess.run(["winget", "upgrade"], capture_output=True, text=True, errors='ignore')
        
        lineas = resultado.stdout.split('\n')
        programas_actualizables = []
        capturando = False
        
        for linea in lineas:
            if "------" in linea:
                capturando = True
                continue
            if capturando and linea.strip():
                partes = re.split(r'\s{2,}', linea.strip())
                if len(partes) >= 2:
                    nombre = partes[0]
                    id_programa = partes[1]
                    if not id_programa.startswith("Conexión") and not id_programa.startswith("opciones"):
                        programas_actualizables.append({"nombre": nombre, "id": id_programa})

        if programas_actualizables:
            print(f"  - Se encontraron {len(programas_actualizables)} programas desactualizados:")
            for p in programas_actualizables:
                print(f"    * {p['nombre']} [{p['id']}]")
            
            respuesta_global = input("\n  ¿Deseas iniciar la actualización automática de todos los programas? (s/n): ").strip().lower()
            if respuesta_global == 's':
                programas_con_error = []
                
                # FASE 1: Intento automático y silencioso para todos
                for p in programas_actualizables:
                    print(f"\n  [!] Actualizando automáticamente: {p['nombre']}...")
                    proceso = subprocess.run(["winget", "upgrade", "--id", p['id'], "--exact"])
                    
                    if proceso.returncode != 0:
                        print(f"  ⚠️ {p['nombre']} falló o requiere atención manual. Se pospone para el final.")
                        programas_con_error.append(p)
                    else:
                        print(f"  ✔ ¡{p['nombre']} se actualizó correctamente!")
                
                # FASE 2: Volver a los errores al finalizar la lista
                if programas_con_error:
                    print("\n" + "="*50)
                    print("   REVISIÓN DE PROGRAMAS CON ERROR / ACCIÓN MANUAL")
                    print("="*50)
                    print(f"  Quedaron {len(programas_con_error)} programas pendientes por resolver:")
                    
                    for p in programas_con_error:
                        while True:
                            print(f"\n  --> Pendiente: {p['nombre']} ({p['id']})")
                            accion = input("      ¿Qué deseas hacer? [r=Reintentar / s=Saltar este programa / c=Cancelar todo el análisis]: ").strip().lower()
                            
                            if accion == 'c':
                                print("  - Proceso de actualizaciones cancelado.")
                                return
                            elif accion == 's':
                                print("  - Programa saltado.")
                                break
                            elif accion == 'r':
                                print(f"  [!] Reintentando actualizar {p['nombre']}...")
                                proceso_reintento = subprocess.run(["winget", "upgrade", "--id", p['id'], "--exact"])
                                if proceso_reintento.returncode == 0:
                                    print(f"  ✔ ¡{p['nombre']} se actualizó correctamente en el segundo intento!")
                                    break
                                else:
                                    print("  ❌ Volvió a fallar.")
                            else:
                                print("      Opción inválida. Usa r, s o c.")
                else:
                    print("\n  ✔ ¡Todos los programas se actualizaron automáticamente sin errores!")
            else:
                print("  - Operación omitida. Los programas se mantendrán en sus versiones actuales.")
        else:
            print("  - ¡Excelente! Todo el software gestionado por Winget parece estar completamente al día.")
    except FileNotFoundError:
        print("  - Winget no está disponible o no se encuentra en el PATH.")

def buscar_procesos_sospechosos():
    print("\n[+] 5. ESCANEANDO PROCESOS EN EJECUCIÓN (ANTIMALWARE BÁSICO)...")
    nombres_sospechosos = ["miner.exe", "crypto", "ransom", "unknown.exe", "keygen"]
    procesos_detectados = 0
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            info = proc.info
            nombre = info['name'] or ""
            nombre_bajo = nombre.lower()
            sospechoso_encontrado = False
            for s in nombres_sospechosos:
                if s in nombre_bajo:
                    sospechoso_encontrado = True
            if sospechoso_encontrado:
                print(f"  - ⚠️ Alerta: Proceso sospechoso por nombre: {nombre} (PID: {info['pid']})")
                procesos_detectados += 1
            ruta_exe = info['exe'] or ""
            ruta_baja = ruta_exe.lower()
            if "temp" in ruta_baja:
                print(f"  - ⚠️ Alerta: Proceso ejecutándose desde Temp: {nombre} -> {ruta_exe}")
                procesos_detectados += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    if procesos_detectados == 0:
        print("  - No se encontraron anomalías evidentes en los procesos activos.")

if __name__ == "__main__":
    print("==================================================")
    print("   SISTEMA DE DIAGNÓSTICO INTEGRAL Y SEGURO")
    print("==================================================")
    if not es_administrador():
        print("💡 Nota: Para aplicar actualizaciones globales del sistema y vaciar 'Prefetch',")
        print("          recuerda ejecutar tu terminal o VS Code como ADMINISTRADOR.")
    revisar_almacenamiento()
    revisar_y_limpiar_archivos_basura()
    analizar_uso_programas()
    revisar_y_ejecutar_actualizaciones()
    buscar_procesos_sospechosos()
    print("\n==================================================")
    print("   ANÁLISIS FINALIZADO CON ÉXITO")
    print("==================================================")