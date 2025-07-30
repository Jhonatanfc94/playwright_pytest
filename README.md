# playwright_pytest

A concise template for automated browser testing using **Playwright** + **Pytest** with Allure reporting.

---

## 📦 Requirements
- Python 3.8+
- Node.js 16+ (for Lighthouse)
- Playwright
- Pytest
- Allure (for reports)
- Scoop (for Windows, to install Allure)

---

## ⚡️ Quick Start

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
   npm install -g lighthouse
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
   locust -f .\tests\performance\locustfile.py --headless --run-time 40m --csv=resultados 
   ```
- **Performance testing with lighthouse:**
  ```bash
   pytest --alluredir=./allure-results --only-lighthouse -s
   ``
   
---

## 🤝 Contributing
1. Fork this repo
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add: your message'
   ```
4. Push and open a Pull Request

---

## 👤 Author
- **Jhonatan Flores** - [@jhonatan](https://github.com/Jhonatanfc94)