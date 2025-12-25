iimport subprocess
import csv
from pathlib import Path

HOSTS_FILE = Path("hosts.txt")
OUTPUT_CSV = Path("ping_results.csv")
PING_COUNT = 2
TIMEOUT_SEC = 2

def load_hosts():
    if not HOSTS_FILE.exists():
        raise FileNotFoundError("hosts.txt not found. Create it and add one host per line.")
    hosts = []
    for line in HOSTS_FILE.read_text().splitlines():
        h = line.strip()
        if h and not h.startswith("#"):
            hosts.append(h)
    if not hosts:
        raise ValueError("hosts.txt is empty. Add at least one host.")
    return hosts

def ping_host(host: str) -> str:
    # Linux ping: -c count, -W timeout (seconds per reply)
    cmd = ["ping", "-c", str(PING_COUNT), "-W", str(TIMEOUT_SEC), host]
    rc = subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return "UP" if rc == 0 else "DOWN"

def main():
    hosts = load_hosts()
    results = []

    for host in hosts:
        status = ping_host(host)
        results.append((host, status))
        print(f"{host} is {status}")

    with OUTPUT_CSV.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Host", "Status"])
        writer.writerows(results)

    print(f"\nSaved results to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()

