#!/usr/bin/env python3
"""
Post-deploy smoke test. PUTs a value, reads it back decrypted and checks
it round-trips, then reads it back encrypted and checks the plaintext
isn't sitting there in the clear. Stdlib only -- no pip install in CI.

Usage: python3 tests/smoke_test.py <api-url>
<api-url> is the CloudFormation stack's "API" output, e.g.
https://xyz.execute-api.us-east-1.amazonaws.com/Prod/encryptdecrypt/
"""
import json
import sys
import time
import urllib.error
import urllib.request


def request(method, url, body=None, attempts=4, delay=3):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    status, text = None, None
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(url, data=data, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.status, resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            status, text = e.code, e.read().decode("utf-8", errors="replace")
            if e.code < 500 or attempt == attempts:
                return status, text
        except urllib.error.URLError as e:
            status, text = None, str(e)
        if attempt < attempts:
            # fresh deploy may still be propagating (cold start, IAM) -- worth a retry
            time.sleep(delay)
    return status, text


def main():
    if len(sys.argv) != 2:
        print("usage: smoke_test.py <api-url>", file=sys.stderr)
        return 2

    base = sys.argv[1].rstrip("/")
    secret_value = f"smoke-test-{int(time.time())}"
    failures = []

    status, body = request("PUT", base, {"Secret": secret_value})
    print(f"PUT                -> {status}")
    if status != 200:
        failures.append(f"PUT returned {status}: {body}")

    status, body = request("GET", base + "?Decrypt=YES")
    print(f"GET ?Decrypt=YES   -> {status}")
    if status != 200:
        failures.append(f"GET (decrypt) returned {status}: {body}")
    else:
        try:
            decrypted = json.loads(body)
        except json.JSONDecodeError:
            decrypted = None
        if decrypted != {"Secret": secret_value}:
            failures.append(f"round-trip mismatch: expected Secret={secret_value!r}, got {decrypted!r}")

    status, body = request("GET", base + "?Decrypt=NO")
    print(f"GET ?Decrypt=NO    -> {status}")
    if status != 200:
        failures.append(f"GET (encrypted) returned {status}: {body}")
    elif secret_value in body:
        failures.append("encrypted response contains the plaintext secret -- data is not encrypted at rest")

    if failures:
        print("\nFAIL:")
        for f in failures:
            print(f" - {f}")
        return 1

    print("\nPASS: PUT/GET round-trip is correct and the encrypted response does not leak the plaintext")
    return 0


if __name__ == "__main__":
    sys.exit(main())
