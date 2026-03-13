# 🎭 Playwright + Pytest - Template de Automatización

¡Bienvenido al entorno de pruebas automatizadas! Este proyecto es una plantilla concisa para realizar pruebas de navegador utilizando **Playwright** y **Pytest**, con reportes visuales increíbles gracias a **Allure**.

Además, incluye herramientas para medir el rendimiento como **Locust** y **Lighthouse**. ¡Vamos a configurarlo paso a paso!

## 🛑 1. Requisitos Previos
Asegúrate de tener instaladas estas herramientas base en tu sistema:
* **Python** (Para correr Playwright y Pytest).
* **Node.js** (Necesario para instalar Lighthouse).
* **Scoop** (Solo en Windows, es un instalador que usaremos para descargar Allure. [Instrucciones de Scoop aquí](https://scoop.sh/)).

## 💻 2. Preparando el Entorno de Python

Primero, vamos a crear nuestro entorno virtual (nuestra "burbuja" de trabajo) para no mezclar las dependencias con otros proyectos.

1. **Abre tu terminal** en la carpeta de este proyecto.
2. **Crea el entorno virtual:**
   ```bash
   python -m venv .venv
   ```
3. **Activa el entorno virtual:**
   * **En Windows (PowerShell):**
     ```powershell
     .venv\Scripts\activate
     ```
     *(Si te da un error rojo de permisos en Windows, ejecuta `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` y vuelve a intentarlo).*
   * **En Mac/Linux:**
     ```bash
     source .venv/bin/activate
     ```

## 📦 3. Instalación de Dependencias

Con el entorno activado `(.venv)`, vamos a instalar las librerías de Python y los navegadores.

1. **Instala los paquetes de Python:**
   *(Asegúrate de tener el archivo `packages.txt` en tu carpeta)*
   ```bash
   pip install -r packages.txt
   ```
2. **Instala los navegadores de Playwright:**
   Playwright necesita descargar sus propios navegadores (Chromium, Firefox, WebKit) para poder hacer las pruebas.
   ```bash
   python -m playwright install
   ```

## 🛠️ 4. Instalación de Herramientas Externas (Reportes y Rendimiento)

Ahora vamos a instalar las herramientas que viven fuera de Python:

1. **Instala Allure (Para generar reportes visuales):**
   *(En Windows usando Scoop)*
   ```bash
   scoop install allure
   ```
2. **Instala Lighthouse globalmente (Para medir rendimiento web):**
   ```bash
   npm install -g lighthouse
   ```

---

## 🚀 5. ¡A Correr las Pruebas!

Aquí tienes tu "hoja de trucos" con los comandos principales para ejecutar tus tests. Puedes copiarlos y pegarlos en tu terminal:

**🖥️ Pruebas Funcionales (UI)**
* Correr todas las pruebas en Google Chrome (modo sin interfaz/oculto):
  ```bash
  pytest --alluredir=./allure-results --browser_name chrome
  ```
* Correr pruebas simulando un dispositivo móvil:
  ```bash
  pytest --alluredir=./allure-results --browser_name device
  ```
* Correr un archivo de prueba específico **viendo el navegador** (`--headed`):
  ```bash
  pytest .\tests\name_test.py --browser_name chrome --headed
  ```

**📊 Generar y Ver Reportes (Allure)**
* Generar el reporte en HTML (limpiando resultados anteriores):
  ```bash
  allure generate ./allure-results -o ./allure-report --clean
  ```
* Abrir el reporte en tu navegador web:
  ```bash
  allure open ./allure-report
  ```

**⚡ Pruebas de Rendimiento**
* **Con Locust** (Pruebas de carga durante 3 minutos, exportando a CSV y HTML):
  ```bash
  locust -f .\tests\performance\locustfile.py --headless --run-time 3m --csv=resultados --html reporte-locust.html
  ```
* **Con Lighthouse** (Auditoría de rendimiento web):
  ```bash
  pytest --alluredir=./allure-results --only-lighthouse -s
  ```

---

## 👤 Autor
* **Jhonatan Flores** - [@jhonatan](https://github.com/Jhonatanfc94)