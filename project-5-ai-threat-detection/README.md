# Project 5: AI-Powered Threat Detection 🤖🔐

> **The "AI Security" Flex** — piping raw security logs through an LLM to produce boardroom-ready threat intelligence reports, mirroring tools like Microsoft Security Copilot.

## What This Does

Takes raw security logs (SSH, Apache, Windows Event) and produces a structured threat intelligence report including:

- **Executive summary** — plain English for non-technical managers
- **MITRE ATT&CK classifications** — industry-standard technique IDs for every detected event
- **Severity scoring** — 1–10 per event and overall
- **Response actions** — immediate steps to contain the threat
- **Indicators of Compromise (IOCs)** — IPs, patterns, and signatures to block

## How It Works

```
Raw Log File
     │
     ▼
threat_analyser.py
     │
     ├── Reads and preprocesses log content
     │
     ├── Sends to Claude API with SOC analyst system prompt
     │
     ├── Receives structured JSON threat analysis
     │
     └── Generates HTML threat intelligence report
```

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
# Windows
set ANTHROPIC_API_KEY=your_key_here

# Mac/Linux
export ANTHROPIC_API_KEY=your_key_here
```

### 3. Run against a sample log
```bash
# SSH brute force attack
python threat_analyser.py --log sample_logs/ssh_brute_force.log

# Web application attacks (SQLi, XSS, path traversal)
python threat_analyser.py --log sample_logs/web_attack.log

# Save HTML report to specific path
python threat_analyser.py --log sample_logs/ssh_brute_force.log --output my_report.html

# Also save raw JSON
python threat_analyser.py --log sample_logs/web_attack.log --json

# Pipe from another tool (chain with a SIEM parser)
cat /var/log/auth.log | python threat_analyser.py --stdin
```

## Sample Output

```
────────────────────────────────────────────────────────────
  THREAT LEVEL : CRITICAL
  SEVERITY     : 9/10
  EVENTS FOUND : 3
────────────────────────────────────────────────────────────

  A sustained brute force attack targeting root SSH access was detected
  from 192.168.1.105, making 20+ attempts over 8 minutes across multiple
  usernames. A second source IP (10.0.0.55) joined the attack, suggesting
  a coordinated campaign. Immediate IP blocking and MFA enforcement are
  strongly recommended.

[+] HTML report saved: threat_report_20260629_143200.html
[+] Analysis complete.
```

The HTML report includes clickable MITRE ATT&CK links for every detected technique.

## Chaining with Project 4 (SIEM Log Analyser)

These two projects form a complete detection pipeline:

```bash
# Project 4 detects and scores → Project 5 provides AI intelligence
python ../siem_analyser.py --log /var/log/auth.log | python threat_analyser.py --stdin
```

## MITRE ATT&CK Techniques Detected

| Attack Type | MITRE ID | Description |
|------------|----------|-------------|
| SSH Brute Force | T1110.001 | Brute Force: Password Guessing |
| Credential Stuffing | T1110.004 | Brute Force: Credential Stuffing |
| SQL Injection | T1190 | Exploit Public-Facing Application |
| XSS | T1059.007 | Command and Scripting: JavaScript |
| Path Traversal | T1083 | File and Directory Discovery |
| Web Reconnaissance | T1595.002 | Active Scanning: Vulnerability Scanning |

## Why This Matters

Enterprise security tools like **Microsoft Security Copilot**, **Google Chronicle AI**, and **Splunk AI** all do exactly this — take raw telemetry and use LLMs to surface actionable intelligence for human analysts. This project demonstrates the core engineering behind those tools:

- **Prompt engineering** — structuring the system prompt to elicit consistent, parseable JSON
- **LLM integration** — calling the Anthropic API and handling responses robustly
- **Security domain knowledge** — knowing what MITRE ATT&CK is and why it matters
- **Output design** — producing reports that serve both technical analysts and non-technical managers

## Prompt Engineering Notes

The system prompt is the core of this tool. Key decisions:

1. **JSON-only output** — forces structured, parseable responses; prevents the model from adding prose that breaks parsing
2. **MITRE technique IDs** — grounds the analysis in an industry-standard framework, not ad-hoc descriptions
3. **Executive summary constraint** — "3 sentences for a non-technical manager" forces concision and audience awareness
4. **Severity as integer** — avoids ambiguous qualitative labels, enables programmatic sorting and filtering

## What to Add Next

- [ ] Real-time mode: `--watch` flag to tail a live log file
- [ ] IP geolocation: enrich IOCs with country/ASN data
- [ ] Slack/email alerting for CRITICAL findings
- [ ] SQLite database to store historical reports and track recurring IOCs
- [ ] Flask web dashboard for browser-based log submission
 
