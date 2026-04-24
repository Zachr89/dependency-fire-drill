# dependency-fire-drill

Simulate supply chain attacks on your dependencies. See exactly what a compromised package can access.

## What is this?

`dependency-fire-drill` is a security auditing CLI that sandboxes your project dependencies and logs their file system, network, and environment access attempts. It generates actionable "blast radius" reports showing the real attack surface of your dependency tree—helping you understand and mitigate supply chain attack risks before they happen.

## Features

- **Sandboxed execution** – Isolates each dependency in a monitored runtime environment
- **Comprehensive access logging** – Tracks file system reads/writes, network connections, and environment variable access
- **Multi-language support** – Audits npm (JavaScript) and PyPI (Python) dependencies
- **Blast radius reports** – JSON and human-readable output showing attack surface per dependency
- **CI/CD ready** – GitHub Actions integration and machine-parseable output formats
- **Zero-trust inspection** – No assumptions; test what dependencies actually do, not what they claim

## Quick Start

### Installation

```bash
pip install dependency-fire-drill
```

### Basic Usage

```bash
# Audit a Node.js project
dependency-fire-drill audit --package-json ./package.json --output report.json

# Audit a Python project
dependency-fire-drill audit --requirements ./requirements.txt --output report.json

# View a formatted report
dependency-fire-drill report --input report.json --format human
```

### CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
- name: Run dependency fire drill
  uses: your-org/dependency-fire-drill@v1
  with:
    package-file: package.json
    fail-on-high: true
```

## Usage Examples

**Scan a single package:**
```bash
dependency-fire-drill audit --package-json package.json
```

**Generate a report with risk scoring:**
```bash
dependency-fire-drill audit --package-json package.json \
  --sandbox-timeout 30 \
  --output blast-radius.json
```

**Export for security dashboard:**
```bash
dependency-fire-drill report --input blast-radius.json \
  --format json \
  --include-graph
```

The output includes:
- Per-dependency access logs (files, network IPs, env vars)
- Risk scores based on access patterns
- Dependency graph showing transitive risks
- Actionable recommendations

## Tech Stack

- **Language:** Python 3.9+
- **Sandboxing:** OS-level process isolation with syscall monitoring
- **Parsing:** npm/PyPI manifest readers
- **Output:** JSON, human-readable text, CI integrations

## License

MIT