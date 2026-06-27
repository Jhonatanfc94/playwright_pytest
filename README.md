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
   python -m venv venv
   ```
3. **Activa el entorno virtual:**
   * **En Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate
     ```
     *(Si te da un error rojo de permisos en Windows, ejecuta `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` y vuelve a intentarlo).*
   * **En Mac/Linux:**
     ```bash
     source venv/bin/activate
     ```

## 📦 3. Instalación de Dependencias

Con el entorno activado `(venv)`, vamos a instalar las librerías de Python y los navegadores.

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
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   irm get.scoop.sh | iex
   scoop install allure
   ```
2. **Instala Lighthouse (Para medir rendimiento web):**
   ```bash
   npm install lighthouse
   ```

---

## 🚀 5. ¡A Correr las Pruebas!

> [!NOTE]
> Gracias a nuestro archivo `pytest.ini`, las pruebas funcionales están configuradas para ejecutarse con **Chrome**, generar reportes de **Allure**, y guardar **trazas en caso de fallo** automáticamente con un simple `pytest`.

Aquí tienes tu "hoja de trucos" con el flujo completo paso a paso (Funcional + Lighthouse + Locust + Reporte):

### Ejecución de pruebas
```bash
# 1. Pruebas Funcionales (E2E UI y API en Pytest)
python -m pytest tests/e2e/test_repositories.py -n 0

# 2. Pruebas de Lighthouse (Rendimiento Web)
python -m pytest tests/performance/test_lighthouse.py --only-lighthouse

# 3. Pruebas de Locust (Pruebas de Carga API)
python -m locust -f tests/performance/locustfile.py --headless --users 10 --spawn-rate 2 --host https://example.com --html reporte-locust.html

# 4. Generar y abrir el reporte consolidado de Allure (UI + Lighthouse)
allure generate ./allure-results -o ./allure-report --clean
allure open ./allure-report
```

**⚙️ Ejecución General (CI/CD y Local)**
* Correr todas las pruebas con la configuración óptima:
  ```bash
  pytest
  ```
  *(Nota: Si en Windows recibes el error "An Application Control policy has blocked this file", usa `python -m pytest` en lugar de `pytest` en todos los comandos).*
* Correr en paralelo con N workers (requiere `pytest-xdist`):
  ```bash
  pytest -n 2
  ```
* Ignorar el paralelismo (ejecución secuencial clásica):
  ```bash
  pytest -n 0
  ```

**🖥️ Pruebas Funcionales Específicas**
* Correr un archivo específico:
  ```bash
  pytest .\tests\e2e\test_repositories.py
  ```
* Simular un dispositivo móvil:
  ```bash
  pytest --browser_name device
  ```

**🐛 Depuración (Debugging)**
* Ver la ejecución en el navegador en tiempo real (Headed):
  ```bash
  pytest --headed -n 0
  ```
* Ver la ejecución MUY lenta para entender qué está fallando (1 segundo por acción):
  ```bash
  pytest --headed --slowmo 1000 -n 0
  ```
* Abrir el inspector/consola de Playwright (Trace Viewer en vivo) antes de que termine el test:
  Añade `page.pause()` en tu código Python, o si usas breakpoints interactivos:
  `breakpoint()`

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
* **Con Locust (Local):** (Pruebas de carga sencillas en tu propia máquina exportando a CSV y HTML):
  ```bash
  locust -f tests/performance/locustfile.py --headless --host https://your-site.com --html reporte-locust.html
  ```
* **Con Locust (CI/CD o Avanzado):** (Ejecución paralela Master/Worker usando Docker Compose):
  ```bash
  export UID_GID=$(id -u):$(id -g)
  docker compose up --build --scale worker=3
  ```
* **Con Lighthouse** (Auditoría de rendimiento web):
  ```bash
  pytest --only-lighthouse -s
  ```

---

## 📁 Estructura del Proyecto

```
├── .agents/rules/          # Reglas y skills para AI assistants
├── .github/workflows/      # CI/CD con GitHub Actions
├── data/                   # Datos de prueba (credentials.json)
├── features/               # Archivos .feature (Gherkin/BDD)
├── poms/                   # Page Object Models
│   ├── base_page.py        # Clase base abstracta
│   └── repository.py       # POM de ejemplo (GitHub)
├── tests/
│   ├── e2e/                # Tests funcionales E2E
│   └── performance/        # Locust + Lighthouse
├── utils/                  # Utilidades compartidas
│   ├── api_testing.py      # Cliente API genérico
│   ├── email_reader.py     # Lector de OTP via IMAP
│   ├── lighthouse_utils.py # Runner de Lighthouse
│   └── screenshot_utils.py # Capturas automáticas en fallo
├── conftest.py             # Fixtures y hooks globales
├── pytest.ini              # Configuración centralizada de pytest
├── packages.txt            # Dependencias Python
└── docker-compose.yml      # Locust distribuido
```

---

## 👤 Autor
* **Jhonatan Flores** - [@jhonatan](https://github.com/Jhonatanfc94)