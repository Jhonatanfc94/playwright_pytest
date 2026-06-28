# Plantilla POM — Apps Flutter Web

## Cuándo usar esta plantilla
- Cuando `flt-glass-pane` existe en el DOM.
- Diferenciar si tiene semántica (`flt-semantics` count > 0) o no.

---

## Plantilla Flutter CON Semántica

```python
import re
from playwright.sync_api import Page, expect
from poms.base_page import BasePage


class NewFlutterPage(BasePage):
    """POM para [nombre de página].

    App type: Flutter Web — accesibilidad habilitada.
    flt-semantics count > 0.
    Solo <input> y <flt-semantics> son elementos HTML reales.
    Botones NO existen como HTML — usar flt-semantics[aria-label] o coordenadas.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # Solo inputs y flt-semantics con aria-label
        self.email_input = self.page.locator("input").first
        self.login_button = self.page.locator(
            "flt-semantics[aria-label*='Login']"
        )

    def verify_page_loaded(self):
        expect(self.page).to_have_url(re.compile(r".*expected-pattern.*"))
        self.page.wait_for_selector(
            "flt-glass-pane", state="attached", timeout=15000
        )

    def click_login(self):
        """Click en botón de login usando semántica Flutter."""
        if self.login_button.count() > 0:
            self.login_button.first.click(force=True)
        else:
            # Fallback: coordenadas del viewport
            width = self.page.viewport_size["width"]
            height = self.page.viewport_size["height"]
            self.page.mouse.click(width * 0.5, height * 0.55)
        # Validación obligatoria
        self.page.wait_for_url(
            re.compile(r".*next-page.*"), timeout=15000
        )
```

---

## Plantilla Flutter SIN Semántica (WASM/Skia)

```python
import re
from playwright.sync_api import Page, expect


class NewFlutterNoSemPage:
    """POM para [nombre de página].

    App type: Flutter Web (WASM/Skia) — accesibilidad deshabilitada.
    0 nodos flt-semantics. Todo el texto visible son píxeles.
    Solo <input> son elementos HTML reales.
    Interacciones via: coordenadas viewport, teclado, URL.
    """

    def __init__(self, page: Page):
        self.page = page
        # Solo inputs son elementos reales
        # NO definir locators de texto ni botones — no existen

    def verify_page_loaded(self):
        self.page.wait_for_url(
            re.compile(r".*patron_url.*"), timeout=30000
        )
        self.page.wait_for_selector(
            "flt-glass-pane", state="attached", timeout=15000
        )
        self.page.wait_for_load_state("networkidle", timeout=30000)
        # Skia necesita tiempo extra para renderizar pixels
        self.page.wait_for_timeout(3000)

    def fill_email(self, email: str):
        """Fill email input — uno de los pocos HTML reales."""
        inputs = self.page.locator("input")
        inputs.first.fill(email)

    def click_submit(self):
        """Click en botón de submit via coordenadas del viewport.

        Coordenadas: botón ubicado a ~50% ancho, ~65% alto del viewport.
        Se usan coordenadas porque Flutter WASM/Skia no genera
        elementos HTML para botones.
        """
        width = self.page.viewport_size["width"]
        height = self.page.viewport_size["height"]
        self.page.mouse.click(width * 0.5, height * 0.65)
        # Validación obligatoria
        self.page.wait_for_url(
            re.compile(r".*next-page.*"), timeout=15000
        )

    def verify_content(self):
        """Validación basada en URL + screenshot (texto no existe en DOM)."""
        expect(self.page).to_have_url(re.compile(r".*patron.*"))
        self.page.screenshot(path="artifacts/page_verification.png")
```

---

## Notas
- Sustituir nombres de clases y patrones de URL por los reales.
- Documentar siempre cómo se calcularon las coordenadas de viewport.
- Para Flutter sin semántica: NO intentar buscar texto en el DOM, siempre fallará.
