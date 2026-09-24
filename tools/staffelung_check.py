#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Staffelungs-Waechter: prueft Geltung gegen Wirksamkeit bei Ankerseiten.

Die Luecke, die dieses Werkzeug schliesst: normtext_check.py prueft, ob eine Norm
noch existiert, und kann das nur fuer deutsches Bundesrecht, weil
gesetze-im-internet.de aufgehobene Vorschriften paragraphengenau als
"(weggefallen)" markiert. Fuer EU-Recht gibt es kein solches Signal -- EUR-Lex
antwortet auf maschinelle Zugriffe mit einer JS-Challenge, und der Cellar-
SPARQL-Endpunkt indexiert nur konsolidierte Fassungen, nicht die Basis-Akte.
In einem europarechtlich gepraegten Wiki liegt damit die Mehrzahl der
Ankerseiten ausserhalb jeder Pruefung.

EU-Recht scheitert ohnehin anders. Verordnungen werden selten aufgehoben; sie
gelten gestaffelt. Zwischen Inkrafttreten und Anwendbarkeit koennen Jahre liegen,
und beim Ueberschreiten einer Stufe aendert sich der Aussagegehalt einer Seite,
ohne dass sich am Normtext ein Zeichen aendert. Der EU AI Act ist in vier Stufen
anwendbar geworden (02.02.2025 Verbote, 02.08.2025 GPAI, 02.08.2026 Hochrisiko,
02.08.2027 Anhang I).

Genau dafuer fuehrt das Schema `in_kraft:` und `wirksam_ab:` -- bislang ungeprueft.
Dieses Werkzeug prueft sie. Vollstaendig lokal, ohne Netzzugriff, damit es auch
offline und beliebig oft laeuft.

Befunde:
  S1  wirksam_ab liegt in der Zukunft, die Seite sagt das nicht
      -> kuenftiges Recht wird als geltendes dargestellt
  S2  Staffelstufe wurde seit dem letzten rechtsstand ueberschritten
      -> Seite wurde zuletzt geprueft, als die Norm noch nicht anwendbar war
  S3  wirksam_ab liegt vor in_kraft
      -> unplausibel, Wirksamkeit kann der Geltung nicht vorausgehen
  S4  Knoten ohne wirksam_ab, waehrend Geschwister desselben Rechtsakts eines fuehren
      -> Staffelung unvollstaendig gepflegt
  S5  Normknoten ganz ohne in_kraft und wirksam_ab (Feldluecke, niedrige Schwere)
      Urteilsknoten sind ausgenommen, sie tragen diese Felder definitionsgemaess nicht.

Ausserdem eine Vorschau der naechsten anstehenden Stufen: Sie sagt, wann der
naechste Lauf faellig ist.

Das Stichdatum ist standardmaessig HEUTE. Ein Waechter mit eingefrorenem Datum
waere sinnlos -- er wuerde das Ueberschreiten einer Stufe nie bemerken.

