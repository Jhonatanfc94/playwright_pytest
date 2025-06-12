class OrdersPage:

    def __init__(self, page):
        self.page = page

    def selectOrder(self, orderId):
        row = self.page.locator("th").filter(has_text=orderId).locator("..")
        row.get_by_role("button", name="View").click()