---
description: Reglas para testing de sitios web externos sin acceso al código fuente
trigger: always_on
---

# Testing de Sitios Web Externos (Sin Acceso a Código Fuente)

Este repositorio testea **páginas web externas** — sitios que no controlamos y cuyo código fuente no tenemos. La "fuente de verdad" para selectores y estructura es el **DOM vivo** del sitio, no un repositorio local.

## 1. Fuente de Verdad = DOM Vivo (OBLIGATORIO)

**RESTRICCIÓN CRÍTICA:**
- No hay repositorio frontend ni backend para consultar.
- Antes de crear o modificar un POM, el agente **DEBE** inspeccionar el DOM actual del sitio.
- Los selectores del POM deben reflejar el estado **actual** del sitio, no suposiciones.
- **NUNCA adivinar selectores basándose en nombres de botones visibles en screenshots.** Lo que se ve en pantalla NO siempre existe en el DOM.

### Cómo inspeccionar el DOM

- **Páginas públicas**: usar `browser_subagent` para navegar e inspeccionar.
- **Páginas protegidas (detrás de login)**: crear un **script de Playwright** que ejecute el flujo completo de autenticación y luego haga `page.evaluate()` para volcar el DOM. Ver sección 8.

## 2. Detección de Tipo de Aplicación Web

**ANTES** de escribir selectores, el agente DEBE identificar qué tipo de aplicación web se está testeando:

| Tipo de App | Señales en el DOM | Estrategia de Interacción |
|---|---|---|
| **HTML Estándar** | `<button>`, `<input>`, `<div>` normales | `get_by_role()`, `get_by_text()`, `get_by_placeholder()` |
| **SPA (React/Vue/Angular)** | Elementos HTML con atributos `data-*`, `class` dinámicas | `get_by_role()`, `get_by_test_id()`, `locator("[data-*]")` |
| **Flutter Web (con semántica)** | `<flt-glass-pane>`, `<flt-semantics>`, `<canvas>` | Ver sección 3 |
| **Flutter Web (sin semántica)** | `<flt-glass-pane>`, `<flt-semantics-placeholder>` con `aria-label='Enable accessibility'`, **0 nodos `<flt-semantics>`** | Ver sección 4 |

> **⚠️ CRÍTICO:** Flutter WASM/Skia con accesibilidad deshabilitada NO genera `<flt-semantics>` ni `<canvas>`. El único elemento semántico es `<flt-semantics-placeholder role='button' aria-label='Enable accessibility'>`. Todo el texto visible son píxeles renderizados por Skia — **no se puede queryar ningún texto del DOM**.

## 3. Flutter Web CON Semántica Habilitada

Cuando `document.querySelectorAll('flt-semantics').length > 0`:

### 3.1 Lo que SÍ funciona:
- `page.locator("input")` — Los campos de texto SÍ generan `<input>` reales.
- `page.locator("flt-semantics[aria-label*='texto']")` — Nodos de semántica con aria-label.
- `page.keyboard.press("Tab")` + `page.keyboard.press("Enter")` — Navegación por teclado.
- `page.mouse.click(x, y)` con coordenadas relativas al viewport.

### 3.2 Lo que NO funciona:
- `get_by_role("button", name="Login")` — Los botones NO tienen roles HTML estándar.
- `get_by_text("Login with Email")` — El texto está pintado como píxeles.
- `expect(element).to_be_visible()` — Snackbars/toasts no son elementos DOM.

### 3.3 Estrategia de Interacción (Prioridad):

| Prioridad | Método | Uso |
|---|---|---|
| 1️⃣ | `page.locator("input").fill(valor)` | Campos de texto (únicos HTML reales) |
| 2️⃣ | `page.locator("flt-semantics[aria-label*='X']").click()` | Widgets con semántica |
| 3️⃣ | `page.mouse.click(width * %, height * %)` | Coordenadas relativas al viewport |
| 4️⃣ | `page.keyboard.press("Tab")` + `page.keyboard.press("Enter")` | Navegación por teclado |
| 5️⃣ | `page.wait_for_url(re.compile(r"patron"))` | Validar navegación exitosa |

## 4. 🎯 Flutter Web SIN Semántica (WASM/Skia) — CRÍTICO

Cuando `document.querySelectorAll('flt-semantics').length == 0` y existe `<flt-semantics-placeholder aria-label='Enable accessibility'>`:

### 4.1 Realidad del DOM:
- **0 nodos `flt-semantics`** — la accesibilidad está deshabilitada.
- **0 elementos `canvas`** — Flutter WASM/Skia no usa `<canvas>` HTML.
- **Solo `<input>` son reales** — los campos de texto sí generan HTML.
- **Todo el texto visible son píxeles** — NO existe en el DOM.

