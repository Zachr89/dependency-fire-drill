"""Blast radius report generation."""

import json
from datetime import datetime
from typing import List

from jinja2 import Template
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .sandbox import TestResult


class BlastRadiusReporter:
    """Generates blast radius reports in multiple formats."""
    
    def __init__(self, results: List[TestResult]):
        self.results = results
        self.summary = self._calculate_summary()
    
    def _calculate_summary(self) -> dict:
        """Calculate summary statistics."""
        total = len(self.results)
        
        risk_counts = {
            "CRITICAL": sum(1 for r in self.results if r.risk_level == "CRITICAL"),
            "HIGH": sum(1 for r in self.results if r.risk_level == "HIGH"),
            "MEDIUM": sum(1 for r in self.results if r.risk_level == "MEDIUM"),
            "LOW": sum(1 for r in self.results if r.risk_level == "LOW"),
        }
        
        behavior_counts = {}
        for result in self.results:
            for behavior in result.behaviors:
                behavior_type = behavior.behavior_type
                behavior_counts[behavior_type] = behavior_counts.get(behavior_type, 0) + 1
        
        return {
            "total_dependencies": total,
            "risk_counts": risk_counts,
            "behavior_counts": behavior_counts,
            "scan_date": datetime.now().isoformat(),
        }
    
    def print_terminal(self, console: Console):
        """Print report to terminal using Rich."""
        
        # Summary panel
        summary_text = f"""
[bold]Total Dependencies:[/bold] {self.summary['total_dependencies']}
[bold red]Critical Risk:[/bold red] {self.summary['risk_counts']['CRITICAL']}
[bold yellow]High Risk:[/bold yellow] {self.summary['risk_counts']['HIGH']}
[bold]Medium Risk:[/bold] {self.summary['risk_counts']['MEDIUM']}
[bold green]Low Risk:[/bold green] {self.summary['risk_counts']['LOW']}
"""
        console.print(Panel(summary_text.strip(), title="🎯 Blast Radius Summary", border_style="blue"))
        
        # Risk table
        table = Table(title="\n🔍 Dependency Risk Assessment")
        table.add_column("Package", style="cyan", no_wrap=True)
        table.add_column("Version", style="magenta")
        table.add_column("Risk", justify="center")
        table.add_column("Behaviors", justify="right")
        table.add_column("Details", style="dim")
        
        # Sort by risk level
        risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_results = sorted(self.results, key=lambda r: risk_order.get(r.risk_level, 4))
        
        for result in sorted_results[:20]:  # Show top 20
            risk_color = {
                "CRITICAL": "bold red",
                "HIGH": "bold yellow",
                "MEDIUM": "yellow",
                "LOW": "green",
            }.get(result.risk_level, "white")
            
            behavior_summary = ", ".join(
                set(b.behavior_type.replace("_", " ") for b in result.behaviors)
            )[:40]
            
            table.add_row(
                result.dependency.name,
                result.dependency.version,
                f"[{risk_color}]{result.risk_level}[/{risk_color}]",
                str(len(result.behaviors)),
                behavior_summary or "No suspicious activity",
            )
        
        console.print(table)
        
        # Recommendations
        if self.summary["risk_counts"]["CRITICAL"] > 0 or self.summary["risk_counts"]["HIGH"] > 0:
            console.print("\n⚠️  [bold yellow]Recommendations:[/bold yellow]")
            console.print("  • Review high-risk dependencies immediately")
            console.print("  • Consider alternatives or vendor lock-in")
            console.print("  • Enable integrity checks (npm: package-lock.json, pip: hash-checking mode)")
            console.print("  • Use dependency scanning in CI/CD")
    
    def generate_json(self) -> dict:
        """Generate JSON report."""
        return {
            "summary": self.summary,
            "dependencies": [
                {
                    "name": r.dependency.name,
                    "version": r.dependency.version,
                    "source": r.dependency.source,
                    "risk_level": r.risk_level,
                    "execution_time": r.execution_time,
                    "error": r.error,
                    "behaviors": [
                        {
                            "type": b.behavior_type,
                            "details": b.details,
                            "risk_level": b.risk_level,
                            "timestamp": b.timestamp,
                        }
                        for b in r.behaviors
                    ],
                }
                for r in self.results
            ],
        }
    
    def generate_markdown(self) -> str:
        """Generate Markdown report."""
        template = Template("""# 🔥 Dependency Fire Drill Report

**Generated:** {{ summary.scan_date }}

## 📊 Summary

| Metric | Count |
|--------|-------|
| Total Dependencies | {{ summary.total_dependencies }} |
| 🔴 Critical Risk | {{ summary.risk_counts.CRITICAL }} |
| 🟡 High Risk | {{ summary.risk_counts.HIGH }} |
| 🟠 Medium Risk | {{ summary.risk_counts.MEDIUM }} |
| 🟢 Low Risk | {{ summary.risk_counts.LOW }} |

## 🎯 Blast Radius

{% for result in results %}
### {{ result.dependency.name }} ({{ result.dependency.version }})

**Risk Level:** {{ result.risk_level }}  
**Behaviors Detected:** {{ result.behaviors|length }}

{% if result.behaviors %}
{% for behavior in result.behaviors %}
- **{{ behavior.behavior_type }}**: {{ behavior.details }}
{% endfor %}
{% else %}
No suspicious activity detected.
{% endif %}

---
{% endfor %}

## 💡 Recommendations

{% if summary.risk_counts.CRITICAL > 0 or summary.risk_counts.HIGH > 0 %}
- ⚠️  **Immediate Action Required**: {{ summary.risk_counts.CRITICAL + summary.risk_counts.HIGH }} dependencies pose high security risk
- Review and consider alternatives for high-risk packages
- Enable dependency integrity checks (lock files with checksums)
- Implement automated security scanning in CI/CD
{% else %}
- ✅ No critical risks detected
- Continue monitoring dependencies regularly
- Keep dependencies updated
{% endif %}
""")
        
        return template.render(summary=self.summary, results=self.results)
    
    def generate_html(self) -> str:
        """Generate HTML report."""
        template = Template("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dependency Fire Drill Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }
        .stat-card.critical { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .stat-card.high { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #333; }
        .stat-card h3 { margin: 0; font-size: 14px; opacity: 0.9; }
        .stat-card p { margin: 10px 0 0; font-size: 32px; font-weight: bold; }
        .dependency { border: 1px solid #ddd; margin: 20px 0; padding: 20px; border-radius: 8px; }
        .risk-badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        .risk-critical { background: #e74c3c; color: white; }
        .risk-high { background: #f39c12; color: white; }
        .risk-medium { background: #f1c40f; color: #333; }
        .risk-low { background: #2ecc71; color: white; }
        .behavior { background: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 3px solid #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Dependency Fire Drill Report</h1>
        <p><strong>Generated:</strong> {{ summary.scan_date }}</p>
        
        <div class="summary">
            <div class="stat-card">
                <h3>Total Dependencies</h3>
                <p>{{ summary.total_dependencies }}</p>
            </div>
            <div class="stat-card critical">
                <h3>Critical Risk</h3>
                <p>{{ summary.risk_counts.CRITICAL }}</p>
            </div>
            <div class="stat-card high">
                <h3>High Risk</h3>
                <p>{{ summary.risk_counts.HIGH }}</p>
            </div>
            <div class="stat-card">
                <h3>Medium Risk</h3>
                <p>{{ summary.risk_counts.MEDIUM }}</p>
            </div>
            <div class="stat-card">
                <h3>Low Risk</h3>
                <p>{{ summary.risk_counts.LOW }}</p>
            </div>
        </div>
        
        <h2>🎯 Dependency Analysis</h2>
        
        {% for result in results %}
        <div class="dependency">
            <h3>{{ result.dependency.name }} <small>v{{ result.dependency.version }}</small></h3>
            <span class="risk-badge risk-{{ result.risk_level|lower }}">{{ result.risk_level }}</span>
            
            {% if result.behaviors %}
            <h4>Detected Behaviors ({{ result.behaviors|length }})</h4>
            {% for behavior in result.behaviors %}
            <div class="behavior">
                <strong>{{ behavior.behavior_type }}:</strong> {{ behavior.details }}
            </div>
            {% endfor %}
            {% else %}
            <p>✅ No suspicious activity detected</p>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
""")
        
        return template.render(summary=self.summary, results=self.results)
