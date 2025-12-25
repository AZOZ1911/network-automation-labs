import argparse
import json
from pathlib import Path
from collections import Counter

SEVERITIES = ["INFO", "WARNING", "ERROR", "CRITICAL"]
SEV_RANK = {s: i for i, s in enumerate(SEVERITIES)}

def detect_severity(line: str) -> str:
    upper = line.upper()
    for sev in reversed(SEVERITIES):  # check CRITICAL first
        if f" {sev} " in upper or upper.startswith(sev) or sev in upper:
            return sev
    return "INFO"

def normalize_message(line: str) -> str:
    """
    Very light normalization to help count recurring patterns.
    Removes timestamps-like prefix if present and keeps the message tail.
    """
    parts = line.split("msg=", 1)
    if len(parts) == 2:
        return parts[1].strip().strip('"')
    return line.strip()

def main():
    parser = argparse.ArgumentParser(description="Parse logs and detect severity.")
    parser.add_argument("--file", required=True, help="Path to log file")
    parser.add_argument("--min", default="INFO", choices=SEVERITIES, help="Minimum severity to include in incidents")
    parser.add_argument("--out", default="report.txt", help="TXT output report file")
    parser.add_argument("--json", dest="json_out", default="report.json", help="JSON output report file")
    parser.add_argument("--top", type=int, default=5, help="Top recurring message patterns to show")
    args = parser.parse_args()

    log_path = Path(args.file)
    if not log_path.exists():
        raise FileNotFoundError(f"Log file not found: {log_path}")

    min_rank = SEV_RANK[args.min]

    counts = Counter()
    pattern_counts = Counter()
    incidents = []

    for line in log_path.read_text(errors="ignore").splitlines():
        if not line.strip():
            continue

        sev = detect_severity(line)
        counts[sev] += 1

        msg_norm = normalize_message(line)
        pattern_counts[msg_norm] += 1

        # incidents: only those >= min severity
        if SEV_RANK[sev] >= min_rank:
            incidents.append({"severity": sev, "raw": line.strip(), "message": msg_norm})

    top_patterns = [{"message": m, "count": c} for m, c in pattern_counts.most_common(args.top)]

    # TXT report
    report_lines = []
    report_lines.append("Log Parser Report")
    report_lines.append("=" * 18)
    report_lines.append(f"File: {log_path}")
    report_lines.append(f"Min severity for incidents: {args.min}")
    report_lines.append("")
    report_lines.append("Summary:")
    for sev in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
        report_lines.append(f"- {sev}: {counts.get(sev, 0)}")

    report_lines.append("")
    report_lines.append(f"Top {args.top} recurring patterns:")
    for item in top_patterns:
        report_lines.append(f"- ({item['count']}) {item['message']}")

    report_lines.append("")
    report_lines.append("Incidents:")
    if incidents:
        for inc in incidents:
            report_lines.append(f"[{inc['severity']}] {inc['raw']}")
    else:
        report_lines.append("No incidents found for selected severity threshold.")

    Path(args.out).write_text("\n".join(report_lines))
    print(f"TXT report saved to: {args.out}")

    # JSON report
    json_payload = {
        "file": str(log_path),
        "min_severity": args.min,
        "summary": {sev: counts.get(sev, 0) for sev in ["CRITICAL", "ERROR", "WARNING", "INFO"]},
        "top_patterns": top_patterns,
        "incidents": incidents,
    }
    Path(args.json_out).write_text(json.dumps(json_payload, indent=2))
    print(f"JSON report saved to: {args.json_out}")

if __name__ == "__main__":
    main()
