---
trigger: "whenever the user pastes a pytest error, a traceback, or reports that a test failed"
---

# Failed Tests Diagnostic Protocol

**This rule has maximum priority when the user reports a broken test.** The agent MUST follow these steps IN ORDER before editing any file.

---

## Step 1: Classify the Error

Leer el traceback completo y clasificarlo:

| Categoría | Señales en el traceback | Fuente de verdad |
|---|---|---|
| **Error de API (4xx/5xx)** | `status_code == 404`, `422`, `500` | `utils/api_testing.py`, `.env` |
| **Error de Selector/UI** | `TimeoutError`, `waiting for locator(...)` | **DOM Vivo** (requiere inspección) |
| **Error de Integridad** | Sitio caído, CAPTCHA, 403 | Browser real |
| **Error de Lógica/Aserción** | `AssertionError` con valores comparados | El test + POM involucrado |
| **Error de Flutter sin semántica** | `flt-semantics` count = 0, texto no encontrado en DOM | Rediseñar validación (URL + screenshot) |

---

## Step 2: Investigate Before Editing

### Para errores de API:
1. Verificar `.env` — confirmar URLs y credenciales.
2. Leer `utils/api_testing.py` — verificar endpoints.
3. **Buscar impacto global**: `grep_search` en todo el proyecto buscando el endpoint viejo o el campo incorrecto.

### Para errores de Selector/UI:
1. **Identificar el tipo de app** (HTML, Flutter con/sin semántica, SPA).
2. **Inspeccionar el DOM**:
   - **Página pública**: usar `browser_subagent`.
   - **Página protegida (detrás de login)**: crear un **script de Playwright** que haga el login completo (con OTP si aplica) y luego `page.evaluate()` para volcar el DOM. **NO usar `browser_subagent` para esto** — no puede hacer login con OTP.
3. Analizar el resultado para determinar la estrategia correcta.

### Para errores de Flutter WASM/Skia (sin semántica):
Si la inspección revela:
- `flt-semantics` count = 0
- Solo existe `<flt-semantics-placeholder aria-label='Enable accessibility'>`
- 0 elementos `<canvas>`

Entonces **el texto buscado NO EXISTE en el DOM**. La solución es:
1. Cambiar la validación a URL + `networkidle` + screenshot.
2. **NO** intentar buscar texto en el DOM — siempre fallará.

### Para errores de Lógica:
1. Leer el test y el POM involucrado.
2. Verificar `shared_data` y fixtures.
3. **NO asumir que el test actual es correcto** — siempre verificar contra la fuente de verdad (DOM vivo, API docs, etc.).

### Verificación de Integridad (Crucial):
**SIEMPRE** que un test falle por un selector no encontrado, abre el navegador con `browser_subagent` para descartar que la página esté rota por un error del sitio.

---

## Step 3: Edit Everything at Once

**PROHIBIDO**: Editar 1 archivo → usuario ejecuta test → falla otro → editar otro archivo.

**OBLIGATORIO antes de la primera edición:**
1. Tener la lista COMPLETA de archivos afectados.
2. Tener TODAS las correcciones listas.
3. Aplicar TODAS las ediciones en una sola ronda.

---

## Anti-patterns to Avoid

❌ **Adivinar selectores** basándose en screenshots — el texto visible NO siempre existe en el DOM.
❌ **Asumir que `flt-semantics` existe** — Flutter WASM/Skia no los genera sin accesibilidad habilitada.
❌ **Usar `browser_subagent` para páginas con login** — no puede hacer OTP. Crear un script de Playwright.
❌ **Editar solo el archivo reportado** — buscar el patrón roto en todo el proyecto.
❌ **Envolver en try/except** — crea falsos positivos.
❌ **Asumir que el test actual es correcto** — "Solo cambió la URL, el payload debe estar bien". No. Siempre verificar contra la fuente de verdad.
❌ **Múltiples lecturas fragmentadas** — Hacer 5 llamadas a `grep_search` buscando distintas cadenas. En su lugar, una sola lectura con `view_file` del archivo fuente te da todo el contexto.
