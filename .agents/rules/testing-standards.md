# Project Rules — Playwright E2E Testing Framework

## 1. Mentalidad Arquitectónica (Escalabilidad y Reusabilidad)

- Rechazar parches locales. Antes de resolver un problema en un solo archivo, analizar: "¿afectará a otros flujos? ¿debería encapsularse globalmente?"
- Issues de infraestructura, latencia, autenticación o dependencias DEBEN migrarse a `conftest.py`, hooks de sesión, o módulos en `utils/`.
- Toda mitigación debe ser modular (DRY). Diseñar soluciones reutilizables para escenarios futuros, no solo el caso inmediato.
- Deber proactivo: no esperar al usuario para optimizar o globalizar. Argumentar por qué un parche local sería mala práctica.

## 2. API First

- Priorizar API para datos dinámicos y para setup/teardown de tests cuando el sitio tenga API disponible.
- NUNCA usar consultas SQL directas ni conexiones a la base de datos en las pruebas.
- Tokens y credenciales siempre desde `os.getenv()`, nunca hardcodeados.
- Verificar que `API_BASE_URL` en `.env` es correcto para el entorno (Staging vs Producción) antes de editar un test de API.
- Si se corrige un endpoint o payload, buscar impacto global con `grep_search` en todo el proyecto y corregir todo en una sola ronda.

## 3. Estándares Playwright + pytest-bdd

- Siempre usar Playwright synchronous API (`playwright.sync_api`).
- Importar `scenarios`, `given`, `when`, `then`, `parsers` desde `pytest_bdd`.
- Usar fixture `shared_data` (dict) para pasar estado entre steps. No instanciar POMs directamente sin pasarlos por `shared_data` o un fixture dedicado.
- El `__init__` del POM debe recibir y guardar la instancia `Page`. Pueden heredar de `BasePage` (`poms/base_page.py`).
- Todo POM DEBE incluir `verify_page_loaded()`.
- **PROHIBIDO** `time.sleep()`. Usar `page.wait_for_timeout(ms)` si se necesita espera fija, y documentar POR QUÉ.
- **PROHIBIDO** `try/except` que silencien errores (causa falsos positivos). Usar `count()` para verificar antes de interactuar, con fallback documentado.
- **PROHIBIDO** XPath como primera opción de selector.
- Toda acción del POM DEBE tener una validación posterior (URL change, elemento presente, etc.).

## 4. Paradigma de Testing (Interno vs Externo)

- Leer `TESTING_PARADIGM` del `.env` para determinar el modo (`internal` o `external`).
- Si no existe la variable, preguntar al usuario UNA VEZ y añadirla automáticamente al `.env`.
- **Modo Interno (acceso al código fuente):** Fuente de verdad = código fuente local. Usar `grep_search` para entender componentes frontend/backend. Se permite inyectar `data-testid` en el código fuente si faltan selectores.
- **Modo Externo (sin código fuente):** Fuente de verdad = DOM vivo del sitio. NUNCA adivinar selectores. Usar `browser_subagent` (páginas públicas) o scripts de Playwright con `page.evaluate()` (páginas protegidas con login/OTP).

## 5. Git Diff en PowerShell

- Prohibido usar `git diff` directo (la paginación corrompe el output en PowerShell).
- Solución obligatoria: volcar a archivo vía Python subprocess.
