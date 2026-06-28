# Protocolos de Detección de Cambios en UI

## Análisis Completo del DOM (Regla Anti-Grep)

**PROHIBIDO** hacer múltiples `grep_search` individuales buscando placeholders o textos en un repositorio local que no existe (modo externo).

**OBLIGATORIO (modo externo):** Cuando un selector falle, el agente DEBE navegar al sitio usando `browser_subagent` y analizar el DOM actual. Una sola inspección visual del DOM da todos los placeholders, textos de botones y atributos `data-testid` o `aria-label` necesarios.

**OBLIGATORIO (modo interno):** Buscar los cambios en el código fuente del frontend con `grep_search` o `git diff`.

## Vocabulario Estándar

- Cuando se reporte un cambio de UI en un sitio externo, referirse a ello como "Cambio en el DOM del Sitio Externo".
- Priorizar el término "Locator Resiliente" (ARIA roles, placeholders) sobre "Selector CSS Frágil".
- Evitar usar el término "direcciones" para referirse a CSS Locators o XPaths. Llamarles "Selectores", "Locators" o "URLs del DOM".

## Verificación Cruzada Obligatoria

Antes de declarar que un POM está "arreglado", el agente debe comprobar que **todos** los selectores del POM coinciden con la fuente de verdad actual:
- **Interno:** Todos los selectores matchean con el código fuente frontend.
- **Externo:** Todos los selectores matchean con el DOM vivo del sitio.

## Screenshots como Documentación

Al actualizar un POM por un cambio en el sitio, toma un screenshot y guárdalo en `screenshots/` como referencia del nuevo estado del DOM.

## Uso de `.wait_for()` con Carruseles y Sliders

- Si los elementos están dentro de carruseles (Sliders) deslizables, no asumir que `page.click()` fallará — Playwright hace Auto-Scroll.
- Aún así, agregar aserciones o `wait_for(state="visible")` antes de clickear para asegurar que elementos escondidos bajo contenedores ocultos funcionen.

## Estrategia Anti-Bloqueo (Autocorrección)

Si un selector falla:
1. **Identificar el tipo de app** (HTML vs Flutter con/sin semántica).
2. **Inspeccionar la fuente de verdad** usando el método apropiado según paradigma.
3. **Actualizar el POM** con la estrategia correcta para ese tipo de app.
4. **Buscar impacto global**: verificar si otros POMs del mismo sitio necesitan el mismo cambio.
