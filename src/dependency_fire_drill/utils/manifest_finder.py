"""Manifest file discovery for monorepo and multi-project structures."""

from pathlib import Path
from typing import List, Optional, Tuple


class ManifestFinder:
    """Smart manifest file discovery with monorepo support."""
    
    MANIFEST_FILES = [
        "package.json",
        "requirements.txt",
        "Pipfile",
        "pyproject.toml",
        "go.mod",
        "Gemfile",
    ]
    
    WORKSPACE_INDICATORS = [
        "lerna.json",
        "pnpm-workspace.yaml",
        "rush.json",
        "nx.json",
    ]
    
    def __init__(self, start_dir: Optional[Path] = None, max_depth: int = 3):
        """Initialize manifest finder.
        
        Args:
            start_dir: Directory to start search from (default: cwd)
            max_depth: Maximum directory levels to search upward
        """
        self.start_dir = start_dir or Path.cwd()
        self.max_depth = max_depth
    
    def find_manifests(self) -> List[Path]:
        """Find all manifest files starting from start_dir.
        
        Returns:
            List of manifest file paths found
        """
        manifests = []
        
        # Search current directory
        manifests.extend(self._search_directory(self.start_dir))
        
        # Search parent directories (for monorepo detection)
        current = self.start_dir
        for _ in range(self.max_depth):
            parent = current.parent
            if parent == current:  # Reached root
                break
            manifests.extend(self._search_directory(parent))
            current = parent
        
        return list(set(manifests))  # Remove duplicates
    
    def find_primary_manifest(self) -> Optional[Path]:
        """Find the most relevant manifest file.
        
        Returns:
            Path to primary manifest, or None if not found
        """
        # First check current directory
        for manifest_name in self.MANIFEST_FILES:
            path = self.start_dir / manifest_name
            if path.exists():
                return path
        
        # Check if we're in a monorepo workspace
        workspace_root = self._find_workspace_root()
        if workspace_root:
            for manifest_name in self.MANIFEST_FILES:
                path = workspace_root / manifest_name
                if path.exists():
                    return path
        
        return None
    
    def is_monorepo(self) -> bool:
        """Check if current project is part of a monorepo.
        
        Returns:
            True if workspace indicators found
        """
        return self._find_workspace_root() is not None
    
    def _search_directory(self, directory: Path) -> List[Path]:
        """Search single directory for manifest files.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of manifest files found in directory
        """
        manifests = []
        for manifest_name in self.MANIFEST_FILES:
            path = directory / manifest_name
            if path.exists():
                manifests.append(path)
        return manifests
    
    def _find_workspace_root(self) -> Optional[Path]:
        """Find monorepo workspace root.
        
        Returns:
            Path to workspace root, or None if not in workspace
        """
        current = self.start_dir
        for _ in range(self.max_depth):
            for indicator in self.WORKSPACE_INDICATORS:
                if (current / indicator).exists():
                    return current
            
            parent = current.parent
            if parent == current:  # Reached root
                break
            current = parent
        
        return None
