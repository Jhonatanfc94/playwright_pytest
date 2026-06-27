import json
import pytest
import allure
from playwright.sync_api import Page
from utils.lighthouse_utils import LighthouseRunner

# Define URLs to audit
URLS_TO_TEST = [
    "https://example.com/", 
]

@pytest.mark.lighthouse
@pytest.mark.parametrize("url", URLS_TO_TEST)
def test_lighthouse_performance(browser_instance: Page, url):
    """
    Runs Lighthouse performance audits for both Mobile and Desktop.
    Results are attached to the Allure report.
    """
    browser_instance.goto(url)
    runner = LighthouseRunner(browser_instance)
    
    # Run both audits
    reports = runner.run_mobile_and_desktop_audits()

    # Attach results to Allure
    for device, report in reports.items():
        # Validate thresholds (optional, based on your self.thresholds)
        # runner.validate_thresholds(report)
        
        # Format insights for console output
        insights = runner.generate_insights_report(report)
        print(f"\nInsights for {device}:\n{insights}")
        
        # Attach JSON report to Allure
        allure.attach(
            json.dumps(report, indent=2),
            name=f"Lighthouse Report ({device}) - {url}",
            attachment_type=allure.attachment_type.JSON
        )
        
        # You could also generate and attach an HTML report if lighthouse was configured to output one