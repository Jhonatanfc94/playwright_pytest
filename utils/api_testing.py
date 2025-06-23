from playwright.sync_api import Playwright
ordersPayLoad = {"orders": [{"country": "Chile", "productOrderedId": "67a8df1ac0d3e6622a297ccb"}]}

class APIUtils:
    def getToken(self, playwright:Playwright, user_credentials):

        api_request_context = playwright.request.new_context(base_url="https://rahulshettyacademy.com/")
        response = api_request_context.post("api/ecom/auth/login",
                                            data={"userEmail":user_credentials['userEmail'],
                                                     "userPassword":user_credentials['userPassword']})
        assert response.ok
        print(response.json())
        responseBody = response.json()
        return responseBody["token"]

    def createOrder(self, playwright:Playwright, user_credentials):
        token=self.getToken(playwright, user_credentials)
        api_request_context = playwright.request.new_context(base_url="https://rahulshettyacademy.com/")
        response = api_request_context.post("api/ecom/order/create-order",
                                 data= ordersPayLoad,
                                 headers={"Authorization":token,
                                          "Content-Type":"application/json"})
        response_body = response.json()
        orderID = response_body["orders"][0]
        return orderID