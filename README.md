# playwright_pytest

A template for automated testing projects using Playwright and Pytest.

---

## 📦 Dependencies

- **Python 3.8+** 🐍
- **Playwright** 🎭
- **Pytest** 🧪
- **Allure** 📊 (for beautiful test reports)
- **Scoop** (for easy Windows installs) 🪟

---
1. **Install Python dependencies:**
    ```bash
    pip install -r packages.txt
    ```
2. **Install Allure (for reporting) on Windows:**
    ```bash
    scoop install allure
    ```

---

## 🚀 Usage

### 1. Run Tests (with browser UI)
```bash
pytest --alluredir=./allure-results --browser_name chrome
```

### 2. Generate HTML Report
```bash
allure generate ./allure-results -o ./allure-report --clean
```

### 3. Open the Report
```bash
allure open ./allure-report
```

---
## 🤝 How to Contribute
1. **Fork** the project  
2. **Create your feature branch**  
   ```bash
   git checkout -b feature/your-feature-name
4. **Commit your changes**
    ```bash
   git commit -m 'Add: your meaningful commit message'
5. **Push to your branch**
    ```bash
   git push origin feature/your-feature-name
6. **Open a Pull Request**

---
## 👤 Author

- **Jhonatan Flores** - [@jhonatan](https://github.com/Jhonatanfc94)