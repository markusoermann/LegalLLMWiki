#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rangpruefung der [!recht]-Callouts.

Prueft ohne LLM und ohne Netz, rein textbasiert, drei Dinge:

  FEHLER  A  Gericht als Normkategorie
             Die Klammer nennt BGH, OLG, VG statt einer Normkategorie. Der Rang
             folgt der Norm, nicht dem Spruchkoerper - auch dann, wenn ein
             nationales Gericht Unionsrecht anwendet.
  FEHLER  B  Rang-Zahl widerspricht der Leitnorm
             Die Zahl passt nicht zu der Norm, auf die sich die Aussage stuetzt.
  INFO    C  Nicht-kanonisches Rangetikett
             Zahl und Kategorie stimmen, nur die Bezeichnung weicht ab. Keine
             Falschaussage, sondern ein Synonym - getrennt ausgewiesen, weil es
             sonst die echten Fehler verdeckt.

Warum A und B Fehler sind und nicht Warnungen: Der Rang ist ein
Klassifikationsfeld in kontrolliertem Vokabular, kein Kommentar. Ein falscher
Wert behauptet etwas, das nicht stimmt, und macht das Feld fuer Abfragen
unbrauchbar - dieselbe Defektklasse wie ein Index-Eintrag ohne Datei.

Sechs Fallen stecken als Kommentar im Code. Jede davon hat beim Erstlauf gegen
einen realen Bestand zugeschlagen und zusammen zwei Drittel der Erstbefunde als
Fehlalarm der Regel selbst entlarvt. Wer die Heuristik anpasst, sollte sie
kennen - sie sind der eigentliche Inhalt dieses Skripts.

