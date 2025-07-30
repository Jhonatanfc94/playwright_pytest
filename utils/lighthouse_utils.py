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
        lighthouse_cmd = os.path.join("node_modules", ".bin", "lighthouse")
        
        if sys.platform.startswith("win"):
            lighthouse_cmd += ".cmd"

        try:
            base_name, ext = os.path.splitext(report_path)
            device_suffix = "mobile" if mobile else "desktop"
            device_report_path = f"{base_name}-{device_suffix}{ext}"
            
            subprocess.run(
                [lighthouse_cmd, url,
                 "--output=json",
                 f"--output-path={device_report_path}",
                 "--chrome-flags=--headless --no-sandbox",
                 "--quiet",
                 "--emulated-form-factor=mobile" if mobile else "--emulated-form-factor=desktop"],
                check=True,
                timeout=120
            )
            
            with open(device_report_path, encoding="utf-8") as f:
                report = json.load(f)
                
            self._print_report(report, mobile)
            return report
                
        except Exception as e:
            raise RuntimeError(f"Error ejecutando Lighthouse: {str(e)}")

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

    def _format_kb(self, bytes: int) -> str:
        return f"{round(bytes / 1024, 1)}KB" if bytes else "0KB"

    def _format_ms(self, ms: float) -> str:
        if ms > 1000:
            return f"{round(ms / 1000, 1)}s"
        return f"{round(ms, 1)}ms"
    
    def extract_optimization_opportunities(self, report: dict) -> dict:
        opportunities = {
            "high_impact": [],
            "blocking_resources": [],
            "code_issues": [],
            "seo_opportunities": []
        }
        
        if "audits" not in report:
            return opportunities

        audits = report["audits"]
        
        # Helper para añadir items con formato consistente
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
                    "Convertir a WebP/AVIF",
                    f"Ahorro potencial: {self._format_kb(savings)}",
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
                    "Optimizar compresión de imágenes",
                    f"Ahorro potencial: {self._format_kb(savings)}",
                    impact,
                    "https://web.dev/uses-optimized-images/"
                )

        # Recursos bloqueantes
        if "render-blocking-resources" in audits:
            opp = audits["render-blocking-resources"]
            items = opp.get("details", {}).get("items", [])
            for item in items[:3]:  # Limitar a los 3 principales
                savings = item.get("wastedMs", 0)
                if savings > 0:
                    impact = self._get_impact_level(savings, "ms")
                    add_opportunity(
                        "blocking_resources",
                        f"Recurso bloqueante: {self._shorten_url(item.get('url', ''))}",
                        f"Tiempo ahorrable: {self._format_ms(savings)}",
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
                    "JavaScript no utilizado",
                    f"Ahorro potencial: {self._format_kb(savings)}",
                    impact,
                    "https://web.dev/unused-javascript/"
                )

        # SEO
        if "meta-description" in audits:
            opp = audits["meta-description"]
            if opp.get("score", 1) < 1:
                add_opportunity(
                    "seo_opportunities",
                    "Meta descripción faltante",
                    "Mejora potencial en posicionamiento SEO",
                    "medium",
                    "https://web.dev/meta-description/"
                )

        return opportunities

    def _get_impact_level(self, value: float, metric: str) -> str:
        thresholds = {
            "bytes": {"high": 500*1024, "medium": 100*1024},
            "ms": {"high": 1000, "medium": 300}
        }
        if value > thresholds[metric]["high"]:
            return "high"
        elif value > thresholds[metric]["medium"]:
            return "medium"
        return "low"

    def _shorten_url(self, url: str) -> str:
        """Acorta URLs largas para mejor visualización"""
        return url.split('/')[-1][:30] + ('...' if len(url) > 30 else '')

    def generate_insights_slide(self, report: dict) -> str:
        opportunities = self.extract_optimization_opportunities(report)
        
        # Emojis para cada nivel de impacto
        impact_emojis = {
            "high": "🔥",
            "medium": "⚠️",
            "low": "🔹"
        }
        
        slide = "# Lighthouse Insights\n\n"
        
        # Sección de alto impacto
        if opportunities["high_impact"]:
            slide += "## 🔥 Optimización Crítica (Alto Impacto)\n"
            for opp in sorted(opportunities["high_impact"], 
                             key=lambda x: x["impact"], reverse=True):
                emoji = impact_emojis.get(opp["impact"], "🔹")
                slide += f"- **{opp['title']}**  \n"
                slide += f"  - {opp['details']} {emoji} {opp['impact'].capitalize()}\n"
                if opp["reference"]:
                    slide += f"  - ▶️ {opp['reference']}\n"
            slide += "\n"
        
        # Recursos bloqueantes
        if opportunities["blocking_resources"]:
            slide += "## ⏱️ Recursos Bloqueantes\n"
            for opp in opportunities["blocking_resources"]:
                emoji = impact_emojis.get(opp["impact"], "🔹")
                slide += f"- **{opp['title']}**  \n"
                slide += f"  - {opp['details']} {emoji}\n"
                if opp["reference"]:
                    slide += f"  - ▶️ {opp['reference']}\n"
            slide += "\n"
        
        # Otras recomendaciones
        if opportunities["code_issues"] or opportunities["seo_opportunities"]:
            slide += "## 🛠️ Otras Recomendaciones\n"
            
            for opp in opportunities["code_issues"]:
                slide += f"- **{opp['title']}**  \n"
                slide += f"  - {opp['details']}\n"
                if opp["reference"]:
                    slide += f"  - ▶️ {opp['reference']}\n"
            
            for opp in opportunities["seo_opportunities"]:
                slide += f"- **{opp['title']}**  \n"
                slide += f"  - {opp['details']}\n"
                if opp["reference"]:
                    slide += f"  - ▶️ {opp['reference']}\n"
        
        return slide