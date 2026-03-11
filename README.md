# playwright_pytest

A concise template for automated browser testing using **Playwright** + **Pytest** with Allure reporting.

python -m venv .venv
---
venv\Scripts\activate

## 📦 Requirements
- Python
- Node.js (for Lighthouse)
- Playwright
- Pytest
- Allure (for reports)
- Scoop (for Windows, to install Allure)

---

## ⚡️ Quick Start

python -m playwright install

1. **Install dependencies:**
   ```bash
   pip install -r packages.txt
   ```
2. **Install Allure (Windows):**
   ```bash
   scoop install allure
   ```
2. **Install Lighthouse globally:**
   ```bash
   npm install lighthouse
   ```
---

## 🚀 Running Tests

- **Run tests with browser UI:**
  ```bash
  pytest --alluredir=./allure-results --browser_name chrome
  pytest --alluredir=./allure-results --browser_name device
  pytest .\tests\name_test.py --browser_name chrome --headed 
  ```
- **Generate HTML report:**
  ```bash
  allure generate ./allure-results -o ./allure-report --clean
  allure generate ./allure-results -o ./allure-report
  ```
- **Open the report:**
  ```bash
  allure open ./allure-report
  ```
- **Performance testing with Locust:**
  ```bash
   locust -f .\tests\performance\locustfile.py --headless --run-time 3m --csv=resultados --html reporte-locust.html
   ```
- **Performance testing with lighthouse:**
  ```bash
   pytest --alluredir=./allure-results --only-lighthouse -s
   ``

## 👤 Author
- **Jhonatan Flores** - [@jhonatan](https://github.com/Jhonatanfc94)