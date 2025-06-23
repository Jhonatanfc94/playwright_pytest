import pytest
from playwright.sync_api import expect
from pytest_bdd import given, when, then, parsers, scenarios

from poms.dashboard import DashboardPage
from poms.login import LoginPage
from poms.order_detail import OrderDetailPage
from poms.orders import OrdersPage
from utils.api_testing import APIUtils

scenarios('../features/orderTransaction.feature')

@pytest.fixture
def shared_data():
    return {}

@given(parsers.parse('place the item order with {username} and {password}'))
def place_item_order(playwright, username, password, shared_data):
    user_credentials={}
    user_credentials['userEmail'] = username
    user_credentials['userPassword'] = password
    api_utils = APIUtils()
    orderID = api_utils.createOrder(playwright, user_credentials)
    shared_data['order_id']=orderID

@given('the user is on landing plage')
def user_on_landing_page(browserInstance, shared_data):
    loginPage = LoginPage(browserInstance)
    loginPage.navigate()
    shared_data['login_page'] = loginPage

@when(parsers.parse('I login to portal with {username} and {password}'))
def login_to_portal(username,password, shared_data):
    loginPage = shared_data['login_page']
    loginPage.login(username, password)

@when('navigate to orders page')
def navigate_tp_orders_page(browserInstance):
    dashboardPage = DashboardPage(browserInstance)
    dashboardPage.ordersNavLink.click()

@when('select the orderId')
def navigate_tp_orders_page(browserInstance, shared_data):
    ordersPage = OrdersPage(browserInstance)
    ordersPage.selectOrder(shared_data['order_id'])

@then('order message is successfully displayed')
def order_message_sucessfully_displayed(browserInstance):
    orderDetail = OrderDetailPage(browserInstance)
    expect(orderDetail.thankYouText).to_contain_text("Thank you for Shopping With Us")