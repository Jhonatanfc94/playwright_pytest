import pytest
from playwright.sync_api import expect
from pytest_bdd import scenarios, given, when, then, parsers
from poms.repository import RepositoryPage

scenarios('../features/repository_scenario.feature')

@pytest.fixture
def shared_data():
    return {}

@given(parsers.parse('the user is on the {page_name} page'), target_fixture="browser_instance")
def navigate_to_page(browser_instance, shared_data, page_name):
    browser_instance.goto(page_name)
    repository_page = RepositoryPage(browser_instance)
    shared_data['repository_page'] = repository_page

@given('the user click on the tab repositories')
def click_repositories_tab(shared_data):
    repository_page: RepositoryPage = shared_data['repository_page']
    repository_page.repositories_tab.click()
    expect(repository_page.search_input).to_be_visible()

@when(parsers.parse('the user search {project}'))
def search_project(shared_data, project):
    repository_page: RepositoryPage = shared_data['repository_page']
    repository_page.search_input.fill(project)
    repository_page.search_input.press("Enter")

@then(parsers.parse('link to the {project} is shown in results'))
def verify_project_in_results(shared_data, project):
    repository_page: RepositoryPage = shared_data['repository_page']
    results = repository_page.get_result_links_text()
    assert any(project in result for result in results), f"Project '{project}' not found in results: {results}"