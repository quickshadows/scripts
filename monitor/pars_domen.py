import gzip
import json

domains = set()

with gzip.open("crawl.json.gz", "rt") as f:
    for line in f:
        data = json.loads(line)
        url = data.get("url", "")
        if url:
            domains.add(url.split("/")[2])

print(list(domains)[:5000])
