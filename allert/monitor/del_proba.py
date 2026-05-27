#!/usr/bin/env python3

import requests
import time


TOKEN = ""
URL = "https://cloud-staging.kube.timeweb.net/api/v1/probes/{}"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

with open("probi") as f:
    ids = [line.strip() for line in f if line.strip()]

for probe_id in ids:
    resp = requests.delete(URL.format(probe_id), headers=headers)

    print(probe_id, resp.status_code, resp.text)
    time.sleep(0.1)
