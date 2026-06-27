# Archivo: utils/api_testing.py
"""
Clase auxiliar reutilizable para operaciones API en pruebas E2E.

Centraliza URLs, payloads y headers en un solo lugar
para que los cambios de endpoint se propaguen automáticamente a todos los tests.

Patrón inspirado en la arquitectura de api_client.py (principio DRY).
Todas las URLs y credenciales se consumen de variables de entorno
(regla pytest-bdd.md #4).
"""
import os
from playwright.sync_api import Playwright


class APIUtils:
    """Cliente HTTP reutilizable para operaciones de autenticación y API.

    Usa la API de request contexts de Playwright para hacer llamadas HTTP
    sin necesidad de instalar librerías adicionales como `requests`.

    Uso típico en fixtures:
        api = APIUtils()
        token = api.getToken(playwright)

    Uso con base_url personalizada:
        api = APIUtils(base_url="https://staging-api.example.com")
        token = api.getToken(playwright, email="test@example.com", password="pass")
    """

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("API_BASE_URL", "")

    def _url(self, path: str) -> str:
        """Construye URL completa desde path relativo."""
        return f"{self.base_url}{path}"

    def _headers(self, token: str = None) -> dict:
        """Construye headers Authorization con Bearer token.

        Args:
            token: Token de autenticación. Si es None, retorna headers vacíos.

        Returns:
            dict: Headers con Authorization si se provee token.
        """
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def getToken(
        self,
        playwright: Playwright,
        email: str = None,
        password: str = None,
        login_path: str = "api/auth/login",
        token_field: str = "data",
    ) -> str:
        """Obtiene un token de autenticación vía API.

        Args:
            playwright: Instancia de Playwright para crear contexto de API.
            email: Email del usuario. Si no se provee, usa TEST_USER_EMAIL del .env.
            password: Contraseña. Si no se provee, usa TEST_USER_PASSWORD del .env.
            login_path: Path relativo del endpoint de login (sin slash inicial).
                Por defecto "api/auth/login". Configúralo según tu backend.
            token_field: Campo del response JSON que contiene el token.
                Por defecto "data". Puede ser "access_token", "token", etc.

        Returns:
            str: Token de autenticación.

        Raises:
            AssertionError: Si el login falla.
            ValueError: Si las credenciales no están configuradas.
        """
        resolved_email = email or os.getenv("TEST_USER_EMAIL")
        resolved_password = password or os.getenv("TEST_USER_PASSWORD")

        if not resolved_email or not resolved_password:
            raise ValueError(
                "Credenciales no configuradas. "
                "Establece TEST_USER_EMAIL y TEST_USER_PASSWORD en tu archivo .env"
            )

        api_request_context = playwright.request.new_context(
            base_url=self.base_url
        )

        payload = {
            "email": resolved_email,
            "password": resolved_password
        }

        response = api_request_context.post(
            login_path,
            data=payload
        )

        assert response.ok, (
            f"Login falló ({response.status}): {response.text()}"
        )

        response_body = response.json()
        return response_body[token_field]