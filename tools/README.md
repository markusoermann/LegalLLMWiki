# tools

Mechanische Prüfwerkzeuge für das LLMWiki. Kein LLM, keine Abhängigkeiten außer der
Python-Standardbibliothek, Laufzeit im Sekundenbereich. Sie prüfen Dinge, die ein
Sprachmodell nicht zuverlässig prüft, und sind billig genug für den Dauerbetrieb.

**Warum getrennt vom Verifikations-Pass:** Der Verifikations-Pass prüft *Belegtheit*
gegen die Literaturverwaltung. Er erfasst nur Seiten mit Quellenangaben. Normknoten
führen definitionsgemäß `quellen: []` und fallen durch sein Raster. Für sie treten
diese Werkzeuge an seine Stelle: der Abgleich gegen die amtliche Fassung, wo es eine
maschinenlesbare gibt, und der Abgleich der Zeitachse, wo es sie nicht gibt.

| Werkzeug | Prüft | Netz |
|---|---|---|
| `wiki_integrity_check.py` | citekeys gegen Zotero, Volltextlage, ECLI-Syntax, Normen ohne Knoten | lokale Zotero-API |
| `knoten_check.py` | `resource:`-URIs auflösbar, Alter des `rechtsstand:`, fehlende Anker-Felder | ja |
| `normtext_check.py` | Normknoten gegen die amtliche konsolidierte Fassung: Wegfall, Fassungsangabe | ja |
| `staffelung_check.py` | `in_kraft:` gegen `wirksam_ab:`: gestaffelte Anwendbarkeit, überschrittene Stufen | **nein** |

## Aufruf

```bash
python3 tools/wiki_integrity_check.py /pfad/zum/vault/WIKI-ORDNER
python3 tools/knoten_check.py         /pfad/zum/vault/WIKI-ORDNER
python3 tools/normtext_check.py       /pfad/zum/vault/WIKI-ORDNER
python3 tools/staffelung_check.py     /pfad/zum/vault/WIKI-ORDNER
python3 tools/staffelung_check.py     /pfad/zum/vault/WIKI-ORDNER --datum=2027-08-02
```

`wiki_integrity_check.py` setzt ein laufendes Zotero mit lokaler API auf Port 23119
voraus. `knoten_check.py` und `normtext_check.py` brauchen Netzzugang.
`staffelung_check.py` läuft vollständig offline; `--datum` verschiebt das Stichdatum
und beantwortet damit die Frage, was sich am Tag einer künftigen Staffelstufe ändert.

## Warum Geltung und Wirksamkeit ein eigenes Werkzeug brauchen

`normtext_check.py` funktioniert, weil `gesetze-im-internet.de` aufgehobene
Vorschriften **paragraphengenau** als „(weggefallen)" markiert. Für EU-Recht existiert
kein vergleichbares Signal. Drei Zugänge wurden geprüft, alle drei scheiden aus:

| Zugang | Ergebnis |
|---|---|
| EUR-Lex HTML (auch über ELI und LexUriServ) | HTTP 202, JS-Challenge — die Statuszeile „No longer in force" ist maschinell nicht erreichbar |
| Cellar REST, `Accept: application/rdf+xml` | HTTP 200, aber ohne Geltungsprädikat im ausgelieferten Rumpf |
| Cellar SPARQL-Endpunkt | erreichbar, indexiert aber nur **konsolidierte** CELEX (`02016R0679-20160504`); Basis-Akte liefern null Treffer, damit kein `in-force`, kein `end-of-validity` |

Hinzu kommt ein Granularitätsbruch: Ankerseiten liegen auf Artikelebene, der
Geltungsstatus im EU-Recht auf Aktebene. Ein Dutzend Artikelknoten kollabiert zu einer
einzigen Auskunft, die fast immer „gilt noch" lautet.

Entscheidend ist aber, dass EU-Recht ohnehin anders scheitert. Verordnungen werden
selten aufgehoben — sie gelten **gestaffelt**. Der EU AI Act wird in vier Stufen
anwendbar (02.02.2025 Verbote, 02.08.2025 GPAI, 02.08.2026 Hochrisiko, 02.08.2027
Anhang I). Beim Überschreiten einer Stufe ändert sich der Aussagegehalt einer Seite,
ohne dass sich am Normtext ein Zeichen ändert: Was gestern im Futur richtig formuliert
war, ist heute falsch. Kein Netzabgleich der Welt bemerkt das, weil sich nichts
geändert hat, das man abgleichen könnte. Prüfbar ist es nur gegen die eigene
Zeitachse — und die steht im Frontmatter.

