import os
import subprocess
import json
import pytest
from playwright.sync_api import Page
import sys

def run_lighthouse(page: Page) -> dict:
    """Ejecuta Lighthouse y valida contra thresholds predefinidos"""

    thresholds = {
        "performance": 0.8,
        "accessibility": 0.9,
        "best-practices": 0.9,
        "seo": 0.8
    }

    report_path = "lighthouse-report.json"
    url = page.url

    # Ruta local al ejecutable de lighthouse
    lighthouse_cmd = os.path.join("node_modules", ".bin", "lighthouse")
    if sys.platform.startswith("win"):
        lighthouse_cmd += ".cmd"

    try:
        subprocess.run(
            [lighthouse_cmd, url,
             "--output=json",
             f"--output-path={report_path}",
             "--chrome-flags=--headless --no-sandbox",
             "--quiet"],
            check=True,
            timeout=120
        )

        with open(report_path, encoding="utf-8") as f:
            report = json.load(f)

        for category, min_score in thresholds.items():
            score = report["categories"][category]["score"]
            assert score >= min_score, f"{category} score ({score:.2f}) < {min_score}"

        return report

    except Exception as e:
        pytest.fail(f"Error ejecutando Lighthouse: {str(e)}")


def test_homepage_performance(page: Page):
    page.goto("https://example.com")  # Cambia a tu URL real
    report = run_lighthouse(page)
    
    # Opcional: Adjuntar reporte a Allure
    if hasattr(pytest, "allure"):
        import allure
        allure.attach(
            json.dumps(report, indent=2),
            name="Lighthouse Report",
            attachment_type=allure.attachment_type.JSON
        )