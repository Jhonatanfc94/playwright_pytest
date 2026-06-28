# Detección de Tipo de Aplicación Web (Flutter)

Este archivo de referencia contiene las tablas y estrategias para detectar e interactuar con aplicaciones Flutter Web. Consultarlo cuando se detecte `flt-glass-pane` en el DOM.

## Tabla de Detección

| Tipo de App | Señales en el DOM | Estrategia de Interacción |
|---|---|---|
| **HTML Estándar** | `<button>`, `<input>`, `<div>` normales | `get_by_role()`, `get_by_text()`, `get_by_placeholder()` |
| **SPA (React/Vue/Angular)** | Elementos HTML con atributos `data-*`, `class` dinámicas | `get_by_role()`, `get_by_test_id()`, `locator("[data-*]")` |
| **Flutter Web (con semántica)** | `<flt-glass-pane>`, `<flt-semantics>`, `<canvas>` | Ver sección "Flutter CON Semántica" |
| **Flutter Web (sin semántica)** | `<flt-glass-pane>`, `<flt-semantics-placeholder>` con `aria-label='Enable accessibility'`, **0 nodos `<flt-semantics>`** | Ver sección "Flutter SIN Semántica" |

> **⚠️ CRÍTICO:** Flutter WASM/Skia con accesibilidad deshabilitada NO genera `<flt-semantics>` ni `<canvas>`. El único elemento semántico es `<flt-semantics-placeholder role='button' aria-label='Enable accessibility'>`. Todo el texto visible son píxeles renderizados por Skia — **no se puede queryar ningún texto del DOM**.

---

## Flutter Web CON Semántica Habilitada

Cuando `document.querySelectorAll('flt-semantics').length > 0`:

### Lo que SÍ funciona:
- `page.locator("input")` — Los campos de texto SÍ generan `<input>` reales.
- `page.locator("flt-semantics[aria-label*='texto']")` — Nodos de semántica con aria-label.
- `page.keyboard.press("Tab")` + `page.keyboard.press("Enter")` — Navegación por teclado.
- `page.mouse.click(x, y)` con coordenadas relativas al viewport.

### Lo que NO funciona:
- `get_by_role("button", name="Login")` — Los botones NO tienen roles HTML estándar.
- `get_by_text("Login with Email")` — El texto está pintado como píxeles.
- `expect(element).to_be_visible()` — Snackbars/toasts no son elementos DOM.

### Estrategia de Interacción (Prioridad):

| Prioridad | Método | Uso |
|---|---|---|
| 1️⃣ | `page.locator("input").fill(valor)` | Campos de texto (únicos HTML reales) |
| 2️⃣ | `page.locator("flt-semantics[aria-label*='X']").click()` | Widgets con semántica |
| 3️⃣ | `page.mouse.click(width * %, height * %)` | Coordenadas relativas al viewport |
| 4️⃣ | `page.keyboard.press("Tab")` + `page.keyboard.press("Enter")` | Navegación por teclado |
| 5️⃣ | `page.wait_for_url(re.compile(r"patron"))` | Validar navegación exitosa |

### Selectores en `__init__` del POM:
- Solo definir locators de `<input>` y `<flt-semantics>` con aria-label.
- **NO** definir locators de botones (no existen como HTML).

---

## Flutter Web SIN Semántica (WASM/Skia) — CRÍTICO

Cuando `document.querySelectorAll('flt-semantics').length == 0` y existe `<flt-semantics-placeholder aria-label='Enable accessibility'>`:

### Realidad del DOM:
- **0 nodos `flt-semantics`** — la accesibilidad está deshabilitada.
- **0 elementos `canvas`** — Flutter WASM/Skia no usa `<canvas>` HTML.
- **Solo `<input>` son reales** — los campos de texto sí generan HTML.
- **Todo el texto visible son píxeles** — NO existe en el DOM.

### Lo que SÍ funciona:
- `page.locator("input")` — Campos de texto.
- `page.mouse.click(width * %, height * %)` — Coordenadas relativas.
- `page.keyboard.press("Tab")` / `page.keyboard.press("Enter")` — Teclado.
- `page.wait_for_url(patron)` — Validar navegación.
- `page.wait_for_load_state("networkidle")` — Esperar carga de datos.

### Lo que NO funciona (NADA de selectores semánticos):
- `flt-semantics[aria-label*='...']` — No existen.
- `get_by_role()`, `get_by_text()`, `locator("text=...")` — No existen.
- `expect(element).to_be_visible()` para textos — Son píxeles.

### Validaciones confiables:

| Validación | Método | Ejemplo |
|---|---|---|
| Navegación exitosa | `page.wait_for_url(patron)` | `page.wait_for_url(re.compile(r".*dashBoard.*"))` |
| Página cargó | `page.wait_for_load_state("networkidle")` | Confirma que los datos API se cargaron |
| Evidencia visual | `page.screenshot(path="artifacts/...")` | Guardar screenshot como prueba |
| Presencia de inputs | `page.locator("input").count()` | Detectar cambio de pantalla |
| Flutter engine listo | `page.wait_for_selector("flt-glass-pane")` | Confirma que el engine cargó |

### Selectores en `__init__` del POM:
- **NO** definir NINGÚN locator de texto o botones — no existen en el DOM.
- Solo definir locators de `<input>` (los únicos elementos HTML reales).
- Las interacciones DEBEN usar: coordenadas viewport (`page.mouse.click(x, y)`) o teclado (`Tab` + `Enter`).
- Las validaciones DEBEN basarse en: URL (`page.wait_for_url()`), network (`page.wait_for_load_state("networkidle")`), y screenshots.

---

## Inspección de Páginas Protegidas (Login Requerido)

Para inspeccionar el DOM de páginas que requieren autenticación, **NO usar `browser_subagent`** (no puede hacer login con OTP). En su lugar, crear un **script de Playwright** que:

1. Ejecute el flujo completo de login (email → OTP → verificación).
2. Navegue a la página objetivo.
3. Use `page.evaluate()` para volcar el DOM completo.
4. Guarde los resultados en `artifacts/`.

```python
# Ejemplo: inspect_dashboard_dom.py
result = page.evaluate("""() => {
    return {
        semantics: document.querySelectorAll('flt-semantics').length,
        inputs: document.querySelectorAll('input').length,
        totalElements: document.querySelectorAll('*').length,
        kamFound: Array.from(document.querySelectorAll('*'))
            .filter(el => (el.textContent || '').includes('KAM'))
            .map(el => ({ tag: el.tagName, text: el.textContent }))
    };
}""")
```
