"""Tests for sandbox runner."""

import pytest

from dependency_fire_drill.scanner import Dependency
from dependency_fire_drill.sandbox import SandboxRunner, TestResult


def test_subprocess_fallback():
    """Test subprocess fallback when Docker unavailable."""
    runner = SandboxRunner(timeout=5)
    runner.use_docker = False  # Force subprocess mode
    
    # Test with a mock dependency
    dep = Dependency(name="requests", version="2.28.0", source="pypi")
    result = runner.test_dependency(dep)
    
    assert isinstance(result, TestResult)
    assert result.dependency == dep
    assert result.execution_time >= 0


def test_risk_calculation():
    """Test risk level calculation."""
    result = TestResult(
        dependency=Dependency(name="test", version="1.0", source="npm")
    )
    
    # No behaviors = LOW
    result.calculate_risk()
    assert result.risk_level == "LOW"
    
    # Add behaviors to increase risk
    from dependency_fire_drill.sandbox import SecurityBehavior
    import time
    
    # Many file accesses = higher risk
    for i in range(15):
        result.behaviors.append(
            SecurityBehavior(
                behavior_type="file_access",
                details=f"Accessed /etc/file{i}",
                timestamp=time.time()
            )
        )
    
    result.calculate_risk()
    assert result.risk_level in ["HIGH", "CRITICAL"]
