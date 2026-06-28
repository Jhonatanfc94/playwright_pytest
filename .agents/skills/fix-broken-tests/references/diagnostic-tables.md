# Tablas de Diagnóstico de Errores

Referencia detallada para clasificar y resolver errores de tests E2E.

## Clasificación Detallada de Errores

### Error de API (4xx/5xx)

| Código | Causa Probable | Acción |
|---|---|---|
| `404` | Endpoint cambió o no existe | Verificar URL en `.env` y `utils/api_testing.py` |
| `422` | Payload incorrecto (campos faltantes/tipo incorrecto) | Leer la respuesta del error para ver qué campo falta |
| `500` | Error del servidor | Verificar si el backend está arriba. Es error de entorno, NO del test |
| `401/403` | Token expirado o permisos insuficientes | Verificar `os.getenv()` para tokens. Regenerar si aplica |

### Error de Selector/UI

| Señal | Tipo de App | Solución |
|---|---|---|
| `TimeoutError: waiting for locator("text=...")` | HTML/SPA | El texto cambió. Inspeccionar DOM vivo para obtener el nuevo texto |
| `TimeoutError: waiting for locator("flt-semantics...")` | Flutter con semántica | El aria-label cambió. Inspeccionar DOM con `page.evaluate()` |
| `TimeoutError: waiting for locator(...)` y 0 flt-semantics | Flutter sin semántica | Los selectores semánticos NO funcionan. Cambiar a coordenadas/teclado/URL |
| `strict mode violation` | Cualquiera | El selector matchea múltiples elementos. Hacerlo más específico |

### Error de Integridad del Sitio

| Señal | Diagnóstico | Acción |
|---|---|---|
| Página en blanco | Sitio caído | Reportar como error de entorno. NO es bug del test |
| CAPTCHA visible | Anti-bot activado | Reportar como error de entorno. Considerar usar credenciales de testing |
| `403 Forbidden` | IP bloqueada o rate limiting | Reportar como error de entorno |
| Redirección inesperada | Login expirado o URL cambiada | Verificar flujo de autenticación |

### Error de Lógica/Aserción

| Señal | Causa Probable | Acción |
|---|---|---|
| `AssertionError: assert 'X' == 'Y'` | Datos de test obsoletos o lógica incorrecta | Verificar shared_data y fixtures |
| `AssertionError: 0 != 1` (counts) | Elemento no encontrado o no cargado | Verificar waits y scroll/paginación |
| `expect(...).to_have_text(...)` falla | Texto del sitio cambió | Inspeccionar DOM para obtener nuevo texto |

## Rate Limiting y Cortesía

- Usar `page.wait_for_load_state("networkidle")` antes de interactuar.
- No paralelizar tests contra el mismo sitio sin evaluarlo primero.
- Si un test falla con `403 Forbidden` o CAPTCHA, es un error del entorno, NO del test.
