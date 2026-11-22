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
| `wiki_integrity_check.py` | citekeys gegen Zotero, **tatsächlich extrahierbarer** Volltext, ECLI-Syntax, Normen ohne Knoten | lokale Zotero-API |
| `knoten_check.py` | `resource:`-URIs auflösbar, Alter des `rechtsstand:`, fehlende Anker-Felder | ja |
| `normtext_check.py` | Normknoten gegen die amtliche konsolidierte Fassung: Wegfall, Fassungsangabe | ja |
| `staffelung_check.py` | `in_kraft:` gegen `wirksam_ab:`: gestaffelte Anwendbarkeit, überschrittene Stufen | **nein** |
| `rang_check.py` | `[!recht]`-Callouts: Gericht als Normkategorie, Rang gegen Leitnorm, Etikettvarianten | **nein** |

## Aufruf

```bash
python3 tools/wiki_integrity_check.py /pfad/zum/vault/WIKI-ORDNER
python3 tools/knoten_check.py         /pfad/zum/vault/WIKI-ORDNER
python3 tools/normtext_check.py       /pfad/zum/vault/WIKI-ORDNER
python3 tools/staffelung_check.py     /pfad/zum/vault/WIKI-ORDNER
python3 tools/staffelung_check.py     /pfad/zum/vault/WIKI-ORDNER --datum=2027-08-02
python3 tools/rang_check.py           /pfad/zum/vault/WIKI-ORDNER
```

`wiki_integrity_check.py` setzt ein laufendes Zotero mit lokaler API auf Port 23119
voraus. `knoten_check.py` und `normtext_check.py` brauchen Netzzugang.
`staffelung_check.py` läuft vollständig offline; `--datum` verschiebt das Stichdatum
und beantwortet damit die Frage, was sich am Tag einer künftigen Staffelstufe ändert.
`rang_check.py` läuft ebenfalls offline und braucht nichts als die Markdown-Dateien.

## Warum es keine Pruefsumme gibt

Die naheliegende Erweiterung waere ein Hash ueber den Normtext, der `rechtsstand:`
von einer Zusage in eine Pruefung verwandelt (so RuML 1.0.0 Kap. 4.12 mit SHA3-256
ueber die kanonisierte Form). **Am 2026-11-19 geprueft und verworfen.**

Der Grund ist `normtext_check.py` selbst: Es prueft die deutschen Normknoten gegen die
amtliche konsolidierte Fassung und erkennt Wegfall **paragraphengenau**. Ein Hash fuegt
dort allein die Erkennung von *Aenderungen* statt *Wegfall* hinzu — zu wenig fuer den
Preis aus Kanonisierungsregel, Erheblichkeitsdefinition und Dauerrauschen. Ein Hash sagt,
*dass* sich etwas geaendert hat, nicht *ob es erheblich ist*; redaktionelle Korrektur und
Tatbestandsaenderung erzeugen denselben Befund.

**Zwei Begruendungen, die unterwegs auftauchten und beide nicht tragen** — hier notiert,
damit sie beim naechsten Anlauf nicht erneut als Argument erscheinen:

- *"Erst wenn LegalDocML.de die GUID-Erhaltung verbindlich regelt."* Verwechselt zwei
  Dinge. Die GUID leistet Identitaet ueber Fassungen hinweg, ein Hash leistet
  Aenderungserkennung. Loest der Anker nach einer Umnummerierung nicht mehr auf, **ist das
  das Signal** — "an dieser Norm hat sich strukturell etwas geaendert" —, nicht sein Ausfall.
- *"EU-Normtext ist maschinell nicht erreichbar."* Gilt fuer EUR-Lex-HTML (HTTP 202,
  JS-Challenge), nicht fuer Cellar: `<manifestation>/DOC_2` mit
  `Accept: application/xhtml+xml` liefert die konsolidierte Fassung mit 198 `art_*`-IDs.
  Der Zugriff war nie der Engpass.

