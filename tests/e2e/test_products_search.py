# Archivo: tests/e2e/test_products_search.py
"""
Test E2E: Buscar productos con 'jeans' en Automation Exercise.

Navega a la página de productos, busca "jeans", extrae los
resultados y los valida contra los productos esperados.
Los resultados se guardan como JSON en artifacts/.
"""
import json
import os
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import Page

from poms.products_page import ProductsPage

scenarios('../../features/products_search.feature')

# ==========================================
# 📦 FIXTURES
# ==========================================

@pytest.fixture
def shared_data():
    """Diccionario para compartir datos entre steps (regla pytest-bdd.md #2)."""
    return {}


# ==========================================
# 📋 STEPS BDD
# ==========================================

@given(
    'the user is on the products page of Automation Exercise',
    target_fixture="browser_instance",
)
def navigate_to_products(browser_instance, shared_data):
    """Navega a la página de productos y verifica que cargó."""
    products_page = ProductsPage(browser_instance)
    products_page.navigate()
    products_page.verify_page_loaded()
    shared_data['products_page'] = products_page


@when(parsers.parse('the user searches for products with "{keyword}"'))
def search_products(shared_data, keyword):
    """Busca productos que contengan el keyword dado."""
    products_page: ProductsPage = shared_data['products_page']
    results = products_page.get_products_containing(keyword)
    shared_data['search_results'] = results
    shared_data['keyword'] = keyword


@then('the matching products are returned as JSON')
def verify_products_json(shared_data):
    """Verifica que se encontraron productos y los guarda como JSON."""
    results = shared_data['search_results']
    keyword = shared_data['keyword']

    # Verificar que se encontraron productos
    assert len(results) > 0, (
        f"No se encontraron productos con '{keyword}' en su nombre"
    )

    # Verificar que todos los resultados contienen el keyword
    for product in results:
        assert keyword.lower() in product["name"].lower(), (
            f"Producto '{product['name']}' no contiene '{keyword}'"
        )

    # Guardar resultados como JSON en artifacts/
    os.makedirs("artifacts", exist_ok=True)
    output_path = os.path.join("artifacts", "jeans_products.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Se encontraron {len(results)} productos con '{keyword}':")
    print(json.dumps(results, indent=2, ensure_ascii=False))
