"""Risk scoring engine for dependency behaviors."""

from typing import Dict, List, Any
from pathlib import Path
import yaml


class RiskScorer:
    """Calculate risk scores for dependency behaviors."""
    
    DEFAULT_WEIGHTS = {
        "file_write_system": 100,      # Writes to /etc, /usr, /var, etc.
        "file_write_home": 50,          # Writes to home directory
        "file_read_sensitive": 80,      # Reads .ssh, .aws, .env files
        "network_external": 50,         # Connections to non-localhost
        "network_suspicious": 90,       # Connections to known bad IPs
        "env_access_secrets": 80,       # Access to SECRET, TOKEN, KEY vars
        "env_access_normal": 10,        # Access to normal env vars
        "subprocess_spawn": 60,         # Spawns child processes
        "eval_usage": 70,               # Uses eval/exec
    }
    
    SYSTEM_PATHS = ["/etc", "/usr", "/var", "/bin", "/sbin", "/lib"]
    SENSITIVE_FILES = [".ssh", ".aws", ".env", ".npmrc", ".pypirc"]
    SECRET_ENV_PATTERNS = ["SECRET", "TOKEN", "KEY", "PASSWORD", "CREDENTIAL"]
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize risk scorer.
        
        Args:
            config_path: Optional path to custom risk weights YAML
        """
        self.weights = self.DEFAULT_WEIGHTS.copy()
        if config_path and config_path.exists():
            self._load_config(config_path)
    
    def score_dependency(self, test_result: Dict[str, Any]) -> int:
        """Calculate risk score for a dependency test result.
        
        Args:
            test_result: Test result dict with file_access, network_access, etc.
            
        Returns:
            Risk score from 0-100
        """
        score = 0
        max_score = 0
        
        # File access scoring
        file_writes = test_result.get("file_access", {}).get("writes", [])
        for file_path in file_writes:
            if any(file_path.startswith(sp) for sp in self.SYSTEM_PATHS):
                score += self.weights["file_write_system"]
                max_score = max(max_score, self.weights["file_write_system"])
            elif file_path.startswith("~") or file_path.startswith("/home"):
                score += self.weights["file_write_home"]
                max_score = max(max_score, self.weights["file_write_home"])
        
        file_reads = test_result.get("file_access", {}).get("reads", [])
        for file_path in file_reads:
            if any(sf in file_path for sf in self.SENSITIVE_FILES):
                score += self.weights["file_read_sensitive"]
                max_score = max(max_score, self.weights["file_read_sensitive"])
        
        # Network access scoring
        network_connections = test_result.get("network_access", [])
        for conn in network_connections:
            host = conn.get("host", "")
            if host not in ["localhost", "127.0.0.1", "::1"]:
                score += self.weights["network_external"]
                max_score = max(max_score, self.weights["network_external"])
        
        # Environment variable access
        env_accessed = test_result.get("env_access", [])
        for env_var in env_accessed:
            if any(pattern in env_var.upper() for pattern in self.SECRET_ENV_PATTERNS):
                score += self.weights["env_access_secrets"]
                max_score = max(max_score, self.weights["env_access_secrets"])
            else:
                score += self.weights["env_access_normal"]
        
        # Process spawning
        if test_result.get("subprocess_spawned", False):
            score += self.weights["subprocess_spawn"]
            max_score = max(max_score, self.weights["subprocess_spawn"])
        
        # Eval/exec usage
        if test_result.get("eval_detected", False):
            score += self.weights["eval_usage"]
            max_score = max(max_score, self.weights["eval_usage"])
        
        # Normalize to 0-100 scale (use max single violation as ceiling)
        return min(100, max_score)
    
    def get_risk_level(self, score: int) -> str:
        """Convert numeric score to risk level label.
        
        Args:
            score: Risk score 0-100
            
        Returns:
            Risk level: "LOW", "MEDIUM", "HIGH", "CRITICAL"
        """
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 30:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _load_config(self, config_path: Path):
        """Load custom risk weights from YAML file.
        
        Args:
            config_path: Path to YAML config file
        """
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        custom_weights = config.get("weights", {})
        self.weights.update(custom_weights)
