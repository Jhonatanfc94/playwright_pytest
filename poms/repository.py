# Archivo: poms/repository.py
"""
POM para la página de repositorios de GitHub.

Sigue la jerarquía de selectores resilientes definida en
external-site-testing.md: get_by_role > get_by_text > locator([data-*]).
"""
import re
from playwright.sync_api import Page, expect
from poms.base_page import BasePage


class RepositoryPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self._setup_locators()

    def _setup_locators(self):
        # Prioridad: data-tab-item es un atributo estable de GitHub
        self.repositories_tab = self.page.locator("[data-tab-item='repositories']").first
        self.search_input = self.page.get_by_placeholder("Find a repository…")

    def verify_page_loaded(self):
        """Verifica que la página de perfil de GitHub cargó correctamente."""
        expect(self.page).to_have_url(re.compile(r"github\.com/"))
        expect(self.repositories_tab).to_be_visible(timeout=10000)

    def click_repositories_tab(self):
        """Navega a la pestaña de repositorios."""
        self.repositories_tab.click()
        expect(self.search_input).to_be_visible(timeout=10000)

    def search_repository(self, query: str):
        """Busca un repositorio por nombre.

        Args:
            query: Término de búsqueda.
        """
        self.search_input.fill(query)
        self.search_input.press("Enter")

    def get_result_links_text(self) -> list:
        """Obtiene los nombres de los repositorios visibles en resultados.

        Returns:
            list: Lista de nombres de repositorios encontrados.
        """
        locators = self.page.locator("[itemprop='name codeRepository']")
        return [el.text_content().strip() for el in locators.element_handles()]

    def verify_repository_visible(self, repo_name: str):
        """Verifica que un repositorio específico sea visible en los resultados.

        Args:
            repo_name: Nombre del repositorio esperado.
        """
        expect(
            self.page.locator("[itemprop='name codeRepository']")
            .filter(has_text=repo_name)
            .first
        ).to_be_visible(timeout=10000)