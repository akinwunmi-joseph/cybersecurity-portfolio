"""
AI-Powered Threat Detection & Analysis Tool
============================================
Pipes raw security logs through an LLM to produce:
- MITRE ATT&CK technique classifications
- Severity scoring (1-10)
- Plain-English executive summary
- Recommended response actions

Can be used standalone or chained with a SIEM log parser.

Usage:
    python threat_analyser.py --log sample_logs/ssh_brute_force.log
    python threat_analyser.py --log sample_logs/web_attack.log --output report.html
    python threat_analyser.py --stdin   (pipe logs from another tool)
"""

import os
import sys
import json
import argparse
import datetime
import re
from pathlib import Path

try:
    import requests
except ImportError:
    print("[!] requests library not found. Run: pip install requests")
    sys.exit(1)


# ── Configuration ─────────────────────────────────────────────────────────────

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

SOC_ANALYST_PROMPT = """You are a senior SOC (Security Operations Centre) analyst with 10 years of experience in threat detection and incident response.

You will be given raw security log data. Your job is to analyse it and return a structured threat report.

You MUST respond only with valid JSON. No preamble, no explanation outside the JSON. Use exactly this structure:

{
  "executive_summary": "3-sentence plain English summary for a non-technical manager",
  "overall_severity": <integer 1-10>,
  "threat_level": "<CRITICAL|HIGH|MEDIUM|LOW|INFO>",
  "events": [
    {
      "type": "<attack type e.g. Brute Force, SQL Injection, Port Scan>",
      "description": "<what happened in 1-2 sentences>",
      "source_ip": "<IP if present, else null>",
      "target": "<targeted user, endpoint, or service>",
      "timestamp": "<timestamp if present, else null>",
      "severity": <integer 1-10>,
      "mitre_technique_id": "<e.g. T1110.001>",
      "mitre_technique_name": "<e.g. Brute Force: Password Guessing>"
    }
  ],
  "response_actions": [
    "<immediate action 1>",
    "<immediate action 2>",
    "<immediate action 3>"
  ],
  "indicators_of_compromise": [
    "<IP, hash, domain, or pattern that should be blocked/monitored>"
  ]
}

Analyse the following logs:"""


# ── API Call ──────────────────────────────────────────────────────────────────

def analyse_logs_with_ai(log_content: str, api_key: str) -> dict:
    """Send log content to Claude and get structured threat analysis back."""

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "model": MODEL,
        "max_tokens": 2000,
        "messages": [
            {
                "role": "user",
                "content": f"{SOC_ANALYST_PROMPT}\n\n{log_content}"
            }
        ]
    }

    print("[*] Sending logs to AI analyst...")
    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        print(f"[!] API error {response.status_code}: {response.text}")
        sys.exit(1)

    data = response.json()
    raw_text = data["content"][0]["text"]

    # Strip markdown code fences if present
    raw_text = re.sub(r"```json|```", "", raw_text).strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"[!] Failed to parse AI response as JSON: {e}")
        print(f"[!] Raw response:\n{raw_text}")
        sys.exit(1)


# ── Report Generation ─────────────────────────────────────────────────────────

SEVERITY_COLOURS = {
    "CRITICAL": "#dc2626",
    "HIGH":     "#ea580c",
    "MEDIUM":   "#d97706",
    "LOW":      "#2563eb",
    "INFO":     "#6b7280",
}

def severity_badge(level: str) -> str:
    colour = SEVERITY_COLOURS.get(level.upper(), "#6b7280")
    return f'<span style="background:{colour};color:white;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600">{level}</span>'

def score_bar(score: int) -> str:
    colour = "#dc2626" if score >= 8 else "#ea580c" if score >= 6 else "#d97706" if score >= 4 else "#2563eb"
    width = score * 10
    return f'<div style="background:#e5e7eb;border-radius:4px;height:8px;width:100px;display:inline-block;vertical-align:middle"><div style="background:{colour};width:{width}%;height:100%;border-radius:4px"></div></div> <span style="font-size:13px;color:{colour};font-weight:600">{score}/10</span>'


