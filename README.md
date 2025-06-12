# playwright_pytest

A template for automated testing projects using Playwright and Pytest.

---

## 📦 Dependencies

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
## 🤝 Cómo contribuir
Por favor lee [CONTRIBUTING.md](CONTRIBUTING.md) antes de hacer un PR.

# Guía de Contribución

1. Haz fork del proyecto
2. Crea tu rama (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -m 'Añade x funcionalidad'`)
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request
```

---
## 👤 Author

- **Jhonatan Flores** - [@jhonatan](https://github.com/Jhonatanfc94)