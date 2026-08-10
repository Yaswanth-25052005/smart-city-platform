"""Post-start platform health verification script."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request


def check_url(url: str) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            body = response.read().decode("utf-8")
            return response.status == 200, body
    except urllib.error.URLError as exc:
        return False, str(exc)


def main() -> int:
    checks = {
        "api_health": "http://localhost:8000/health",
        "dashboard_health": "http://localhost:8501/_stcore/health",
    }

    failed = False
    results: dict[str, object] = {}

    for name, url in checks.items():
        ok, body = check_url(url)
        results[name] = {"url": url, "ok": ok}
        if ok and name == "api_health":
            try:
                results[name]["payload"] = json.loads(body)
            except json.JSONDecodeError:
                results[name]["payload"] = body
        elif not ok:
            results[name]["error"] = body
            failed = True

    print(json.dumps(results, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
