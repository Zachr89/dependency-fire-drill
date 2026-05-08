# Dependency Fire Drill Roadmap

## Version 0.2.0 (Current Release) ✅
**Focus:** Issue backlog cleanup, core stability

- ✅ Full Windows support (native sandbox)
- ✅ Monorepo/workspace detection
- ✅ Risk scoring system
- ✅ HTML report generation
- ✅ Comparison mode (track changes over time)
- ✅ Config file support
- ✅ Parallel execution
- ✅ Verbose logging
- ✅ Dependency graph visualization
- ✅ Custom sandbox profiles
- ✅ Exclusion patterns

---

## Version 0.3.0 (Q2 2025) 🚧
**Focus:** Multi-language expansion, caching

### New Language Support
- **Ruby (Bundler/Gemfile)** — Community contribution welcome
  - Parser for `Gemfile.lock`
  - Docker image: `ruby:3.2-alpine`
  - Gem installation via `bundle install`
  
- **Go (go.mod)** — Community contribution welcome
  - Parser for `go.mod` + `go.sum`
  - Docker image: `golang:1.21-alpine`
  - Module installation via `go mod download`

### Performance Improvements
- **Result caching** — Skip re-testing unchanged package@version combinations
  - Cache key: `{package_name}@{version}@{sandbox_profile_hash}`
  - Storage: SQLite database in `~/.fire-drill/cache/`
  - CLI flag: `--no-cache` to force re-scan
  
- **Incremental scanning** — Only test new/updated dependencies
  - Compare current manifest with previous scan
  - Reuse cached results for unchanged deps

### Enhanced Reporting
- **SBOM export** — Generate SPDX/CycloneDX software bill of materials
  - Includes risk scores as custom properties
  - CLI: `fire-drill sbom --format spdx --output sbom.json`

---

## Version 0.4.0 (Q3 2025) 🔮
**Focus:** Advanced security features, integrations

### Static + Dynamic Analysis
- **Hybrid scanning** — Combine static code analysis with runtime testing
  - Integrate with Semgrep/CodeQL for pre-execution checks
  - Correlate static findings with observed behaviors
  - Flag discrepancies (e.g., code suggests network access but none observed)

### Threat Intelligence Integration
- **Known malicious package detection**
  - Check packages against public malware databases
  - OSV.dev integration for vulnerability data
  - npm/PyPI advisory feeds

### Honeypot Mode
- **Simulate sensitive data** to detect exfiltration attempts
  - Create fake `.env` files with tracking tokens
  - Monitor network requests containing honeypot data
  - Alert on credential harvesting behavior

### GitHub Integration
- **GitHub Advanced Security integration**
  - Export results to GitHub Security tab
  - Block PRs that introduce high-risk dependencies
  - Scheduled scans via GitHub Actions cron

---

## Version 0.5.0 (Q4 2025) 🔮
**Focus:** Enterprise features, machine learning

### Enterprise Features
- **Multi-project dashboards**
  - Centralized view of all scanned projects
  - Trend analysis (risk over time)
  - Organization-wide policy enforcement

- **SSO/RBAC** for team collaboration
  - Authenticate via SAML/OIDC
  - Role-based access to scan results
  - Audit logging for compliance

### Machine Learning
- **Anomaly detection** — Flag unusual behaviors automatically
  - Train on corpus of known-safe packages
  - Detect outlier behaviors (e.g., crypto mining patterns)
  - Adaptive risk scoring based on ecosystem norms

### Policy as Code
- **Define security policies in YAML**
  ```yaml
  policies:
    - rule: no_system_writes
      condition: file_write_system > 0
      action: block
      severity: critical
  ```

---

## Community Requests (Backlog)

### Language Support Requests
- **Rust (Cargo.toml)** — 12 upvotes
- **PHP (composer.json)** — 8 upvotes
- **.NET (packages.config / .csproj)** — 6 upvotes

### Feature Requests
- **Docker image scanning** — Marked as wontfix (use Trivy instead)
- **VSCode extension** — Investigating feasibility
- **Slack/Discord notifications** — Planned for v0.4.0

---

## Contributing to the Roadmap

We welcome community input! To propose features:

1. **Check existing issues:** https://github.com/yourusername/dependency-fire-drill/issues
2. **Open a feature request:** Use the "Feature Request" template
3. **Vote with 👍 reactions** on issues you want prioritized
4. **Submit PRs** for items marked "Community contribution welcome"

### Contribution Guidelines
- Language support PRs must include:
  - Manifest parser implementation
  - Docker image configuration
  - Unit tests with example projects
  - Documentation updates

- Major features require RFC (Request for Comments) discussion before implementation

---

## Release Schedule

- **Minor versions (0.x.0):** Quarterly
- **Patch versions (0.x.y):** As needed for bug fixes
- **LTS support:** TBD (will announce when project reaches 1.0)

---

**Last Updated:** 2025-01-XX  
**Maintainers:** @yourusername  
**License:** MIT
