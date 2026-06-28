---
name: fix-broken-tests
description: Fixes broken E2E tests by diagnosing the error against the source of truth and applying all corrections at once. Use this when the user pastes a failing pytest traceback, an AssertionError, or a TimeoutError.
---

# Broken Test Repairer

## When to use this skill
When the user pastes a pytest error (traceback, AssertionError, TimeoutError) and requests to fix the test.

## Flujo Principal

### Paso 1: Determinar Paradigma de Testing

Leer la variable `TESTING_PARADIGM` del archivo `.env`:

- Si `TESTING_PARADIGM=internal` → la fuente de verdad es el **código fuente local**.
- Si `TESTING_PARADIGM=external` → la fuente de verdad es el **DOM vivo del sitio**.
- Si la variable NO existe → preguntar al usuario: *"¿Este proyecto testea código propio (internal) o sitios externos (external)?"*. Añadir la respuesta al `.env` automáticamente.

---

### Paso 2: Clasificar el Error (NO editar nada aún)

Leer el traceback completo y clasificar:

| Categoría | Señales en el traceback | Fuente de verdad |
|---|---|---|
| **Error de API (4xx/5xx)** | `status_code == 404`, `422`, `500` | `utils/api_testing.py`, `.env` |
| **Error de Selector/UI** | `TimeoutError`, `waiting for locator(...)` | Depende del paradigma (ver Paso 3) |
| **Error de Integridad** | Sitio caído, CAPTCHA, 403 | Browser real |
| **Error de Lógica/Aserción** | `AssertionError` con valores comparados | El test + POM involucrado |
| **Error de Flutter sin semántica** | `flt-semantics` count = 0, texto no encontrado | Rediseñar validación (URL + screenshot) |

Consultar `references/diagnostic-tables.md` para más detalle sobre cada categoría.

---

### Paso 3: Investigar según Paradigma

#### Branch A — Testing Interno (Con acceso al código fuente)

**Para errores de API:**
1. Verificar `.env` — confirmar URLs y credenciales.
2. Leer `utils/api_testing.py` — verificar endpoints.
3. Revisar si un deploy reciente cambió los endpoints (consultar `git log` del backend si hay acceso).

**Para errores de Selector/UI:**
1. Buscar el componente en el código frontend con `grep_search`.
2. Verificar si el componente cambió en un commit reciente (`git log` / `git diff`).
3. Decidir: ¿actualizar el test o revertir el cambio en el frontend?
4. Si el selector cambió, verificar si hay `data-testid` disponibles. Si no, sugerir inyectarlos.

**Para errores de Lógica:**
1. Leer el test y el POM involucrado completos (con `view_file`, no greps individuales).
2. Verificar `shared_data` y fixtures.
3. Contrastar con el código fuente real del frontend/backend.

#### Branch B — Testing Externo (Sin acceso al código fuente)

**Para errores de API:**
1. Verificar `.env` — confirmar URLs y credenciales.
2. Leer `utils/api_testing.py` — verificar endpoints.
3. Buscar impacto global con `grep_search` en todo el proyecto.

**Para errores de Selector/UI:**
1. **Identificar el tipo de app** (HTML, Flutter con/sin semántica, SPA).
2. **Inspeccionar el DOM vivo:**
   - **Página pública**: usar `browser_subagent`.
   - **Página protegida (detrás de login)**: crear un **script de Playwright** que haga el login completo y luego `page.evaluate()` para volcar el DOM. **NO usar `browser_subagent`** — no puede hacer OTP.
3. Analizar el resultado para determinar la estrategia correcta.

**Para errores de Flutter WASM/Skia (sin semántica):**
Si la inspección revela `flt-semantics` count = 0:
1. Cambiar la validación a URL + `networkidle` + screenshot.
2. **NO** intentar buscar texto en el DOM — siempre fallará.

**Para errores de Lógica:**
1. Leer el test y el POM involucrado completos.
2. **NO asumir que el test actual es correcto** — siempre verificar contra la fuente de verdad (DOM vivo, API docs, etc.).

**Verificación de Integridad (Crucial):**
SIEMPRE que un test falle por un selector no encontrado, abrir el navegador con `browser_subagent` para descartar que la página esté rota por un error del sitio.

---

### Paso 4: Buscar Impacto Global

**OBLIGATORIO antes de la primera edición:**
1. Buscar con `grep_search` el patrón roto en todo el proyecto.
2. Tener la lista COMPLETA de archivos afectados.
3. Tener TODAS las correcciones listas.

---

### Paso 5: Ejecutar Todas las Ediciones

- Editar TODOS los archivos afectados en una sola ronda.
- Usar `multi_replace_file_content` cuando haya múltiples cambios en el mismo archivo.
- Al finalizar, presentar un resumen de todos los cambios con una tabla.

**PROHIBIDO**: Editar 1 archivo → usuario ejecuta test → falla otro → editar otro archivo.

---

## Anti-patterns a Evitar

❌ **Adivinar selectores** basándose en screenshots — el texto visible NO siempre existe en el DOM.
❌ **Asumir que `flt-semantics` existe** — Flutter WASM/Skia no los genera sin accesibilidad.
❌ **Usar `browser_subagent` para páginas con login** — no puede hacer OTP.
❌ **Editar solo el archivo reportado** — buscar el patrón roto en todo el proyecto.
❌ **Envolver en try/except** — crea falsos positivos.
❌ **Asumir que el test actual es correcto** — siempre verificar contra la fuente de verdad.
❌ **Múltiples lecturas fragmentadas** — una sola lectura con `view_file` del archivo fuente da todo el contexto.

## Archivos de Referencia del Proyecto

| Capa | Archivo | Propósito |
|---|---|---|
| POMs | `poms/*.py` | Page Object Models (selectores UI) |
| Tests | `tests/e2e/*.py` | Step definitions y fixtures |
| Features | `features/*.feature` | Escenarios BDD |
| Config | `conftest.py` | Fixtures globales y hooks |
| Utils | `utils/*.py` | Funciones auxiliares (email, API) |

## Checklist Post-Fix

- [ ] ¿Se identificó el tipo de app?
- [ ] ¿Se inspeccionó la fuente de verdad (código o DOM)?
- [ ] ¿Cada acción del POM tiene una validación?
- [ ] ¿No hay `try/except` que silencien errores?
- [ ] ¿Se buscó impacto global en otros POMs/tests?
- [ ] ¿Se verificó que el test NO asumía datos obsoletos?
- [ ] ¿Se verificó manejo de listas (scroll/paginación) si aplica?
