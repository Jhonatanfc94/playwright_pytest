---
trigger: always_on
---

# Rules for Page Object Model (POM) with Playwright Sync

When editing or creating files in the `poms/` directory, you must strictly follow these conventions:

## 1. Fundamentos

1. Always use the Playwright synchronous API (`playwright.sync_api`).
2. The `__init__` constructor must receive and store the `Page` instance.
3. POMs can optionally inherit from `BasePage` (`poms/base_page.py`).
4. Assertions within the POM must use `expect` from `playwright.sync_api` or `assert`.

## 2. Selectores — Dependen del Tipo de App

### Apps HTML Estándar (GitHub, SPAs, etc.):
- Definir locators en `__init__` usando `get_by_role`, `get_by_text`, `locator`.
- Ver `poms/repository.py` como referencia.

### Flutter Web con semántica:
- Solo definir locators de `<input>` y `<flt-semantics>` con aria-label en `__init__`.
- **NO** definir locators de botones (no existen como HTML).

### Flutter Web SIN semántica (WASM/Skia):
- **NO** definir NINGÚN locator de texto o botones en `__init__` — no existen en el DOM.
- Solo definir locators de `<input>` (los únicos elementos HTML reales).
- Las interacciones DEBEN usar: coordenadas viewport (`page.mouse.click(x, y)`) o teclado (`Tab` + `Enter`).
- Las validaciones DEBEN basarse en: URL (`page.wait_for_url()`), network (`page.wait_for_load_state("networkidle")`), y screenshots.

## 3. 🚫 Regla Anti-Falsos Positivos (MÁXIMA PRIORIDAD)

**PROHIBIDO ABSOLUTAMENTE** envolver interacciones en `try/except` que silencien errores:

```python
# ❌ PROHIBIDO — Esto crea falsos positivos
def click_login(self):
    try:
        self.page.locator("text=Login").click()
    except Exception:
        pass  # El test "pasa" sin hacer nada
```

**OBLIGATORIO** — Usar `count()` para verificar antes de interactuar, con fallback documentado:

```python
# ✅ CORRECTO — Verificar antes, fallback sin silenciar
def click_login(self):
    semantic = self.page.locator("flt-semantics[aria-label*='Login']")
    if semantic.count() > 0:
        semantic.first.click(force=True)
    else:
        # Fallback: coordenadas del viewport (botón a 50% ancho, 55% alto)
        width = self.page.viewport_size["width"]
        height = self.page.viewport_size["height"]
        self.page.mouse.click(width * 0.5, height * 0.55)
    # VALIDAR que la acción tuvo efecto
    self.page.wait_for_url(re.compile(r".*emailOTP.*"), timeout=15000)
```

## 4. Cada Acción DEBE tener una Validación

Toda función del POM que realice una acción **DEBE** verificar que tuvo efecto:

| Acción | Validación Recomendada |
|---|---|
| Click en botón de navegación | `page.wait_for_url(patron)` |
| Submit de formulario | `page.wait_for_url(patron)` o verificar nuevo elemento |
| Fill de campo | Verificar valor con `input_value()` si es posible |
| Login exitoso | `page.wait_for_url(patron_dashboard)` + `page.wait_for_load_state("networkidle")` |

### Patrón de cascada con validación entre intentos

Cuando hay múltiples estrategias de interacción, validar después de cada una:

```python
def click_continue(self):
    otp_pattern = re.compile(r".*emailOTP.*", re.IGNORECASE)

    # Estrategia 1: semántica
    semantic = self.page.locator("flt-semantics[aria-label*='Continue']")
    if semantic.count() > 0:
        semantic.first.click(force=True)
        self.page.wait_for_timeout(3000)
        if not otp_pattern.match(self.page.url):
            return  # Funcionó

    # Estrategia 2: coordenadas
    width = self.page.viewport_size["width"]
    height = self.page.viewport_size["height"]
    self.page.mouse.click(width * 0.5, height * 0.65)
    self.page.wait_for_timeout(3000)
    if not otp_pattern.match(self.page.url):
        return  # Funcionó

    # Estrategia 3: teclado
    self.page.keyboard.press("Tab")
    self.page.keyboard.press("Enter")
    # Validación final obligatoria
    self.page.wait_for_url(re.compile(r".*dashBoard.*"), timeout=30000)
```

## 5. Waits — Usar Playwright, no time.sleep()

- **PROHIBIDO** `time.sleep()`. Usar `page.wait_for_timeout(ms)` si se necesita una espera fija.
- Preferir esperas inteligentes sobre esperas fijas:

| Prioridad | Método | Cuándo usar |
|---|---|---|
| 1️⃣ | `page.wait_for_url(patron)` | Después de navegación |
| 2️⃣ | `page.wait_for_load_state("networkidle")` | Después de carga de datos |
| 3️⃣ | `page.wait_for_selector(sel, state="attached")` | Esperar elemento específico |
| 4️⃣ | `page.wait_for_timeout(ms)` | Solo cuando Flutter necesita tiempo extra para renderizar |

- Si se usa `page.wait_for_timeout()`, documentar POR QUÉ es necesario.

## 6. Documentación de Locators No Obvios

Cuando un locator use coordenadas, keyboard shortcuts, o técnicas no estándar, **DEBE** documentar:
- POR QUÉ no se puede usar un selector semántico.
- CÓMO se calcularon las coordenadas (ej: "65% del viewport height").
- QUÉ tipo de aplicación es (Flutter WASM/Skia, CanvasKit, React, etc.).

## 7. Manejo de Listas y Paginación

Antes de asumir que un elemento no existe en una lista o grid, verifica el comportamiento de carga:

| Comportamiento | Estrategia |
|---|---|
| **Infinite Scroll** | Hacer scroll explícitamente (`page.evaluate("window.scrollTo(0, document.body.scrollHeight)")`) y esperar la red antes de asertar |
| **Paginación** | Interactuar con botones de paginación / "Load More" antes de buscar elementos |
| **Lazy Loading** | Usar `page.wait_for_load_state("networkidle")` después de scroll |

```python
# ✅ CORRECTO — Scroll + esperar antes de asertar
def get_all_items(self):
    """Hace scroll hasta cargar todos los items (Infinite Scroll)."""
    previous_count = 0
    while True:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_load_state("networkidle", timeout=10000)
        current_count = self.page.locator(".item-card").count()
        if current_count == previous_count:
            break
        previous_count = current_count
    return current_count
```
