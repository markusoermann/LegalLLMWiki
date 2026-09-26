---
type: wiki-schema
updated: 2026-09-23
---

# Wiki Schema

Technische Referenz für Claude. Wird bei jedem Ingest gelesen.

## Frontmatter-Schema

Pflichtfelder für alle Wiki-Seiten:

```yaml
---
type: wiki-page
wiki-category: konzept | entitaet | synthese
thema: [Thema1, Thema2]
quellen: ["@citekey1", "@citekey2"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
rechtsstand: YYYY-MM-DD   # optional; nur bei Seiten mit zeitkritischem juristischen Inhalt
verifiziert: YYYY-MM-DD   # optional; Datum des letzten bestandenen Verifikations-Passes (s. Abschnitt Verifikations-Pass)
---
```

### Optionale juristische Felder

Nur bei Seiten mit Rechtsbezug. Machen Normen und Entscheidungen maschinenlesbar abfragbar (ergänzen den `quellen:`-Mechanismus um die juristische Dimension).

```yaml
normen:            # maschinenlesbare Normreferenzen, je eine pro Zeile
  - "DSGVO Art. 6 Abs. 1 lit. f"
  - "EU AI Act Art. 10 Abs. 5"
urteile:           # Gerichtsentscheidungen, ECLI bevorzugt, sonst Fundstelle
  - "ECLI:DE:BVerfG:1983:rs19831215.1bvr020983"
  - "BVerfGE 65, 1"
rechtsgebiet:      # Rechtsgebiet-Klassifikation
  - Datenschutzrecht
  - KI-Recht
rang:              # nur bei Normknoten-/Leitentscheidungs-Seiten: 1–6 (s. Rechtshierarchie)
normtyp:           # nur Normknoten: Normfunktion (Hohfeld-granular) — s.u. (10 Werte, kombinierbar)
in_kraft:          # nur Normknoten: Datum des Inkrafttretens (formaler Geltungsbeginn), YYYY-MM-DD
wirksam_ab:        # nur Normknoten: Datum der Anwendbarkeit/Wirksamkeit (Beginn der Rechtsfolgen), YYYY-MM-DD
ecli:              # nur bei Leitentscheidungs-Seiten: ECLI-Identifikator
bindungswirkung:   # nur Leitentscheidungen: Gesetzeskraft | faktisch (s.u.)
resource:          # optional: stabile URI des zugrunde liegenden Rechts-Assets (ELI/ECLI/DOI)
```

**Normalisierung:** Norm-Strings einheitlich als `<Gesetz> Art./§ <N> Abs. <N> lit. <x>` (Gesetz zuerst), damit Backlinks und Abfragen nicht zersplittern. ECLI-Werte niemals erfinden — nur verifizierte Identifikatoren; sonst nur Fundstelle führen.

**`resource:` (stabile Asset-URI, OKF-Empfehlungsfeld).** Verweist auf die maschinenlesbare Primärquelle der Seite. Konventionen:
- **Normknoten:** ELI-URI — EU-Recht über `http://data.europa.eu/eli/…` (z.B. DSGVO: `http://data.europa.eu/eli/reg/2016/679/oj`), Bundesrecht über `https://recht.bund.de/eli/…`.
- **Leitentscheidungs-Seiten:** ECLI-Resolver — EuGH/EU über EUR-Lex (`https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=ecli:<ECLI>`), deutsche Gerichte über `https://www.rechtsprechung-im-internet.de` bzw. den ECLI-Resolver.
- **Quellen-/Konzeptseiten:** DOI (`https://doi.org/…`) oder Zotero-Select-Link.
- URIs nur setzen, wenn verifiziert (kein Erfinden, analog ECLI-Regel).

**`normtyp:` (Normfunktion, Hohfeld-granular).** Klassifiziert, *welche Rechtsposition* eine Norm etabliert — vollständig an der LKIF-Core-Ontologie ausgerichtet (`norm`-Modul: Deontik + Hohfeld + Expression). Kontrolliertes Vokabular:

*Deontische Modalität:*
- **Gebot** — gebietet ein Tun (LKIF `Obligation`/`Obliged`), z.B. DSGVO Art. 5.
- **Verbot** — untersagt ein Verhalten (LKIF `Prohibition`/`Disallowed`), z.B. EU AI Act Art. 5.
- **Erlaubnis** — erlaubt/rechtfertigt ein Verhalten (LKIF `Permission`/`Allowed`), z.B. DSGVO Art. 6.

*Hohfeld'sche Rechtspositionen:*
- **Anspruchsnorm** — subjektives Recht mit korrelativer Pflicht (Claim; LKIF `Right`/`Obligative_Right`/`Liability_Right`), z.B. DSGVO Art. 15, 17, 82.
- **Freiheitsrecht** — Freiheits-/Abwehrposition (Privilege/Liberty; LKIF `Liberty_Right`/`Permissive_Right`), z.B. GG Art. 5, GRCh Art. 11.
- **Kompetenznorm** — hoheitliche Ermächtigung/Zuständigkeit (Power; LKIF `Hohfeldian_Power`/`Enabling_`/`Declarative_`/`Action_Power`), z.B. GG Art. 70, DSGVO Art. 83.
- **Gestaltungsrecht** — einseitige privatrechtliche Rechtsgestaltung (potestativ; LKIF `Potestative_Right`), z.B. Kündigung, Widerruf, Anfechtung.
- **Immunität** — Schutz vor fremder Rechtsmacht / Bereichsausnahme (LKIF `Immunity`/`Exclusionary_Right`), z.B. Indemnität (Art. 46 GG), Medienprivileg.

*Funktionsnormen:*
- **Definitionsnorm** — Legaldefinition (LKIF `Definitional_Expression`), z.B. DSGVO Art. 4.
- **Qualifikationsnorm** — rechtliche Einordnung/Statuszuweisung (LKIF `Qualificatory_Expression`), z.B. Hochrisiko-Einstufung EU AI Act Art. 6.

Nur auf Normknoten-Seiten. **Kombinierbar als Liste** (z.B. `[Verbot, Erlaubnis]`; Grundrecht `[Freiheitsrecht, Gebot]` = Abwehr + Schutzpflicht). Sanktions-/Bußgeldnormen werden als `Kompetenznorm` geführt (Ermächtigung zur Sanktion). Grep-bar für `query wiki`.

