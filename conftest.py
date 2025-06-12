import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--browser_name", action="store", default="chrome", help="browser selection"
    )

@pytest.fixture(scope="session")
def user_credentials(request):
    return request.param

@pytest.fixture()
def browserInstance(playwright, request):
    browser_name = request.config.getoption("browser_name")
    if browser_name == "chrome":
        browser = playwright.chromium.launch(headless=True)
    elif browser_name == "firefox":
        browser = playwright.firefox.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
    browser.close()

def pytest_configure(config):
    config._metadata = {
        "Proyecto": "Automatización QA",
        "Tester": "Jhonatan Flores",
        "Navegador": "Chromium"
    }