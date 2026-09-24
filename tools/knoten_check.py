#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mechanische Pruefung der Anker-Seiten (Normknoten + Leitentscheidungen).

E  resource:-URIs aufloesen (ELI, ECLI-Resolver, DOI, gesetze-im-internet.de)
F  rechtsstand: Alter
G  Anker-Seiten ohne resource: bzw. Leitentscheidungen ohne ecli:

HTTP 000 bedeutet: aus dieser Umgebung nicht erreichbar. Das ist KEIN Befund
ueber die URI, sondern ueber die Netzwerklage, und wird gesondert ausgewiesen.
"""
import os, re, io, sys, ssl, datetime, urllib.request, urllib.error
import concurrent.futures as cf

WIKI = sys.argv[1] if len(sys.argv) > 1 else "/PFAD/ZU/DEINEM/VAULT/[WIKI-ORDNER]"
HEUTE = datetime.date(2026, 9, 24)
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def anker():
    out = []
    for dp, dn, fn in os.walk(WIKI):
        dn[:] = [d for d in dn if not d.startswith(".") and d not in ("Persönlich", "Werkzeuge")]
        for f in fn:
            if not f.endswith(".md"): continue
            p = os.path.join(dp, f); t = io.open(p, encoding="utf-8").read()
            if not t.startswith("---") or "type: wiki-page" not in t.split("---")[1]: continue
            fm = t.split("---")[1]
            if not re.search(r'^rang:', fm, re.M): continue
            g = lambda k: (re.search(r'^%s:\s*"?([^"\n]*)"?\s*$' % k, fm, re.M) or [None, ""])[1].strip()
            out.append(dict(name=f[:-3], rel=os.path.relpath(p, WIKI), rang=g("rang"),
                            ecli=g("ecli"), res=g("resource"), rs=g("rechtsstand")))
    return out

def hole(url):
    """GET mit Weiterleitungsfolge. HEAD ist unbrauchbar: mehrere amtliche Server
    (bundesverfassungsgericht.de, recht.bund.de) antworten darauf mit 303 bzw. 400,
    obwohl die Ressource existiert. Es wird nur ein Byte gelesen."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh) wiki-integrity-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
            r.read(1)
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0

def main():
    ks = anker()
    mit = [k for k in ks if k["res"]]
    print("Anker-Seiten: %d · davon mit resource: %d\n" % (len(ks), len(mit)))
    print("=" * 74); print("E  resource:-URIs aufloesen"); print("=" * 74)
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        codes = list(ex.map(lambda k: hole(k["res"]), mit))
    ok = [(k, c) for k, c in zip(mit, codes) if 200 <= c < 400]
    fehl = [(k, c) for k, c in zip(mit, codes) if c >= 400]
    unklar = [(k, c) for k, c in zip(mit, codes) if c == 0]
    print("  erreichbar: %d · Fehlercode: %d · aus dieser Umgebung nicht erreichbar: %d"
          % (len(ok), len(fehl), len(unklar)))
    if fehl:
        print("\n  BEFUNDE (URI antwortet mit Fehler):")
        for k, c in sorted(fehl, key=lambda x: -x[1]):
            print("   HTTP %-3s %-44s %s" % (c, k["name"][:44], k["res"][:74]))
    if unklar:
        hosts = {}
        for k, c in unklar:
            h = re.sub(r'^https?://([^/]+).*', r'\1', k["res"]); hosts[h] = hosts.get(h, 0) + 1
        print("\n  NICHT ERREICHBAR (kein Befund ueber die URI, sondern ueber das Netz):")
        for h, n in sorted(hosts.items(), key=lambda x: -x[1]):
            print("   %-52s %d URIs" % (h, n))

    print("\n" + "=" * 74); print("F  rechtsstand: Alter"); print("=" * 74)
    alt = []
    for k in ks:
        m = re.match(r'(\d{4})-(\d{2})-(\d{2})', k["rs"] or "")
        if not m: continue
        d = datetime.date(*map(int, m.groups())); alt.append((k, (HEUTE - d).days))
    alt.sort(key=lambda x: -x[1])
    for grenze in (365, 180, 90):
        print("   aelter als %3d Tage: %3d von %d" % (grenze, sum(1 for _, a in alt if a > grenze), len(alt)))
    print("\n   Aelteste fuenf:")
    for k, a in alt[:5]:
        print("     %-46s %s  (%d Tage)" % (k["name"][:46], k["rs"], a))

    print("\n" + "=" * 74); print("G  Fehlende Anker-Felder"); print("=" * 74)
    ohne_res = [k for k in ks if not k["res"]]
    print("   ohne resource: %d von %d" % (len(ohne_res), len(ks)))
    for k in ohne_res[:12]: print("     %s" % k["name"][:66])
    if len(ohne_res) > 12: print("     ... und %d weitere" % (len(ohne_res) - 12))

if __name__ == "__main__":
    main()
