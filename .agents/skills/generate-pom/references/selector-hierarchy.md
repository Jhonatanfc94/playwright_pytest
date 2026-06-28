# Jerarquía de Selectores por Tipo de Aplicación

## Apps HTML Estándar (GitHub, SPAs, sitios web normales)

| Prioridad | Método | Ejemplo | Resiliencia |
|---|---|---|---|
| 1️⃣ | `get_by_role()` | `page.get_by_role("button", name="Sign in")` | ⭐⭐⭐⭐⭐ |
| 2️⃣ | `get_by_text()` / `get_by_label()` | `page.get_by_text("Repositories")` | ⭐⭐⭐⭐ |
| 3️⃣ | `get_by_placeholder()` | `page.get_by_placeholder("Search...")` | ⭐⭐⭐⭐ |
| 4️⃣ | `get_by_test_id()` | `page.get_by_test_id("repo-list")` | ⭐⭐⭐ |
| 5️⃣ | `locator("[data-*]")` | `page.locator("[data-tab-item='repos']")` | ⭐⭐⭐ |
| 6️⃣ | CSS selector | `page.locator("nav .search-input")` | ⭐⭐ |

**PROHIBIDO** usar XPath como primera opción.

## Apps SPA con Testing Interno (acceso al código)

Cuando se tiene acceso al código fuente, la prioridad cambia porque se pueden **inyectar** atributos:

| Prioridad | Método | Cuándo |
|---|---|---|
| 1️⃣ | `get_by_test_id()` | Si el equipo inyecta `data-testid` en componentes |
| 2️⃣ | `get_by_role()` | Siempre disponible si hay HTML semántico |
| 3️⃣ | `get_by_label()` | Para formularios con `<label>` |
| 4️⃣ | `locator("[data-*]")` | Atributos custom del framework |

## Regla Anti-Falsos Positivos (aplica a TODOS los tipos)

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

## Patrón de Cascada con Validación

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

## Waits — Prioridad

| Prioridad | Método | Cuándo usar |
|---|---|---|
| 1️⃣ | `page.wait_for_url(patron)` | Después de navegación |
| 2️⃣ | `page.wait_for_load_state("networkidle")` | Después de carga de datos |
| 3️⃣ | `page.wait_for_selector(sel, state="attached")` | Esperar elemento específico |
| 4️⃣ | `page.wait_for_timeout(ms)` | Solo cuando Flutter necesita tiempo extra para renderizar |

## Manejo de Listas y Paginación

| Comportamiento | Estrategia |
|---|---|
| **Infinite Scroll** | Hacer scroll explícitamente y esperar la red antes de asertar |
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

## Documentación de Locators No Obvios

Cuando un locator use coordenadas, keyboard shortcuts, o técnicas no estándar, **DEBE** documentar:
- POR QUÉ no se puede usar un selector semántico.
- CÓMO se calcularon las coordenadas (ej: "65% del viewport height").
- QUÉ tipo de aplicación es (Flutter WASM/Skia, CanvasKit, React, etc.).
