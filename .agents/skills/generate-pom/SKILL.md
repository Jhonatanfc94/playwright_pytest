---
name: generate-pom
description: Generates a new Page Object Model (POM) class for UI automation with Playwright and Pytest. Use this when the user needs to map a new screen, create a new POM, or add a new page to the test framework.
---

# Page Object Generator

## When to use this skill
Use this when the user requests to create a new POM for a specific web page, screen, or section of a site.

## Flujo Principal

### Paso 1: Determinar Paradigma de Testing

Leer la variable `TESTING_PARADIGM` del archivo `.env`:

- Si `TESTING_PARADIGM=internal` → seguir **Branch A (Interno)**.
- Si `TESTING_PARADIGM=external` → seguir **Branch B (Externo)**.
- Si la variable NO existe → preguntar al usuario: *"¿Este proyecto testea código propio (internal) o sitios externos (external)?"*. Añadir la respuesta al `.env` automáticamente.

---

### Paso 2: Identificar tipo de app y obtener selectores

#### Branch A — Testing Interno (Con acceso al código fuente)

1. **Buscar componentes en el código frontend** usando `grep_search`:
   - Buscar el componente o página por nombre, ruta, o textos visibles.
   - Identificar los atributos `data-testid`, `aria-label`, roles semánticos ya existentes.
2. **Si no hay selectores claros:**
   - Sugerir al usuario inyectar `data-testid` en los componentes clave del frontend.
   - Documentar qué atributos se añadieron y en qué archivos.
3. **Identificar tipo de app:** HTML estándar, SPA (React/Vue/Angular), Flutter, etc.
4. **Consultar** `references/selector-hierarchy.md` para la jerarquía de selectores.

#### Branch B — Testing Externo (Sin acceso al código fuente)

1. **Inspeccionar el DOM vivo:**
   - **Página pública:** Usar `browser_subagent` para navegar e inspeccionar.
   - **Página protegida (login requerido):** Crear un script de Playwright que ejecute el flujo de autenticación completo (email → OTP → verificación) y use `page.evaluate()` para volcar el DOM. **NO usar `browser_subagent`** para páginas protegidas — no puede hacer OTP.
2. **Identificar tipo de app** analizando el DOM:
   - Consultar `references/flutter-detection.md` para la tabla de detección y estrategias Flutter.
   - Consultar `references/selector-hierarchy.md` para la jerarquía de selectores HTML.
3. **NUNCA adivinar selectores** basándose en screenshots o textos visibles. Lo que se ve en pantalla NO siempre existe en el DOM (especialmente en Flutter).

---

### Paso 3: Crear el POM

1. Crear el archivo en `poms/` heredando de `BasePage` (`poms/base_page.py`).
2. Definir `__init__` con `super().__init__(page)` y los locators apropiados para el tipo de app.
3. Implementar `verify_page_loaded()` según el tipo de app (consultar `references/templates-html.md` o `references/templates-flutter.md`).
4. Añadir métodos que representen acciones de usuario (ej: `login_user()`, no `click_button_and_fill_text()`).
5. **Cada acción DEBE tener una validación** (URL change, element present, etc.).
6. **Manejo de Listas:** Si la página usa Infinite Scroll, hacer scroll + esperar red antes de asertar. Si usa paginación, interactuar con botones primero.

### Paso 4: Documentar

- Documentar el tipo de app en el docstring de la clase.
- Si se usan coordenadas de viewport, documentar cómo se calcularon.
- Guardar un screenshot de referencia en `screenshots/`.

## Archivos de referencia

| Tipo de app | Referencia |
|---|---|
| Detección de Flutter | `references/flutter-detection.md` |
| Jerarquía de selectores | `references/selector-hierarchy.md` |
| Plantilla HTML/SPA | `references/templates-html.md` |
| Plantilla Flutter | `references/templates-flutter.md` |
| Clase base | `poms/base_page.py` |