**Dokumentierte Restluecke.** `normtext_check.py` deckt **EU-Recht nicht ab** und konnte es
nie — es beruht auf dem `(weggefallen)`-Marker, den EU-Recht nicht kennt. Fuer EU-Normknoten
bleibt Aenderungserkennung damit **quellengetrieben**: Sie greift, wenn eine
Aenderungsverordnung in der Literaturverwaltung landet und ingested wird. Das hat am
2026-11-18 funktioniert (Digital-Omnibus-Verordnung, rund 70 Aenderungen am AI Act), haengt
aber daran, dass die Quelle ankommt. Versagt dieser Pfad einmal, ist dieser Abschnitt der
Ort, an dem nachzusehen waere.

## Warum Geltung und Wirksamkeit ein eigenes Werkzeug brauchen

`normtext_check.py` funktioniert, weil `gesetze-im-internet.de` aufgehobene
Vorschriften **paragraphengenau** als „(weggefallen)" markiert. Für EU-Recht existiert
kein vergleichbares Signal. Drei Zugänge wurden geprüft, alle drei scheiden aus:

| Zugang | Ergebnis |
|---|---|
| EUR-Lex HTML (auch über ELI und LexUriServ) | HTTP 202, JS-Challenge — die Statuszeile „No longer in force" ist maschinell nicht erreichbar |
| Cellar REST, `Accept: application/rdf+xml` | HTTP 200, aber ohne Geltungsprädikat im ausgelieferten Rumpf |
| Cellar SPARQL-Endpunkt | erreichbar, indexiert für **Rechtsakte** aber nur **konsolidierte** CELEX (`02016R0679-20160504`); Basis-Akte liefern null Treffer, damit kein `in-force`, kein `end-of-validity`. **Für Rechtsprechung gilt das nicht** — s. Abschnitt unten |

### Nachtrag 2026-11-19: Für Rechtsprechung trägt Cellar doch

Der Negativbefund oben war zu breit formuliert. Er gilt für **Rechtsakte** — dort
indexiert Cellar nur konsolidierte Fassungen. Für **Rechtsprechung** liefert derselbe
Endpunkt das Prädikat `cdm:case-law_ecli` und damit eine belastbare ECLI-Verifikation:

```bash
curl -s -G "https://publications.europa.eu/webapi/rdf/sparql" \
  --data-urlencode "query=PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
    SELECT DISTINCT ?celex ?d WHERE {
      ?w cdm:case-law_ecli 'ECLI:EU:C:2023:957'^^<http://www.w3.org/2001/XMLSchema#string> .
      ?w cdm:resource_legal_id_celex ?celex .
      OPTIONAL { ?w cdm:work_date_document ?d }
    } LIMIT 1" \
  --data-urlencode "format=application/sparql-results+json"
# → 62021CJ0634, 2023-12-07  (C-634/21 SCHUFA)
```

Am 2026-11-19 gegen den Bestand getestet: **10 von 10 EuGH-ECLI bestätigt**, CELEX-Nummer
und Entscheidungsdatum stimmten durchweg mit der Knotenbezeichnung überein. Das schließt
die Lücke, die für EuGH-Entscheidungen bestand, seit EUR-Lex nicht mehr erreichbar ist.

**Volltext einer EuGH-Entscheidung, in einer bestimmten Sprache** (gelöst 2026-11-20):

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX cmr: <http://publications.europa.eu/ontology/cdm/cmr#>
SELECT ?m WHERE {
  ?w cdm:resource_legal_id_celex '62023CJ0416'^^xsd:string .
  ?e cdm:expression_belongs_to_work ?w ; cmr:lang ?l .
  FILTER(STR(?l) = 'deu')
  ?m cdm:manifestation_manifests_expression ?e ; cdm:manifestation_type ?t .
  FILTER(STR(?t) = 'xhtml')
}
```
Danach `<manifestation>/DOC_1` mit `Accept: application/xhtml+xml`.

**Drei Stolpersteine, an denen zwei Anläufe gescheitert sind:**
1. Das Sprachprädikat liegt im Namensraum **`cdm/cmr#`**, nicht in `cdm#`, und heißt dort
   `lang` — also `cmr:lang`, nicht `cdm:lang` und nicht `cdm:expression_uses_language`.
   Sein Wert ist ein **schlichtes Stringliteral** (`'deu'`, daneben `'de'`), **keine
   Sprach-URI** aus dem Authority-Vokabular. Beide Fehlformen liefern null Treffer,
   **ohne zu scheitern** — der naheliegende Fehlschluss ist dann, Cellar könne keine
   Sprachauswahl. (Diese Korrektur am 2026-11-22: Die erste hier dokumentierte Fassung
   nannte `cdm:lang` mit URI-Filter und funktionierte deshalb nicht.)
