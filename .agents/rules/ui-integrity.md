---
description: Reglas para verificar integridad visual de páginas externas durante testing
trigger: "siempre que se ejecute un test E2E o se reporte un fallo visual"
---

# Verificación de Integridad de UI (Sitios Externos)

Para evitar falsos positivos y detectar cuando un sitio externo tiene problemas, sigue estos pasos obligatorios:

## 1. Verificación de Estado HTTP

Antes de interactuar con cualquier página, el test debe confirmar:
- La página cargó correctamente (no 404, 500, o CAPTCHA)
- No hay redirecciones inesperadas
- El contenido principal es visible (no solo un spinner eterno)

## 2. Validación en Caliente (Browser Check)

Cuando un test falle por selector no encontrado, el agente **DEBE** usar `browser_subagent` para:
1. Abrir la URL del test
2. Verificar que la página carga correctamente
3. Confirmar que el error es por cambio de DOM (no por sitio caído)
4. Si el sitio está caído o bloqueado, reportar como error de entorno

## 3. Detección de Cambios en Sitios Externos

Los sitios externos cambian sin aviso. Señales de cambio:
- `TimeoutError` en selectores que antes funcionaban
- Nuevos elementos de UI (banners, popups, modales de cookies)
- Cambios en clases CSS o estructura HTML

**Protocolo ante cambios detectados:**
1. Capturar screenshot actual
2. Listar todos los selectores afectados del POM
3. Actualizar TODOS los selectores en una sola ronda (regla de edición global)
4. Buscar impacto en otros POMs del mismo sitio

## 4. Manejo de Popups y Overlays Inesperados

Sitios externos frecuentemente muestran:
- Banners de cookies
- Modales de newsletter
- Popups de promoción

El `conftest.py` debe incluir lógica global para cerrar estos overlays antes de los tests, evitando parches locales en cada POM (regla `mindset_scalability.md`).
