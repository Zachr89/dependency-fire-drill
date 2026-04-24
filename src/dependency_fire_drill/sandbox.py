"""Sandbox execution environment for testing dependencies."""

import json
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Set

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

from .scanner import Dependency


@dataclass
class SecurityBehavior:
    """Represents a security-relevant behavior detected during testing."""
    
    behavior_type: str  # "file_access", "network_call", "env_var_access", "process_spawn"
    details: str
    timestamp: float
    risk_level: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL


@dataclass
class TestResult:
    """Results from testing a single dependency."""
    
    dependency: Dependency
    behaviors: List[SecurityBehavior] = field(default_factory=list)
    execution_time: float = 0.0
    error: str = ""
    risk_level: str = "LOW"
    
    def calculate_risk(self):
        """Calculate overall risk level based on behaviors."""
        file_accesses = sum(1 for b in self.behaviors if b.behavior_type == "file_access")
        network_calls = sum(1 for b in self.behaviors if b.behavior_type == "network_call")
        env_accesses = sum(1 for b in self.behaviors if b.behavior_type == "env_var_access")
        process_spawns = sum(1 for b in self.behaviors if b.behavior_type == "process_spawn")
        
        # Risk scoring
        risk_score = 0
        
        if file_accesses > 10:
            risk_score += 3
        elif file_accesses > 5:
            risk_score += 2
        elif file_accesses > 0:
            risk_score += 1
        
        if network_calls > 5:
            risk_score += 3
        elif network_calls > 2:
            risk_score += 2
        elif network_calls > 0:
            risk_score += 1
        
        if env_accesses > 3:
            risk_score += 2
        elif env_accesses > 0:
            risk_score += 1
        
        if process_spawns > 0:
            risk_score += 3
        
        # Determine level
        if risk_score >= 7:
            self.risk_level = "CRITICAL"
        elif risk_score >= 5:
            self.risk_level = "HIGH"
        elif risk_score >= 3:
            self.risk_level = "MEDIUM"
        else:
            self.risk_level = "LOW"


class SandboxRunner:
    """Runs dependencies in isolated sandbox and monitors behavior."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.use_docker = DOCKER_AVAILABLE
        
        if self.use_docker:
            try:
                self.docker_client = docker.from_env()
            except Exception:
                self.use_docker = False
    
    def test_dependency(self, dep: Dependency) -> TestResult:
        """Test a single dependency in sandbox."""
        result = TestResult(dependency=dep)
        start_time = time.time()
        
        try:
            if self.use_docker:
                result = self._test_with_docker(dep)
            else:
                result = self._test_with_subprocess(dep)
        except Exception as e:
            result.error = str(e)
        
        result.execution_time = time.time() - start_time
        result.calculate_risk()
        
        return result
    
    def _test_with_docker(self, dep: Dependency) -> TestResult:
        """Test dependency using Docker sandbox."""
        result = TestResult(dependency=dep)
        
        # Create test script
        if dep.source == "npm":
            test_script = self._create_npm_test_script(dep)
            image = "node:18-alpine"
        elif dep.source == "pypi":
            test_script = self._create_python_test_script(dep)
            image = "python:3.11-alpine"
        else:
            result.error = f"Unsupported source: {dep.source}"
            return result
        
        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            script_path = tmppath / "test.sh"
            script_path.write_text(test_script)
            script_path.chmod(0o755)
            
            # Run container with monitoring
            try:
                container = self.docker_client.containers.run(
                    image,
                    command="/test/test.sh",
                    volumes={str(tmppath): {"bind": "/test", "mode": "ro"}},
                    network_mode="none",  # No network access
                    mem_limit="256m",
                    cpu_quota=50000,
                    detach=True,
                    remove=True,
                )
                
                # Wait for completion
                exit_code = container.wait(timeout=self.timeout)
                logs = container.logs().decode("utf-8")
                
                # Parse behaviors from logs
                result.behaviors = self._parse_behaviors(logs, dep)
                
            except docker.errors.ContainerError as e:
                result.error = f"Container error: {e}"
            except Exception as e:
                result.error = f"Docker error: {e}"
        
        return result
    
    def _test_with_subprocess(self, dep: Dependency) -> TestResult:
        """Fallback: test dependency using subprocess (less secure)."""
        result = TestResult(dependency=dep)
        
        # Simulate some common behaviors for demo
        # In production, this would use strace/dtrace or similar
        
        # Simulate file access behavior
        if "config" in dep.name.lower() or "env" in dep.name.lower():
            result.behaviors.append(
                SecurityBehavior(
                    behavior_type="env_var_access",
                    details="Accessed HOME, PATH environment variables",
                    timestamp=time.time(),
                    risk_level="LOW",
                )
            )
        
        # Simulate network behavior for http/request packages
        if any(x in dep.name.lower() for x in ["http", "request", "axios", "urllib"]):
            result.behaviors.append(
                SecurityBehavior(
                    behavior_type="network_call",
                    details="Attempted connection to external host",
                    timestamp=time.time(),
                    risk_level="MEDIUM",
                )
            )
        
        # Simulate file access for fs/path packages
        if any(x in dep.name.lower() for x in ["fs", "path", "file", "os"]):
            result.behaviors.append(
                SecurityBehavior(
                    behavior_type="file_access",
                    details="Read files outside package directory",
                    timestamp=time.time(),
                    risk_level="MEDIUM",
                )
            )
        
        return result
    
    def _create_npm_test_script(self, dep: Dependency) -> str:
        """Generate test script for npm package."""
        return f"""#!/bin/sh
set -e

# Install package
npm install --no-audit --no-fund {dep.name}@{dep.version}

# Import and run basic usage
node -e "const pkg = require('{dep.name}'); console.log('LOADED:', '{dep.name}');"

# Monitor would happen here - for demo, just echo
echo "FILE_ACCESS: /etc/hosts"
echo "ENV_ACCESS: HOME"
"""
    
    def _create_python_test_script(self, dep: Dependency) -> str:
        """Generate test script for Python package."""
        return f"""#!/bin/sh
set -e

# Install package
pip install --no-cache-dir {dep.name}=={dep.version}

# Import package
python -c "import {dep.name.replace('-', '_')}; print('LOADED: {dep.name}')"

# Monitor would happen here - for demo, just echo
echo "FILE_ACCESS: /etc/passwd"
echo "ENV_ACCESS: PATH"
"""
    
    def _parse_behaviors(self, logs: str, dep: Dependency) -> List[SecurityBehavior]:
        """Parse security behaviors from container logs."""
        behaviors = []
        
        for line in logs.splitlines():
            if line.startswith("FILE_ACCESS:"):
                path = line.split(":", 1)[1].strip()
                behaviors.append(
                    SecurityBehavior(
                        behavior_type="file_access",
                        details=f"Accessed {path}",
                        timestamp=time.time(),
                        risk_level="MEDIUM",
                    )
                )
            elif line.startswith("ENV_ACCESS:"):
                var = line.split(":", 1)[1].strip()
                behaviors.append(
                    SecurityBehavior(
                        behavior_type="env_var_access",
                        details=f"Read environment variable: {var}",
                        timestamp=time.time(),
                        risk_level="LOW",
                    )
                )
            elif line.startswith("NETWORK:"):
                host = line.split(":", 1)[1].strip()
                behaviors.append(
                    SecurityBehavior(
                        behavior_type="network_call",
                        details=f"Connected to {host}",
                        timestamp=time.time(),
                        risk_level="HIGH",
                    )
                )
        
        return behaviors
