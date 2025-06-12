Playwright + Pytest Automation Framework
Project Overview
Template for browser automation testing using Playwright and Pytest.

Author
👨‍💻 Jhonatan Flores
https://img.shields.io/badge/GitHub-Profile-blue?style=flat&logo=github

🛠️ Dependencies Installation
Python Packages
pip install -r packages.txt

Reporting Tools (Windows)
scoop install allure

� Running Tests
Basic Execution
# Run tests in headless mode (default)
pytest --alluredir=./allure-results --browser_name chrome

# Run tests with visible browser
pytest --alluredir=./allure-results --browser_name chrome --headed

📊 Generating Reports
Generate HTML report:
allure generate ./allure-results -o ./allure-report --clean
Open the report:
allure open ./allure-report