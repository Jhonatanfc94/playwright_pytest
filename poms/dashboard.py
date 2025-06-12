class DashboardPage:

    def __init__(self, page):
        self.page = page
        self.ordersNavLink = self.page.get_by_role("button", name="ORDERS")