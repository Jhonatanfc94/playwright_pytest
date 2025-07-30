import json
import pytest
from playwright.sync_api import Page, Playwright, expect
from utils.api_testing import APIUtils

def pytest_addoption(parser):
    parser.addoption(
        "--browser_name", action="store", default="device", help="browser selection"
    )
    parser.addoption(
        "--only-lighthouse",
        action="store_true",
        default=False,
        help="Run only lighthouse tests"
    )

@pytest.fixture(scope="session")
def user_credentials(request):
    return request.param

@pytest.fixture()
def browser_instance(playwright, request):
    browser_name = request.config.getoption("browser_name")
    only_lighthouse = request.config.getoption("--only-lighthouse")

    browser = None
    context = None

    if browser_name == "lighthouse":
        yield None
        return

    if browser_name == "chrome":
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={ 'width': 1366 , 'height': 768 }
        )
    elif browser_name == "firefox":
        browser = playwright.firefox.launch(headless=False)
        context = browser.new_context(
            viewport={ 'width': 1366 , 'height': 768 }
        )
    elif browser_name == "device":
        device = playwright.devices['iPhone 13']
        browser = playwright.webkit.launch(headless=False)
        context = browser.new_context(
            **device,
        )
    else:
        raise ValueError(f"Unsupported browser_name: {browser_name}")
    
    page = context.new_page()
    yield page

    context.close()
    browser.close()

def pytest_configure(config):
    config._metadata = {
        "Proyecto": "Playwright Pytest",
        "Tester": "Jhonatan Flores",
        "Navegador": config.getoption("--browser_name")
    }

def pytest_collection_modifyitems(config, items):
    browser_name = config.getoption("--browser_name")
    only_lighthouse = config.getoption("--only-lighthouse")

    if only_lighthouse:
        selected = [item for item in items if item.get_closest_marker("lighthouse")]
        items[:] = selected
        return
    
    if not only_lighthouse and browser_name != "lighthouse":
        remaining = [item for item in items if not item.get_closest_marker("lighthouse")]
        items[:] = remaining

@pytest.fixture(scope="function")
def logged_in_page(browser_instance: Page, playwright: Playwright) -> Page:
    api_utils = APIUtils()
    token = api_utils.getToken(playwright)

    session_data = {
        'token': token
    }

    script = f"""
        const sessionData = {json.dumps(session_data)};
        Object.keys(sessionData).forEach(key => {{
            localStorage.setItem(key, sessionData[key]);
        }});
    """
    browser_instance.add_init_script(script)
    
    browser_instance.goto("https://example.com")

    expect(browser_instance).to_have_url("https://example.com/home", timeout=10000)
    
    yield browser_instance