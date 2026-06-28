# Plantilla POM — Apps HTML Estándar / SPA (React, Vue, Angular)

## Cuándo usar esta plantilla
- Cuando la app es HTML estándar con `<button>`, `<input>`, `<div>` normales.
- Cuando es una SPA (React/Vue/Angular) con atributos `data-*`.
- Cuando `flt-glass-pane` NO existe en el DOM.

## Plantilla Base

```python
import re
from playwright.sync_api import Page, expect
from poms.base_page import BasePage


class NewPage(BasePage):
    """POM para [nombre de página].

    App type: HTML Estándar / SPA (React/Vue/Angular).
    Selectores basados en roles semánticos y data-testid.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self._setup_locators()

    def _setup_locators(self):
        # Prioridad: data-testid > get_by_role > get_by_text
        self.main_heading = self.page.get_by_role("heading", name="...")
        self.submit_button = self.page.get_by_role("button", name="Submit")

    def verify_page_loaded(self):
        expect(self.page).to_have_url(re.compile(r".*expected-pattern.*"))
        expect(self.main_heading).to_be_visible(timeout=10000)
```

## Notas
- Sustituir `NewPage` por el nombre real de la clase.
- Sustituir `"..."` por los textos reales obtenidos de la inspección del DOM.
- Añadir métodos que representen acciones de usuario (ej: `login_user()`, `search_item(query)`).
- Cada método de acción DEBE incluir una validación (assert, wait_for_url, etc.).