2. `cdm:manifestation_type 'xhtml'` als getyptes Literal matcht nicht zuverlässig;
   `FILTER(STR(?t)='xhtml')` schon.
3. Der Text liegt unter `<manifestation>/DOC_1` **oder** `/DOC_2`. Die Manifestations-URI
   selbst liefert nur RDF-Metadaten, nicht den Text.

Ohne Sprachfilter bekommt man eine beliebige der rund 25 Fassungen — im Testlauf war es
Irisch. Für Zahlen-, Tenor- und Randnummernprüfung genügt jede Fassung; für wörtliche
Zitate nicht.

Zwei Einschränkungen: Die Abfrage braucht einen **gebundenen Gegenstand** (ECLI oder
CELEX) — unbeschränkte Prädikatssuchen laufen in den Timeout. Und sie verifiziert eine
**vorhandene** ECLI; sie findet keine fehlende. Die Richtung Aktenzeichen → ECLI bleibt
unscharf und darf nicht automatisiert werden.

Für deutsche Entscheidungen ist das Gegenstück `testphase.rechtsinformationen.bund.de/v1/rechtsprechung`.
Dort trägt **nicht nur `ecli`**, sondern auch die Kombination **`fileNumber` + `court`**:

```bash
curl -s -G "https://testphase.rechtsinformationen.bund.de/v1/rechtsprechung" \
  --data-urlencode "fileNumber=VI ZR 277/22" --data-urlencode "size=5"
# → ECLI:DE:BGH:2023:121223BVIZR277.22.0
```

Das korrigiert eine ältere Einschätzung: Die Richtung Aktenzeichen → Entscheidung galt als
unbrauchbar, weil `searchTerm="1 BvR 209/83"` 468 Treffer lieferte. Das ist ein Befund über
`searchTerm`, nicht über die API — der dedizierte `fileNumber`-Filter trifft punktgenau.
Am 2026-11-19 über 45 Fundstellen aus dem Bestand geprüft: 20 bestätigt, 0 Fehltreffer.

**Die Trefferquote ist selbst ein Befund und muss so gelesen werden.** Bestätigt wurden
ausschließlich Bundesgerichte (BGH, BVerfG, BVerwG, BAG, BFH), nicht getroffen ausschließlich
Instanzgerichte (OLG, LG, AG, VG). Der Bestand des Portals ist bundesgerichtszentriert und
beginnt etwa bei 2010. Ein Nulltreffer ist deshalb `nicht prüfbar`, **niemals** `erfunden` —
wer das verwechselt, erzeugt aus einer Bestandsgrenze eine Falschbeschuldigung gegen den
eigenen Bestand. Und weiterhin gilt: Aus einem Nulltreffer darf keine ECLI erschlossen werden.

Vorsicht bei der Auswertung: `fileNumber` matcht auch quer über Gerichtsbarkeiten. „6 S 21/21"
traf ein BSG-Verfahren, „15 W 13/26" ein BPatG-Verfahren. Das Gericht des Treffers ist deshalb
gegen das zitierte Gericht abzugleichen, sonst zählt man Zufallstreffer als Bestätigung.
Dessen Bestand beginnt etwa bei 2010: Lüth (1958), Spiegel (1966) und Volkszählung (1983)
liefern null Treffer. Das ist ein Befund über den Bestand, **nicht über die ECLI** — solche
Fälle gehören als `nicht prüfbar` geführt, nicht als Fehler.

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

