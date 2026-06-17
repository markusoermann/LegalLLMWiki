#!/usr/bin/env python3
"""
Batch-verify DOIs via CrossRef and arXiv.
Usage: python verify_dois.py '[{"label": "Smith 2023", "doi": "10.1234/abc"}]'
Output: JSON list with status, crossref_year, crossref_title, http_code per entry
"""
import sys
import json
import time
import urllib.request
import urllib.error
import urllib.parse

EMAIL = "your-email@example.com"  # Replace with your email for the CrossRef/OpenAlex polite pool
HEADERS = {"User-Agent": f"QuellenCheck/1.0 mailto:{EMAIL}"}
SLEEP_MS = 0.1  # 100ms between requests


def check_crossref(doi):
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='/')}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.load(r)
            msg = data.get("message", {})
            title = (msg.get("title") or ["?"])[0]
            # Try multiple year fields in order of preference
            year = None
            for field in ("published", "published-print", "published-online", "issued"):
                parts = msg.get(field, {}).get("date-parts", [[]])[0]
                if parts:
                    year = str(parts[0])
                    break
            return {"status": "OK", "http_code": 200, "crossref_title": title, "crossref_year": year or "?"}
    except urllib.error.HTTPError as e:
        return {"status": "FEHLER", "http_code": e.code, "crossref_title": "", "crossref_year": ""}
    except Exception as e:
        return {"status": "FEHLER", "http_code": 0, "crossref_title": "", "crossref_year": str(e)[:60]}


def check_arxiv(arxiv_id):
    """Check an arXiv paper by ID (e.g., '1908.09635')."""
    url = f"https://arxiv.org/abs/{arxiv_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            content = r.read(4000).decode("utf-8", errors="replace")
            # Try to extract title from page
            import re
            m = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
            title = m.group(1).strip() if m else "?"
            return {"status": "OK", "http_code": r.status, "crossref_title": title[:80], "crossref_year": "arXiv"}
    except urllib.error.HTTPError as e:
        return {"status": "FEHLER", "http_code": e.code, "crossref_title": "", "crossref_year": ""}
    except Exception as e:
        return {"status": "FEHLER", "http_code": 0, "crossref_title": "", "crossref_year": str(e)[:60]}


def resolve_doi(doi):
    """Try doi.org as final fallback."""
    url = f"https://doi.org/{doi}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return {"status": "OK", "http_code": r.status, "crossref_title": "(via doi.org)", "crossref_year": "?"}
    except urllib.error.HTTPError as e:
        return {"status": "FEHLER", "http_code": e.code, "crossref_title": "", "crossref_year": ""}
    except Exception as e:
        return {"status": "FEHLER", "http_code": 0, "crossref_title": "", "crossref_year": str(e)[:60]}


def check_doi(label, doi):
    result = {"label": label, "doi": doi}

    # arXiv DOIs need special handling
    if doi.startswith("10.48550/arXiv.") or doi.startswith("10.48550/arxiv."):
        arxiv_id = doi.split("arXiv.")[-1].split("arxiv.")[-1]
        arxiv_result = check_arxiv(arxiv_id)
        result.update(arxiv_result)
        result["note"] = "arXiv DOI — CrossRef not applicable"
        return result

    # Primary: CrossRef
    cr_result = check_crossref(doi)
    result.update(cr_result)

    # Fallback: doi.org resolver (if CrossRef failed)
    if result["status"] == "FEHLER" and result["http_code"] != 404:
        time.sleep(SLEEP_MS)
        fallback = resolve_doi(doi)
        if fallback["status"] == "OK":
            result.update(fallback)
            result["note"] = "CrossRef failed, confirmed via doi.org"

    return result


def detect_year_mismatch(citation_year, crossref_year):
    """Return (mismatch_level, note) where level is None / 'minor' / 'significant'."""
    try:
        cy = int(citation_year)
        crf = int(crossref_year)
        diff = cy - crf
        if diff == 0:
            return None, None
        elif 0 < diff <= 1:
            return "minor", f"CrossRef: {crf}, Zitation: {cy} — wahrscheinlich Online-first vs. Druckausgabe"
        elif diff == -1:
            return "minor", f"CrossRef: {crf}, Zitation: {cy} — Zitation ein Jahr vor CrossRef (ggf. Preprint)"
        else:
            return "significant", f"CrossRef: {crf}, Zitation: {cy} — Differenz {diff} Jahr(e)"
    except (ValueError, TypeError):
        return None, None


def main():
    if len(sys.argv) < 2:
        print("Usage: verify_dois.py '[{\"label\": \"...\", \"doi\": \"...\", \"citation_year\": \"...\"}]'")
        sys.exit(1)

    entries = json.loads(sys.argv[1])
    results = []

    for entry in entries:
        label = entry.get("label", "?")
        doi = entry.get("doi", "").strip()
        citation_year = str(entry.get("citation_year", ""))

        result = check_doi(label, doi)

        # Year mismatch detection
        if result.get("crossref_year") and citation_year:
            mismatch_level, mismatch_note = detect_year_mismatch(citation_year, result["crossref_year"])
            if mismatch_level:
                result["year_mismatch"] = mismatch_level
                result["year_mismatch_note"] = mismatch_note

        results.append(result)
        time.sleep(SLEEP_MS)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
