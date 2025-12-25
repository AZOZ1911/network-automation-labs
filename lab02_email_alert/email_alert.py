
import os
import subprocess
import smtplib
from email.message import EmailMessage
from pathlib import Path

HOSTS_FILE = Path("hosts.txt")
PING_COUNT = 2
TIMEOUT_SEC = 2

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
MAIL_FROM = os.getenv("MAIL_FROM", SMTP_USER)
MAIL_TO = os.getenv("MAIL_TO")

def load_hosts():
    if not HOSTS_FILE.exists():
        raise FileNotFoundError("hosts.txt not found. Add one host per line.")
    hosts = []
    for line in HOSTS_FILE.read_text().splitlines():
        h = line.strip()
        if h and not h.startswith("#"):
            hosts.append(h)
    if not hosts:
        raise ValueError("hosts.txt is empty.")
    return hosts

def ping_host(host: str) -> bool:
    cmd = ["ping", "-c", str(PING_COUNT), "-W", str(TIMEOUT_SEC), host]
    rc = subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return rc == 0

def send_email(subject: str, body: str):
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS, MAIL_TO]):
        raise ValueError("Missing SMTP settings. Use environment variables.")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = MAIL_TO
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

def main():
    hosts = load_hosts()
    down_hosts = []

    for host in hosts:
        ok = ping_host(host)
        print(f"{host} is {'UP' if ok else 'DOWN'}")
        if not ok:
            down_hosts.append(host)

    if down_hosts:
        subject = f"[ALERT] {len(down_hosts)} host(s) DOWN"
        body = "Unreachable hosts:\n\n" + "\n".join(down_hosts)
        send_email(subject, body)
        print("Email alert sent.")
    else:
        print("All hosts are UP. No email sent.")

if __name__ == "__main__":
    main()
