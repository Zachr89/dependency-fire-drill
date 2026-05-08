# dependency-fire-drill

Simulate supply chain attacks on your dependencies. See exactly what each package can access—and fix it before it becomes real.

## What is this?

dependency-fire-drill is a CLI security tool that sandboxes your project dependencies and measures their potential blast radius. It reveals what file system, network, and environment data each package could access if compromised. Perfect for DevSecOps teams managing supply chain risk in npm, PyPI, and other ecosystems.

## Features

- **Sandboxed execution** — Run dependency code in isolated environments to safely detect malicious capabilities
- **Blast radius reporting** — Quantify which dependencies have access to secrets, source code, or network
- **Multi-language support** — Analyze Node.js (npm) and Python (PyPI) projects
- **CI/CD integration** — Generate actionable reports for automated security gates
- **Risk scoring** — Prioritize remediation by attack surface area
- **Comparison mode** — Track risk changes across versions and commits

## Quick Start

### Installation

```bash
pip install dependency-fire-drill
```

### Basic Usage

```bash
# Scan your project
dfd scan

# Generate a blast radius report
dfd report --format html --output report.html

# Compare risk between two dependency states
dfd compare old-lockfile.json new-lockfile.json
```

### For Node.js Projects

```bash
dfd scan --manifest package.json --lock package-lock.json
```

### For Python Projects

```bash
dfd scan --manifest requirements.txt
dfd scan --manifest pyproject.toml
```

## Usage Examples

**View what each dependency can access:**
```bash
dfd scan --verbose
```

**Generate compliance-ready PDF report:**
```bash
dfd report --format pdf --threshold high
```

**Fail CI if risky dependencies detected:**
```bash
dfd scan --fail-on-risk-score 70
```

**Track risk regression across releases:**
```bash
dfd compare v1.0.0-lockfile.json v1.1.0-lockfile.json --report
```

## Tech Stack

- **Language**: Python 3.9+
- **Sandboxing**: Container-based isolation (Docker/system namespaces)
- **Reporting**: Jinja2 templating, PDF/HTML output
- **CLI**: Click framework
- **Testing**: pytest

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — System design and sandboxing strategy
- [Troubleshooting](docs/TROUBLESHOOTING.md) — Common issues and solutions
- [Roadmap](ROADMAP.md) — Planned features and improvements

## License

MIT