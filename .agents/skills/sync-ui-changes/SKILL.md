---
name: sync-ui-changes
description: Audits and updates all POMs and tests when the UI of a site has changed. Use this when the user reports a redesign, a deploy with UI changes, or asks to update all POMs proactively — without a specific test failure traceback.
---

# UI Changes Synchronizer

## When to use this skill
When the user reports that a site has been redesigned, a new deploy changed the UI, or requests a proactive audit of all POMs — **without** pasting a specific pytest traceback. If the user pastes a traceback, use `fix-broken-tests` instead.

## Flujo Principal

### Paso 1: Determinar Paradigma de Testing

Leer la variable `TESTING_PARADIGM` del archivo `.env`:

- Si `TESTING_PARADIGM=internal` → seguir **Branch A (Interno)**.
- Si `TESTING_PARADIGM=external` → seguir **Branch B (Externo)**.
- Si la variable NO existe → preguntar al usuario: *"¿Este proyecto testea código propio (internal) o sitios externos (external)?"*. Añadir la respuesta al `.env` automáticamente.

---

### Paso 2: Identificar qué cambió

#### Branch A — Testing Interno (Con acceso al código fuente)

1. **Revisar los cambios recientes del frontend:**
   - Volcar `git diff` a un archivo (en PowerShell, obligatorio usar Python subprocess):
     ```bash
     python -c "import subprocess; out = subprocess.check_output(['git', 'log', '--oneline', '-20'], encoding='utf-8', errors='replace'); open('diff.txt', 'w', encoding='utf-8').write(out)"
     ```
   - Leer `diff.txt` para identificar los componentes que cambiaron.
2. **Mapear cambios del frontend a POMs existentes:**
   - Buscar con `grep_search` en `poms/` los selectores que referencian componentes modificados.
   - Listar todos los POMs afectados.
3. **Si hay `data-testid` nuevos o cambiados:**
   - Actualizar los locators del POM para usar los nuevos `data-testid`.
   - Si se eliminaron `data-testid`, sugerir al usuario restaurarlos o usar un selector alternativo resiliente.

#### Branch B — Testing Externo (Sin acceso al código fuente)

1. **Navegar al sitio con `browser_subagent`:**
   - Abrir la URL principal del sitio.
   - Verificar que la página carga correctamente (no 404, 500, ni CAPTCHA).
   - Tomar screenshot actual del estado nuevo.
2. **Inspeccionar el DOM actual:**
   - Identificar el tipo de app (HTML/SPA/Flutter con/sin semántica).
   - Extraer los selectores actuales disponibles (roles, textos, aria-labels, data-testid).
3. **Si la página requiere login:**
   - Crear un script de Playwright que haga login completo y use `page.evaluate()` para volcar el DOM.
   - **NO usar `browser_subagent`** para páginas protegidas.
4. **Comparar con screenshots guardados** (si existen en `screenshots/`) para detectar cambios visuales.

---

### Paso 3: Auditar TODOS los POMs afectados

1. **Listar todos los POMs** del sitio afectado en `poms/`.
2. **Para cada POM:**
   - Verificar cada selector contra el DOM actual (interno: código fuente, externo: DOM vivo).
   - Marcar selectores obsoletos.
   - Proponer el selector de reemplazo siguiendo la jerarquía: `get_by_role` > `get_by_text` > `get_by_placeholder` > `get_by_test_id` > CSS.
3. **Verificar `verify_page_loaded()`** de cada POM — los patrones de URL podrían haber cambiado.

---

### Paso 4: Aplicar todas las correcciones en una sola ronda

- **PROHIBIDO** editar un POM, esperar a que el usuario teste, y luego editar el siguiente.
- Editar TODOS los POMs afectados de una sola vez.
- Usar `multi_replace_file_content` cuando haya múltiples cambios en el mismo archivo.

---

### Paso 5: Actualizar referencia visual

- Tomar nuevos screenshots de las páginas afectadas.
- Guardarlos en `screenshots/` para referencia futura.
- Presentar un resumen con tabla de todos los cambios realizados.

---

## Manejo de Popups y Overlays Inesperados

Sitios externos frecuentemente muestran elementos que interfieren con tests:
- Banners de cookies
- Modales de newsletter
- Popups de promoción

**Protocolo:**
1. Si se detectan nuevos overlays, añadir lógica de cierre en `conftest.py` (fixture global).
2. **NO** parchear en cada POM individualmente (regla de escalabilidad).
3. Documentar el overlay y su selector en el conftest.

## Verificación de Estado HTTP

Antes de concluir que un cambio de UI es intencional, verificar:
- La página no devuelve errores HTTP (404, 500).
- No hay redirecciones inesperadas.
- El contenido principal es visible (no solo un spinner eterno).

## Detección de Cambios — Señales

| Señal | Probable Causa |
|---|---|
| `TimeoutError` en selectores que antes funcionaban | Cambio de DOM / rediseño |
| Nuevos elementos de UI (banners, popups, modales) | Feature nueva o A/B testing |
| Cambios en clases CSS o estructura HTML | Refactor del frontend |
| URLs de páginas cambiaron | Reestructuración de rutas |

## Referencia adicional

Consultar `references/change-detection.md` para protocolos detallados de detección de cambios.