def generate_html_report(analysis: dict, log_filename: str) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    threat_level = analysis.get("threat_level", "UNKNOWN")
    colour = SEVERITY_COLOURS.get(threat_level, "#6b7280")

    events_html = ""
    for event in analysis.get("events", []):
        events_html += f"""
        <div style="border:1px solid #e5e7eb;border-left:4px solid {colour};border-radius:6px;padding:16px;margin-bottom:12px">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <strong style="font-size:15px">{event.get('type', 'Unknown')}</strong>
                {score_bar(event.get('severity', 0))}
            </div>
            <p style="color:#374151;margin:0 0 8px;font-size:14px">{event.get('description', '')}</p>
            <table style="font-size:13px;color:#6b7280;border-collapse:collapse;width:100%">
                <tr><td style="padding:2px 12px 2px 0"><strong>Source IP</strong></td><td>{event.get('source_ip') or '—'}</td></tr>
                <tr><td style="padding:2px 12px 2px 0"><strong>Target</strong></td><td>{event.get('target') or '—'}</td></tr>
                <tr><td style="padding:2px 12px 2px 0"><strong>Timestamp</strong></td><td>{event.get('timestamp') or '—'}</td></tr>
                <tr><td style="padding:2px 12px 2px 0"><strong>MITRE ID</strong></td><td><a href="https://attack.mitre.org/techniques/{event.get('mitre_technique_id','').replace('.','/')}" target="_blank" style="color:#2563eb">{event.get('mitre_technique_id','—')}</a> — {event.get('mitre_technique_name','')}</td></tr>
            </table>
        </div>"""

    actions_html = "".join(
        f'<li style="padding:6px 0;color:#374151;font-size:14px">{a}</li>'
        for a in analysis.get("response_actions", [])
    )

    iocs_html = "".join(
        f'<li style="padding:4px 0;font-family:monospace;font-size:13px;color:#dc2626">{ioc}</li>'
        for ioc in analysis.get("indicators_of_compromise", [])
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Threat Intelligence Report</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 40px; background: #f9fafb; color: #111827; }}
  .container {{ max-width: 860px; margin: 0 auto; }}
  h1 {{ font-size: 24px; margin: 0 0 4px; }}
  h2 {{ font-size: 16px; font-weight: 600; color: #374151; margin: 24px 0 12px; border-bottom: 1px solid #e5e7eb; padding-bottom: 6px; }}
  .card {{ background: white; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 20px; }}
  ul {{ margin: 0; padding-left: 20px; }}
</style>
</head>
<body>
<div class="container">

  <div class="card" style="border-top: 4px solid {colour}">
    <div style="display:flex;justify-content:space-between;align-items:flex-start">
      <div>
        <h1>Threat Intelligence Report</h1>
        <p style="color:#6b7280;margin:0;font-size:14px">Source: {log_filename} &nbsp;|&nbsp; Generated: {now}</p>
      </div>
      <div style="text-align:right">
        {severity_badge(threat_level)}
        <div style="margin-top:8px">{score_bar(analysis.get('overall_severity', 0))}</div>
      </div>
    </div>
  </div>

  <div class="card">
    <h2>Executive Summary</h2>
    <p style="font-size:15px;line-height:1.7;color:#374151;margin:0">{analysis.get('executive_summary', '')}</p>
  </div>

  <div class="card">
    <h2>Detected Events ({len(analysis.get('events', []))})</h2>
    {events_html}
  </div>

  <div class="card">
    <h2>Recommended Response Actions</h2>
    <ul>{actions_html}</ul>
  </div>

  <div class="card">
    <h2>Indicators of Compromise (IOCs)</h2>
    <ul>{iocs_html}</ul>
  </div>

  <p style="font-size:12px;color:#9ca3af;text-align:center;margin-top:24px">
    Generated by AI Threat Detection Tool — github.com/akinwunmi-joseph
  </p>

</div>
</body>
</html>"""


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI-Powered Security Log Threat Analyser")
    parser.add_argument("--log",    type=str, help="Path to log file to analyse")
    parser.add_argument("--stdin",  action="store_true", help="Read log data from stdin (pipe mode)")
    parser.add_argument("--output", type=str, default=None, help="Output HTML report path (default: auto-named)")
    parser.add_argument("--json",   action="store_true", help="Also save raw JSON analysis")
    args = parser.parse_args()

    # Get API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[!] ANTHROPIC_API_KEY environment variable not set.")
        print("    Set it with: set ANTHROPIC_API_KEY=your_key_here  (Windows)")
        print("                 export ANTHROPIC_API_KEY=your_key_here  (Mac/Linux)")
        sys.exit(1)

    # Get log content
    if args.stdin:
        print("[*] Reading logs from stdin...")
        log_content = sys.stdin.read()
        log_filename = "stdin"
    elif args.log:
        log_path = Path(args.log)
        if not log_path.exists():
            print(f"[!] Log file not found: {args.log}")
            sys.exit(1)
        print(f"[*] Reading log file: {args.log}")
        log_content = log_path.read_text()
        log_filename = log_path.name
    else:
        parser.print_help()
        sys.exit(1)

    if not log_content.strip():
        print("[!] Log content is empty.")
        sys.exit(1)

    # Analyse
    analysis = analyse_logs_with_ai(log_content, api_key)

    # Print summary to terminal
    print("\n" + "─" * 60)
    print(f"  THREAT LEVEL : {analysis.get('threat_level', 'UNKNOWN')}")
    print(f"  SEVERITY     : {analysis.get('overall_severity', '?')}/10")
    print(f"  EVENTS FOUND : {len(analysis.get('events', []))}")
    print("─" * 60)
    print(f"\n  {analysis.get('executive_summary', '')}\n")

    # Save HTML report
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = args.output or f"threat_report_{timestamp}.html"
    html = generate_html_report(analysis, log_filename)
    Path(output_path).write_text(html)
    print(f"[+] HTML report saved: {output_path}")

    # Optionally save JSON
    if args.json:
        json_path = output_path.replace(".html", ".json")
        Path(json_path).write_text(json.dumps(analysis, indent=2))
        print(f"[+] JSON analysis saved: {json_path}")

    print("\n[+] Analysis complete.")


if __name__ == "__main__":
    main()
