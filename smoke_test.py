import os
import sys
import time
import requests

BASE = os.getenv("API_BASE", "http://localhost:8000")
ENDPOINTS = ["/", "/materials/books", "/users"]


def check(url):
    try:
        r = requests.get(url, timeout=5)
        return r.status_code, r.text[:200]
    except Exception as e:
        return None, str(e)


if __name__ == "__main__":
    # allow the server a few seconds to start
    time.sleep(1)
    failures = 0
    for ep in ENDPOINTS:
        url = BASE.rstrip("/") + ep
        code, body = check(url)
        if code and 200 <= code < 300:
            print(f"OK: {url} -> {code}")
        else:
            print(f"FAIL: {url} -> {code} | {body}")
            failures += 1

    if failures:
        print(f"Smoke test failed: {failures} endpoints failing")
        sys.exit(2)
    else:
        print("Smoke test passed")
        sys.exit(0)
