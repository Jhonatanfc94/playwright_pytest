# Archivo: poms/base_page.py
"""
Clase base abstracta para todos los Page Object Models.

Todos los POMs deben heredar de esta clase e implementar
`verify_page_loaded()` como mínimo.

Principio mindset_scalability.md: lógica común centralizada,
no duplicada en cada POM.
"""
from playwright.sync_api import Page


class BasePage:
    """Clase base para Page Object Models.

    Provee la interfaz común que todos los POMs deben implementar.
    Subclases deben sobreescribir `verify_page_loaded()` con
    la verificación específica de cada página.

    Args:
        page: Instancia de Playwright Page.
    """

    def __init__(self, page: Page):
        self.page = page

    def verify_page_loaded(self):
        """Verifica que la página cargó correctamente.

        Cada subclase DEBE implementar este método con validaciones
        específicas para su tipo de página:
        - HTML estándar: expect(page).to_have_url(...) + elemento visible
        - Flutter con semántica: wait_for_selector("flt-glass-pane")
        - Flutter sin semántica: wait_for_url + networkidle + screenshot

        Raises:
            NotImplementedError: Si la subclase no implementa este método.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} debe implementar verify_page_loaded()"
        )

    def take_screenshot(self, name: str = "screenshot") -> str:
        """Captura un screenshot de la página actual.

        Args:
            name: Nombre base del archivo (sin extensión).

        Returns:
            str: Ruta al archivo del screenshot.
        """
        path = f"artifacts/{name}.png"
        self.page.screenshot(path=path, full_page=True)
        return path
