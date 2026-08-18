"""Check external source links in the 30 chapter manuscripts.

The checker follows redirects and reports hard failures separately from sites that
refuse automated requests. It does not rewrite manuscripts.
"""

from __future__ import annotations

import argparse
import re
import ssl
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
URL_RE = re.compile(r"https://[^\s)>\]]+")


def collect_links() -> list[str]:
    links: set[str] = set()
    for path in sorted((ROOT / "book" / "chapters").glob("week*.qmd")):
        for value in URL_RE.findall(path.read_text(encoding="utf-8")):
            links.add(value.rstrip(".,;:'\""))
    return sorted(links)


def check(url: str, timeout: float) -> tuple[str, int | str, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/124 Safari/537.36"
            )
        },
    )
    try:
        with urllib.request.urlopen(
            request, timeout=timeout, context=ssl.create_default_context()
        ) as response:
            return url, response.status, response.geturl()
    except urllib.error.HTTPError as exc:
        return url, exc.code, str(exc)
    except Exception as exc:  # Network/DNS/TLS failures need a human-readable report.
        return url, "ERR", f"{type(exc).__name__}: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()

    links = collect_links()
    results: list[tuple[str, int | str, str]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(check, url, args.timeout) for url in links]
        for future in as_completed(futures):
            results.append(future.result())

    hard_failures = []
    blocked = []
    for url, status, detail in sorted(results):
        if (isinstance(status, int) and status >= 500) or status in (404, 410):
            hard_failures.append((status, url, detail))
        elif status == "ERR" or (isinstance(status, int) and status >= 400):
            blocked.append((status, url, detail))

    print(f"checked={len(links)} hard_failures={len(hard_failures)} blocked={len(blocked)}")
    for status, url, detail in hard_failures:
        print(f"FAIL {status} {url} :: {detail}")
    for status, url, detail in blocked:
        print(f"BLOCKED {status} {url} :: {detail}")
    return 1 if hard_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
