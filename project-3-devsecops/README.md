# Project 3: Automated DevSecOps Pipeline 🚀

> **The "Engineering Flex"** — proving I can build the automated security gates that protect production systems at every stage of the development cycle.

## What This Implements

A full "shift-left" security pipeline that runs automatically on every `git push`. Five security stages gate the code before it can reach production:

```
git push
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  1. 🔑  Gitleaks     — Secrets Detection            │
│  2. 🔍  Bandit       — Python SAST                  │
│  3. 📦  pip-audit    — Dependency CVE Scan          │
│  4. 🐳  Trivy        — Container Image Scan         │
│  5. 🏗️  Checkov      — Dockerfile / IaC Scan        │
│                                                     │
│  ✅  Security Gate — blocks deploy on failure       │
└─────────────────────────────────────────────────────┘
```

---

## Pipeline Stages Explained

### 1. Secrets Detection (Gitleaks)
Scans the **entire git history** for accidentally committed secrets — API keys, passwords, tokens. Catches what code review misses. Fatal on any finding.

### 2. SAST — Bandit
Static analysis of Python code for known vulnerability patterns:
- Hardcoded passwords / credentials
- Use of weak cryptographic algorithms (MD5, SHA1)
- SQL injection risks
- Use of `subprocess` with shell=True
- Insecure use of `pickle`, `yaml.load`, `eval`

Pipeline fails on any **HIGH** severity finding.

### 3. Dependency Scanning (pip-audit)
Checks every package in `requirements.txt` against the **OSV vulnerability database**. Catches the "Log4Shell" style supply-chain attacks before deployment.

### 4. Container Scanning (Trivy)
Scans the built Docker image for **CVEs in OS packages and language dependencies** at the image layer level. Reports uploaded to GitHub's Security tab as SARIF. Blocks on CRITICAL/HIGH findings.

### 5. IaC Scanning (Checkov)
Analyses the `Dockerfile` for security misconfigurations:
- Running as root
- Exposing unnecessary ports
- Missing `USER` instruction
- Pulling from `latest` (unpinned) tags

---

## How to Set It Up

### 1. Create the Repo
```bash
git init
git add .
git commit -m "feat: initial DevSecOps pipeline"
git remote add origin https://github.com/YOUR_USERNAME/cybersecurity-portfolio.git
git push -u origin main
```

### 2. Enable GitHub Actions
GitHub Actions runs automatically on push. No configuration needed — the workflow file at `.github/workflows/security.yml` is auto-detected.

### 3. Watch It Run
Go to your repo → **Actions** tab → watch each security stage execute in parallel.

---

## Key Concepts

### "Shifting Left"
Traditionally, security was checked right before deployment (far *right* in the timeline). "Shifting left" means catching issues at the *earliest* point — when a developer pushes code — making fixes 10–100x cheaper than finding them in production.

### Security as Code
Every security policy in this pipeline is defined in a YAML file under version control. It's auditable, reviewable, and reproducible — unlike manual security checklists.

### The Security Gate
The final `security-gate` job aggregates all results. If any critical scanner fails, the gate blocks the deployment. This is the enforcement mechanism that makes the policy real.
