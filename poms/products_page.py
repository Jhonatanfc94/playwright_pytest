# Archivo: poms/products_page.py
"""
POM para la página de productos de Automation Exercise.

Sigue la jerarquía de selectores resilientes definida en
external-site-testing.md: get_by_role > get_by_text > locator([data-*]).
"""
import re
from playwright.sync_api import Page, expect
from poms.base_page import BasePage


class ProductsPage(BasePage):
    """Page Object Model para https://automationexercise.com/products.

    Permite navegar a la página de productos, buscar por término,
    y extraer la información de los productos encontrados.
    """

    URL = "https://automationexercise.com/products"

    def __init__(self, page: Page):
        super().__init__(page)
        self._setup_locators()

    def _setup_locators(self):
        """Configura los locators principales de la página de productos."""
        self.search_input = self.page.locator("#search_product")
        self.search_button = self.page.locator("#submit_search")
        self.product_cards = self.page.locator(".features_items .col-sm-4")
        self.product_names = self.page.locator(".features_items .productinfo p")
        self.product_prices = self.page.locator(".features_items .productinfo h2")

    def navigate(self):
        """Navega a la página de productos de Automation Exercise."""
        self.page.goto(self.URL)

    def verify_page_loaded(self):
        """Verifica que la página de productos cargó correctamente."""
        expect(self.page).to_have_url(re.compile(r"automationexercise\.com/products"))
        expect(self.search_input).to_be_visible(timeout=15000)

    def search_product(self, query: str):
        """Busca productos usando la barra de búsqueda.

        Args:
            query: Término de búsqueda.
        """
        self.search_input.fill(query)
        self.search_button.click()
        # Esperar a que los resultados se carguen
        self.page.wait_for_load_state("domcontentloaded")

    def get_product_names(self) -> list[str]:
        """Obtiene los nombres de todos los productos visibles.

        Returns:
            list[str]: Lista de nombres de productos.
        """
        self.product_names.first.wait_for(state="visible", timeout=10000)
        return [name.text_content().strip() for name in self.product_names.all()]

    def get_products_data(self) -> list[dict]:
        """Obtiene nombre y precio de todos los productos visibles.

        Returns:
            list[dict]: Lista de diccionarios con 'name' y 'price'.
        """
        names = self.product_names.all()
        prices = self.product_prices.all()

        products = []
        for name_el, price_el in zip(names, prices):
            products.append({
                "name": name_el.text_content().strip(),
                "price": price_el.text_content().strip(),
            })
        return products

    def get_products_containing(self, keyword: str) -> list[dict]:
        """Busca y retorna productos cuyo nombre contiene el keyword.

        Realiza la búsqueda en la página y filtra los resultados.

        Args:
            keyword: Palabra clave a buscar (case-insensitive).

        Returns:
            list[dict]: Productos que contienen el keyword en su nombre.
        """
        self.search_product(keyword)
        all_products = self.get_products_data()
        return [
            p for p in all_products
            if keyword.lower() in p["name"].lower()
        ]
