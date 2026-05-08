# Troubleshooting Guide

Common issues and solutions for Dependency Fire Drill.

---

## Installation Issues

### `pip install dependency-fire-drill` fails

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement dependency-fire-drill
```

**Solutions:**
1. Ensure Python 3.9+: `python --version`
2. Upgrade pip: `pip install --upgrade pip`
3. Try with explicit index: `pip install --index-url https://pypi.org/simple dependency-fire-drill`

---

### Docker not found

**Symptoms:**
```
Error: Docker daemon not running or not installed
```

**Solutions:**

**macOS:**
```bash
brew install --cask docker
# Then start Docker Desktop from Applications
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER  # Avoid sudo
# Log out and back in
```

**Windows:**
- Install Docker Desktop from docker.com
- Enable WSL 2 backend in settings
- Alternatively, use native Windows sandbox (no Docker needed):
  ```bash
  fire-drill scan --sandbox-backend windows
  ```

---

## Permission Errors

### Linux: "Permission denied" accessing Docker socket

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/var/run/docker.sock'
```

**Solutions:**

**Option 1: Add user to docker group (recommended)**
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

**Option 2: Use sudo (not recommended for regular use)**
```bash
sudo fire-drill scan --manifest package.json
```

**Option 3: Rootless Docker**
```bash
# Follow Docker docs for rootless setup
dockerd-rootless-setuptool.sh install
```

---

### Docker: "permission denied while trying to connect to the Docker daemon socket"

**Symptoms:**
```
docker: Got permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
Same as above — add user to `docker` group and restart session.

---

## Scan Failures

### Timeout errors on large projects

**Symptoms:**
```
TimeoutError: Dependency 'package-name' exceeded 30s timeout
```

**Solutions:**

**Increase timeout:**
```bash
fire-drill scan --timeout 120  # 2 minutes per package
```

**Enable parallel execution:**
```bash
fire-drill scan --parallel 8  # Test 8 packages simultaneously
```

**Sample large projects:**
```bash
fire-drill scan --sample 50  # Only test 50 random dependencies
```

**Quick scan mode (skip transitive deps):**
```bash
fire-drill scan --max-depth 1
```

---

### Manifest not found in monorepo

**Symptoms:**
```
Error: No manifest file found
```

**Solution:**

**Explicit path:**
```bash
fire-drill scan --manifest ./packages/my-app/package.json
```

**Search depth:**
```bash
fire-drill scan --manifest-search-depth 5  # Search up to 5 parent dirs
```

---

### Network errors during dependency installation

**Symptoms:**
```
ERROR: Could not install package 'example-pkg' - network connection failed
```

**Solutions:**

**Check Docker network:**
```bash
docker network inspect bridge
```

**Allow network access in sandbox:**
```bash
fire-drill scan --sandbox-profile permissive
```

**Configure proxy (if behind corporate firewall):**
```yaml
# .firedrillrc
sandbox:
  environment:
    HTTP_PROXY: "http://proxy.company.com:8080"
    HTTPS_PROXY: "http://proxy.company.com:8080"
```

---

## Windows-Specific Issues

### Windows Sandbox not available

**Symptoms:**
```
Error: Windows Sandbox not available on this system
```

**Requirements:**
- Windows 10 Pro/Enterprise/Education (Home edition not supported)
- Virtualization enabled in BIOS
- Windows Sandbox feature enabled

**Enable Windows Sandbox:**
1. Open "Turn Windows features on or off"
2. Check "Windows Sandbox"
3. Restart computer

**Alternative: Use Docker on Windows**
```bash
fire-drill scan --sandbox-backend docker
```

---

### Path too long errors

**Symptoms:**
```
OSError: [WinError 206] The filename or extension is too long
```

**Solution:**

