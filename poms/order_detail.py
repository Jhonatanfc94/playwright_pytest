class OrderDetailPage:

    def __init__(self, page):
        self.page = page
        self.thankYouText = page.locator(".tagline")