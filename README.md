# SysAdmin & Security Automation Scripts

Colección de utilidades modulares desarrolladas en **Python** y **PowerShell** para automatizar tareas de administración de sistemas, diagnóstico de redes y controles básicos de seguridad en Windows y Linux.

## Herramientas incluidas

* **Inventario de Hardware y Software:** Recolección rápida de especificaciones del equipo, versión del sistema operativo y programas instalados para soporte técnico y auditoría.
* **Monitor de Red Local y Auditoría Wi-Fi:** Detección de dispositivos conectados en la subred, análisis de intensidad de señal y verificación del tipo de cifrado inalámbrico.
* **Escáner de Puertos Abiertos:** Comprobación ligera de puertos TCP activos en hosts locales para validar servicios expuestos.
* **Verificador de Integridad de Archivos (FIM básico):** Cálculo y comparación de hashes (SHA-256) sobre directorios críticos para detectar modificaciones no autorizadas.
* **Analizador de Logs:** Filtrado rápido de eventos relevantes y errores en registros del sistema.

## Requisitos

* Python 3.10+ (librerías estándar: `socket`, `hashlib`, `subprocess`, `platform`, `os`).
* PowerShell 5.1 o superior (para utilidades nativas de Windows).
