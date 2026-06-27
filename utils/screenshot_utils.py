# Archivo: utils/screenshot_utils.py
"""
Utilidades centralizadas para capturas de pantalla.

Provee funciones de integración con pytest hooks y Allure
para captura automática en caso de fallo de tests.
(Principio mindset_scalability.md: solución global, no parches locales)
"""
import os
from datetime import datetime
from playwright.sync_api import Page

try:
    import allure
    HAS_ALLURE = True
except ImportError:
    HAS_ALLURE = False


SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")


def ensure_screenshots_dir():
    """Crea el directorio de screenshots si no existe."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def capture_screenshot_on_failure(page: Page, test_name: str) -> str:
    """Captura un screenshot y lo adjunta a Allure si está disponible.

    Diseñado para ser llamado desde el hook `pytest_runtest_makereport`
    en conftest.py cuando un test falla.

    Args:
        page: Instancia de Playwright Page.
        test_name: Nombre del test que falló.

    Returns:
        str: Ruta al archivo del screenshot.
    """
    ensure_screenshots_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Limpiar nombre de test para usarlo como filename
    safe_name = test_name.replace("/", "_").replace("::", "_").replace(" ", "_")
    filename = f"FAIL_{safe_name}_{timestamp}.png"
    filepath = os.path.join(SCREENSHOTS_DIR, filename)

    try:
        page.screenshot(path=filepath, full_page=True)

        if HAS_ALLURE:
            with open(filepath, "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"Screenshot: {test_name}",
                    attachment_type=allure.attachment_type.PNG
                )

        return filepath
    except Exception as e:
        print(f"⚠ No se pudo capturar screenshot: {e}")
        return ""
