---
trigger: "whenever the user reports visual changes, interface updates, or failures in UI selectors / POMs"
---

# Frontend and Testing Synchronization Rule (Playwright)

To avoid inefficient repository scanning and high latency when figuring out which selectors changed, strictly follow this protocol:

## 1. Análisis Completo del DOM (Regla Anti-Grep)

**PROHIBIDO** hacer múltiples `grep_search` individuales buscando placeholders o textos en un repositorio local que no existe.

**OBLIGATORIO:** Cuando un selector falle, el agente **DEBE** navegar al sitio usando `browser_subagent` y analizar el **DOM actual**. Una sola inspección visual del DOM da todos los placeholders, textos de botones y atributos `data-testid` o `aria-label` necesarios.

**Ejemplo correcto:**
```
# En lugar de adivinar el selector...
# Navega y analiza:
browser_subagent → navegar a la URL del sitio externo
```

## 2. Claridad del Cambio (Vocabulario)

- Cuando se reporte un cambio de UI en un sitio externo, referirse a ello como "Cambio en el DOM del Sitio Externo".
- Priorizar el término "Locator Resiliente" (ARIA roles, placeholders) sobre "Selector CSS Frágil".
- Evitar usar el término "direcciones" para referirse a CSS Locators o XPaths, y en su lugar llamarles "Selectores", "Locators" o "URLs del DOM".

## 3. Jerarquía de Selectores (Prioridad para Sitios Externos)

1. `get_by_role()`
2. `get_by_label()`
3. `get_by_placeholder()`
4. `get_by_test_id()` o `locator("[data-...]")`
5. `.locator("text=...")`

**PROHIBIDO** usar XPath como primera opción.

## 4. Verificación Cruzada Obligatoria

Antes de declarar que un POM está "arreglado", el agente debe comprobar en el navegador que **todos** los selectores del POM coinciden con el DOM actual.

## 5. Screenshots como Documentación

Al actualizar un POM por un cambio en el sitio externo, toma un screenshot y guárdalo en `screenshots/` como referencia del nuevo estado del DOM.

## 6. Uso de `.wait_for()` con Carruseles y Sliders

- Si los elementos están dentro de carruseles (Sliders) deslizables, no asumas que `page.click()` fallará, Playwright hace Auto-Scroll. Aún así, agrega aserciones o `wait_for(state="visible")` antes de clickear para asegurar que elementos escondidos bajo contenedores ocultos funcionen.

## 7. Debugging Inteligente (Git Diff en PowerShell)

- Cuando necesites inspeccionar el `git diff` en Windows PowerShell, **está prohibido usar el comando directo `git diff`** ya que la terminal en paginación puede corromper el formato truncando los outputs.
- **Solución Obligatoria:** Siempre extraer las diferencias usando un wrapper de Python nativo, volcando la salida a un archivo para leer sin bloqueos:
  ```bash
  python -c "import subprocess; out = subprocess.check_output(['git', 'diff'], encoding='utf-8', errors='replace'); open('diff.txt', 'w', encoding='utf-8').write(out)"
  ```
