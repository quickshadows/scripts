import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_FILE = "200.txt"
TIMEOUT = 5
THREADS = 100

def check_domain(domain):
    urls = [
        f"http://{domain}",
        f"https://{domain}"
    ]

    for url in urls:
        try:
            r = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
            return domain, url, r.status_code
        except Exception as e:
            continue

    return domain, None, "DOWN"


with open(INPUT_FILE) as f:
    domains = [d.strip() for d in f if d.strip()]

results = []

with ThreadPoolExecutor(max_workers=THREADS) as ex:
    futures = [ex.submit(check_domain, d) for d in domains]

    for f in as_completed(futures):
        domain, url, status = f.result()
        print(f"{domain:40} -> {status}")

        if status != "DOWN":
            results.append((domain, url, status))

# сохранить живые
with open("alive.txt", "w") as f:
    for d, u, s in results:
        f.write(f"{d} {u} {s}\n")
