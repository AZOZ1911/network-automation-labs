## Lab 03 – Log Parser + Severity Detection

Parse a log file and detect incidents based on severity keywords.

### What it does
- Reads log lines from a file
- Detects severity (CRITICAL / ERROR / WARNING / INFO)
- Generates a summary report

### How to Run
```bash
python log_parser.py --file sample.log