Enable long paths in Windows:
```powershell
# Run as Administrator
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

Or use shorter output paths:
```bash
fire-drill scan -o C:\scan.json  # Short path
```

---

## Report Generation Issues

### HTML report charts not rendering

**Symptoms:**
HTML report opens but charts are blank

**Solution:**

Ensure internet connection (charts use CDN resources) or use offline mode:
```bash
fire-drill scan --format html --offline-mode
```

---

### JSON report too large to open

**Symptoms:**
Report file is several GB, crashes text editors

**Solution:**

Use summary mode:
```bash
fire-drill report --input large-report.json --format terminal --summary-only
```

Or query specific dependencies:
```bash
fire-drill report --input large-report.json --filter "express,lodash"
```

---

## CI/CD Integration Issues

### GitHub Actions timeout

**Symptoms:**
```
Error: The operation was canceled.
```

**Solution:**

Add timeout and sampling to workflow:
```yaml
- name: Run fire drill
  run: |
    fire-drill scan \
      --timeout 60 \
      --parallel 4 \
      --sample 100 \
      --output report.json
  timeout-minutes: 30
```

---

### CI fails with "no such file" error

**Symptoms:**
```
Error: [Errno 2] No such file or directory: 'package.json'
```

**Solution:**

Check working directory in CI:
```yaml
- name: Run fire drill
  run: fire-drill scan --manifest ./package.json
  working-directory: ./app  # If manifest is in subdirectory
```

---

## Performance Issues

### Scan is very slow

**Typical causes:**
1. Large dependency tree (100+ packages)
2. Sequential execution (default: 4 parallel)
3. Slow network (downloading packages)

**Solutions:**

**Maximize parallelism:**
```bash
fire-drill scan --parallel $(nproc)  # Linux: use all CPU cores
fire-drill scan --parallel 8         # Explicit number
```

**Cache Docker images:**
```bash
# Pre-pull language images
docker pull node:18-alpine
docker pull python:3.11-slim
```

**Use local package cache:**
```yaml
# .firedrillrc
sandbox:
  volumes:
    - ~/.npm:/root/.npm:ro          # npm cache
    - ~/.cache/pip:/root/.cache/pip:ro  # pip cache
```

**Sample large projects:**
```bash
fire-drill scan --sample 50 --max-depth 1
```

---

## False Positives

### Known-safe packages flagged as high-risk

**Example:** `webpack` flagged for file system writes (legitimate — it's a build tool)

**Solution:**

**Exclude specific packages:**
```bash
fire-drill scan --exclude "webpack,rollup,babel-*"
```

**Or use config file:**
```yaml
# .firedrillrc
exclusions:
  - "webpack"
  - "@babel/*"
  - "eslint-*"
```

**Adjust risk scoring:**
```yaml
# custom-risk.yaml
weights:
  file_write_home: 10  # Lower risk for home directory writes
```

```bash
fire-drill scan --risk-config custom-risk.yaml
```

---

## Getting Help

### Still stuck?

1. **Check logs:**
   ```bash
   fire-drill scan --debug --log-file debug.log
   cat debug.log  # Review detailed trace
   ```

2. **Search existing issues:**
   https://github.com/yourusername/dependency-fire-drill/issues

3. **Ask in Discussions:**
   https://github.com/yourusername/dependency-fire-drill/discussions

4. **Report a bug:**
   ```bash
   # Include output of:
   fire-drill --version
   docker --version
   python --version
   uname -a  # Linux/macOS
   systeminfo  # Windows
   ```

---

## Error Code Reference

| Code | Meaning | Solution |
|------|---------|----------|
| 1 | General error | Check `--debug` output |
| 2 | Manifest not found | Specify `--manifest` path |
| 3 | Docker unavailable | Install/start Docker |
| 4 | Timeout exceeded | Increase `--timeout` |
| 5 | Permission denied | Fix file/Docker permissions |
| 10 | High-risk detected (CI mode) | Review report, update deps |

---

**Last Updated:** 2025-01-XX  
**Version:** 0.2.0
