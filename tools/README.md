# tools

Mechanische Prüfwerkzeuge für das LLMWiki. Kein LLM, keine Abhängigkeiten außer der
Python-Standardbibliothek, Laufzeit im Sekundenbereich. Sie prüfen Dinge, die ein
Sprachmodell nicht zuverlässig prüft, und sind billig genug für den Dauerbetrieb.

**Warum getrennt vom Verifikations-Pass:** Der Verifikations-Pass prüft *Belegtheit*
gegen die Literaturverwaltung. Er erfasst nur Seiten mit Quellenangaben. Normknoten
führen definitionsgemäß `quellen: []` und fallen durch sein Raster. Für sie ist der
Abgleich gegen die amtliche Fassung die einzige Prüfung.

| Werkzeug | Prüft | Netz |
|---|---|---|
| `wiki_integrity_check.py` | citekeys gegen Zotero, Volltextlage, ECLI-Syntax, Normen ohne Knoten | lokale Zotero-API |
| `knoten_check.py` | `resource:`-URIs auflösbar, Alter des `rechtsstand:`, fehlende Anker-Felder | ja |
| `normtext_check.py` | Normknoten gegen die amtliche konsolidierte Fassung: Wegfall, Fassungsangabe | ja |

## Aufruf

```bash
python3 tools/wiki_integrity_check.py /pfad/zum/vault/WIKI-ORDNER
python3 tools/knoten_check.py         /pfad/zum/vault/WIKI-ORDNER
python3 tools/normtext_check.py       /pfad/zum/vault/WIKI-ORDNER
```

`wiki_integrity_check.py` setzt ein laufendes Zotero mit lokaler API auf Port 23119
voraus. Die beiden anderen brauchen Netzzugang.

## Anpassung an die eigene Lage

- **`EXCLUDE`** in allen dreien: Ordner innerhalb des Wiki-Ordners, die nicht zum Wiki gehören.
- **`GESETZE`** in `normtext_check.py`: Zuordnung von Gesetzeskürzeln zu Portal-Slugs.
  Die mitgelieferte Tabelle gilt für deutsches Bundesrecht auf `gesetze-im-internet.de`.
  EU-Recht, Staatsverträge und Konventionsrecht liegen dort nicht und werden übersprungen.
  Für andere Rechtsordnungen ist diese Tabelle samt `BASIS`-URL zu ersetzen.

## Erfahrungen aus dem Betrieb

Drei Punkte, die beim Nachbau Zeit sparen:

1. **Jeder Befund braucht eine Gegenprobe, bevor er zu einer Handlung führt.** Beim
   ersten Einsatz produzierten alle drei Werkzeuge Fehlalarme: ein ECLI-Muster, das für
   Gerichtskürzel nur Großbuchstaben zuließ und damit jede deutsche ECLI traf; ein
   citekey-Muster, das am Punkt abbrach; eine URL-Prüfung per HEAD, die amtliche Server
   als tot meldete, die auf GET mit 200 antworten. Alle drei Ursachen sind im Code
   kommentiert.
2. **Historie ausnehmen.** `log.md` und `index.md` dürfen von Korrekturläufen nicht
   erfasst werden. Ein Protokoll hält fest, was damals geschah, und wird nicht
   nachträglich geglättet.
3. **HTML-Entities vor dem Vergleich auflösen.** `gesetze-im-internet.de` liefert `§`
   als `&#167;`; ein Muster auf `§` findet dort nichts.

## Was sie nicht können

Keines der Werkzeuge prüft, ob eine Aussage inhaltlich zutrifft. `normtext_check.py`
erkennt, dass eine Norm weggefallen ist, nicht ob die Auslegung auf der Seite stimmt.
Die Grenze ist dieselbe wie beim Verifikations-Pass: geprüft wird Belegtheit und
Aktualität, nicht Richtigkeit.
