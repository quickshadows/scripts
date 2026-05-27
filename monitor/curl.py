#!/usr/bin/env python3

import requests
import time
import random

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

URLS = [
    "https://homdgr7ax1.cdn.twcstorage.ru/",
    "https://pl4r28q8vr.cdn.twcstorage.ru/",
    "https://e6qrtnnedn.cdn.twcstorage.ru/1.jpg"
]

while True:
    print("\n=== NEW ITERATION ===")

    try:
        r1 = session.get(URLS[0], headers=headers, allow_redirects=True, timeout=10)
        print("1:", r1.status_code)

        time.sleep(3)

        r2 = session.get(URLS[1], headers=headers, allow_redirects=True, timeout=10)
        print("2:", r2.status_code)

        time.sleep(3)

        r3 = session.get(URLS[2], headers=headers, allow_redirects=True, timeout=10)
        print("3:", r3.status_code)

        with open("file1.jpg", "wb") as f:
            f.write(r3.content)

    except Exception as e:
        print("ERROR:", e)

    time.sleep(random.randint(180, 300))
