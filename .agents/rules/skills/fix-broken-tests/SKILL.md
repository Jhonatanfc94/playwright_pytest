---
name: fix-broken-tests
description: Fixes broken E2E tests by diagnosing the error against the live DOM and applying all corrections at once. Use this when the user pastes a failing pytest traceback.
---

# Broken Test Repairer

## When to use this skill
When the user pastes a pytest error (traceback, AssertionError, TimeoutError) and requests to fix the test.

## How to use it

### Phase 1: Diagnóstico Rápido (NO editar nada aún)

1. **Leer el traceback** e identificar la categoría:
   - `TimeoutError: waiting for locator(...)` → Selector desactualizado
   - `AssertionError: text not found in DOM` → Posible Flutter sin semántica
   - `4xx / 422 / 500` → Problema de API
   - `AssertionError: assert X == Y` → Lógica o datos incorrectos

2. **Consultar las fuentes de verdad:**

   **Si es error de API:**
   ```
   view_file(".env")
   view_file("utils/api_testing.py")
   ```

   **Si es error de Selector/UI en página pública:**
   ```
   # Navega al sitio externo para analizar el DOM Vivo
   browser_subagent → navegar a la URL
   ```

   **Si es error de Selector/UI en página protegida (detrás de login):**
   ```
   # Crear un script de Playwright que haga login completo + page.evaluate()
   # NO usar browser_subagent — no puede hacer OTP
   python inspect_<page>_dom.py
   ```

   **Si es error de Flutter sin semántica (0 flt-semantics):**
   ```
   # El texto NO existe en el DOM. Cambiar validación a:
   # URL + networkidle + screenshot
   ```

3. **Leer el POM y test afectados** completos (con `view_file`, no greps individuales).

4. **Buscar impacto global** — buscar el patrón roto en todo el proyecto.

5. **NO asumir que el test actual es correcto** — siempre verificar contra la fuente de verdad.

### Fase 2: Planificar Todas las Correcciones

Antes de editar, listar:
- Todos los archivos con el mismo problema
- Todos los selectores/validaciones que necesitan actualización
- El tipo de app de cada página afectada

### Fase 3: Ejecutar Todas las Ediciones

- Editar TODOS los archivos afectados en una sola ronda.
- Usar `multi_replace_file_content` cuando haya múltiples cambios en el mismo archivo.
- Al finalizar, presentar un resumen de todos los cambios con una tabla.

## Archivos de Referencia del Proyecto

| Capa       | Archivo                | Propósito                          |
|---|---|---|
| POMs       | `poms/*.py`            | Page Object Models (selectores UI) |
| Tests      | `tests/e2e/*.py`       | Step definitions y fixtures        |
| Features   | `features/*.feature`   | Escenarios BDD                     |
| Config     | `conftest.py`          | Fixtures globales y hooks          |
| Utils      | `utils/*.py`           | Funciones auxiliares (email, API)  |
| Externo    | **DOM Vivo**           | 🔒 Fuente de verdad UI             |

## Checklist de Verificación Post-Fix

- [ ] ¿Se identificó el tipo de app (HTML / Flutter con semántica / Flutter sin semántica / SPA)?
- [ ] ¿Se inspeccionó el DOM real (no se adivinaron selectores)?
- [ ] ¿Cada acción del POM tiene una validación?
- [ ] ¿No hay `try/except` que silencien errores?
- [ ] ¿Se buscó impacto global en otros POMs/tests?
- [ ] ¿Se verificó que el test NO asumía datos obsoletos?
- [ ] ¿Se verificó manejo de listas (scroll/paginación) si aplica?
