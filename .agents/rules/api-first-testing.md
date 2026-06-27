# Rules for API-First Validations and Fixtures

When building E2E tests or performing complex state assertions (such as database interactions, verification status, counters, etc.), follow these speed and stability guidelines:

1. **Prioriza API para Datos Dinámicos**: Si el sitio externo tiene una API pública documentada, úsala para verificar el estado interno en lugar de scrapear el DOM.
2. **Setup y Teardown Limpio vía API**: Todos los objetos de prueba (usuarios, datos de test, etc.) deben crearse y destruirse vía API cuando sea posible. **NUNCA utilices consultas SQL directas o conexiones directas a la base de datos** en las pruebas. Las operaciones de creación y limpieza también sirven como pruebas implícitas de que los endpoints funcionan.
3. **Tokens desde el Entorno**: NUNCA hardcodees tokens de API. Consúmelos siempre desde `os.getenv()`.
4. **Resiliencia ante Network Latency**: Dado que los sitios externos pueden tener latencia variable, usa `page.wait_for_load_state("networkidle")` y evita esperas de tiempo fijo.
5. **Resuelve cuellos creando endpoints de soporte**: Si necesitas preparar un estado muy complejo y faltan endpoints, pide (o crea) un endpoint dedicado de administración en lugar de saltarte la API inyectando datos directamente.

---

## Regla de Verificación de Endpoints

**ANTES** de editar un test de API, verifica que el `API_BASE_URL` en el `.env` es el correcto para el entorno de ejecución (Staging vs Producción).

---

## Regla de Impacto Global (OBLIGATORIA)

Cuando corrijas un endpoint o payload en `utils/api_testing.py` o en cualquier test, **SIEMPRE** busca con `grep_search` todos los archivos del proyecto que usen ese mismo endpoint o patrón de payload, y corrígelos **todos en una sola ronda de edición**. Nunca edites solo el archivo que falló.

Esta metodología evita *Timeouts* de Playwright debidos a problemas de consistencia, desacopla la base de datos del entorno E2E puro, y hace que los tests sean instantáneos.
