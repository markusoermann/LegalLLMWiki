#!/usr/bin/env python3
"""
Batch HTTP-check for URLs in a bibliography.
Usage: python verify_urls.py '[{"label": "ACE 2024", "url": "https://..."}]'
Output: JSON list with status, http_code, final_url, note per entry
"""
import sys
import json
import time
import urllib.request
import urllib.error

BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
SLEEP_S = 0.3
TIMEOUT = 15

UNRELIABLE_DOMAINS = {
    "academia.edu": "academia.edu ist keine stabile Publikationsplattform — kanonische Quelle (Zeitschrift/Verlag) sollte angegeben werden",
    "researchgate.net": "ResearchGate ist keine zitierfähige Primärquelle — kanonische Quelle angeben",
}


def check_url(label, url):
    result = {"label": label, "url": url, "status": "FEHLER", "http_code": 0, "final_url": url, "note": ""}

    # Flag unreliable domains before even checking
    for domain, note in UNRELIABLE_DOMAINS.items():
        if domain in url:
            result["note"] = note

    req = urllib.request.Request(
        url,
        headers={"User-Agent": BROWSER_UA, "Accept": "text/html,application/xhtml+xml,*/*"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            result["http_code"] = r.status
            result["final_url"] = r.url
            if r.status in range(200, 300):
                result["status"] = "OK"
            elif r.status == 403:
                result["status"] = "UNKLAR"
                result["note"] = (result["note"] + " Login/Paywall — Seite existiert, aber Zugang gesperrt").strip()
            else:
                result["status"] = "UNKLAR"
    except urllib.error.HTTPError as e:
        result["http_code"] = e.code
        if e.code == 404:
            result["status"] = "FEHLER"
            result["note"] = (result["note"] + " 404 — Seite nicht gefunden").strip()
        elif e.code == 403:
            result["status"] = "UNKLAR"
            result["note"] = (result["note"] + " 403 — Zugang gesperrt (Login/Paywall)").strip()
        elif e.code == 523:
            result["status"] = "FEHLER"
            result["note"] = (result["note"] + " 523 — Cloudflare/Server nicht erreichbar").strip()
        else:
            result["status"] = "FEHLER"
            result["note"] = (result["note"] + f" HTTP {e.code}").strip()
    except TimeoutError:
        result["status"] = "FEHLER"
        result["note"] = (result["note"] + " Timeout nach 15s").strip()
    except Exception as e:
        result["status"] = "FEHLER"
        result["note"] = (result["note"] + f" {str(e)[:60]}").strip()

    # Detect redirect to a very different domain (possible broken redirect)
    if result["final_url"] != url:
        from urllib.parse import urlparse
        orig_domain = urlparse(url).netloc
        final_domain = urlparse(result["final_url"]).netloc
        if orig_domain != final_domain and result["status"] == "OK":
            result["note"] = (result["note"] + f" → umgeleitet zu {final_domain}").strip()

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: verify_urls.py '[{\"label\": \"...\", \"url\": \"https://...\"}]'")
        sys.exit(1)

    entries = json.loads(sys.argv[1])
    results = []

    for entry in entries:
        label = entry.get("label", "?")
        url = entry.get("url", "").strip()
        if not url:
            continue
        result = check_url(label, url)
        results.append(result)
        time.sleep(SLEEP_S)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
