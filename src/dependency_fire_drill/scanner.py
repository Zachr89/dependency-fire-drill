"""Dependency manifest scanner."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set
import tomli


@dataclass
class Dependency:
    """Represents a project dependency."""
    
    name: str
    version: str
    source: str  # "npm", "pypi", etc.
    depth: int = 1  # Depth in dependency tree


class DependencyScanner:
    """Scans project manifests for dependencies."""
    
    def __init__(self, manifest_path: Path, max_depth: int = 1):
        self.manifest_path = manifest_path
        self.max_depth = max_depth
        self.manifest_type = self._detect_type()
    
    def _detect_type(self) -> str:
        """Detect manifest type from file name."""
        name = self.manifest_path.name
        
        if name == "package.json":
            return "npm"
        elif name in ("requirements.txt", "Pipfile", "pyproject.toml"):
            return "python"
        else:
            raise ValueError(f"Unsupported manifest type: {name}")
    
    def scan(self) -> List[Dependency]:
        """Scan manifest and return list of dependencies."""
        if self.manifest_type == "npm":
            return self._scan_npm()
        elif self.manifest_type == "python":
            return self._scan_python()
        else:
            raise ValueError(f"Unknown manifest type: {self.manifest_type}")
    
    def _scan_npm(self) -> List[Dependency]:
        """Scan package.json for npm dependencies."""
        data = json.loads(self.manifest_path.read_text())
        dependencies = []
        
        for dep_type in ["dependencies", "devDependencies"]:
            if dep_type in data:
                for name, version in data[dep_type].items():
                    # Clean version string
                    version = version.lstrip("^~>=<")
                    dependencies.append(
                        Dependency(name=name, version=version, source="npm", depth=1)
                    )
        
        return dependencies
    
    def _scan_python(self) -> List[Dependency]:
        """Scan Python manifest for dependencies."""
        dependencies = []
        
        if self.manifest_path.name == "requirements.txt":
            dependencies = self._scan_requirements_txt()
        elif self.manifest_path.name == "pyproject.toml":
            dependencies = self._scan_pyproject_toml()
        
        return dependencies
    
    def _scan_requirements_txt(self) -> List[Dependency]:
        """Parse requirements.txt."""
        dependencies = []
        content = self.manifest_path.read_text()
        
        for line in content.splitlines():
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            
            # Parse package name and version
            match = re.match(r"^([a-zA-Z0-9_-]+)([><=!]+)?([\d.]+)?", line)
            if match:
                name = match.group(1)
                version = match.group(3) or "latest"
                dependencies.append(
                    Dependency(name=name, version=version, source="pypi", depth=1)
                )
        
        return dependencies
    
    def _scan_pyproject_toml(self) -> List[Dependency]:
        """Parse pyproject.toml."""
        dependencies = []
        
        with open(self.manifest_path, "rb") as f:
            data = tomli.load(f)
        
        # Check [project.dependencies]
        if "project" in data and "dependencies" in data["project"]:
            for dep_spec in data["project"]["dependencies"]:
                # Parse "package>=1.0.0" format
                match = re.match(r"^([a-zA-Z0-9_-]+)([><=!]+)?([\d.]+)?", dep_spec)
                if match:
                    name = match.group(1)
                    version = match.group(3) or "latest"
                    dependencies.append(
                        Dependency(name=name, version=version, source="pypi", depth=1)
                    )
        
        return dependencies
