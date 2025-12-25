import argparse
from pathlib import Path
from collections import Counter

SEVERITIES = ["CRITICAL", "ERROR", "WARNING", "INFO"]

def detect_severity(line: str) -> str:
    upper = line.upper()
    for sev in SEVERITIES:
        if f" {sev} " in upper or upper.startswith(sev) or sev in upper:
            return sev
    return "INFO"

def main():
    parser = argparse.ArgumentParser(description="Parse logs and detect severity.")
    parser.add_argument("--file", required=True, help="Path to log file")
    parser.add_argument("--out", default="report.txt", help="Output report file")
    args = parser.parse_args()

    log_path = Path(args.file)
    if not log_path.exists():
        raise FileNotFoundError(f"Log file not found: {log_path}")

    counts = Counter()
    incidents = []

    for line in log_path.read_text(errors="ignore").splitlines():
        if not line.strip():
            continue
        sev = detect_severity(line)
        counts[sev] += 1
        if sev in ("CRITICAL", "ERROR", "WARNING"):
            incidents.append((sev, line))

    report_lines = []
    report_lines.append("Log Parser Report")
    report_lines.append("=" * 18)
    report_lines.append(f"File: {log_path}")
    report_lines.append("")
    report_lines.append("Summary:")
    for sev in SEVERITIES:
        report_lines.append(f"- {sev}: {counts.get(sev, 0)}")
    report_lines.append("")
    report_lines.append("Incidents:")
    if incidents:
        for sev, line in incidents:
            report_lines.append(f"[{sev}] {line}")
    else:
        report_lines.append("No incidents found.")

    out_path = Path(args.out)
    out_path.write_text("\n".join(report_lines))
    print(f"Report saved to: {out_path}")

if __name__ == "__main__":
    main()
