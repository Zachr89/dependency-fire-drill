"""CLI entry point for dependency fire drill."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from .scanner import DependencyScanner
from .sandbox import SandboxRunner
from .reporter import BlastRadiusReporter

console = Console()


@click.group()
@click.version_option()
def main():
    """Simulate supply chain attacks on your project's dependencies.
    
    Shows what file system, network, and environment access each dependency
    could exploit if compromised.
    """
    pass


@main.command()
@click.option(
    "--manifest",
    type=click.Path(exists=True, path_type=Path),
    help="Path to package.json or requirements.txt (auto-detected if not specified)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file for JSON report (default: prints to stdout)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "markdown", "html", "terminal"]),
    default="terminal",
    help="Output format",
)
@click.option(
    "--timeout",
    type=int,
    default=30,
    help="Timeout in seconds for each dependency test",
)
@click.option(
    "--max-depth",
    type=int,
    default=1,
    help="Maximum dependency tree depth to scan (1 = direct deps only)",
)
@click.option(
    "--sample",
    type=int,
    help="Only test a random sample of N dependencies (useful for large projects)",
)
@click.option(
    "--ci",
    is_flag=True,
    help="CI mode: exit with code 1 if any high-risk behaviors detected",
)
def scan(
    manifest: Optional[Path],
    output: Optional[Path],
    format: str,
    timeout: int,
    max_depth: int,
    sample: Optional[int],
    ci: bool,
):
    """Scan dependencies and generate blast radius report."""
    
    console.print("[bold blue]🔥 Dependency Fire Drill[/bold blue]")
    console.print("Simulating supply chain attacks...\n")
    
    # Auto-detect manifest if not specified
    if not manifest:
        for candidate in ["package.json", "requirements.txt", "Pipfile", "pyproject.toml"]:
            path = Path.cwd() / candidate
            if path.exists():
                manifest = path
                break
        
        if not manifest:
            console.print("[red]❌ No manifest file found. Specify with --manifest[/red]")
            sys.exit(1)
    
    console.print(f"📋 Scanning manifest: [cyan]{manifest}[/cyan]\n")
    
    # Scan dependencies
    scanner = DependencyScanner(manifest, max_depth=max_depth)
    dependencies = scanner.scan()
    
    if sample and len(dependencies) > sample:
        import random
        dependencies = random.sample(dependencies, sample)
        console.print(f"🎲 Sampled {sample} of {len(dependencies)} dependencies\n")
    
    console.print(f"Found [bold]{len(dependencies)}[/bold] dependencies to test\n")
    
    # Run sandbox tests
    runner = SandboxRunner(timeout=timeout)
    results = []
    
    with console.status("[bold green]Running security tests...") as status:
        for i, dep in enumerate(dependencies, 1):
            status.update(f"[bold green]Testing {i}/{len(dependencies)}: {dep.name}")
            result = runner.test_dependency(dep)
            results.append(result)
    
    # Generate report
    reporter = BlastRadiusReporter(results)
    
    if format == "terminal":
        reporter.print_terminal(console)
    elif format == "json":
        report = reporter.generate_json()
        if output:
            output.write_text(json.dumps(report, indent=2))
            console.print(f"\n✅ Report saved to [cyan]{output}[/cyan]")
        else:
            print(json.dumps(report, indent=2))
    elif format == "markdown":
        report = reporter.generate_markdown()
        if output:
            output.write_text(report)
            console.print(f"\n✅ Report saved to [cyan]{output}[/cyan]")
        else:
            print(report)
    elif format == "html":
        report = reporter.generate_html()
        if output:
            output.write_text(report)
            console.print(f"\n✅ Report saved to [cyan]{output}[/cyan]")
        else:
            print(report)
    
    # CI mode: fail if high-risk behaviors detected
    if ci:
        high_risk_count = sum(1 for r in results if r.risk_level == "HIGH")
        if high_risk_count > 0:
            console.print(f"\n[red]❌ CI FAIL: {high_risk_count} high-risk dependencies detected[/red]")
            sys.exit(1)
        else:
            console.print("\n[green]✅ CI PASS: No high-risk dependencies[/green]")


@main.command()
def init():
    """Initialize fire drill config in current project."""
    
    config_path = Path.cwd() / ".firedrill.yml"
    
    if config_path.exists():
        console.print("[yellow]⚠️  .firedrill.yml already exists[/yellow]")
        return
    
    config_template = """# Dependency Fire Drill Configuration

# Maximum dependency tree depth to scan
max_depth: 1

# Timeout for each dependency test (seconds)
timeout: 30

# Risk thresholds
thresholds:
  file_access: 5      # Max number of files accessed outside package dir
  network_calls: 3    # Max number of external network calls
  env_vars: 2         # Max number of environment variables accessed

# Allowlist patterns (dependencies that won't be tested)
allowlist:
  - "^typing-extensions$"
  - "^certifi$"

# Paths to exclude from file access monitoring
exclude_paths:
  - "/tmp/"
  - "/dev/"
  - ".pyc"
"""
    
    config_path.write_text(config_template)
    console.print(f"✅ Created [cyan].firedrill.yml[/cyan]")
    console.print("\nEdit the config file to customize security thresholds.")


if __name__ == "__main__":
    main()