## Anpassung an die eigene Lage

- **`EXCLUDE`** in allen dreien: Ordner innerhalb des Wiki-Ordners, die nicht zum Wiki gehören.
- **`GESETZE`** in `normtext_check.py`: Zuordnung von Gesetzeskürzeln zu Portal-Slugs.
  Die mitgelieferte Tabelle gilt für deutsches Bundesrecht auf `gesetze-im-internet.de`.
  EU-Recht, Staatsverträge und Konventionsrecht liegen dort nicht und werden übersprungen.
  Für andere Rechtsordnungen ist diese Tabelle samt `BASIS`-URL zu ersetzen.
- **`SAGT_KUENFTIG`** und **`IST_URTEIL`** in `staffelung_check.py`: beide Muster sind
  **sprachgebunden**. `SAGT_KUENFTIG` erkennt an deutschen Formulierungen, ob eine Seite
  sich selbst als künftiges Recht ausweist; `IST_URTEIL` erkennt Entscheidungsknoten an
  deutschen und europäischen Gerichtskürzeln und Aktenzeichenformaten. Wer in einer
  anderen Sprache oder Rechtsordnung schreibt, muss beide ersetzen — sonst meldet S5
  sämtliche Entscheidungen als Feldlücke.

## Erfahrungen aus dem Betrieb

Drei Punkte, die beim Nachbau Zeit sparen:

1. **Jeder Befund braucht eine Gegenprobe, bevor er zu einer Handlung führt.** Beim
   ersten Einsatz produzierte jedes Werkzeug Fehlalarme: ein ECLI-Muster, das für
   Gerichtskürzel nur Großbuchstaben zuließ und damit jede deutsche ECLI traf; ein
   citekey-Muster, das am Punkt abbrach; eine URL-Prüfung per HEAD, die amtliche Server
   als tot meldete, die auf GET mit 200 antworten. Alle drei Ursachen sind im Code
   kommentiert.
2. **Historie ausnehmen.** `log.md` und `index.md` dürfen von Korrekturläufen nicht
   erfasst werden. Ein Protokoll hält fest, was damals geschah, und wird nicht
   nachträglich geglättet.
3. **HTML-Entities vor dem Vergleich auflösen.** `gesetze-im-internet.de` liefert `§`
   als `&#167;`; ein Muster auf `§` findet dort nichts.
4. **Entscheidungsknoten nicht am `ecli:`-Feld erkennen.** Naheliegend, aber falsch: ein
   großer Teil der Entscheidungsknoten führt kein ECLI — ältere BVerfGE-Zitate, BGH-
   Aktenzeichen, Instanzgerichte. Beim ersten Lauf meldete `staffelung_check.py` deshalb
   elf Urteile als fehlende Normfelder. Die Erkennung braucht zusätzlich ein Muster auf
   Gerichtskürzel und Aktenzeichen.
5. **Ein Wächter mit eingefrorenem Stichdatum ist keiner.** Die anderen Werkzeuge dürfen
   ein festes Datum tragen, weil sie gegen eine externe Quelle prüfen. Dieses prüft gegen
   den Kalender: Es nimmt `date.today()`, sonst bemerkt es das Überschreiten einer Stufe
   nie. Vor der Übernahme empfiehlt sich ein Lauf mit `--datum` auf ein Datum jenseits der
   nächsten Stufe — ein Prüfwerkzeug, das nie auslöst, sieht von einem funktionierenden
   nicht zu unterscheiden aus.

## Was sie nicht können

Keines der Werkzeuge prüft, ob eine Aussage inhaltlich zutrifft. `normtext_check.py`
erkennt, dass eine Norm weggefallen ist, nicht ob die Auslegung auf der Seite stimmt.
`staffelung_check.py` prüft die Zeitachse gegen die eigenen Frontmatter-Angaben — ist
ein `wirksam_ab:` von vornherein falsch eingetragen, bestätigt er diesen Fehler
widerspruchsfrei. Er meldet Unstimmigkeit, nicht Unrichtigkeit.

Die Grenze ist dieselbe wie beim Verifikations-Pass: geprüft wird Belegtheit und
Aktualität, nicht Richtigkeit.
