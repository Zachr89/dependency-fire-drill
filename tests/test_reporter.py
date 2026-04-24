"""Tests for report generation."""

from dependency_fire_drill.scanner import Dependency
from dependency_fire_drill.sandbox import TestResult, SecurityBehavior
from dependency_fire_drill.reporter import BlastRadiusReporter


def test_json_report():
    """Test JSON report generation."""
    results = [
        TestResult(
            dependency=Dependency(name="test-pkg", version="1.0.0", source="npm"),
            risk_level="HIGH",
        )
    ]
    
    reporter = BlastRadiusReporter(results)
    report = reporter.generate_json()
    
    assert "summary" in report
    assert "dependencies" in report
    assert report["summary"]["total_dependencies"] == 1
    assert report["summary"]["risk_counts"]["HIGH"] == 1


def test_markdown_report():
    """Test Markdown report generation."""
    results = [
        TestResult(
            dependency=Dependency(name="test-pkg", version="1.0.0", source="npm"),
            risk_level="MEDIUM",
        )
    ]
    
    reporter = BlastRadiusReporter(results)
    markdown = reporter.generate_markdown()
    
    assert "# 🔥 Dependency Fire Drill Report" in markdown
    assert "test-pkg" in markdown
    assert "MEDIUM" in markdown


def test_html_report():
    """Test HTML report generation."""
    results = [
        TestResult(
            dependency=Dependency(name="test-pkg", version="1.0.0", source="npm"),
            risk_level="LOW",
        )
    ]
    
    reporter = BlastRadiusReporter(results)
    html = reporter.generate_html()
    
    assert "<!DOCTYPE html>" in html
    assert "test-pkg" in html
    assert "LOW" in html
