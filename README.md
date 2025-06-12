# playwright_pytest
Template for testing projects

# Dependencies
Install dependencies:
pip install -r packages.txt
Reporting:
scoop install allure (Windows)

# 1. Execute test --headed if you want to see the browser
pytest --alluredir=./allure-results --browser_name chrome
# 2. Generate HTML report
allure generate ./allure-results -o ./allure-report --clean
# 3. Open the report
allure open ./allure-report