Aufruf:  python3 staffelung_check.py [WIKI-ROOT] [--datum YYYY-MM-DD]
"""
import os, re, io, sys, datetime, collections

EXCLUDE = {"Persönlich", "Werkzeuge"}

# Formulierungen, mit denen eine Seite kenntlich macht, dass sie kuenftiges Recht
# beschreibt. Bewusst weit gefasst: ein Fehlalarm kostet einen Blick, ein
# uebersehener Fall kostet eine falsche Aussage.
SAGT_KUENFTIG = re.compile(
    r'noch\s+nicht\s+(?:anwendbar|anzuwenden|wirksam|in\s+geltung)'
    r'|(?:gilt|gelten|anwendbar|anzuwenden|wirksam)\s+(?:erst\s+)?ab'
    r'|ab\s+dem\s+\d{1,2}\.\s*\d{1,2}\.\s*\d{4}'
    r'|wird\s+(?:erst\s+)?(?:ab|zum)\s'
    r'|künftig|zukünftig|übergangsfrist|geltungsbeginn|anwendungsbeginn',
    re.I)

# Urteilsknoten tragen in_kraft/wirksam_ab definitionsgemaess nicht und muessen
# ausgenommen werden. Das ecli:-Feld allein genuegt zur Erkennung NICHT: ein
# grosser Teil der Entscheidungsknoten fuehrt kein ECLI (BVerfGE-Zitate, aeltere
# BGH-Aktenzeichen). Ohne diese Namenserkennung meldet S5 Urteile als Feldluecke.
IST_URTEIL = re.compile(
    r'^(?:BVerfGE|BVerwGE|BGHZ|BGHSt|BAGE|BSGE)\b'
    r'|^(?:BVerfG|BVerwG|BGH|BAG|BSG|BFH|EuGH|EuG|EGMR|OLG|OVG|VGH|LG|KG|AG|VG|LAG)\b'
    r'|\b[CT]-\d+[-/]\d+\b'                      # EuGH/EuG-Rechtssachen C-311/18
    r'|\b\d+\s+[A-Z]{1,3}\s?[A-Za-z]*\s\d+[-/]\d+\b'  # Aktenzeichen 1 BvR 16/13
)

def datum(s):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', s or "")
    return datetime.date(*map(int, m.groups())) if m else None

def anker(wiki):
    """Ankerseiten = Wiki-Seiten mit rang: im Frontmatter."""
    out = []
    for dp, dn, fn in os.walk(wiki):
        dn[:] = [d for d in dn if not d.startswith(".") and d not in EXCLUDE]
        for f in fn:
            if not f.endswith(".md"):
                continue
            p = os.path.join(dp, f)
            t = io.open(p, encoding="utf-8").read()
            if not t.startswith("---") or "type: wiki-page" not in t.split("---")[1]:
                continue
            fm = t.split("---")[1]
            if not re.search(r'^rang:', fm, re.M):
                continue
            g = lambda k: (re.search(r'^%s:\s*"?([^"\n]*)"?\s*$' % k, fm, re.M) or [None, ""])[1].strip()
            body = t.split("---", 2)[-1]
            out.append(dict(
                name=f[:-3], rel=os.path.relpath(p, wiki), rang=g("rang"),
                ik=datum(g("in_kraft")), wa=datum(g("wirksam_ab")),
                rs=datum(g("rechtsstand")),
                ik_roh=g("in_kraft"), wa_roh=g("wirksam_ab"), rs_roh=g("rechtsstand"),
                ecli=g("ecli"), sagt=bool(SAGT_KUENFTIG.search(body)),
                urteil=bool(g("ecli")) or bool(IST_URTEIL.search(f[:-3]))))
    return out

def rechtsakt(name):
    """Gruppiert Knoten nach Rechtsakt: alles vor 'Art.' bzw. '§'."""
    return re.split(r'\s+(?:Art\.|§§?)\s*', name)[0].strip()

def main():
    roh = sys.argv[1:]
    m = re.search(r'--datum[= ](\d{4}-\d{2}-\d{2})', " ".join(roh))
    heute = datum(m.group(1)) if m else datetime.date.today()
    # Den Datumswert aus den Positionsargumenten entfernen, sonst wird er als
    # Wiki-Wurzel gelesen und der Lauf findet null Seiten.
    weg = {m.group(1)} if m else set()
    args = [a for a in roh if not a.startswith("--") and a not in weg]
    wiki = args[0] if args else "/PFAD/ZU/DEINEM/VAULT/[WIKI-ORDNER]"

    ks = anker(wiki)
    norm = [k for k in ks if not k["urteil"]]
    print("Staffelungs-Abgleich (Geltung vs. Wirksamkeit) -- rein lokal, kein Netzzugriff")
    print("Stichdatum: %s" % heute)
    print("Ankerseiten: %d  ·  davon Normknoten: %d  ·  Urteilsknoten: %d\n"
          % (len(ks), len(norm), len(ks) - len(norm)))

    # ---------------------------------------------------------------- S1
    s1 = [k for k in norm if k["wa"] and k["wa"] > heute and not k["sagt"]]
    s1ok = [k for k in norm if k["wa"] and k["wa"] > heute and k["sagt"]]
    print("=" * 78)
    print("S1  wirksam_ab in der Zukunft, Seite sagt es nicht  (%d)" % len(s1))
    print("=" * 78)
    for k in s1:
        print("   %-38s wirksam_ab=%s  (in %d Tagen)"
              % (k["name"][:38], k["wa_roh"], (k["wa"] - heute).days))
    if not s1:
        print("   keine")
    if s1ok:
        print("   nachrichtlich, korrekt gekennzeichnet: %s"
              % ", ".join(k["name"][:34] for k in s1ok))

    # ---------------------------------------------------------------- S2
    s2 = [k for k in norm if k["wa"] and k["rs"] and k["rs"] < k["wa"] <= heute]
    print("\n" + "=" * 78)
    print("S2  Staffelstufe seit dem letzten rechtsstand ueberschritten  (%d)" % len(s2))
    print("=" * 78)
    print("   Die Seite wurde zuletzt geprueft, als die Norm noch nicht anwendbar war.")
    print("   Formulierungen im Futur sind seither ueberholt.")
    for k in sorted(s2, key=lambda x: x["wa"]):
        print("   %-38s rechtsstand=%s < wirksam_ab=%s"
              % (k["name"][:38], k["rs_roh"], k["wa_roh"]))
    if not s2:
        print("   keine")

    # ---------------------------------------------------------------- S3
    s3 = [k for k in norm if k["wa"] and k["ik"] and k["wa"] < k["ik"]]
    print("\n" + "=" * 78)
    print("S3  wirksam_ab liegt vor in_kraft  (%d)" % len(s3))
    print("=" * 78)
    for k in s3:
        print("   %-38s in_kraft=%s  wirksam_ab=%s" % (k["name"][:38], k["ik_roh"], k["wa_roh"]))
    if not s3:
        print("   keine")

    # ---------------------------------------------------------------- S4
    akt = collections.defaultdict(list)
    for k in norm:
        akt[rechtsakt(k["name"])].append(k)
    s4 = []
    for a, gruppe in akt.items():
        mit = [x for x in gruppe if x["wa"]]
        ohne = [x for x in gruppe if not x["wa"]]
        if mit and ohne and len(gruppe) > 1:
            stufen = sorted({x["wa_roh"] for x in mit})
            for x in ohne:
                s4.append((x, a, len(mit), stufen))
    print("\n" + "=" * 78)
    print("S4  Knoten ohne wirksam_ab, Geschwister desselben Akts fuehren eines  (%d)" % len(s4))
    print("=" * 78)
    for x, a, n, stufen in sorted(s4, key=lambda y: -y[2]):
        print("   %-38s %s: %d Geschwister mit Staffelung" % (x["name"][:38], a, n))
        print("      vorhandene Stufen: %s" % ", ".join(stufen))
    if not s4:
        print("   keine")

    # ---------------------------------------------------------------- S5
    s5 = [k for k in norm if not k["ik"] and not k["wa"]]
    print("\n" + "=" * 78)
    print("S5  Normknoten ohne in_kraft und ohne wirksam_ab  (%d)" % len(s5))
    print("=" * 78)
    print("   Niedrige Schwere: bei zeitlich unauffaelligen Normen vertretbar.")
    nach_rang = collections.Counter(k["rang"] for k in s5)
    print("   nach Rang: %s" % ("  ".join("Rang %s: %d" % (r, n) for r, n in sorted(nach_rang.items())) or "—"))
    for k in sorted(s5, key=lambda x: (x["rang"], x["name"]))[:14]:
        print("     Rang %-3s %s" % (k["rang"], k["name"][:56]))
    if len(s5) > 14:
        print("     ... und %d weitere" % (len(s5) - 14))

    # ---------------------------------------------------------------- Vorschau
    kommend = sorted({k["wa"] for k in norm if k["wa"] and k["wa"] > heute})
    print("\n" + "=" * 78)
    print("VORSCHAU  naechste Staffelstufen")
    print("=" * 78)
    if kommend:
        for d in kommend[:6]:
            betroffen = [k["name"] for k in norm if k["wa"] == d]
            print("   %s  (in %4d Tagen)  %d Knoten: %s"
                  % (d, (d - heute).days, len(betroffen),
                     ", ".join(n[:30] for n in betroffen[:3]) + (" ..." if len(betroffen) > 3 else "")))
        print("\n   Naechster faelliger Lauf: %s" % kommend[0])
    else:
        print("   keine kuenftige Stufe im Bestand hinterlegt")

    print("\n" + "=" * 78)
    print("ZUSAMMENFASSUNG")
    print("=" * 78)
    print("   S1 kuenftiges Recht als geltend:      %d" % len(s1))
    print("   S2 Stufe seit Pruefung ueberschritten: %d" % len(s2))
    print("   S3 wirksam_ab vor in_kraft:           %d" % len(s3))
    print("   S4 Staffelung unvollstaendig:         %d" % len(s4))
    print("   S5 Feldluecke (niedrige Schwere):     %d" % len(s5))
    print("\n   Was dieses Werkzeug NICHT prueft: ob der Normtext sich geaendert hat.")
    print("   Es prueft nur die Zeitachse gegen die eigenen Frontmatter-Angaben.")

if __name__ == "__main__":
    main()