- **`EXCLUDE`** in allen vieren: Ordner innerhalb des Wiki-Ordners, die nicht zum Wiki gehören.
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

Sechs Punkte, die beim Nachbau Zeit sparen:

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
5. **Ein PDF-Attachment ist noch kein Volltext.** Die naheliegende Prüfung, ob eine
   Quelle belegprüfbar ist, fragt nach einem PDF- oder HTML-Attachment. Sie geht fehl,
   sobald das PDF ein Scan ohne OCR-Ebene ist: Die Datei liegt vor, liefert aber null
   Zeichen. Im Betrieb betraf das fünf zitierte Quellen, darunter die einzige tragende
   Quelle eines ganzen Kernabschnitts, und der Verifier meldete dort folgerichtig
   „nicht prüfbar", während der Integritäts-Check dieselbe Quelle als versorgt führte.
   Die Prüfung muss deshalb `pdftotext` gegen die Datei laufen lassen. Umgekehrt gilt:
   Ein leerer Volltext-Cache der Literaturverwaltung beweist **nicht**, dass die
   Textebene fehlt — er kann schlicht nicht aufgebaut worden sein. Auch hier trennt
   erst der Blick in die Datei die beiden Fälle.

   Behebbar ist der Scan-Fall mechanisch: `ocrmypdf --language deu --skip-text <pdf>
   <pdf-neu>`. Das Werkzeug weist die betroffenen Quellen deshalb als eigene Klasse
   aus, statt sie mit den Quellen ohne Attachment zu vermengen, denn die einen lassen
   sich in Minuten erschließen und die anderen gar nicht.
6. **Ein Wächter mit eingefrorenem Stichdatum ist keiner.** Die anderen Werkzeuge dürfen
   ein festes Datum tragen, weil sie gegen eine externe Quelle prüfen. Dieses prüft gegen
   den Kalender: Es nimmt `date.today()`, sonst bemerkt es das Überschreiten einer Stufe
   nie. Vor der Übernahme empfiehlt sich ein Lauf mit `--datum` auf ein Datum jenseits der
   nächsten Stufe — ein Prüfwerkzeug, das nie auslöst, sieht von einem funktionierenden
   nicht zu unterscheiden aus.

## Was sie nicht können

`wiki_integrity_check.py` setzt für die Volltextprüfung `pdftotext` (Poppler) voraus
und erwartet den Attachment-Speicher unter `~/Zotero/storage`. Fehlt eines von beidem,
fällt die Prüfung auf die alte Attachment-Heuristik zurück, statt falsche Befunde zu
erzeugen.

Keines der Werkzeuge prüft, ob eine Aussage inhaltlich zutrifft. `normtext_check.py`
erkennt, dass eine Norm weggefallen ist, nicht ob die Auslegung auf der Seite stimmt.
`staffelung_check.py` prüft die Zeitachse gegen die eigenen Frontmatter-Angaben — ist
ein `wirksam_ab:` von vornherein falsch eingetragen, bestätigt er diesen Fehler
widerspruchsfrei. Er meldet Unstimmigkeit, nicht Unrichtigkeit.

`rang_check.py` kann einen Callout nur prüfen, wenn er eine **Norm nennt**. Steht dort
allein eine Entscheidung (`· EuGH C-131/12 (Google Spain)`), fehlt ihm der Anknüpfungs-
punkt und er schweigt. Im Referenzbestand stand genau dort jahrelang Rang 2, obwohl das
Urteil zur Richtlinie 95/46/EG erging und damit Rang 3 ist. Callouts ohne Normangabe
bleiben Handarbeit — das Werkzeug verengt die Prüffläche, es ersetzt sie nicht.

Die Grenze ist dieselbe wie beim Verifikations-Pass: geprüft wird Belegtheit und
Aktualität, nicht Richtigkeit.