### 4.2 Lo que SÍ funciona:
- `page.locator("input")` — Campos de texto.
- `page.mouse.click(width * %, height * %)` — Coordenadas relativas.
- `page.keyboard.press("Tab")` / `page.keyboard.press("Enter")` — Teclado.
- `page.wait_for_url(patron)` — Validar navegación.
- `page.wait_for_load_state("networkidle")` — Esperar carga de datos.

### 4.3 Lo que NO funciona (NADA de selectores semánticos):
- `flt-semantics[aria-label*='...']` — No existen.
- `get_by_role()`, `get_by_text()`, `locator("text=...")` — No existen.
- `expect(element).to_be_visible()` para textos — Son píxeles.

### 4.4 Validaciones confiables:

| Validación | Método | Ejemplo |
|---|---|---|
| Navegación exitosa | `page.wait_for_url(patron)` | `page.wait_for_url(re.compile(r".*dashBoard.*"))` |
| Página cargó | `page.wait_for_load_state("networkidle")` | Confirma que los datos API se cargaron |
| Evidencia visual | `page.screenshot(path="artifacts/...")` | Guardar screenshot como prueba |
| Presencia de inputs | `page.locator("input").count()` | Detectar cambio de pantalla |
| Flutter engine listo | `page.wait_for_selector("flt-glass-pane")` | Confirma que el engine cargó |

## 5. Jerarquía de Selectores para Apps HTML Estándar

Cuando la aplicación SÍ usa HTML estándar, prioriza:

| Prioridad | Método | Ejemplo | Resiliencia |
|---|---|---|---|
| 1️⃣ | `get_by_role()` | `page.get_by_role("button", name="Sign in")` | ⭐⭐⭐⭐⭐ |
| 2️⃣ | `get_by_text()` / `get_by_label()` | `page.get_by_text("Repositories")` | ⭐⭐⭐⭐ |
| 3️⃣ | `get_by_placeholder()` | `page.get_by_placeholder("Search...")` | ⭐⭐⭐⭐ |
| 4️⃣ | `get_by_test_id()` | `page.get_by_test_id("repo-list")` | ⭐⭐⭐ |
| 5️⃣ | `locator("[data-*]")` | `page.locator("[data-tab-item='repos']")` | ⭐⭐⭐ |
| 6️⃣ | CSS selector | `page.locator("nav .search-input")` | ⭐⭐ |

**PROHIBIDO** usar XPath como primera opción.

## 6. Anti-Fragilidad: `verify_page_loaded()`

Todo POM **DEBE** incluir `verify_page_loaded()`. La implementación depende del tipo de app:

**HTML Estándar:**
```python
def verify_page_loaded(self):
    expect(self.page).to_have_url(re.compile(r"github\.com/.*"))
    expect(self.page.get_by_role("heading")).to_be_visible(timeout=10000)
```

**Flutter con semántica:**
```python
def verify_page_loaded(self):
    expect(self.page).to_have_url(re.compile(r".*invercorp.*"))
    self.page.wait_for_selector("flt-glass-pane", state="attached", timeout=15000)
```

**Flutter SIN semántica (WASM/Skia):**
```python
def verify_page_loaded(self):
    self.page.wait_for_url(re.compile(r".*dashBoard.*"), timeout=30000)
    self.page.wait_for_selector("flt-glass-pane", state="attached", timeout=15000)
    self.page.wait_for_load_state("networkidle", timeout=30000)
    self.page.wait_for_timeout(3000)  # Skia necesita tiempo extra para renderizar
```

## 7. Rate Limiting y Cortesía

- Usar `page.wait_for_load_state("networkidle")` antes de interactuar.
- No paralelizar tests contra el mismo sitio sin evaluarlo primero.
- Si un test falla con `403 Forbidden` o CAPTCHA, es un error del entorno, NO del test.

## 8. 🔍 Inspección de Páginas Protegidas (Login Requerido)

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
        // Buscar texto específico en todo el DOM
        kamFound: Array.from(document.querySelectorAll('*'))
            .filter(el => (el.textContent || '').includes('KAM'))
            .map(el => ({ tag: el.tagName, text: el.textContent }))
    };
}""")
```

## 9. Estrategia Anti-Bloqueo (Autocorrección)

Si un selector falla:
1. **Identificar el tipo de app** (HTML vs Flutter con/sin semántica).
2. **Inspeccionar el DOM** usando el método apropiado (sección 8 si requiere login).
3. **Actualizar el POM** con la estrategia correcta para ese tipo de app.
4. **Buscar impacto global**: verificar si otros POMs del mismo sitio necesitan el mismo cambio.