Aufruf:  python3 rang_check.py [WIKI-ROOT]
Voraussetzung: keine. Laeuft offline auf den Markdown-Dateien.
"""
import os, re, sys, collections

WIKI = sys.argv[1] if len(sys.argv) > 1 else "/PFAD/ZU/DEINEM/VAULT/[WIKI-ORDNER]"
EXCLUDE = {"Persönlich", "Werkzeuge"}
SKIP_FILES = {"wiki-schema.md", "log.md"}   # Schema und Protokoll zitieren Callouts, tragen aber keine

CALLOUT = re.compile(r"⚖️ Rang (\d) \(([^)]*)\)([^\n]*)")

# Gerichte und Instanzen. Bewusst auch die ausgeschriebenen Formen: im Bestand
# fanden sich "Bundesgesetz/Landgericht" und "Bundesgesetz/VG".
COURTS = (r"(BGH|BVerwG|BAG|BFH|BSG|BVerfG|OLG|OVG|VGH|LG|VG|AG|KG|EuGH|EGMR|OGH"
          r"|Bundesgericht|Landgericht|Oberlandesgericht|Verwaltungsgericht"
          r"|Instanzgericht|Hoechstgericht|Höchstgericht)")
COURT_ANY  = re.compile(COURTS + r"\b")
COURT_LEAD = re.compile(r"^\s*" + COURTS + r"\b")

# Kanonisches Vokabular je Rang. Mehrere Eintraege, wo ein Rang mehrere
# Normkategorien traegt. Praezisierende Zusaetze nach " — " sind zulaessig.
KANON = {
    1: ["EU-Primärrecht"],
    2: ["EU-Sekundärrecht — Verordnung"],
    3: ["EU-Richtlinie"],
    4: ["Verfassungsrecht"],
    5: ["Bundesgesetz", "Staatsvertrag der Länder",
        "Völkerrechtlicher Vertrag", "Völkerrecht — allgemeine Regel"],
    6: ["Landesgesetz", "Landesrecht"],
}

# Normerkennung. Die Reihenfolge in dieser Liste ist KEINE Prioritaet - gewertet
# wird die textlich erste Fundstelle (s. Falle 2). Richtlinien stehen trotzdem
# vor Verordnungen, weil "RL (EU) 2024/2831" beide Muster enthalten kann.
PATTERNS = [
    (r"\bEMRK\b|\bZP I\b|Genfer Abkommen|UN-Charta",                      5),
    (r"-RL\b|\bRichtlinie\b|RL \d|RL \(EU\)|RL \(EG\)",                   3),
    (r"\bDSGVO\b|\bDSA\b|\bDMA\b|AI Act|KI-VO|VO \(EU\)|VO \(EG\)",       2),
    (r"\bGRCh\b|\bGRC\b|\bAEUV\b|\bEUV\b",                                1),
    (r"\bGG\b|\bAPR\b",                                                   4),
    (r"\bLPG\b|Landesrecht|Landespresse|Prüfungsordnung|MBO-Ä",           6),
    (r"\bMStV\b|\bRStV\b|\bGlüStV\b",                                     5),
    (r"UWG|UrhG|BGB|StGB|ZPO|StPO|TDDDG|TTDSG|IFG|BBG|DDG|TMG|KUG"
     r"|UrhDaG|BDG|GWB|BVerfGG|TKG|SGB|VwGO|BetrVG|FlugDaG",              5),
]


def rang_der_leitnorm(segment):
    """Rang der textlich ERSTEN Norm im Segment, oder None."""
    # Falle 3: "Rechtsverordnung" enthaelt "Verordnung". Ohne diese Zeile wird
    # jede deutsche Rechtsverordnung zur EU-Verordnung.
    segment = re.sub(r"Rechtsverordnung", "", segment)
    treffer = []
    for muster, rang in PATTERNS:
        m = re.search(muster, segment)
        if m:
            treffer.append((m.start(), rang))
    # Falle 2: Bei i.V.m.-Ketten entscheidet die Textposition, nicht die Liste.
    # "UrhG § 11 i.V.m. GG Art. 14" ist Rang 5, nicht Rang 4.
    return min(treffer)[1] if treffer else None


def leitnorm_segment(rest):
    """Das Stueck Text, in dem die Leitnorm steht.

    Falle 1 - der folgenreichste Fehler. Das Format lautet
        · [Gericht/Norm] → [Referenz]
    Die Leitnorm steht also NACH dem Mittelpunkt, nicht nach dem Pfeil; der
    Pfeil zeigt auf die Folge oder die Fundstelle:
        · Art. 3 RL 2000/31/EG → implementiert in § 3 DDG
    Nur wenn nach dem Mittelpunkt ein GERICHT steht, gilt die Norm dahinter:
        · BGH, Urt. v. … → DSGVO Art. 82
    Wer das umdreht, erzeugt mehr Fehlalarme als Befunde.
    """
    seg = rest.split("·", 1)[1] if "·" in rest else rest
    # Falle 5: Bei mehreren gleichrangigen Normen zaehlt die erste. Nachrangige
    # sind inline annotiert ("; § 123 VwGO (Rang 5)") und duerfen nicht werten.
    erstes_glied = re.split(r"[;→]", seg)[0]
    if COURT_LEAD.match(erstes_glied.strip()):
        if "→" in seg:
            return re.split(r";", seg.split("→", 1)[1])[0]
        return erstes_glied
    return erstes_glied


def basis(kategorie):
    """Kategorie ohne praezisierenden Zusatz.

    Falle 6: Gerichtsnamen stehen auch INNERHALB zusammengesetzter Etiketten -
    "(Bundesgesetz/Landgericht)" ist ein Fehler, obwohl das Etikett mit einer
    gueltigen Kategorie beginnt. Umgekehrt sind Zusaetze nach " — " zulaessig:
    "(Verfassungsrecht — BVerfG-Grundsatzurteil)" ist korrekt. Geprueft wird
    deshalb nur der Teil vor dem Gedankenstrich.
    """
    return kategorie.split(" — ")[0].strip()


def ist_kanonisch(rang, kategorie):
    return any(kategorie == k or kategorie.startswith(k + " — ")
               for k in KANON.get(rang, []))


def seiten(wurzel):
    for pfad, dirs, dateien in os.walk(wurzel):
        dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith(".")]
        for name in dateien:
            if not name.endswith(".md") or name in SKIP_FILES:
                continue
            voll = os.path.join(pfad, name)
            try:
                text = open(voll, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            # Falle 4: Nur Wiki-Seiten. Lernnotizen und Klausurschemata
            # enthalten Paragraphenketten und erzeugen sonst Dauerrauschen.
            if "type: wiki-page" not in text[:700]:
                continue
            yield os.path.relpath(voll, wurzel), text


def main():
    if not os.path.isdir(WIKI):
        sys.exit("Wiki-Ordner nicht gefunden: %s\nAufruf: python3 rang_check.py [WIKI-ROOT]" % WIKI)

    a, b, c = [], [], collections.Counter()
    gesamt = 0
    for rel, text in seiten(WIKI):
        for nr, zeile in enumerate(text.split("\n"), 1):
            m = CALLOUT.search(zeile)
            if not m:
                continue
            gesamt += 1
            rang, kat, rest = int(m.group(1)), m.group(2).strip(), m.group(3)

            if COURT_ANY.search(basis(kat)):
                a.append((rel, nr, kat))
                continue
            soll = rang_der_leitnorm(leitnorm_segment(rest))
            if soll and soll != rang:
                b.append((rel, nr, rang, soll, leitnorm_segment(rest).strip()[:58]))
                continue
            if not ist_kanonisch(rang, kat):
                c[(rang, kat)] += 1

    print("=" * 78)
    print("RANGPRUEFUNG  %d [!recht]-Callouts in %s" % (gesamt, WIKI))
    print("=" * 78)

    print("\nFEHLER A  Gericht als Normkategorie: %d" % len(a))
    for rel, nr, kat in a:
        print("   %s:%d  (%s)" % (rel, nr, kat))

    print("\nFEHLER B  Rang widerspricht der Leitnorm: %d" % len(b))
    for rel, nr, ist, soll, seg in b:
        print("   %s:%d  Rang %d -> %d   Leitnorm: %s" % (rel, nr, ist, soll, seg))

    print("\nINFO C  Nicht-kanonisches Rangetikett: %d" % sum(c.values()))
    for (rang, kat), n in c.most_common():
        print("   %3dx  Rang %d (%s)   kanonisch: %s"
              % (n, rang, kat, " / ".join(KANON.get(rang, ["-"]))))

    print("\n" + "=" * 78)
    print("ZUSAMMENFASSUNG")
    print("=" * 78)
    print("   A Gericht als Normkategorie : %d  (Fehler)" % len(a))
    print("   B Rang widerspricht Leitnorm: %d  (Fehler)" % len(b))
    print("   C Etikettvariante           : %d  (Info)" % sum(c.values()))
    print("\n   Was dieses Werkzeug NICHT prueft: ob der Rang sachlich richtig")
    print("   zugeordnet ist, wenn der Callout gar keine Norm nennt. Ein Callout")
    print("   wie '· EuGH C-131/12 (Google Spain)' ohne Normangabe entgeht der")
    print("   Pruefung - im Bestand stand dort jahrelang Rang 2, obwohl das")
    print("   Urteil zur Richtlinie 95/46/EG erging und damit Rang 3 ist.")
    print("   Callouts ohne Normangabe sind deshalb von Hand zu sichten.")


if __name__ == "__main__":
    main()
