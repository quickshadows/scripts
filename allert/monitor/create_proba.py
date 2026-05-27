#!/usr/bin/env python3
import requests
import time

TOKEN = ""
URL = "https://cloud-staging.kube.timeweb.net/api/v1/probes"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

with open("hosts_url.txt") as f:
    hosts = [line.strip() for line in f if line.strip()]

for i, host in enumerate(hosts, start=1):
    payload = {
        "probe": "http",
        "host": host,
        "interval": 60,
        "timeout": 30,
        "regions": ["ru-1", "kz-1", "de-1","nl-1"],
        "name": f"headfilANDnhttps-{host}-{i}",
        "preset_id": 3737,
        "project_id": 103757,
        "parameters": {
            "request_method": "GET",
            "follow_redirects": True,
            "is_check_cert": True
        }
    }

    try:
        resp = requests.post(URL, headers=headers, json=payload, timeout=10)
        print(f"{host} -> {resp.status_code}")
        print("BODY:", resp.text)
        time.sleep(0.3)
    except requests.exceptions.RequestException as e:
        print(f"{host} -> ERROR: {e}")