**`in_kraft:` / `wirksam_ab:` (Inkrafttreten vs. Anwendbarkeit).** Das LKIF-`time-modification`-Modul trennt `In_Force_Interval` (formaler Geltungsbeginn) von `Efficacy_Interval` (tatsächlicher Beginn der Rechtsfolgen). Beide fallen oft auseinander: die DSGVO war ab 24.05.2016 *in Kraft*, aber erst ab 25.05.2018 *anwendbar*. `in_kraft:` = Inkrafttreten, `wirksam_ab:` = Anwendbarkeit/Wirksamkeit. Nur setzen, wenn die Daten divergieren oder rechtlich relevant sind; bei Gleichlauf genügt `in_kraft:` (s. Abschnitt „Geltung: Inkrafttreten vs. Wirksamkeit").

**`bindungswirkung:` (Bindungswirkung von Leitentscheidungen).** LKIF unterscheidet `Mandatory_Precedent` von `Persuasive_Precedent`. Für deutsche Verhältnisse: **Gesetzeskraft** = förmliche Bindung (BVerfG-Entscheidungen nach § 31 Abs. 1 BVerfGG, teils mit Gesetzeskraft nach § 31 Abs. 2 BVerfGG); **faktisch** = keine förmliche Bindung, aber Leitwirkung (sonstige Obergerichtsentscheidungen, EuGH-Auslegung im nationalen Kontext). Nur auf Leitentscheidungs-Seiten. Der Wert ist unabhängig vom `rang:` — der folgt der Norm, nicht der Bindungswirkung des Urteils.

## Seiten-Typen

### Konzept-Seite
- Namensschema: `[Begriff].md` (z.B. `Algorithmische Verantwortung.md`)
- Eine Seite pro Konzept/Fachbegriff
- `wiki-category: konzept`

### Entitäts-Seite
- Namensschema: `[Name].md` (z.B. `EU AI Act.md`, `Balkin Jack.md`)
- Für: Personen (Nachname Vorname), Gesetze/Verordnungen (offizielle Abkürzung), Institutionen
- `wiki-category: entitaet`

### Normknoten-Seite
- Spezialform der Entitäts-Seite für eine einzelne Leitnorm (Artikel/Paragraph)
- Namensschema: `[Gesetz] [Norm].md` (z.B. `DSGVO Art. 6.md`, `MStV § 93.md`)
- `wiki-category: entitaet`, zusätzlich `rang:` (1–6) gesetzt; optional `normtyp:`, `in_kraft:`/`wirksam_ab:`
- Struktur: Definition · Absätze/Tatbestandsmerkmale (mit Wikilinks zu Konzeptseiten) · Leitentscheidungen · Verhältnis zu anderen Normen
- Zweck: Anker-Knoten — Konzeptseiten verlinken hierauf; Backlinks ersetzen die SPARQL-Abfrage des KG-Konzepts
- Abgrenzung zur Gesetz-Entität: `DSGVO.md` beschreibt die Verordnung als Ganzes; `DSGVO Art. 6.md` ist der granulare Normknoten und verlinkt auf die Gesetz-Seite

### Leitentscheidungs-Seite
- Spezialform der Entitäts-Seite für eine Grundsatzentscheidung
- Namensschema: `[Kurzbezeichnung].md` (z.B. `BVerfGE 65,1 (Volkszählungsurteil).md`)
- `wiki-category: entitaet`, zusätzlich `rang:`, `ecli:` (wo verifiziert vorhanden), `rechtsstand:`; optional `bindungswirkung:`
- Struktur: Leitsatz · Tragende Erwägungen · Bezug zu Normen (Wikilinks) · Nachfolge-/Vorgängerentscheidungen
- Zweck: Anker-Knoten für Rechtsprechung; verknüpft Normknoten mit Konzeptseiten

### Synthese-Seite
- Namensschema: `Synthese - [Thema].md` (z.B. `Synthese - Plattformregulierung.md`)
- Themenübergreifende Zusammenführung mehrerer Quellen
- `wiki-category: synthese`

## Seiten-Template

```markdown
---
type: wiki-page
wiki-category: [konzept|entitaet|synthese]
thema: [Thema]
quellen: ["@citekey"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# [Titel]

## Definition / Überblick

## Kernaspekte

## Bezüge & Kontroversen

## Verwandte Konzepte
[[Wikilink1]] · [[Wikilink2]]

## Quellen
[[@citekey1]], [[@citekey2]]
```

## Tiefenstandard

Wiki-Seiten sollen wissenschaftlich substanziell sein — nicht nur zusammenfassen, sondern einordnen, differenzieren und vernetzen.

**Definition / Überblick:** Mindestens ein vollständiger Absatz (4–6 Sätze). Systematische Einordnung (Rechtsgebiet, Normebene), Herkunft/Geschichte des Konzepts, Abgrenzung zu verwandten Begriffen.

**Kernaspekte:** Mindestens 3 benannte Unterabschnitte mit je 3–5 Sätzen. Konkrete Normbezüge (Artikel, Paragraphen), Tatbestandsmerkmale, Rechtsfolgen. Jede zentrale Aussage belegt — entweder mit `[!recht]`-Callout (bei Rechtsnormen/Urteilen) oder mit Quellenangabe.

**Bezüge & Kontroversen:** Mindestens 2 konkrete Diskussionspunkte oder Abgrenzungsfragen. Wo relevant: Gegenansichten, offene Rechtsfragen, Reformdiskussionen, Spannungsverhältnisse zu anderen Rechtsbereichen.

**Verwandte Konzepte:** Mindestens 3 Wikilinks, davon mindestens einer themenübergreifend (in andere Wiki-Ordner).

## Rechtshierarchie-Annotation

Aussagen in Wiki-Seiten, die sich direkt auf eine Rechtsnorm oder Gerichtsentscheidung stützen, werden mit einem Obsidian-Callout annotiert. Der Callout steht *unter* der jeweiligen Aussage im Fließtext.

### Format

```
> [!recht] ⚖️ Rang [N] ([Normkategorie]) · [Gericht/Norm] → [Referenz]
> [Optionaler Kurzkommentar zur Verbindlichkeit oder Einordnung]
```

Beispiele:

```
> [!recht] ⚖️ Rang 2 (EU-Verordnung) · DSA Art. 33 Abs. 1
> Direkt anwendbares EU-Sekundärrecht; verbindlich seit 17.02.2023.

> [!recht] ⚖️ Rang 4 (Verfassungsrecht) · BVerfGE 65, 1 → Art. 2 Abs. 1 GG
> Volkszählungsurteil; Grundlage des Rechts auf informationelle Selbstbestimmung.

> [!recht] ⚖️ Rang 5 (Bundesgesetz) · BGH I ZR 69/08 → UrhG § 97
```

### Rechtshierarchie (6 Ränge, normzentriert)

| Rang | Normkategorie | Beispiel-Normen | Entscheidungen in diesem Rang |
|---|---|---|---|
| 1 | EU-Primärrecht | AEUV, EUV, GRC | EuGH zu Grundfreiheiten und GRC |
| 2 | EU-Sekundärrecht — Verordnung | DSGVO, DSA, DMA, AI Act | EuGH, BVerfG, BGH zu diesen VO |
| 3 | EU-Sekundärrecht — Richtlinie (umgesetzt) | AVMD-RL, NIS2-RL | EuGH, BGH zu umgesetzten RL |
| 4 | Deutsches Verfassungsrecht | GG, Landesverfassungen | BVerfG, VerfGH zu GG-Normen |
| 5 | Bundesgesetz / Staatsvertrag | TKG, TTDSG, UrhG, MStV | BGH, BVerwG, OLG zu Bundesgesetzen |
| 6 | Landesgesetz / Rechtsverordnung | LPG, LRfG, Landes-VO | OVG, VGH, LG zu Landesrecht |

Der Rang folgt der Norm, nicht dem Gericht. Ein BVerfG-Urteil zu Art. 5 GG ist Rang 4; ein EuGH-Urteil zur DSGVO ist Rang 2.

> **Hinweis:** Diese Hierarchie ist EU-/deutschlandspezifisch. Für andere Jurisdiktionen müssen die Normkategorien und Ränge entsprechend angepasst werden.

### Wann annotieren

- ✅ Bei Aussagen, die sich direkt auf eine konkrete Norm oder Entscheidung zurückführen lassen
- ✅ Bei Definitionen oder Tatbestandsmerkmalen aus Gesetzen
- ❌ Nicht bei allgemeinen Zusammenfassungen oder Literaturmeinungen
- ❌ Nicht bei jeder Aussage auf einer Seite — nur bei rechtlich fundierten Kernaussagen

## Belege und Locator-Granularität

Das Feld `quellen:` belegt eine Seite als Ganzes. Das reicht nicht aus, um eine einzelne Aussage zu prüfen. Jede Kernaussage trägt deshalb zusätzlich ihren eigenen **Locator**: citekey plus Fundstelle. Das ist zugleich die Voraussetzung dafür, dass der Verifikations-Pass billig bleibt, denn geprüft wird eine Passage und nicht ein ganzes PDF. Das Vorbild ist die agentische Codeextraktion, in der jedes generierte Werkzeug einen Verweis auf die konkrete Codestelle trägt, aus der es abgeleitet wurde.

### Juristische Aussagen: `Beleg:`-Zeile im `[!recht]`-Callout

Der `[!recht]`-Callout erhält eine optionale, aber erwünschte `Beleg:`-Zeile. Sie steht direkt unter der Titelzeile, vor dem Kurzkommentar:

```
> [!recht] ⚖️ Rang 2 (EU-Verordnung) · DSGVO Art. 6 Abs. 1 lit. f
> Beleg: @citekey S. 142 Rn. 18
> Direkt anwendbares EU-Sekundärrecht; verbindlich seit 25.05.2018.
```

Stützt sich die Aussage unmittelbar auf den Normtext selbst und nicht auf Literatur, entfällt die `Beleg:`-Zeile: Der Normverweis in der Titelzeile *ist* dann der Locator. Pflicht ist sie dort, wo eine **Auslegung, Streitdarstellung oder Zahlenangabe** aus einer Sekundärquelle stammt.

### Nicht-juristische Kernaussagen: Inline-Locator

Aussagen ohne Norm- oder Entscheidungsbezug, die auf eine Quelle zurückgehen, tragen den Locator am Satzende in Klammern:

```markdown
Der Effekt ist in den Daten ab 2023 messbar und betrifft vor allem Berufseinsteiger:innen (@citekey, S. 14).
```

Format: `(@citekey, S. N)` bzw. `(@citekey, Abschn. N)`, oder `(@citekey)`, wenn die Quelle keine Paginierung hat (Website, Preprint ohne Seitenzählung). Die Form ist grep-bar über `\(@[a-z]`.

### Nicht bestandene Aussagen: `[!unbelegt]`-Callout

Aussagen, die den Verifikations-Pass nicht bestehen und nicht korrigiert werden konnten, werden **markiert statt stillschweigend behalten**:

```
> [!unbelegt] ⚠️ Nicht belegt — geprüft YYYY-MM-DD
> Die angegebene Quelle @citekey trägt diese Aussage an der genannten Stelle nicht.
> Entweder Locator korrigieren, Quelle nachliefern oder Aussage entfernen.
```

Der Callout ist ein offener Befund, kein Dauerzustand: Der Lint meldet `[!unbelegt]`-Befunde, die älter als 30 Tage sind, als Warnung.

## Volltext-Vorbedingung des Ingests

**Ohne extrahierbaren Volltext wird nicht ingestet.** Das ist ein Abbruchkriterium, keine Empfehlung.

Zu prüfen ist, ob die Quelle **Text liefert**, nicht ob ein Attachment vorhanden ist. Ein Scan ohne OCR-Ebene erscheint in der Attachment-Liste als versorgt und liefert null Zeichen. Gegenprobe: `pdftotext -q <datei> -`.

| Lage | Verhalten |
|---|---|
| Volltext extrahierbar | regulärer Ingest |
| PDF vorhanden, aber Scan ohne Textebene | **Ingest anhalten.** Nutzer informieren, OCR anbieten (`ocrmypdf --language <sprache> --skip-text <pdf> <pdf-neu>`), danach neu ansetzen |
| Kein Volltext beschaffbar (kein Attachment, Buch im Regal, Sammelnachweis) | **Ausdrücklich warnen und Entscheidung einholen.** Nicht stillschweigend aus Metadaten schreiben |

Wird auf ausdrücklichen Wunsch dennoch geschrieben, gilt kumulativ: Die Seite trägt einen `[!unbelegt]`-Callout mit dem Vermerk, dass sie **nicht aus der Quelle gearbeitet** ist; `verifiziert:` bleibt offen; der `log.md`-Eintrag trägt `[kein Volltext]`.

### Warum die Regel scharf ist

Im Betrieb wurden drei Quellen nach OCR-Erschließung erstmals prüfbar. Bei allen dreien ergab die Prüfung, dass die daraus entstandenen Seiten **aus Modellwissen geschrieben waren**, nicht aus dem Text. Der Protokolleintrag einer dieser Quellen behauptete sogar, sie sei gelesen worden.

Entscheidend ist, wie diese Seiten aussahen: Sie trafen ihren Gegenstand weitgehend richtig. Genau deshalb fiel es niemandem auf. **Ein Ingest ohne Volltext erzeugt kein erkennbar lückenhaftes Referat, sondern ein plausibles.** Die Fehler saßen nicht in der Substanz, sondern an den architektonischen Fugen, und zwar in vier wiederkehrenden Formen:

- **Erfundene Fundstellen**, die das Nummernschema des Werks verfehlen (ein „Kapitel 23" in einem Buch, das teilintern 3.1 bis 3.9 zählt).
- **Superlative ohne Grundlage** („der einflussreichste Theoretiker", „am schärfsten formuliert", „die maßgebliche Synopse").
- **Zugeschriebene Haltungen** („X sieht die Umsetzbarkeit skeptisch", „X fordert strukturelle Transparenz"), die der Autor nicht vertritt.
- **Zuordnungen über Grenzen hinweg, die der Autor selbst zieht** — ein Merkmal wird dem falschen von zwei Typen zugeschlagen, die die Quelle ausdrücklich trennt.

Ein weiteres Erkennungszeichen: Die Seite reproduziert zuverlässig, was in der Sekundärrezeption kanonisch ist, und **nichts**, was nur beim Lesen auffällt — keine Zahl aus einer Erhebung, keinen Nebenstrang, nicht den Schlusssatz.

### Bibliografische Gegenprobe

Ist der Volltext erschlossen, ist zusätzlich zu prüfen, ob die Datei die Ausgabe ist, die der Eintrag behauptet. Im selben Lauf erwies sich eine als US-Erstausgabe geführte Datei als britische Ausgabe mit **abweichender Paginierung** — jeder daraus gezogene Locator wäre falsch gewesen. Titelblatt und Kolumnentitel beantworten das in Sekunden.

## Verifikations-Pass (Ingest-Schritt 7)

Der Lint prüft **Struktur**: tote Links, Index-Konsistenz, Frontmatter-Drift. Er prüft nicht, ob ein Satz von seiner Quelle gedeckt ist. Genau diese Lücke schließt der Verifikations-Pass. Das Muster stammt aus der agentischen Codeextraktion: Was sich nicht gegen die Quelle prüfen lässt, wird nicht stillschweigend übernommen, sondern mit Befund gekennzeichnet oder entfernt.

Zwei Konstruktionsentscheidungen tragen das Verfahren und sollten beim Anpassen nicht wegfallen. **Erstens prüft ein frischer Subagent ohne den Schreibkontext.** Wer einen Text verfasst hat, liest ihn gegen die Quelle als Bestätigung und nicht als Prüfung; die Trennung ist der Kern, keine Formalie. **Zweitens wird Nichtbestandenes ausgeschlossen statt behalten.** Eine Aussage, die ihre Quelle nicht trägt, verschwindet entweder oder wird sichtbar markiert, und sie bleibt nie unkommentiert stehen.

Herkunft und Belege für beides: Miao u.a., *Reimagining research papers as interactive and reliable AI agents*, Nature 2026, DOI [10.1038/s41586-026-11044-y](https://doi.org/10.1038/s41586-026-11044-y); Referenzimplementierung [jmiao24/Paper2Agent](https://github.com/jmiao24/Paper2Agent). Ausführlich in `docs/de/07-verifikation.md`.

### Grundsatz: Belegtheit, nicht Richtigkeit

Juristische Aussagen haben keinen ausführbaren Prüfmaßstab, weil Auslegung streitig ist. Der Verifier stellt deshalb **ausschließlich** fest, ob die angegebene Quellenstelle die Aussage trägt. Er entscheidet nicht, ob die Aussage zutrifft, und er ersetzt keine fachliche Prüfung. Wer beides verwechselt, erzeugt falsche Sicherheit.

### Ablauf

Der Pass läuft **automatisch als Schritt 7 jedes Ingests** und zusätzlich auf den Trigger `verify wiki [Seite|Thema|letzter Ingest]`.

1. **Frischer Subagent.** Die Prüfung übernimmt ein Subagent *ohne* den Schreibkontext. Wer den Text geschrieben hat, kann ihn nicht unbefangen gegenprüfen. Das ist der Kern des Verfahrens, keine Formalie.
2. **Eingabe:** Seitenpfad, alle Locator der Seite (`Beleg:`-Zeilen, Inline-Locator, `quellen:`) sowie `normen:`/`urteile:`/`ecli:`.
3. **Quellenrückgriff:** Passagen per Zotero MCP nachschlagen (`get_content` gezielt, `search_fulltext` für die Locator-Stelle, `get_annotations`).
4. **Klassifikation je Aussage:**

| Befund | Bedeutung | Konsequenz |
|---|---|---|
| `belegt` | Quellenstelle trägt die Aussage | nichts |
| `nicht belegt` | Stelle existiert, trägt die Aussage aber nicht | max. 2 Nachbesserungsversuche (Locator korrigieren, bessere Stelle suchen), danach `[!unbelegt]` |
| `widersprochen` | Quelle sagt etwas anderes | Aussage im selben Durchgang korrigieren, Korrektur in `log.md` vermerken |
| `nicht prüfbar` | kein Volltext vorhanden | Seite behält die Aussage, `verifiziert:` wird **nicht** gesetzt, `log.md`-Vermerk `[kein Volltext]` |

5. **Hard-Fail-Klasse, sofortige Entfernung ohne Nachbesserung:**
   - erfundene oder nicht auffindbare **ECLI**
   - erfundene **Normbezeichnung** (Artikel oder Paragraph existiert im zitierten Gesetz nicht)
   - erfundene **Fundstelle** (Band, Seite oder Randnummer nicht verifizierbar)
   - erfundener **citekey** (nicht in Zotero vorhanden)

   Diese vier Fälle werden entfernt, nicht markiert, und im `log.md`-Eintrag als `Hard-Fail` geführt.

   **Beim Entfernen einer Quelle ist der Fließtext mitzuprüfen, nicht nur `quellen:`.** Eine als nicht existent erkannte Quelle aus dem Frontmatter und dem Quellenverzeichnis zu streichen, genügt nicht: Die Attributionen stehen im Text als Autor-Jahr-Nennung und überleben die Bereinigung. Im Betrieb entstanden so vier Hard Fails auf zwei Seiten, auf denen wenige Zeilen tiefer vermerkt war, dass es die Quelle nicht gibt. Der Suchlauf muss deshalb den **Nachnamen** erfassen, nicht den citekey.

   **Vor der Entfernung ist der Befund gegenzuprüfen, und zwar an der ranghöheren Quelle:** Die Publikation selbst geht den Metadaten der Literaturverwaltung vor, der amtliche Normtext der Sekundärliteratur. Ein gemeldeter Hard Fail, der auf abgeleiteten Daten beruht, kann korrekte Angaben treffen. Lässt sich eine bezweifelte Angabe nicht klären, wird sie entfernt und nicht gegen eine zweite ungeprüfte ausgetauscht. Die Schema-Regel „ECLI niemals erfinden" ist damit nicht mehr nur eine Anweisung, sondern eine Prüfung. Anweisungen erzwingen nichts, Prüfungen schon.

6. **Abschluss:** Besteht die Seite ohne offenen Befund, wird `verifiziert: YYYY-MM-DD` gesetzt. Bleibt ein `[!unbelegt]`-Callout stehen, wird das Feld **nicht** gesetzt.

### Bestandsschutz und Heben beim Anfassen

Wer den Verifikations-Pass in einem gewachsenen Wiki einführt, steht vor einem Altbestand, der ihn nicht durchlaufen hat. Ihn nachträglich vollständig zu prüfen ist teuer: Ein Locator setzt voraus, die Quelle gelesen zu haben — das ist faktisch ein Re-Ingest jeder Seite.

Die tragfähige Regel besteht aus zwei Hälften, die nur zusammen funktionieren:

**Bestandsschutz.** Seiten mit `updated:` vor `[EINFÜHRUNGSDATUM]` werden nicht aktiv nachgezogen. Keine Kampagne. Das ist keine Nachlässigkeit, sondern korrekte Kennzeichnung: Fehlt `verifiziert:`, gilt die Seite als ungeprüft, und genau das ist sie auch.

**Heben beim Anfassen.** Sobald eine Altseite aus anderem Anlass inhaltlich geändert wird — Ingest, Korrektur, Normersetzung, Ergänzung —, verliert sie den Bestandsschutz und ist in derselben Bearbeitung zu heben: Locator setzen, Verifikations-Pass, `verifiziert:` setzen. **Maßgeblich ist der Umfang der Seite, nicht der Umfang der Änderung.** Wer einen Satz korrigiert, hebt die Seite; wer die Seite nicht heben will, ändert sie nicht.

Der Bestand konvergiert damit über die normale Arbeit statt über eine Sonderanstrengung, und zwar in der richtigen Reihenfolge: Was oft angefasst wird, wird zuerst geprüft.

Zwei Abgrenzungen, ohne die die Regel kippt:

- **Sprengt das Heben den Rahmen** — sehr umfangreiche Altseiten mit vielen Quellen —, wird `updated:` gesetzt (es ist eine Tatsache), `verifiziert:` bleibt **offen**, und `log.md` hält fest, welcher Teil geprüft wurde und welcher nicht. Ein halb geprüfter Stand darf nie als geprüft ausgewiesen werden: `verifiziert:` bezieht sich auf die ganze Seite, nicht auf die letzte Änderung.
- **Rein mechanische Läufe heben nicht.** Korrektur eines citekeys, Nachtragen einer `resource:`-URI, Umbenennen eines Links berührt keine Aussage und löst die Hebepflicht nicht aus. Sonst erzwingt eine Suchen-und-Ersetzen-Operation über 40 Dateien 40 Verifikations-Pässe.

### Eintrag in `log.md`

```
- **Verifikation** [[Seitenname]] — 14 Aussagen: 12 belegt, 1 korrigiert, 1 unbelegt, 0 Hard-Fail
```

## Typisierte Wikilinks (Relationsvokabular)

Rechtliche Beziehungen zwischen Knoten werden im Fließtext mit einem kontrollierten Relationsverb vor dem Wikilink ausgedrückt. Lesbar für Menschen, grep-bar für `query wiki`. Übernimmt die typisierten Kanten des KG-Konzepts (setzt_um, ändert, konkretisiert) Obsidian-nativ ohne Schema-Overhead.

Kontrolliertes Vokabular:

- **setzt um** — Richtlinie → Umsetzungsgesetz
- **ändert** / **hebt auf** — Novellierung/Aufhebung
- **verdrängt** — Anwendungsvorrang (lex superior/posterior)
- **konkretisiert** — Rechtsprechung präzisiert ältere Entscheidung/Norm
- **definiert** — Norm definiert einen Begriff
- **wendet an** — Entscheidung wendet eine Norm an
- **setzt aus** — vorübergehende Aussetzung der Wirksamkeit (LKIF `Suspension`)
- **erklärt für nichtig** — gerichtliche Nichtigerklärung, ex tunc (LKIF `Annulment`; ≠ gesetzgeberische Aufhebung „hebt auf")
- **wirkt nach** — abgelöste Norm bleibt für Altfälle anwendbar (Nachwirkung, LKIF `Ultractivity`)
- **wirkt zurück** — Norm erfasst rückwirkend abgeschlossene Sachverhalte (LKIF `Retroactivity`)
- **zitiert** — allgemeiner Verweis

Beispiel:

> Der DSA **verdrängt** [[NetzDG]] §§ 2, 3 (seit 17.02.2024); der Gesetzgeber **hebt** die §§ 2 bis 3f mit Wirkung zum 14.05.2024 **auf**; das österr. KoPl-G-Analogon ist europarechtswidrig laut [[EuGH C-376-22 (KoPl-G)]].

## Rechtliche Aktualität und Normersetzung

### Grundregel

Das Wiki spiegelt immer den **aktuellen Rechtsstand** wider — es ist kein historisches Archiv. Wenn eine neu ingested Quelle eine bereits dokumentierte Norm oder Entscheidung ablöst, modifiziert oder verdrängt, werden die betroffenen Wiki-Seiten im selben Ingest-Durchgang aktualisiert. Neuere Rechtslage überschreibt ältere Inhalte; veraltete Callouts werden entsprechend gekennzeichnet.

### Vier Supersessionstypen

| Typ | Auslöser | Beispiel | Konsequenz |
|---|---|---|---|
| **Vollständige Ablösung** | Neue Norm ersetzt alte vollständig (Aufhebungsklausel) | MStV (2020) ersetzt RStV | Callout um Hinweis ergänzen: `→ aufgehoben durch [X] seit [Datum]` |
| **Partielle Verdrängung** | EU-Verordnung mit Anwendungsvorrang (lex posterior/superior) | DSA Art. 15, 16 verdrängen NetzDG § 2, § 3 Abs. 2 | Verdrängten Teil im Callout markieren; verbliebenen Restanwendungsbereich dokumentieren |
| **Novellierung** | Geänderte Fassung einer bestehenden Norm | AVMD-RL 2018/1808 ändert AVMD-RL 2010/13/EU | Neue Fassung ist maßgeblich; Fassung/Datum im Callout führen (`i.d.F. [Jahr]`) |
| **Rechtsprechungsänderung** | Neueres Urteil klärt, präzisiert oder revidiert ältere Entscheidung | BVerfGE 158, 389 konkretisiert BVerfGE 149, 222 | Neueres Urteil primär zitieren; älteres Urteil mit Kontexthinweis auf Nachfolgeentscheidung versehen |

### Geltung: Inkrafttreten vs. Wirksamkeit

Das LKIF-`time-modification`-Modul trennt zwei Zeitachsen, die Seiten zu zeitkritischen Normen sauber halten sollten:

- **Inkrafttreten** (`In_Force`, Feld `in_kraft:`) — ab wann die Norm formal zur Rechtsordnung gehört.
- **Wirksamkeit/Anwendbarkeit** (`Efficacy`, Feld `wirksam_ab:`) — ab wann sie tatsächlich Rechtsfolgen erzeugt.

Divergieren beide, im `[!recht]`-Callout beide Daten führen (Beispiel unten). Für abgelöste Normen ist relevant, dass das Inkrafttreten enden kann, die Wirksamkeit für Altfälle aber fortbesteht → **Nachwirkung** (s.u.).

### Weitere Modifikationstypen

Über die vier Supersessionstypen hinaus kennt das LKIF-`time-modification`-Modul temporale Modifikationen, die keine Ablösung sind, aber den Geltungsstatus verändern. Mit dem Relationsvokabular ausdrücken und im Callout kennzeichnen:

| Typ | LKIF-Klasse | Auslöser | Konsequenz |
|---|---|---|---|
| **Aussetzung** | `Suspension` | Wirksamkeit vorübergehend ausgesetzt (gerichtliche Anordnung, Moratorium) | Relation `setzt aus`; Callout `⏸️ ausgesetzt [Zeitraum/Grund]`; Seite bleibt gültig, Status markiert |
| **Nichtigerklärung** | `Annulment` | Gericht erklärt Norm für nichtig (ex tunc) — ≠ gesetzgeberische Aufhebung | Relation `erklärt für nichtig`; Callout mit Gericht/ECLI; von „aufgehoben" (durch Gesetzgeber) abgrenzen |
| **Nachwirkung** | `Ultractivity` | Abgelöste Norm bleibt für Altfälle anwendbar (Übergangsrecht) | Relation `wirkt nach`; Callout: verdrängt ab [Datum], **aber** anwendbar auf Sachverhalte vor [Datum] |
| **Rückwirkung** | `Retroactivity` | Norm erfasst rückwirkend abgeschlossene Sachverhalte | Relation `wirkt zurück`; Callout `wirkt zurück auf [Datum]`; ggf. verfassungsrechtl. Rückwirkungsverbot vermerken |

### Warnung: Verdrängung wird gern für den Endzustand gehalten

Der häufigste Fehler beim Pflegen dieses Abschnitts ist nicht das Übersehen einer Ablösung, sondern das **Stehenbleiben beim ersten Vorgang**. Eine Norm kann nacheinander mehrfach betroffen sein, und wer nur die erste Stufe protokolliert, führt am Ende eine falsche Aussage.

Der Lehrfall dazu ist das deutsche NetzDG:

1. Ab 17.02.2024 verdrängte der unmittelbar geltende DSA die §§ 2, 3 NetzDG kraft Anwendungsvorrangs. Die Vorschriften bestanden fort und traten nur zurück. § 3a (Meldepflicht an das Bundeskriminalamt) hatte kein DSA-Äquivalent und galt deshalb als **verbleibender Restanwendungsbereich**.
2. Nur wenige Monate später hob der Gesetzgeber die §§ 2 bis 3f, einschließlich § 3a, **förmlich auf** (Art. 29 Nr. 2 des Gesetzes zur Durchführung der Verordnung (EU) 2022/2065 v. 06.05.2024, BGBl. 2024 I Nr. 149; in Kraft am 14.05.2024).

Ein Wiki, das nur Schritt 1 erfasst hat, behauptet danach, § 3a bleibe eigenständig anwendbar. Das ist unrichtig, klingt aber plausibel und ist gut belegt, weil die Literatur bis 2024 genau das schrieb.

Zwei Konsequenzen für die Praxis:

- **Verdrängung ist ein Zustand, kein Abschluss.** Wo `verdrängt` gesetzt wird, gehört das Thema auf Wiedervorlage; der Gesetzgeber zieht in solchen Konstellationen oft nach.
- **Ein Restanwendungsbereich ist die fragilste Aussage des ganzen Vokabulars.** Er behauptet, dass etwas übrig geblieben ist. Genau das ändert sich am schnellsten. Solche Aussagen brauchen ein `rechtsstand:` und eine Gegenprobe an der amtlichen Fassung, nicht nur an der Sekundärliteratur.

### Ingest-Pflicht: Normersetzungsprüfung

Bei jedem Ingest einer juristischen Quelle (Gesetz, Verordnung, Urteil, Kommentar) **vor dem Schreiben**:

1. **Identifikation** — Welche älteren Normen oder Entscheidungen werden durch die neue Quelle abgelöst, abgeändert oder verdrängt? Auf Signalformulierungen im Quelltext achten: „ersetzt", „aufgehoben", „tritt an die Stelle von", „verdrängt", „Anwendungsvorrang", „gilt nicht mehr", „überholt durch".
2. **Wiki-Scan** — `index.md` und betroffene Wiki-Seiten auf Callouts und Fließtextstellen prüfen, die die supersedierte Norm/Entscheidung zitieren.
3. **Update** — Betroffene Seiten im selben Ingest-Durchgang aktualisieren (Callouts kennzeichnen, Fließtext bei wesentlichen inhaltlichen Änderungen anpassen, `updated`- und `rechtsstand`-Datum setzen).
4. **Abschlusskontrolle** — Die Prüfung ist erst abgeschlossen, wenn ein Suchlauf über den **gesamten** Bestand nach der überholten Aussage null Treffer liefert, nicht wenn die offensichtlich betroffenen Seiten bearbeitet sind. Im Betrieb überlebte eine aufgehobene Vorschrift nach einer für abgeschlossen gemeldeten Korrektur an sechs weiteren Stellen, darunter in einem `[!recht]`-Callout, also genau in dem Element, das Normgeltung behauptet. Die Suchbegriffe sind aus der **alten** Aussage zu bilden, nicht aus der neuen. Das Protokoll (`log.md`) ist von diesem Lauf auszunehmen: Es hält fest, was damals galt.

### Callout-Kennzeichnung abgelöster Normen

Vollständig aufgehobene oder ersetzte Norm:

```
> [!recht] ⚖️ Rang 5 (Bundesgesetz) · NetzDG § 2 i.d.F. 2021
> ⚠️ Verdrängt durch DSA Art. 15 Abs. 1 mit Wirkung ab 17.02.2024.
```

Teilweise verdrängte Norm mit verbleibendem Restanwendungsbereich:

```
> [!recht] ⚖️ Rang 5 (Bundesgesetz) · NetzDG § 3 Abs. 2 i.d.F. 2021
> Weitgehend verdrängt durch DSA Art. 16 Abs. 6 (seit 17.02.2024).
> Restanwendungsbereich: § 5 NetzDG (inländischer Zustellungsbevollmächtigter) bleibt eigenständig anwendbar.
```

Präzisierte oder revidierte Gerichtsentscheidung:

```
> [!recht] ⚖️ Rang 4 (Verfassungsrecht) · BVerfGE 149, 222 (Rundfunkbeitrag, 2018)
> Durch BVerfGE 158, 389 (Sachsen-Anhalt, 2021) in der Frage der Mitverantwortungspflicht der Länder konkretisiert.
```

In Kraft, aber noch nicht anwendbar (Geltung ≠ Wirksamkeit):

```
> [!recht] ⚖️ Rang 2 (EU-Verordnung) · EU AI Act Art. 5
> In Kraft seit 01.08.2024; Verbote anwendbar ab 02.02.2025.
```

Für nichtig erklärte Norm (≠ gesetzgeberische Aufhebung):

```
> [!recht] ⚖️ Rang 5 (Bundesgesetz) · [Norm] i.d.F. [Jahr]
> ⚠️ Vom BVerfG für nichtig erklärt (ex tunc) durch [ECLI/Fundstelle].
```

Abgelöste Norm mit Nachwirkung für Altfälle:

```
> [!recht] ⚖️ Rang 5 (Bundesgesetz) · [Norm] i.d.F. [Jahr]
> Verdrängt durch [X] ab [Datum]; wirkt nach auf vor [Datum] abgeschlossene Sachverhalte.
```

### rechtsstand-Frontmatter-Feld

Das optionale Feld `rechtsstand: YYYY-MM-DD` markiert, bis zu welchem Datum die Rechtslage einer Seite vollständig geprüft wurde. Es wird gesetzt oder aktualisiert, wenn im Rahmen eines Ingest eine vollständige Normersetzungsprüfung für diese Seite durchgeführt wurde. Fehlt das Feld, gilt die Seite als bzgl. Aktualität ungeprüft.

Das Feld wird **nicht** bei jeder inhaltlichen Ergänzung gesetzt — nur nach expliziter Aktualitätsprüfung. Es hat keinen Einfluss auf `updated`, das bei jeder inhaltlichen Änderung fortgeschrieben wird.

## Thematische Ordner (Wiki-Bereich)

Vom Nutzer selbst festzulegen — je ein Ordner pro Fachgebiet unter `[WIKI-ORDNER]/`. Beispiel-Notation (durch eigene Themen ersetzen):

- `[WIKI-ORDNER]/[Thema 1]/`
- `[WIKI-ORDNER]/[Thema 2]/`
- `[WIKI-ORDNER]/[Thema 3]/` …

Eigene Nicht-Wiki-Ordner (z.B. `Persönlich/`, `Werkzeuge/`) bleiben außen vor.

## Workflow-Seiten (`type: wiki-workflow`)

Die Wiki-Seiten halten Wissen fest, nicht Verfahren. Verfahrensschritte (wie eine Normprüfung abläuft, in welcher Reihenfolge geprüft wird) liegen sonst als Prosa über dieses Schema verstreut, bleiben implizit und wirken nur beim Ingest. Workflow-Seiten machen sie explizit und aufrufbar.

- **Ort:** `[WIKI-ORDNER]/Workflows/`, ein **Infrastruktur-Ordner** und kein Themenordner. Er wird von thematischen Auswertungen und vom Tiefenstandard nicht erfasst.
- **Namensschema:** `Workflow - [Verfahren].md`
- **Frontmatter:** `type: wiki-workflow`, dazu `thema:`, `created:`, `updated:`. Kein `wiki-category:` (das bleibt Wiki-Seiten vorbehalten), kein `quellen:`-Zwang.
- **Trigger:** `workflow: [Name]`. Der Agent liest die Seite und arbeitet sie Schritt für Schritt ab.
- **Aufbau:** `Zweck` · `Schritte` (nummeriert, je mit Prüffrage) · `Abbruchkriterien` · `Verwandte Knoten` (Wikilinks auf Normknoten und Konzeptseiten).

Workflow-Seiten sind **keine** Wiki-Seiten i.S.d. Tiefenstandards und werden von allen Lint-Checks, die auf `type: wiki-page` filtern, nicht erfasst. Sie sind zugleich der Ort, an dem andere Skills (Lehrmaterial, Gutachten, Fallstudien) Verfahrenswissen abholen, statt es jeweils neu zu rekonstruieren.

Ein vollständiges Beispiel liegt in `examples/Workflow - Normprüfung.md`.

### Welche Verfahren eine eigene Seite verdienen

Nicht jedes juristische Prüfschema gehört hierher. Der brauchbare Test lautet: **Erzeugt das Verfahren ein Artefakt, das dieses Schema definiert?**

- **Ja** bei Betriebsverfahren des Wikis (Verifikations-Pass, Normersetzungsprüfung) und bei Bauanleitungen für einen Seitentyp. Die Normprüfung etwa füllt genau die vier Abschnitte, die für Normknoten-Seiten vorgeschrieben sind.
- **Nein** bei allgemeiner juristischer Methodik ohne Entsprechung im Bestand. Eine Grundrechtsprüfung nach Schutzbereich, Eingriff und Rechtfertigung ist fachlich richtig, erzeugt aber keinen Seitentyp. Ihre Abnehmer sind Gutachten-, Lehr- und Fallstudien-Skills. Solange diese die Seite nicht konsultieren, ist sie totes Gewicht, und der Lint-Check *Workflow-Drift* meldet sie zu Recht.

### Verhältnis zu diesem Schema

In einer laufenden Installation empfiehlt es sich, die **Workflow-Seite zur maßgeblichen Fassung des Verfahrens** zu erklären und dieses Schema an der betreffenden Stelle nur noch auf sie verweisen zu lassen. Im Schema bleiben dann die Festlegungen, auf die sich Frontmatter und Lint beziehen (Befundklassen, Typologien, Callout-Formate), im Workflow der Ablauf. Sonst steht dasselbe Verfahren an zwei Orten und läuft auseinander.

Dieses Template belässt beide Verfahren bewusst vollständig hier, weil `examples/` beim Nachbau nicht zwingend mitinstalliert wird und das Schema für sich lesbar bleiben muss.

## Zotero MCP-Tools (Referenz)

Für den Ingest wird ausschließlich der Zotero MCP-Server genutzt (nativer MCP-über-HTTP-Endpoint `http://127.0.0.1:23120/mcp`, Zotero-Plugin `zotero-mcp-plugin` v1.5.0). Die Tools sind direkt als `mcp__zotero__*` aufrufbar. Die meisten Lese-Tools akzeptieren optional `libraryID` (Default: Nutzerbibliothek) und `mode` (`minimal`|`preview`|`standard`|`complete`) zur Ergebnis-/Inhaltssteuerung.

| Tool | Verwendung im Ingest |
|---|---|
| `search_library` | Item zu @citekey, DOI/ISBN oder Thema finden; liefert `itemKey` (Params: `q`, `title`, `yearRange`, `fulltext`, `itemType`, `sort`, `mode`) |
| `get_item_details` | Vollständige Metadaten, Attachment-Liste, Tags, Notizen (Params: `itemKey`, `mode`) |
| `get_item_abstract` | Nur Abstract/Zusammenfassung (Params: `itemKey`, `format`) |
| `get_content` | Volltext aus PDF/Attachment/Notizen (Params: `itemKey` **oder** `attachmentKey`, `mode`; ganzes Dokument = `mode: "complete"`; **kein `page`-Parameter**) |
| `search_fulltext` | Volltextsuche über alle Dokumente; liefert Passagen mit Kontext |
| `get_annotations` | Annotationen/Notizen eines Items (Param: `itemKey` **oder** `annotationId` **oder** `annotationIds[]`; Filter `colors`, `tags`, `types`) |
| `search_annotations` | Annotationssuche über die gesamte Bibliothek (mind. eines von `q`, `colors`, `tags`) |
| `get_collections` | Alle Kollektionen auflisten (Params: `mode`, `recursive`, `parentCollection`) |
| `get_collection_items` | Alle Items einer Kollektion (Param: `collectionKey`) |
| `get_subcollections` | Unterkollektionen einer Kollektion (Params: `collectionKey`, `recursive`) |

**Fallback auf lokale API (Port 23119):** Nur wenn der MCP-Server nicht antwortet (Zotero-Plugin nicht aktiv). Dann wie bisher per HTTP-Calls via Python/curl.

## Ingest-Dekomposition (Sub-Agenten mit JSON-Handoff)

Der lineare Ingest lädt Volltext, Index und Schreibkontext in ein einziges Kontextfenster. Genau daher stammt das Abbruchprotokoll beim Token-Budget. Die Alternative ist Zerlegung: Ein Orchestrator dispatcht spezialisierte Sub-Agenten, die Daten **ausschließlich über standardisierte JSON-Reports** austauschen und nie über geteilten Kontext. Die monolithische Variante schneidet selbst in einem großen Kontextfenster messbar schlechter ab (Ablation bei Miao u.a., *Reimagining research papers as interactive and reliable AI agents*, Nature 2026, DOI [10.1038/s41586-026-11044-y](https://doi.org/10.1038/s41586-026-11044-y)).

### Wann anwenden

Nicht bei jedem Ingest, denn der Overhead lohnt sich erst ab:

- Bulk-Ingest mit **mehr als 3 Quellen**, oder
- Einzelquelle mit **mehr als ~50 Seiten** Volltext (Monografien, Kommentare, Sammelbände).

Darunter bleibt der klassische lineare Ablauf richtig.

### Vier Rollen

| Rolle | Eingabe | Ausgabe | Hält im Kontext |
|---|---|---|---|
| **Extraktor** | Zotero-Item | `extraktion.json` | nur die eine Quelle |
| **Kollisionsprüfer** | `extraktion.json` + `index.md` | `kollision.json` | nur Index und JSON |
| **Schreiber** (parallel, je Seite) | ein Eintrag aus `kollision.json` | `schreibbericht.json` | nur seine Seite |
| **Verifier** (frisch) | Seite und Locator | `verifikat.json` | nur Passagen |

Der Orchestrator hält **nur die JSONs**, nie die PDFs. Damit wird die Grenze von etwa 15 Seiten pro Ingest von einer Kontextfrage zu einer Durchsatzfrage.

### Ablage

`/tmp/wiki-ingest/<citekey>/`, bewusst außerhalb des Vaults, damit Zwischenstände den Wissensbestand nicht verunreinigen. Nach erfolgreichem Abschluss kann der Ordner verworfen werden; bei Abbruch ist er der Wiederaufsetzpunkt (Verweis im `log.md`-Eintrag `[unterbrochen …]`).

### Schemata

```jsonc
// extraktion.json
{
  "citekey": "citekey2024",
  "titel": "...",
  "volltext_status": "complete | partial | kein_volltext",
  "konzepte":   [{"name": "...", "kurz": "...", "belege": [{"locator": "S. 142", "zitat": "..."}]}],
  "entitaeten": [{"name": "...", "art": "person | gesetz | institution"}],
  "normen":     ["DSGVO Art. 6 Abs. 1 lit. f"],
  "urteile":    ["EuGH C-300-21 (Österreichische Post)"],
  "themen":     ["[Thema 1]"]
}

// kollision.json
{
  "neu":               [{"titel": "...", "pfad": "[Thema 1]/....md", "kategorie": "konzept"}],
  "update":            [{"pfad": "[Thema 2]/....md", "aenderung": "Abschnitt Kernaspekte ergaenzen"}],
  "normknoten_faellig":[{"norm": "MStV § 93", "zitiert_in": 3}]
}

// schreibbericht.json
{"pfad": "...", "status": "erstellt | aktualisiert | uebersprungen",
 "wikilinks": 7, "callouts": 2, "locatoren": 5}

// verifikat.json
{"pfad": "...", "geprueft": 14, "belegt": 12,
 "nicht_belegt": [{"aussage": "...", "locator": "S. 88"}],
 "widersprochen": [], "hard_fail": []}
```

## Ingest-Checkliste

Vor dem Schreiben:
- [ ] `[WIKI-ORDNER]/index.md` gelesen?
- [ ] Betroffene Themenordner identifiziert?
- [ ] Prüfen: gibt es bereits eine Seite für dieses Konzept/diese Entität?
- [ ] **Volltext-Check:** Anhänge über Zotero MCP `get_item_details` abrufen (liefert `attachments`-Feld mit `contentType`): `application/pdf` → PDF per `get_content`, `text/html` → HTML-Snapshot via Read-Tool (`~/Zotero/storage/[ATTKEY]/`)
- [ ] **Normersetzungsprüfung (juristische Quellen):** Enthält die Quelle Normen oder Entscheidungen, die bereits dokumentierte Wiki-Inhalte ablösen, abändern oder verdrängen? → Betroffene Wiki-Seiten über `index.md` identifizieren; Update erfolgt im Schritt „Seiten schreiben/aktualisieren" (s. Abschnitt *Rechtliche Aktualität und Normersetzung*)

Quellenlesen (Standard — immer vor dem Schreiben):
- [ ] Metadaten + Abstract per Zotero MCP `get_item_details` (bzw. `get_item_abstract`) gelesen?
- [ ] **PDF vorhanden?** (`contentType: application/pdf`) → Volltext per `get_content` (MCP) abrufen:
  - Artikel/Kapitel: `get_content(itemKey, mode: "complete")` = gesamtes Dokument
  - Bücher/lange Dokumente: mit `mode: "standard"`/`"preview"` sondieren, dann bei Bedarf `mode: "complete"` (kein seitenweiser `page`-Parameter mehr); alternativ `search_fulltext` für gezielte Passagen
  - Annotations per `get_annotations` (MCP) auswerten
- [ ] **Kein PDF, aber HTML-Snapshot vorhanden?** (`contentType: text/html`) → Volltext lesen mit Read-Tool (`~/Zotero/storage/[ATTKEY]/`):
  - HTML-Datei vollständig lesen; HTML-Tags beim Auswerten ignorieren
  - Wie PDF behandeln: vollständig für Artikel, selektiv für längere Dokumente
  - Annotations per `get_annotations` (MCP) auswerten
- [ ] Weder PDF noch HTML? → Aus Metadaten, Abstract und eigenem Fachwissen arbeiten; im log.md vermerken: `[kein Volltext]`

Beim Schreiben:
- [ ] Inhalt basiert auf tatsächlichem Quelltext, nicht nur auf Titelkenntnis
- [ ] Konkrete Seitenangaben oder Kapitelreferenzen wo möglich eingebaut
- [ ] Frontmatter vollständig (alle Pflichtfelder)?
- [ ] Cross-Links mit [[Wikilinks]] gesetzt?
- [ ] Bestehende atomare Notizen im selben Ordner auf Verlinkbarkeit geprüft?
- [ ] `updated`-Datum aktualisiert?
- [ ] **Locator gesetzt?** Jede Aussage aus einer Sekundärquelle trägt eine `Beleg:`-Zeile (juristisch) oder einen Inline-Locator `(@citekey, S. N)` (sonstige), s. Abschnitt *Belege und Locator-Granularität*

Nach dem Schreiben:
- [ ] **Verifikations-Pass (Schritt 7) durchgeführt?** Frischer Subagent, Befundklassen, Hard-Fail-Prüfung, s. Abschnitt *Verifikations-Pass*
- [ ] `verifiziert:`-Datum gesetzt (nur wenn kein offener `[!unbelegt]`-Befund verbleibt)?
- [ ] `[WIKI-ORDNER]/index.md` aktualisiert?
- [ ] `[WIKI-ORDNER]/log.md` Eintrag angehängt? (inkl. `[kein PDF]` falls zutreffend)
- [ ] Neuer Ordner angelegt? → Dann auch CLAUDE.md und wiki-schema.md Themenordner-Liste aktualisieren

## Lint-Spezifikation

`lint wiki` führt einen vollständigen Integritäts-Audit durch. Befunde werden nach Schweregrad klassifiziert.

### Schweregrade

| Schweregrad | Bedeutung | Beispiele |
|---|---|---|
| **Fehler** | Strukturell kaputt, muss behoben werden | Broken Wikilinks, Index-Einträge ohne Datei |
| **Warnung** | Qualitätsproblem, sollte behoben werden | Orphan-Seiten, stale claims, missing pages |
| **Info** | Verbesserungspotenzial | Fehlende Cross-Links, data gaps |

### Checks

**Fehler:**
- [ ] **Broken Wikilinks** — `[[Seite]]`-Verweise auf nicht existierende Dateien. **Beim Parsen das echte Linkziel isolieren**, bevor gegen Dateien geprüft wird: Alias nach `|` *und* nach escaptem `\|` (Pflicht-Escaping in Markdown-Tabellen!) abtrennen, `#`-Sprungmarken abtrennen, Pfad auf letztes Segment reduzieren. Sonst entstehen Fehlalarme bei Tabellen-Links wie `[[Antrag X\|Alias]]` und Anker-Links wie `[[Seite#Abschnitt]]`. **Unicode-Normalisierung beachten:** macOS legt Dateinamen auf APFS/iCloud in **NFD** ab (`ü` = `u` + Kombinationszeichen), Markdown-Dateien enthalten dagegen **NFC**. Ein naiver Stringvergleich meldet deshalb *jede* Seite mit Umlaut im Dateinamen als broken. Vor dem Vergleich beide Seiten mit `unicodedata.normalize("NFC", …)` normalisieren. (Lauf vom 2026-09-23: 3 von 4 verbliebenen Treffern waren Fehlalarme dieser Art, u.a. `[[LG München I 26 O 869-26 (Google AI Overview)]]` und `[[Anchoring Bias (KI-gestützte Entscheidungen)]]`.) Ebenso eine etwaige `.md`-Endung im Linkziel abschneiden (`[[00 Kontext/Grundannahmen.md]]`), sonst entsteht derselbe Fehlalarm. **Quellen-Wikilinks ausnehmen:** Links der Form `[[@citekey]]` im Abschnitt *Quellen* verweisen auf den Zotero-Eintrag und **nicht** auf eine Vault-Datei. Es gibt bewusst keine `@citekey.md`-Dateien. Da praktisch jede Wiki-Seite einen solchen Link führt, erzeugt ein Check ohne diese Ausnahme mehr Fehlalarme als der gesamte Bestand Seiten hat. Linkziele, die mit `@` beginnen, deshalb überspringen.
- [ ] **Index-Konsistenz** — Einträge in `index.md` ohne zugehörige Datei (und umgekehrt: Dateien mit `type: wiki-page` die nicht in `index.md` stehen)

**Warnungen:**
- [ ] **Orphan-Seiten** — Wiki-Seiten mit `type: wiki-page` die von keiner anderen Seite verlinkt werden
- [ ] **Stale claims** — Seiten mit `[!recht]`-Callouts zu Normen, die laut neueren Quellen (erkennbar aus `log.md`) abgelöst oder geändert wurden, ohne dass die Seite aktualisiert wurde
- [ ] **Missing pages** — Begriffe die in mehreren Seiten per `[[Wikilink]]` referenziert werden, aber keine eigene Datei haben
- [ ] **Norm ohne Knoten** — Normen in `normen:`-Frontmatter, die in ≥3 Seiten vorkommen, aber keine eigene Normknoten-Seite haben
- [ ] **Urteil ohne Knoten** — Urteile in `urteile:`-Frontmatter, die in ≥3 Seiten vorkommen, aber keine eigene Leitentscheidungs-Seite haben
- [ ] **Frontmatter-Drift** — Seite mit `[!recht]`-Callout zu einer Norm/Entscheidung, die nicht im `normen:`/`urteile:`-Frontmatter steht
- [ ] **Unverifiziert** — Seiten mit `type: wiki-page` und nicht-leerem `quellen:`, die kein `verifiziert:`-Feld führen und deren `updated:` nach dem `[EINFÜHRUNGSDATUM]` liegt. Trage dort das Datum ein, an dem du den Verifikations-Pass eingeführt hast; ältere Seiten sind vom Bestandsschutz erfasst und werden nicht gemeldet.
- [ ] **Offener Belegbefund** — Seiten mit `[!unbelegt]`-Callout, dessen Prüfdatum mehr als 30 Tage zurückliegt. Ein `[!unbelegt]` ist ein offener Vorgang, kein Dauerzustand.

**Info:**
- [ ] **Beleg ohne Locator** — Seite führt `quellen:` und enthält `[!recht]`-Callouts, von denen keiner eine `Beleg:`-Zeile trägt. Kein Fehler (normtextgestützte Aussagen brauchen keine), aber ein Hinweis auf ungeprüfte Sekundärzitate.
- [ ] **Workflow-Drift** — `type: wiki-workflow`-Seiten, die von keiner Wiki-Seite, keinem Skill und keiner `AGENTS.md`/`CLAUDE.md` referenziert werden.
- [ ] **Data gaps** — Wiki-Seiten mit weniger als 2 Quellen im `quellen:`-Frontmatter (Themen mit dünner Abdeckung)
- [ ] **Fehlende Cross-Links** — Seiten zum gleichen Thema ohne gegenseitige Verlinkung (erkennbar durch übereinstimmende `thema:`-Felder)
- [ ] **Seiten ohne Frontmatter** — Dateien in Wiki-Ordnern ohne `type: wiki-page`

### Ausgabeformat

```
## Lint-Ergebnis — YYYY-MM-DD

### Fehler (N)
- [[Seitenname]]: broken link zu [[NichtExistierendSeite]]

### Warnungen (N)
- [[Seitenname]]: Orphan-Seite (keine eingehenden Links)
- [[Seitenname]]: stale claim — NetzDG § 3 Abs. 2 (verdrängt durch DSA seit 17.02.2024, nicht markiert)

### Info (N)
- [[Seitenname]]: nur 1 Quelle, Thema unterrepräsentiert
```

Befunde in `log.md` mit Syntax `- **Lint** — N Fehler, N Warnungen, N Info` dokumentieren.

### Empfohlene Kadenz

Nach je 10 Ingests oder monatlich als Mindest-Wartung.

---

## Benchmark-Spezifikation

Der Lint misst Struktur. Er misst nicht die **Antwortqualität**, also ob das Wiki eine Frage richtig beantwortet und ob es eine Frage, die es nicht beantworten kann, auch korrekt zurückweist. Ohne diese Messung lässt sich nicht feststellen, ob eine Schema-Änderung (etwa die Einführung von `normtyp:`) überhaupt etwas verbessert hat.

- **Datei:** `[BENCHMARK-ORT]/benchmark.md`. `[BENCHMARK-ORT]` ist ein Ordner **außerhalb** von `[WIKI-ORDNER]/`, etwa ein Kontext- oder Konfigurationsordner des Vaults.
- **Trigger:** `bench wiki`
- **Kadenz:** nach je 10 Ingests, gemeinsam mit `lint wiki`

**Ablageort außerhalb des Wiki-Ordners.** Die Datei liegt bewusst **nicht** in `[WIKI-ORDNER]/`, sondern daneben (hier: `00 Kontext/Wiki-Benchmark.md`). Grund: `query wiki` durchsucht den gesamten Wiki-Ordner. Läge das Frageset darin, fänden die antwortenden Agenten beim Grep die Goldantworten und bei den Out-of-Scope-Fragen den Vermerk „Zurückweisung". Die Messung würde dann nicht mehr erfassen, ob das Wiki seine Grenze erkennt, sondern ob der Agent den Spickzettel findet. Im Lauf vom 2026-09-24 ist genau das eingetreten: Alle vier antwortenden Agenten stießen beim Grep auf die Datei, drei legten es von sich aus offen. Das Ergebnis jenes Laufs ist deshalb nicht verwertbar.

### Aufbau

Zwei Blöcke:

1. **Wissensfragen** sind Fragen, deren Antwort im Wiki nachweislich steht. Je Eintrag: `Frage` · `Goldantwort` · `Belegseite` (Wikilink). Die Goldantworten werden **aus den Wiki-Seiten abgeleitet** und nicht aus dem Modellwissen formuliert.
2. **Out-of-Scope-Fragen** sind Fragen zu Themen, die das Wiki nachweislich *nicht* führt. Die korrekte Antwort ist die **Zurückweisung** („Dazu steht nichts im Wiki."). Solche Fragen vor der Aufnahme per Grep auf Trefferfreiheit prüfen.

Der zweite Block ist der wichtigere. Eine Wissensbasis, die auf Lücken mit plausiblem Modellwissen antwortet, ist gefährlicher als eine, die schweigt, weil die Antwort wie belegtes Wiki-Wissen aussieht.

### Durchführung

Jede Frage wird über `query wiki` gestellt, ohne dass die Goldantwort im Kontext liegt. Bewertet wird zweistufig: **inhaltlich korrekt** (ja/nein) und **korrekt belegt** (verweist auf die Belegseite). Eine inhaltlich richtige, aber unbelegte Antwort zählt als Teiltreffer und wird gesondert ausgewiesen.

### Eintrag in `log.md`

```
- **Bench** — Wissen 13/15 korrekt (11 belegt), Out-of-Scope 5/5 zurückgewiesen
```

## Namenskonventionen

- Dateinamen: normale Schreibweise mit Leerzeichen und Großbuchstaben
- Personen: `Nachname Vorname.md` (z.B. `Balkin Jack.md`)
- Gesetze/Verordnungen: offizielle Kurzbezeichnung (z.B. `DSGVO.md`, `EU AI Act.md`, `MStV.md`)
- Institutionen: gebräuchlichste Kurzform (z.B. `Bundesnetzagentur.md`, `KEF.md`)
- Konzepte: Hauptbegriff, ggf. mit Klammer für Disambiguierung (z.B. `Verantwortung (KI).md`)

## log.md Syntax

Eintrag-Format:

```
## YYYY-MM-DD

- **Ingest** `@citekey` ([Kurztitel])
  → erstellt: [[Seitenname1]], [[Seitenname2]]
  → aktualisiert: [[Seitenname3]]
  → Thema: Thema1, Thema2

- **Bulk-Ingest** ([N] Quellen, Thema: [Thema])
  → [N] neue Seiten, [N] aktualisiert

- **Lint** — [N] Probleme gefunden, [N] behoben

- **Neuer Ordner** `[Thema]/` angelegt
```

Unterbrochene Sessions markieren mit:
`[unterbrochen nach N Quellen, N ausstehend]`

---

## Nicht-Wiki-Seitentypen

Neben den Wiki-Seiten (`type: wiki-page`) tragen alle übrigen `.md`-Dateien in `[WIKI-ORDNER]/` ebenfalls ein `type`-Feld (OKF-Anforderung, s.u.). Kontrolliertes Vokabular:

- `hub` — Themen-Hub-Seite (Dateiname == Ordnername, z.B. `KI/KI.md`)
- `quelle` — Zotero-/Literatur-Quellenüberblick (`tags: [literatur]`)
- `notiz` — sonstige Notizen (atomare Gedanken, Referenz-/Hilfsnotizen ohne Wiki-Seiten-Status)
- `wiki-workflow` — aufrufbare Verfahrensseite in `Workflows/` (s. Abschnitt *Workflow-Seiten*)

Diese Typen sind **keine** Wiki-Seiten i.S.d. Tiefenstandards und werden von Lint-/Ingest-Routinen, die auf `type: wiki-page` filtern, nicht erfasst. `Persönlich/` und `Werkzeuge/` bleiben ganz außen vor.

## OKF-Kompatibilität (Google Open Knowledge Format v0.1)

Das Wiki ist bewusst weitgehend OKF-kompatibel gehalten (Knowledge-Austausch mit Dritten/Agenten).

- **Pflichtregel erfüllt:** Jede Nicht-Reserved-`.md` in `[WIKI-ORDNER]/` trägt ein nicht-leeres `type`-Feld. Alle übrigen Felder (`wiki-category`, `normen`, `urteile`, `rang`, `normtyp`, `in_kraft`, `wirksam_ab`, `bindungswirkung`, `ecli`, `thema`, `quellen`) sind OKF-konforme Extensions — Consumer müssen unbekannte Keys tolerieren.
- **`resource:`** ist das OKF-Empfehlungsfeld für die Asset-URI (s. Frontmatter-Schema oben; ELI/ECLI/DOI).
- **Reserved Files:** `index.md` + `log.md` vorhanden. Hinweis: OKF sieht für `index.md` *kein* Frontmatter vor — unser `type: wiki-index` ist eine geduldete Abweichung. Optional kann im Root-`index.md` `okf_version: 0.1` deklariert werden.
- **Bewusste Divergenz — Links:** Wir nutzen Obsidian-`[[Wikilinks]]` statt OKF-Standard-Markdown-Links (`[Text](/pfad.md)`). OKF toleriert das (Links werden als „broken" geduldet, Relationssemantik liegt ohnehin im Fließtext). Für einen echten OKF-Export wäre eine Build-Pipeline (Wikilinks → Markdown-Links) der richtige Weg — nicht die Umstellung des Vaults.
