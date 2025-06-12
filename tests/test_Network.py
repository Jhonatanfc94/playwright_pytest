from playwright.sync_api import Playwright, Page, expect
import json
import pytest
from utils.api_base import APIUtils

fakePayloadLoadResponse = {"data":[],"message":"No Orders"}

def intercept_response(route):
    route.fulfill(
        json = fakePayloadLoadResponse
    )

def intercept_request(route):
    route.continue_(url="https://rahulshettyacademy.com/api/ecom/order/get-orders-details?id=682e2eab5d3fd9ffa0fcff10")

with open('data/credentials.json') as f:
    test_data = json.load(f)
    user_credentials_list = test_data['user_credentials']

def test_Network(page:Page):
    page.goto("https://rahulshettyacademy.com/client")
    page.route("https://rahulshettyacademy.com/api/ecom/order/get-orders-details?id=*", intercept_request)
    page.get_by_placeholder("email@example.com").fill("jhonatanfc94@gmail.com")
    page.get_by_placeholder("enter your passsword").fill("Testing1")
    page.get_by_role("button", name="Login").click()

    page.get_by_role("button", name="ORDERS").click()
    page.get_by_role("button",name="View").first.click()
    #order_text = page.locator(".mt-4").text_content()
    order_text = page.locator(".blink_me").text_content()
    print(order_text)

@pytest.mark.parametrize('user_credentials', user_credentials_list)
def test_session_storage(playwright:Playwright, browserInstance, user_credentials):
    api_utils = APIUtils()
    token = api_utils.getToken(playwright, user_credentials)
    #browser = playwright.chromium.launch(headless=False)
    browserInstance.add_init_script(f"""localStorage.setItem('token','{token}')""")
    browserInstance.goto("https://rahulshettyacademy.com/client")
    browserInstance.get_by_role("button", name="ORDERS").click()
    expect(browserInstance.get_by_text("Your Orders")).to_be_visible()