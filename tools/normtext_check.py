#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normtext-Abgleich: prueft Normknoten gegen die amtliche konsolidierte Fassung.

Die Luecke, die dieses Werkzeug schliesst: Der Verifikations-Pass prueft Belegtheit
gegen die Literaturverwaltung. Normknoten fuehren definitionsgemaess `quellen: []`
und fallen durch sein Raster. Fuer sie ist der Abgleich gegen die amtliche Fassung
die einzige Pruefung. Genau in dieser Luecke sass im Bestand die Aussage, NetzDG
§ 3a bleibe anwendbar, obwohl die Vorschrift 2024 aufgehoben wurde.

Befunde:
  H1  Norm ist amtlich weggefallen, die Wiki-Seite sagt das nicht
  H2  Einzelnorm amtlich nicht auffindbar und kein Wegfall nachweisbar
  H3  Wiki behauptet Aufhebung, amtlich nicht erkennbar (Sichtkontrolle)
  H4  Fassungsangabe je Gesetz ("zuletzt geaendert durch")

JURISDIKTIONSABHAENGIG. GESETZE bildet Gesetzeskuerzel auf Portal-Slugs des
deutschen Bundesrechts ab. EU-Recht, Staatsvertraege (z.B. MStV) und
Konventionsrecht (EMRK) liegen dort nicht und werden uebersprungen.

Netzschonend: je Gesetz wird das Inhaltsverzeichnis genau einmal geladen,
Sammeldateien und Gesamtausgabe ebenfalls. Pro Knoten faellt hoechstens eine
zusaetzliche Abfrage an.

