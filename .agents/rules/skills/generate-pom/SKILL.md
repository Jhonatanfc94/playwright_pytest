---
name: generate-pom
description: Generates a new Page Object Model (POM) class for UI automation with Playwright and Pytest. Use this when you need to map a new screen.
---

# Page Object Generator

## When to use this skill
Use this when the user requests to create a new POM for a specific web page.

## Cómo usarla

### Paso 1: Identificar el tipo de app
Antes de escribir código, determinar el tipo de aplicación:

| Tipo | Cómo detectar | Estrategia |
|---|---|---|
| HTML Estándar | `<button>`, `<div>` normales | Selectores semánticos (`get_by_role`, etc.) |
| SPA (React/Vue/Angular) | Atributos `data-*`, `class` dinámicas | `get_by_test_id`, `get_by_role` |
| Flutter con semántica | `flt-semantics` count > 0 | Mezcla de `<input>` + `flt-semantics` |
| Flutter sin semántica | `flt-semantics` count = 0, `flt-semantics-placeholder` presente | Solo `<input>`, coordenadas, teclado, URL |

### Paso 2: Inspeccionar el DOM

**Página pública:**
- Usar `browser_subagent` para navegar e inspeccionar.

**Página protegida (requiere login):**
- Crear un script de Playwright que ejecute el login completo (con OTP si aplica) y use `page.evaluate()` para volcar el DOM.
- **NO usar `browser_subagent`** — no puede hacer login con OTP.

### Paso 3: Crear el POM

1. Crear el archivo en `poms/` heredando de `BasePage` (`poms/base_page.py`).
2. Definir `__init__` con `super().__init__(page)` y los locators apropiados para el tipo de app.
3. Implementar `verify_page_loaded()` según el tipo de app.
4. Añadir métodos que representen acciones de usuario (ej: `login_user()`, no `click_button_and_fill_text()`).
5. **Cada acción DEBE tener una validación** (URL change, element present, etc.).
6. **Manejo de Listas**: Si la página usa Infinite Scroll, hacer scroll + esperar red antes de asertar. Si usa paginación, interactuar con botones primero.

### Paso 4: Documentar

- Documentar el tipo de app en el docstring de la clase.
- Si se usan coordenadas de viewport, documentar cómo se calcularon.
- Guardar un screenshot de referencia en `artifacts/`.

## Archivos de referencia

| Tipo de app | Ejemplo de referencia |
|---|---|
| HTML Estándar | `poms/repository.py` (ejemplo incluido) |
| Clase base | `poms/base_page.py` (interfaz abstracta) |

## Plantilla para HTML Estándar (SPAs, sitios web normales)

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

## Plantilla para Flutter sin semántica (WASM/Skia)

```python
from playwright.sync_api import Page, expect
import re


class NewPage:
    """POM para [nombre de página].

    App type: Flutter Web (WASM/Skia) — accesibilidad deshabilitada.
    0 nodos flt-semantics. Todo el texto visible son píxeles.
    Solo <input> son elementos HTML reales.
    """

    def __init__(self, page: Page):
        self.page = page

    def verify_page_loaded(self):
        self.page.wait_for_url(
            re.compile(r".*patron_url.*"), timeout=30000
        )
        self.page.wait_for_selector(
            "flt-glass-pane", state="attached", timeout=15000
        )
        self.page.wait_for_load_state("networkidle", timeout=30000)
        self.page.wait_for_timeout(3000)

    def verify_content(self):
        """Validación basada en URL + screenshot (texto no existe en DOM)."""
        expect(self.page).to_have_url(re.compile(r".*patron.*"))
        self.page.screenshot(path="artifacts/page_verification.png")
```
