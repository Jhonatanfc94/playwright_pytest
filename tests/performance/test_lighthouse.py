import json
import pytest
from playwright.sync_api import Page
from utils.lighthouse_utils import LighthouseRunner

URLS_TO_TEST = [
    "https://www.petwiseworld.org/#/"
]

@pytest.mark.lighthouse
@pytest.mark.parametrize("url", URLS_TO_TEST)
def test_lighthouse_scores(page: Page, url):
    page.goto(url)
    runner = LighthouseRunner(page)
    reports = runner.run_mobile_and_desktop_audits()

    for device, report in reports.items():
        insights = runner.generate_insights_slide(report)
        print(f"\nInsights for {device}:\n")
        print(insights)
        runner.validate_thresholds(report)

    if hasattr(pytest, "allure"):
        import allure
        for device, report in reports.items():
            allure.attach(
                json.dumps(report, indent=2),
                name=f"Lighthouse Report ({device}) - {url}",
                attachment_type=allure.attachment_type.JSON
            )