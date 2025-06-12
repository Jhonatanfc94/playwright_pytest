import time

from playwright.sync_api import Page, expect


def test_UIValidationDynamicScript(page:Page):
    page.goto("https://rahulshettyacademy.com/loginpagePractise/")
    page.get_by_label("Username:").fill("rahulshettyacademy")
    page.get_by_label("Password:").fill("learning")
    page.get_by_role("combobox").select_option("teach")
    page.locator("#terms").check()
    page.get_by_role("link", name="terms and conditions").click()
    page.get_by_role("button", name="Sign In").click()
    #expect(page.get_by_text("Incorrect username/password.")).to_be_visible()
    iphoneProduct = page.locator("app-card").filter(has_text="iphone X")
    iphoneProduct.get_by_role("button").click()
    nokiaProduct = page.locator("app-card").filter(has_text="Nokia Edge")
    nokiaProduct.get_by_role("button").click()
    page.get_by_text("Checkout").click()
    expect(page.locator(".media-body")).to_have_count(2)

def test_childWindowHandle(page:Page):
    page.goto("https://rahulshettyacademy.com/loginpagePractise/")
    with page.expect_popup() as newPage_info:
        page.locator(".blinkingText").click()
        newPage = newPage_info.value
        webElement = newPage.locator(".red")
        expect(webElement).to_contain_text("mentor@rahulshettyacademy.com")

def test_moreValidations(page:Page):
    page.goto("https://rahulshettyacademy.com/AutomationPractice/")
    expect(page.get_by_placeholder("Hide/Show Example")).to_be_visible()
    page.get_by_role("button",name="Hide").click()
    expect(page.get_by_placeholder("Hide/Show Example")).to_be_hidden()

    page.on("dialog",lambda dialog:dialog.accept())
    page.get_by_role("button", name="Confirm").click()
    time.sleep(4)

    pageFrame = page.frame_locator("#courses-iframe")
    pageFrame.get_by_role("link", name= "All Access plan").click()
    expect(pageFrame.locator("body")).to_contain_text("Happy Subscibers")

def test_childWindowHandle(page:Page):
    page.goto("https://rahulshettyacademy.com/seleniumPractise/#/offers")

    for column in range(page.locator("th").count()):
        if page.locator("th").nth(column).filter(has_text="Price").count()>0:
            colValue = column
            print(f"Price column value is {colValue}")
            break

    riceRow = page.locator("tr").filter(has_text="Rice")
    expect(riceRow.locator("td").nth(colValue)).to_have_text("37")


