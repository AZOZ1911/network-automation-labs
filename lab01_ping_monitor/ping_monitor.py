import subprocess
import csv

hosts = [
    "8.8.8.8",
    "1.1.1.1"
]

results = []

for host in hosts:
    response = subprocess.call(
        ["ping", "-c", "2", host],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    status = "UP" if response == 0 else "DOWN"
    results.append((host, status))
    print(f"{host} is {status}")

with open("ping_results.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Host", "Status"])
    writer.writerows(results)
