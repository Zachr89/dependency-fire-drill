"""Tests for dependency scanner."""

import json
import tempfile
from pathlib import Path

import pytest

from dependency_fire_drill.scanner import DependencyScanner, Dependency


def test_npm_scanner():
    """Test scanning package.json."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest = Path(tmpdir) / "package.json"
        manifest.write_text(json.dumps({
            "dependencies": {
                "express": "^4.18.0",
                "lodash": "~4.17.21"
            },
            "devDependencies": {
                "jest": ">=29.0.0"
            }
        }))
        
        scanner = DependencyScanner(manifest)
        deps = scanner.scan()
        
        assert len(deps) == 3
        assert any(d.name == "express" and d.version == "4.18.0" for d in deps)
        assert all(d.source == "npm" for d in deps)


def test_requirements_txt_scanner():
    """Test scanning requirements.txt."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest = Path(tmpdir) / "requirements.txt"
        manifest.write_text("""
# Comment line
requests>=2.28.0
flask==2.3.0
numpy

-e git+https://github.com/user/repo.git#egg=package
""")
        
        scanner = DependencyScanner(manifest)
        deps = scanner.scan()
        
        assert len(deps) == 3
        assert any(d.name == "requests" and d.version == "2.28.0" for d in deps)
        assert any(d.name == "flask" and d.version == "2.3.0" for d in deps)
        assert all(d.source == "pypi" for d in deps)


def test_unsupported_manifest():
    """Test error handling for unsupported manifest."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest = Path(tmpdir) / "Gemfile"
        manifest.write_text("gem 'rails'")
        
        with pytest.raises(ValueError, match="Unsupported manifest type"):
            DependencyScanner(manifest)
