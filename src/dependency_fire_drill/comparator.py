"""Compare dependency scan results over time."""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class DependencyDiff:
    """Represents changes to a single dependency."""
    name: str
    status: str  # "added", "removed", "changed", "unchanged"
    risk_change: int  # Positive = increased risk, negative = decreased
    new_behaviors: List[str]
    removed_behaviors: List[str]


class ReportComparator:
    """Compare two dependency scan reports."""
    
    def __init__(self, baseline_path: Path, current_path: Path):
        """Initialize comparator.
        
        Args:
            baseline_path: Path to baseline JSON report
            current_path: Path to current JSON report
        """
        with open(baseline_path) as f:
            self.baseline = json.load(f)
        
        with open(current_path) as f:
            self.current = json.load(f)
    
    def compare(self) -> Dict[str, Any]:
        """Generate comparison report.
        
        Returns:
            Dict with diff summary and per-dependency changes
        """
        baseline_deps = {d["name"]: d for d in self.baseline.get("results", [])}
        current_deps = {d["name"]: d for d in self.current.get("results", [])}
        
        diffs = []
        
        # Check for added/removed/changed dependencies
        all_dep_names = set(baseline_deps.keys()) | set(current_deps.keys())
        
        for name in sorted(all_dep_names):
            baseline_data = baseline_deps.get(name)
            current_data = current_deps.get(name)
            
            if not baseline_data:
                # Newly added dependency
                diffs.append(DependencyDiff(
                    name=name,
                    status="added",
                    risk_change=current_data.get("risk_score", 0),
                    new_behaviors=self._extract_behaviors(current_data),
                    removed_behaviors=[],
                ))
            elif not current_data:
                # Removed dependency
                diffs.append(DependencyDiff(
                    name=name,
                    status="removed",
                    risk_change=-baseline_data.get("risk_score", 0),
                    new_behaviors=[],
                    removed_behaviors=self._extract_behaviors(baseline_data),
                ))
            else:
                # Existing dependency - check for changes
                baseline_risk = baseline_data.get("risk_score", 0)
                current_risk = current_data.get("risk_score", 0)
                
                baseline_behaviors = set(self._extract_behaviors(baseline_data))
                current_behaviors = set(self._extract_behaviors(current_data))
                
                new_behaviors = list(current_behaviors - baseline_behaviors)
                removed_behaviors = list(baseline_behaviors - current_behaviors)
                
                if new_behaviors or removed_behaviors or baseline_risk != current_risk:
                    diffs.append(DependencyDiff(
                        name=name,
                        status="changed",
                        risk_change=current_risk - baseline_risk,
                        new_behaviors=new_behaviors,
                        removed_behaviors=removed_behaviors,
                    ))
                else:
                    diffs.append(DependencyDiff(
                        name=name,
                        status="unchanged",
                        risk_change=0,
                        new_behaviors=[],
                        removed_behaviors=[],
                    ))
        
        return {
            "baseline_report": str(self.baseline.get("metadata", {}).get("timestamp", "unknown")),
            "current_report": str(self.current.get("metadata", {}).get("timestamp", "unknown")),
            "summary": self._generate_summary(diffs),
            "changes": [self._diff_to_dict(d) for d in diffs if d.status != "unchanged"],
        }
    
    def has_regressions(self) -> bool:
        """Check if any dependencies have increased risk.
        
        Returns:
            True if any dependency shows increased risky behavior
        """
        comparison = self.compare()
        for change in comparison["changes"]:
            if change["risk_change"] > 0:
                return True
        return False
    
    def _extract_behaviors(self, dep_data: Dict[str, Any]) -> List[str]:
        """Extract list of risky behaviors from dependency data.
        
        Args:
            dep_data: Dependency test result dict
            
        Returns:
            List of behavior descriptions
        """
        behaviors = []
        
        # File writes to system paths
        writes = dep_data.get("file_access", {}).get("writes", [])
        if any(w.startswith("/etc") or w.startswith("/usr") for w in writes):
            behaviors.append("system_file_write")
        
        # Network access
        if dep_data.get("network_access"):
            behaviors.append("network_access")
        
        # Environment variable access
        if dep_data.get("env_access"):
            behaviors.append("env_access")
        
        # Subprocess spawning
        if dep_data.get("subprocess_spawned"):
            behaviors.append("subprocess_spawn")
        
        return behaviors
    
    def _generate_summary(self, diffs: List[DependencyDiff]) -> Dict[str, Any]:
        """Generate summary statistics.
        
        Args:
            diffs: List of dependency diffs
            
        Returns:
            Summary dict with counts
        """
        added = sum(1 for d in diffs if d.status == "added")
        removed = sum(1 for d in diffs if d.status == "removed")
        changed = sum(1 for d in diffs if d.status == "changed")
        unchanged = sum(1 for d in diffs if d.status == "unchanged")
        
        risk_increased = sum(1 for d in diffs if d.risk_change > 0)
        risk_decreased = sum(1 for d in diffs if d.risk_change < 0)
        
        return {
            "total_dependencies": len(diffs),
            "added": added,
            "removed": removed,
            "changed": changed,
            "unchanged": unchanged,
            "risk_increased": risk_increased,
            "risk_decreased": risk_decreased,
        }
    
    def _diff_to_dict(self, diff: DependencyDiff) -> Dict[str, Any]:
        """Convert DependencyDiff to dict for JSON serialization.
        
        Args:
            diff: DependencyDiff object
            
        Returns:
            Dict representation
        """
        return {
            "name": diff.name,
            "status": diff.status,
            "risk_change": diff.risk_change,
            "new_behaviors": diff.new_behaviors,
            "removed_behaviors": diff.removed_behaviors,
        }
