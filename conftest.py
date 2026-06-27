import os
import json
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, Playwright, expect
from utils.screenshot_utils import capture_screenshot_on_failure

# ==========================================
# 📦 CARGAR VARIABLES DE ENTORNO
# ==========================================
load_dotenv()

# ==========================================
# 📦 CARGAR CREDENCIALES DESDE JSON
# ==========================================
_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "data", "credentials.json")


def _load_credentials() -> dict:
    """Carga credenciales desde data/credentials.json.

    Returns:
        dict: Contenido del archivo de credenciales.

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    with open(_CREDENTIALS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ==========================================
# 🚀 HOOKS GLOBALES
# ==========================================

def pytest_sessionstart(session):
    """
    Hook global que se ejecuta 1 sola vez antes de que inicie cualquier prueba.
    Verifica que las variables de entorno críticas estén configuradas.

    Si se corre en paralelo con pytest-xdist, esto solo lo ejecuta el proceso maestro.
    """
    # Guard para pytest-xdist: solo ejecutar en el proceso maestro
    if hasattr(session.config, "workerinput"):
        return

    base_url = os.getenv("BASE_URL")
    if not base_url:
        print("\n[INIT] BASE_URL no está configurada en .env — algunos tests podrían fallar.")
    else:
        print(f"\n[INIT] BASE_URL configurada: {base_url}")


def pytest_addoption(parser):
    parser.addoption(
        "--browser_name", action="store", default="chrome", help="browser selection: chrome, firefox, or device"
    )
    parser.addoption(
        "--only-lighthouse",
        action="store_true",
        default=False,
        help="Run only lighthouse performance tests"
    )

# ==========================================
# 🌐 FIXTURE: BROWSER INSTANCE
# ==========================================

@pytest.fixture()
def browser_instance(playwright, request):
    """Fixture principal que provee una instancia de página del navegador.

    Soporta Chrome, Firefox y emulación de dispositivo móvil.
    La opción headless se controla con la variable de entorno HEADLESS.
    """
    browser_name = request.config.getoption("browser_name")
    headless = os.getenv("HEADLESS", "false").lower() == "true"

    browser = None
    context = None

    if browser_name == "lighthouse":
        yield None
        return

    if browser_name == "chrome":
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={'width': 1366, 'height': 768}
        )
    elif browser_name == "firefox":
        browser = playwright.firefox.launch(headless=headless)
        context = browser.new_context(
            viewport={'width': 1366, 'height': 768}
        )
    elif browser_name == "device":
        # Simulate a mobile device
        device = playwright.devices['iPhone 13']
        browser = playwright.webkit.launch(headless=headless)
        context = browser.new_context(
            **device,
        )
    else:
        raise ValueError(f"Unsupported browser_name: {browser_name}")

    page = context.new_page()
    yield page

    context.close()
    browser.close()

# ==========================================
# 🔐 FIXTURE: LOGGED-IN SESSION
# ==========================================

@pytest.fixture(scope="function")
def logged_in_page(browser_instance: Page, playwright: Playwright) -> Page:
    """Fixture que provee una página con sesión activa via localStorage.

    Obtiene un token de autenticación vía API y lo inyecta en localStorage
    antes de navegar a la URL base. Útil para tests que requieren usuario
    autenticado sin pasar por el flujo de login en UI.

    Las credenciales se obtienen de variables de entorno (regla pytest-bdd.md #4).

    Requires:
        - API_BASE_URL configurado en .env
        - TEST_USER_EMAIL y TEST_USER_PASSWORD configurados en .env
    """
    from utils.api_testing import APIUtils

    api_utils = APIUtils()
    token = api_utils.getToken(playwright)

    session_data = {
        'token': token
    }

    script = f"""
        const sessionData = {json.dumps(session_data)};
        Object.keys(sessionData).forEach(key => {{
            localStorage.setItem(key, sessionData[key]);
        }});
    """
    browser_instance.add_init_script(script)

    base_url = os.getenv("BASE_URL")
    assert base_url, "BASE_URL no está configurada en .env — no se puede navegar."
    browser_instance.goto(base_url)

    yield browser_instance

# ==========================================
# 📸 HOOK: SCREENSHOT ON FAILURE
# ==========================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Captura un screenshot automáticamente cuando un test falla.

    Principio mindset_scalability.md: solución global en conftest,
    no parches locales en cada test.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Intentar obtener la instancia de page del test
        page = item.funcargs.get("browser_instance")
        if page and hasattr(page, "screenshot"):
            capture_screenshot_on_failure(page, item.nodeid)

# ==========================================
# 📋 FIXTURE: SHARED DATA (patrón pytest-bdd)
# ==========================================

@pytest.fixture(scope="function")
def shared_data():
    """Diccionario para compartir datos entre los pasos BDD.

    Regla pytest-bdd.md #2: Usar shared_data para pasar estado
    y datos dinámicos entre diferentes steps.
    """
    return {}

# ==========================================
# ⚙️ CONFIGURACIÓN DE PYTEST & METADATA
# ==========================================

def pytest_configure(config):
    config._metadata = {
        "Project": "Automation Framework Base",
        "Tester": "AI Assistant / QA Team",
        "Browser": config.getoption("--browser_name")
    }
    config.addinivalue_line("markers", "lighthouse: marks tests as lighthouse-related for performance auditing")

def pytest_collection_modifyitems(config, items):
    """Filters tests based on command line options."""
    browser_name = config.getoption("--browser_name")
    only_lighthouse = config.getoption("--only-lighthouse")

    if only_lighthouse:
        selected = [item for item in items if item.get_closest_marker("lighthouse")]
        items[:] = selected
        return

    if not only_lighthouse and browser_name != "lighthouse":
        remaining = [item for item in items if not item.get_closest_marker("lighthouse")]
        items[:] = remaining