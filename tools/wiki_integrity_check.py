#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mechanischer Integritaets-Check des LLMWiki.

Prueft ohne LLM, rein datenbasiert:
  A  citekeys aus quellen:-Frontmatter gegen die Zotero-Bibliothek
  B  Volltextlage je aufgeloester Quelle (PDF/HTML-Attachment vorhanden?)
  C  ECLI-Syntax in ecli:-Feldern und urteile:-Eintraegen
  D  Normen/Urteile, die in >=3 Seiten vorkommen, aber keinen Knoten haben

Aufruf:  python3 wiki_integrity_check.py [WIKI-ROOT]
Voraussetzung: Zotero laeuft, lokale API auf Port 23119 erreichbar.
"""
import os, re, io, sys, json, urllib.request, collections, unicodedata

WIKI = sys.argv[1] if len(sys.argv) > 1 else "/PFAD/ZU/DEINEM/VAULT/[WIKI-ORDNER]"
EXCLUDE = set()  # Nicht-Wiki-Ordner eintragen, z.B. {"Persoenlich", "Werkzeuge"}
API = "http://localhost:23119/api/users/0/items"
N = lambda s: unicodedata.normalize("NFC", s)

# ---------------------------------------------------------------- Zotero laden
def load_zotero():
    """citekey -> {key, title, itemType, attachments:[contentType]}"""
    items, start = {}, 0
    children = collections.defaultdict(list)
    while True:
        url = "%s?limit=100&start=%d&format=json" % (API, start)
        try:
            raw = urllib.request.urlopen(url, timeout=30).read()
        except Exception as e:
            sys.exit("Zotero nicht erreichbar (%s). Laeuft Zotero?" % e)
        batch = json.loads(raw)
        if not batch:
            break
        for it in batch:
            d = it["data"]
            if d.get("itemType") == "attachment":
                children[d.get("parentItem")].append(d.get("contentType", ""))
            ck = d.get("citationKey")
            if ck:
                items[ck] = {"key": d["key"], "title": d.get("title", ""),
                             "itemType": d.get("itemType", ""), "att": []}
        start += 100
    bykey = {v["key"]: v for v in items.values()}
    for parent, cts in children.items():
        if parent in bykey:
            bykey[parent]["att"] = cts
    return items

# ---------------------------------------------------------------- Wiki lesen
# Gerichtskuerzel duerfen gemischte Schreibweise haben (BVerfG, BVerwG, BSG).
# Eine reine Grossbuchstaben-Klasse erzeugt Fehlalarme auf allen deutschen ECLI.
ECLI_RE = re.compile(r'ECLI:[A-Z]{2}:[A-Za-z0-9]{1,7}:\d{4}:[A-Za-z0-9.\-]+$')

def scan_wiki():
    pages = []
    for dp, dn, fn in os.walk(WIKI):
        dn[:] = [d for d in dn if not d.startswith(".") and d not in EXCLUDE]
        for f in fn:
            if not f.endswith(".md"):
                continue
            p = os.path.join(dp, f)
            t = io.open(p, encoding="utf-8").read()
            if not t.startswith("---"):
                continue
            fm = t.split("---")[1]
            if "type: wiki-page" not in fm:
                continue
            rel = os.path.relpath(p, WIKI)
            q = re.search(r'quellen:\s*\[(.*?)\]', fm, re.S)
            # citekeys duerfen Punkte enthalten (z.B. kanzleidr.bahrRechtsNewsletter...).
            # Ein Muster ohne Punkt zerschneidet sie und meldet das Fragment als fehlend.
            keys = re.findall(r'@([A-Za-z][A-Za-z0-9_.\-]*[A-Za-z0-9])', q.group(1)) if q else []
            ecli = re.findall(r'^ecli:\s*"?([^"\n]+)"?\s*$', fm, re.M)
            def block(name):
                m = re.search(r'^%s:\s*\n((?:\s*-\s*.*\n)+)' % name, fm, re.M)
                return [x.strip().strip('"') for x in re.findall(r'^\s*-\s*(.+)$', m.group(1), re.M)] if m else []
            pages.append({"rel": rel, "keys": keys,
                          "ecli": [e.strip() for e in ecli if e.strip()],
                          "normen": block("normen"), "urteile": block("urteile"),
                          "knoten": bool(re.search(r'^rang:', fm, re.M))})
    return pages

def main():
    print("Lade Zotero-Bibliothek ...")
    zot = load_zotero()
    print("  %d Items mit citationKey\n" % len(zot))
    pages = scan_wiki()
    print("Wiki: %d Seiten mit type: wiki-page\n" % len(pages))

    # --- A + B
    use = collections.defaultdict(list)
    for pg in pages:
        for k in pg["keys"]:
            use[k].append(pg["rel"])
    missing, nofull, ok = [], [], 0
    for k, where in sorted(use.items(), key=lambda x: -len(x[1])):
        if k not in zot:
            missing.append((k, where))
        else:
            att = zot[k]["att"]
            if not any(("pdf" in c) or ("html" in c) for c in att):
                nofull.append((k, where, zot[k]["title"][:60]))
            else:
                ok += 1

    print("=" * 72)
    print("A  citekey-Aufloesung")
    print("=" * 72)
    print("  %d distinkte citekeys im Wiki · %d aufgeloest · %d NICHT aufgeloest"
          % (len(use), len(use) - len(missing), len(missing)))
    def kandidaten(ck):
        m = re.match(r'^([a-z]+)', ck)
        nach = m.group(1) if m else ck[:6].lower()
        jahr = re.search(r'(\d{4})', ck)
        jahr = int(jahr.group(1)) if jahr else None
        out = []
        for zk in zot:
            if not zk.lower().startswith(nach):
                continue
            zj = re.search(r'(\d{4})', zk)
            if jahr and zj and abs(int(zj.group(1)) - jahr) > 4:
                continue
            out.append(zk)
        return sorted(out)[:4]

    for k, where in missing:
        print("\n  ✗ @%s  (%d Seiten)" % (k, len(where)))
        kand = kandidaten(k)
        if kand:
            print("      Kandidat(en) in Zotero: %s" % ", ".join("@" + c for c in kand))
        else:
            print("      kein Kandidat in Zotero gefunden")
        for w in where[:6]:
            print("      %s" % w)
        if len(where) > 6:
            print("      ... und %d weitere" % (len(where) - 6))

    print("\n" + "=" * 72)
    print("B  Volltextlage der aufgeloesten Quellen")
    print("=" * 72)
    print("  %d mit PDF/HTML-Attachment · %d ohne" % (ok, len(nofull)))
    print("  (ohne Attachment = Belegpruefung nicht moeglich, Befund 'nicht pruefbar')")
    for k, where, title in nofull[:15]:
        print("  ○ @%-42s %d Seiten  %s" % (k, len(where), title))
    if len(nofull) > 15:
        print("  ... und %d weitere" % (len(nofull) - 15))

    # --- C
    print("\n" + "=" * 72)
    print("C  ECLI-Syntax")
    print("=" * 72)
    bad, total = [], 0
    for pg in pages:
        for e in pg["ecli"]:
            total += 1
            if not ECLI_RE.match(e):
                bad.append((pg["rel"], e))
    print("  %d ECLI-Felder geprueft · %d syntaktisch auffaellig" % (total, len(bad)))
    for rel, e in bad:
        print("  ✗ %-52s %s" % (rel, e))

    # --- D
    print("\n" + "=" * 72)
    print("D  Normen und Urteile ohne eigenen Knoten (Schwelle 3)")
    print("=" * 72)
    files = set()
    for dp, dn, fn in os.walk(WIKI):
        dn[:] = [d for d in dn if not d.startswith(".")]
        for f in fn:
            if f.endswith(".md"):
                files.add(N(f[:-3]))
    for feld in ("normen", "urteile"):
        cnt = collections.Counter()
        for pg in pages:
            for v in set(pg[feld]):
                cnt[v] += 1
        fehlt = [(v, n) for v, n in cnt.items() if n >= 3 and N(v) not in files]
        print("  %s: %d Werte · %d ab 3 Vorkommen ohne Knoten" % (feld, len(cnt), len(fehlt)))
        for v, n in sorted(fehlt, key=lambda x: -x[1])[:10]:
            print("     %-46s %dx" % (v, n))

    print("\n" + "=" * 72)
    print("ZUSAMMENFASSUNG")
    print("=" * 72)
    print("  Nicht aufloesbare citekeys:      %d  (betreffen %d Seiten)"
          % (len(missing), len(set(w for _, ws in missing for w in ws))))
    print("  Quellen ohne Volltext:          %d  (betreffen %d Seiten)"
          % (len(nofull), len(set(w for _, ws, _ in nofull for w in ws))))
    print("  ECLI syntaktisch auffaellig:    %d" % len(bad))

if __name__ == "__main__":
    main()
