import os
import subprocess
import json
import sys
from typing import Dict, Optional
from playwright.sync_api import Page

class LighthouseRunner:
    def __init__(self, page: Page, thresholds: Optional[Dict[str, float]] = None):
        self.page = page
        self.default_thresholds = {
            "performance": 0.8,
            "accessibility": 0.8,
            "best-practices": 0.8,
            "seo": 0.8
        }
        self.thresholds = thresholds or self.default_thresholds

    def run_audit(self, report_path: str = "lighthouse-report.json", mobile: bool = False) -> dict:
        url = self.page.url
        # Path to lighthouse CLI
        lighthouse_cmd = os.path.join("node_modules", ".bin", "lighthouse")
        
        if sys.platform.startswith("win"):
            lighthouse_cmd += ".cmd"

        try:
            base_name, ext = os.path.splitext(report_path)
            device_suffix = "mobile" if mobile else "desktop"
            device_report_path = f"{base_name}-{device_suffix}{ext}"
            
            result = subprocess.run(
                [lighthouse_cmd, url,
                 "--output=json",
                 f"--output-path={device_report_path}",
                 "--chrome-flags=--headless --no-sandbox",
                 "--quiet",
                 "--emulated-form-factor=mobile" if mobile else "--emulated-form-factor=desktop"],
                check=False,
                timeout=120,
                capture_output=True,
                text=True
            )
            
            if not os.path.exists(device_report_path):
                raise RuntimeError(f"Lighthouse falló y no generó reporte. Salida: {result.stderr}")
            
            with open(device_report_path, encoding="utf-8") as f:
                report = json.load(f)
                
            self._print_report(report, mobile)
            return report
                
        except Exception as e:
            raise RuntimeError(f"Error executing Lighthouse: {str(e)}")

    def _print_report(self, report: dict, mobile: bool):
        device = "Mobile" if mobile else "Desktop"
        print(f"\n{'='*40}")
        print(f"Lighthouse Results ({device})")
        print(f"URL: {report['finalUrl']}")
        print(f"{'='*40}")
        
        for category_id, category in report['categories'].items():
            score = category['score'] * 100 if category['score'] is not None else 0
            print(f"{category['title']}: {score:.0f}/100")
        
        print(f"{'='*40}\n")

    def validate_thresholds(self, report: dict):
        for category, min_score in self.thresholds.items():
            score = report["categories"][category]["score"]
            if score < min_score:
                raise AssertionError(f"{category} score ({score:.2f}) < {min_score}")

    def run_mobile_and_desktop_audits(self, report_path: str = "lighthouse-report.json"):
        print("Running Lighthouse audits...")
        mobile_report = self.run_audit(report_path, mobile=True)
        desktop_report = self.run_audit(report_path, mobile=False)
        return {"mobile": mobile_report, "desktop": desktop_report}

    # ==========================================
    # 📊 ANÁLISIS DE OPORTUNIDADES
    # ==========================================

    def _format_kb(self, bytes_val: int) -> str:
        """Formatea bytes a KB legible."""
        return f"{round(bytes_val / 1024, 1)}KB" if bytes_val else "0KB"

    def _format_ms(self, ms: float) -> str:
        """Formatea milisegundos a formato legible."""
        if ms > 1000:
            return f"{round(ms / 1000, 1)}s"
        return f"{round(ms, 1)}ms"

    def _shorten_url(self, url: str) -> str:
        """Acorta URLs largas para mejor visualización."""
        return url.split('/')[-1][:30] + ('...' if len(url) > 30 else '')

    def _get_impact_level(self, value: float, metric: str) -> str:
        """Clasifica el nivel de impacto de una oportunidad."""
        thresholds = {
            "bytes": {"high": 500*1024, "medium": 100*1024},
            "ms": {"high": 1000, "medium": 300}
        }
        if value > thresholds[metric]["high"]:
            return "high"
        elif value > thresholds[metric]["medium"]:
            return "medium"
        return "low"

    def extract_optimization_opportunities(self, report: dict) -> dict:
        """Extrae y categoriza oportunidades de optimización del reporte.

        Analiza las auditorías de Lighthouse para identificar mejoras en:
        - Imágenes (formatos modernos, compresión)
        - Recursos bloqueantes (CSS/JS que retrasan renderizado)
        - Código no utilizado (JavaScript muerto)
        - SEO (meta descripciones, etc.)

        Returns:
            dict: Oportunidades categorizadas por impacto.
        """
        opportunities = {
            "high_impact": [],
            "blocking_resources": [],
            "code_issues": [],
            "seo_opportunities": []
        }
        
        if "audits" not in report:
            return opportunities

        audits = report["audits"]
        
        def add_opportunity(category, title, details, impact, reference=None):
            entry = {
                "title": title,
                "details": details,
                "impact": impact,
                "reference": reference
            }
            opportunities[category].append(entry)

        # Análisis de imágenes
        if "modern-image-formats" in audits:
            opp = audits["modern-image-formats"]
            savings = opp.get("details", {}).get("overallSavingsBytes", 0)
            if savings > 0:
                impact = self._get_impact_level(savings, "bytes")
                add_opportunity(
                    "high_impact",
                    "Convert to WebP/AVIF",
                    f"Potential savings: {self._format_kb(savings)}",
                    impact,
                    "https://web.dev/uses-webp-images/"
                )

        if "uses-optimized-images" in audits:
            opp = audits["uses-optimized-images"]
            savings = opp.get("details", {}).get("overallSavingsBytes", 0)
            if savings > 0:
                impact = self._get_impact_level(savings, "bytes")
                add_opportunity(
                    "high_impact",
                    "Optimize image compression",
                    f"Potential savings: {self._format_kb(savings)}",
                    impact,
                    "https://web.dev/uses-optimized-images/"
                )

        # Recursos bloqueantes
        if "render-blocking-resources" in audits:
            opp = audits["render-blocking-resources"]
            items = opp.get("details", {}).get("items", [])
            for item in items[:3]:
                savings = item.get("wastedMs", 0)
                if savings > 0:
                    impact = self._get_impact_level(savings, "ms")
                    add_opportunity(
                        "blocking_resources",
                        f"Blocking resource: {self._shorten_url(item.get('url', ''))}",
                        f"Time savings: {self._format_ms(savings)}",
                        impact,
                        "https://web.dev/render-blocking-resources/"
                    )

        # Código no utilizado
        if "unused-javascript" in audits:
            opp = audits["unused-javascript"]
            savings = opp.get("details", {}).get("overallSavingsBytes", 0)
            if savings > 0:
                impact = self._get_impact_level(savings, "bytes")
                add_opportunity(
                    "code_issues",
                    "Unused JavaScript",
                    f"Potential savings: {self._format_kb(savings)}",
                    impact,
                    "https://web.dev/unused-javascript/"
                )

        # SEO
        if "meta-description" in audits:
            opp = audits["meta-description"]
            if opp.get("score", 1) < 1:
                add_opportunity(
                    "seo_opportunities",
                    "Missing meta description",
                    "Potential SEO positioning improvement",
                    "medium",
                    "https://web.dev/meta-description/"
                )

        return opportunities

    def generate_insights_report(self, report: dict) -> str:
        """Genera un reporte formateado de insights de optimización.

        Returns:
            str: Reporte en formato Markdown con emojis de impacto.
        """
        opportunities = self.extract_optimization_opportunities(report)
        
        impact_emojis = {
            "high": "🔥",
            "medium": "⚠️",
            "low": "🔹"
        }
        
        output = "# Lighthouse Insights\n\n"
        
        # High impact section
        if opportunities["high_impact"]:
            output += "## 🔥 Critical Optimization (High Impact)\n"
            for opp in sorted(opportunities["high_impact"],
                             key=lambda x: x["impact"], reverse=True):
                emoji = impact_emojis.get(opp["impact"], "🔹")
                output += f"- **{opp['title']}**\n"
                output += f"  - {opp['details']} {emoji} {opp['impact'].capitalize()}\n"
                if opp["reference"]:
                    output += f"  - ▶️ {opp['reference']}\n"
            output += "\n"
        
        # Blocking resources
        if opportunities["blocking_resources"]:
            output += "## ⏱️ Blocking Resources\n"
            for opp in opportunities["blocking_resources"]:
                emoji = impact_emojis.get(opp["impact"], "🔹")
                output += f"- **{opp['title']}**\n"
                output += f"  - {opp['details']} {emoji}\n"
                if opp["reference"]:
                    output += f"  - ▶️ {opp['reference']}\n"
            output += "\n"
        
        # Other recommendations
        if opportunities["code_issues"] or opportunities["seo_opportunities"]:
            output += "## 🛠️ Other Recommendations\n"
            
            for opp in opportunities["code_issues"]:
                output += f"- **{opp['title']}**\n"
                output += f"  - {opp['details']}\n"
                if opp["reference"]:
                    output += f"  - ▶️ {opp['reference']}\n"
            
            for opp in opportunities["seo_opportunities"]:
                output += f"- **{opp['title']}**\n"
                output += f"  - {opp['details']}\n"
                if opp["reference"]:
                    output += f"  - ▶️ {opp['reference']}\n"
        
        return output