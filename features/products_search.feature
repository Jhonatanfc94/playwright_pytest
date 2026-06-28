Feature: Automation Exercise - Búsqueda de productos Jeans
  Verificar que se pueden buscar productos con "jeans" en su nombre
  y obtener los resultados como JSON

  Scenario: Buscar productos que contengan "jeans" en su nombre
    Given the user is on the products page of Automation Exercise
    When the user searches for products with "jeans"
    Then the matching products are returned as JSON
