import json
import pytest
from playwright.sync_api import Playwright, expect
import time

from poms.dashboard import DashboardPage
from poms.login import LoginPage
from poms.order_detail import OrderDetailPage
from poms.orders import OrdersPage
from utils.api_base import APIUtils

with open('data/credentials.json') as f:
    test_data = json.load(f)
    user_credentials_list = test_data['user_credentials']

@pytest.mark.smoke
@pytest.mark.parametrize('user_credentials', user_credentials_list)
def test_e2e_web_api(playwright:Playwright, browserInstance, user_credentials):
    userName = user_credentials["userEmail"]
    password = user_credentials["userPassword"]

    api_utils = APIUtils()
    orderID = api_utils.createOrder(playwright, user_credentials)
    loginPage = LoginPage(browserInstance)
    loginPage.navigate()
    loginPage.login(userName,password)
    dashboardPage = DashboardPage(browserInstance)
    dashboardPage.ordersNavLink.click()

    time.sleep(2)

    for column in range(browserInstance.locator("th").count()):
        if browserInstance.locator("th").nth(column).filter(has_text="Order Id").count()>0:
            colValue = column
            break

    ordersPage = OrdersPage(browserInstance)
    ordersPage.selectOrder(orderID)
    orderDetail = OrderDetailPage(browserInstance)
    expect(orderDetail.thankYouText).to_contain_text("Thank you for Shopping With Us")