Aufruf:  python3 normtext_check.py [WIKI-ROOT]
"""
import os, re, io, sys, ssl, html, urllib.request, urllib.error

WIKI = sys.argv[1] if len(sys.argv) > 1 else "/PFAD/ZU/DEINEM/VAULT/[WIKI-ORDNER]"
EXCLUDE = set()  # Nicht-Wiki-Ordner eintragen, z.B. {"Persoenlich", "Werkzeuge"}
BASIS = "https://www.gesetze-im-internet.de"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

GESETZE = {
    "GG": "gg", "BGB": "bgb", "StGB": "stgb", "UrhG": "urhg", "UWG": "uwg_2004",
    "NetzDG": "netzdg", "TDDDG": "ttdsg", "TTDSG": "ttdsg", "TKG": "tkg_2021",
    "BDSG": "bdsg_2018", "VwVfG": "vwvfg", "TMG": "tmg", "DDG": "ddg",
}
NAME = re.compile(r'^([A-Za-zÄÖÜäöü0-9\-]+)\s+(§§?|Art\.)\s*(\d+[a-z]?)')
_cache = {}

def hol(url, n=300000):
    if url in _cache: return _cache[url]
    try:
        r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh) normtext-check/1.0"})
        with urllib.request.urlopen(r, timeout=30, context=CTX) as x:
            raw = x.read(n).decode("utf-8", "replace")
        t = html.unescape(re.sub(r'<[^>]+>', ' ', raw))
        out = (200, re.sub(r'\s+', ' ', t), raw)
    except urllib.error.HTTPError as e:
        out = (e.code, "", "")
    except Exception:
        out = (0, "", "")
    _cache[url] = out
    return out

def gesetz_info(slug):
    """Inhaltsverzeichnis, Sammeldateien mit Wegfall-Vermerk, Fassungsangabe."""
    key = ("INFO", slug)
    if key in _cache: return _cache[key]
    code, txt, raw = hol("%s/%s/" % (BASIS, slug))
    weggefallen = set()
    stand = "keine Angabe gefunden"
    if code == 200:
        for s in set(re.findall(r'(_{2,3}[\w]+_bis_[\w]+\.html)', raw)):
            c2, t2, _ = hol("%s/%s/%s" % (BASIS, slug, s))
            if c2 == 200 and "(weggefallen)" in t2:
                m = re.search(r'§§\s*(\d+[a-z]?)\s*bis\s*(\d+[a-z]?)', t2)
                if m: weggefallen.add((m.group(1), m.group(2), s))
        gm = re.search(r'href="\.?/?(BJNR[\w]+\.html)"', raw)
        if gm:
            c3, t3, _ = hol("%s/%s/%s" % (BASIS, slug, gm.group(1)))
            # Nicht bei "N" abbrechen: "Stand: Neugefasst durch ..." wuerde sofort enden.
            # Die Angabe endet auf der Seite vor dem Hinweis "Naeheres zur Standangabe".
            sm = re.search(r'Stand:\s*(.{0,120}?)\s*(?:Näheres zur Standangabe|Fußnote|$)', t3) if c3 == 200 else None
            if sm and sm.group(1).strip(): stand = sm.group(1).strip()
    res = dict(weggefallen=weggefallen, stand=stand)
    _cache[key] = res
    return res

def im_bereich(nr, von, bis):
    """Liegt Paragraph nr im Bereich von..bis? Vergleich ueber Zahl plus Buchstabe."""
    z = lambda s: (int(re.match(r'\d+', s).group(0)), re.sub(r'^\d+', '', s))
    return z(von) <= z(nr) <= z(bis)

def knoten():
    out = []
    for dp, dn, fn in os.walk(WIKI):
        dn[:] = [d for d in dn if not d.startswith(".") and d not in EXCLUDE]
        for f in fn:
            if not f.endswith(".md"): continue
            p = os.path.join(dp, f); t = io.open(p, encoding="utf-8").read()
            if not t.startswith("---") or "type: wiki-page" not in t.split("---")[1]: continue
            fm = t.split("---")[1]
            if not re.search(r'^rang:', fm, re.M): continue
            m = NAME.match(f[:-3])
            if not m or m.group(1) not in GESETZE: continue
            body = t.split("---", 2)[-1].lower()
            out.append(dict(name=f[:-3], gesetz=m.group(1), art=m.group(2), nr=m.group(3),
                            sagt_aufgehoben=bool(re.search(r'aufgehoben|weggefallen|außer kraft', body)),
                            rs=(re.search(r'^rechtsstand:\s*(\S+)', fm, re.M) or [None, "—"])[1]))
    return out

def main():
    ks = sorted(knoten(), key=lambda k: (k["gesetz"], k["nr"]))
    print("Normtext-Abgleich gegen %s" % BASIS)
    print("Pruefbare Normknoten: %d\n" % len(ks))
    res = []
    for k in ks:
        slug = GESETZE[k["gesetz"]]
        info = gesetz_info(slug)
        pfad = ("art_%s" % k["nr"]) if k["art"] == "Art." else ("__%s" % k["nr"])
        url = "%s/%s/%s.html" % (BASIS, slug, pfad)
        code, txt, _ = hol(url, 80000)
        weg = False; quelle = None
        if code == 200:
            weg = bool(re.search(r'(?:§+|Art\.?)\s*%s[a-z]?\s*\(weggefallen\)' % re.escape(k["nr"]), txt))
            if weg: quelle = url
        else:
            for von, bis, datei in info["weggefallen"]:
                if k["art"] != "Art." and im_bereich(k["nr"], von, bis):
                    weg = True; quelle = "%s/%s/%s" % (BASIS, slug, datei); break
        res.append(dict(k, code=code, weg=weg, quelle=quelle, stand=info["stand"]))

    h1 = [r for r in res if r["weg"] and not r["sagt_aufgehoben"]]
    h2 = [r for r in res if r["code"] != 200 and not r["weg"]]
    h3 = [r for r in res if r["sagt_aufgehoben"] and not r["weg"] and r["code"] == 200]
    ok = [r for r in res if r["code"] == 200 and not r["weg"] and not r["sagt_aufgehoben"]]
    korrekt = [r for r in res if r["weg"] and r["sagt_aufgehoben"]]

    print("=" * 76); print("H1  AMTLICH WEGGEFALLEN, Wiki-Seite sagt es nicht  (%d)" % len(h1)); print("=" * 76)
    for r in h1: print("   %-32s %s" % (r["name"][:32], r["quelle"]))
    if not h1: print("   keine")

    print("\n" + "=" * 76); print("H2  Amtlich nicht auffindbar, Wegfall nicht nachweisbar  (%d)" % len(h2)); print("=" * 76)
    for r in h2: print("   HTTP %-3s %-30s" % (r["code"], r["name"][:30]))
    if not h2: print("   keine")

    print("\n" + "=" * 76); print("H3  Wiki behauptet Aufhebung, amtlich nicht erkennbar  (%d)" % len(h3)); print("=" * 76)
    print("   Auch blosse Verdraengung loest diesen Befund aus. Kein Fehler, sondern")
    print("   Aufforderung zur Sichtkontrolle.")
    for r in h3: print("   %-32s rechtsstand=%s" % (r["name"][:32], r["rs"]))
    if not h3: print("   keine")

    print("\n" + "=" * 76); print("H4  Fassungsangaben"); print("=" * 76)
    for g in sorted(set(k["gesetz"] for k in ks)):
        print("   %-10s %s" % (g, gesetz_info(GESETZE[g])["stand"][:88]))

    print("\n   korrekt als aufgehoben gefuehrt: %d · unauffaellig: %d · Summe: %d"
          % (len(korrekt), len(ok), len(h1) + len(h2) + len(h3) + len(ok) + len(korrekt)))

if __name__ == "__main__":
    main()
