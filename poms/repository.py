from playwright.sync_api import Page, expect

class RepositoryPage:
    def __init__(self, page: Page):
        self.page = page
        self._setup_locators()

    def _setup_locators(self):
        self.repositories_tab = self.page.locator("//*[@data-tab-item='repositories']").first
        self.search_input = self.page.locator("//input[@name='q']")

    def get_result_links_text(self):
        locators = self.page.locator("//a[@itemprop='name codeRepository']")
        return [el.text_content() for el in locators.element_handles()]