# 🛠️ USB Recovery Tool

![Versión](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.x-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

**USB Recovery Tool** es una utilidad profesional y minimalista diseñada para rescatar y restaurar unidades flash USB dañadas o con errores de formato. Con una interfaz moderna en "Dark Mode", permite devolver la vida a tus dispositivos de almacenamiento de forma rápida y segura.

---

## ✨ Características Principales

* **🌑 Interfaz Premium**: Diseño oscuro elegante con efectos visuales dinámicos (Hover) y una experiencia de usuario fluida.
* **📊 Feedback en Tiempo Real**: Barra de progreso animada que indica el estado actual de la operación.
* **🔍 Detección Inteligente**: Sistema de triple motor (WMI, Storage y PhysicalDisk) para reconocer dispositivos incluso cuando Windows no muestra su capacidad.
* **🛡️ Modo Simulación**: Prueba todas las funciones sin riesgo de borrar datos reales.
* **💾 Sistemas de Archivos**:
    * **exFAT**: Recomendado para máxima compatibilidad y archivos grandes.
    * **FAT32**: Para dispositivos heredados.
    * **NTFS**: Para uso avanzado en Windows.

---

## 🚀 Instalación y Uso

### 🔧 Requisitos del Sistema
- Windows 10 o Windows 11.
- Privilegios de Administrador (necesarios para interactuar con `diskpart`).

### 🛠️ Cómo ejecutar el código
Si prefieres ejecutarlo desde la fuente:
1. Asegúrate de tener instalado Python 3.x.
2. Ejecuta el script directamente:
   ```bash
   python USBRecovery.py
