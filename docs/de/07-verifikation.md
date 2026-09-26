# 07 · Verifikation, Belege & Benchmark

`lint wiki` prüft **Struktur**: tote Links, verwaiste Seiten, fehlende Knoten, Frontmatter-Drift. Es prüft nicht, ob ein Satz von der Quelle gedeckt ist, die unter ihm steht. Genau diese Lücke schließt der **Verifikations-Pass**.

## Die Belegschicht

`quellen:` belegt eine Seite als Ganzes. Für eine Prüfung reicht das nicht: Geprüft wird eine Passage, nicht ein ganzes PDF. Jede Kernaussage trägt deshalb ihren eigenen **Locator**.

| Mechanismus | Wo | Wofür |
|---|---|---|
| `Beleg:`-Zeile | im `[!recht]`-Callout, direkt unter der Titelzeile | juristische Aussagen aus Sekundärquellen (Auslegung, Streitstand, Zahlen) |
| Inline-Locator | am Satzende | nicht-juristische Kernaussagen aus einer Quelle |
| `[!unbelegt]`-Callout | unter der Aussage | Befund, der die Prüfung nicht bestanden hat |
| `verifiziert:` | Frontmatter | Datum des letzten bestandenen Passes |

```
> [!recht] ⚖️ Rang 2 (EU-Verordnung) · DSGVO Art. 6 Abs. 1 lit. f
> Beleg: @kuehling2024 S. 142 Rn. 18
> Direkt anwendbares EU-Sekundärrecht; verbindlich seit 25.05.2018.
```

```markdown
Der Effekt ist in den Daten ab 2023 messbar (@mustermann2026, S. 14).
```

Stützt sich eine Aussage unmittelbar auf den Normtext, entfällt die `Beleg:`-Zeile: Der Normverweis in der Titelzeile **ist** der Locator. Das Inline-Format lautet `(@citekey, S. N)`, `(@citekey, Abschn. N)` oder `(@citekey)` bei Quellen ohne Paginierung, grep-bar über `\(@[a-z]`.

```
> [!unbelegt] ⚠️ Nicht belegt — geprüft YYYY-MM-DD
> Die angegebene Quelle @citekey trägt diese Aussage an der genannten Stelle nicht.
> Entweder Locator korrigieren, Quelle nachliefern oder Aussage entfernen.
```

Der Callout ist ein offener Befund, kein Dauerzustand: `lint wiki` meldet `[!unbelegt]`-Befunde ab 30 Tagen Alter als Warnung.

## Verifikations-Pass

Der Pass läuft automatisch als **Schritt 6 jedes Ingests** und zusätzlich auf den Trigger `verify wiki [Seite|Thema|letzter Ingest]`.

Geprüft wird von einem **frischen Subagenten ohne den Schreibkontext**. Wer den Text geschrieben hat, kann ihn nicht unbefangen gegenprüfen; das ist der Kern des Verfahrens, keine Formalie. Der Subagent bekommt Seitenpfad, alle Locator und die Felder `normen:`/`urteile:`/`ecli:`, schlägt die Passagen per Zotero-MCP nach (primär `get_content`; `search_fulltext` nur bei bekannter Originalwendung, da es Substrings und keine Termkombinationen sucht) und klassifiziert jede Aussage:

| Befund | Bedeutung | Konsequenz |
|---|---|---|
| `belegt` | Quellenstelle trägt die Aussage | nichts |
| `nicht belegt` | Stelle existiert, trägt die Aussage aber nicht | max. 2 Nachbesserungsversuche (Locator korrigieren, bessere Stelle suchen), danach `[!unbelegt]` |
| `widersprochen` | Quelle sagt etwas anderes | Aussage im selben Durchgang korrigieren, Korrektur in `log.md` |
| `nicht prüfbar` | kein Volltext vorhanden | Aussage bleibt, `verifiziert:` wird **nicht** gesetzt, `log.md`-Vermerk `[kein Volltext]` |

**Hard-Fail (sofortige Entfernung, keine Nachbesserung):** erfundene oder nicht auffindbare ECLI, erfundene Normbezeichnung (Artikel/Paragraph existiert im zitierten Gesetz nicht), erfundene Fundstelle (Band, Seite, Randnummer nicht verifizierbar), erfundener citekey (nicht in Zotero vorhanden). Diese vier Fälle werden entfernt, nicht markiert, und im Log als `Hard-Fail` geführt. Die Regel „ECLI niemals erfinden" war bis dahin eine Anweisung; hier wird sie zur Prüfung. Anweisungen erzwingen nichts, Prüfungen schon.

Besteht die Seite ohne offenen Befund, wird `verifiziert: YYYY-MM-DD` gesetzt. Bleibt ein `[!unbelegt]`-Callout stehen, wird das Feld nicht gesetzt.

```
- **Verifikation** [[Seitenname]] — 14 Aussagen: 12 belegt, 1 korrigiert, 1 unbelegt, 0 Hard-Fail
```

## Belegtheit ≠ Richtigkeit

> Der Verifier stellt **ausschließlich** fest, ob die angegebene Quellenstelle die Aussage trägt. Er entscheidet nicht, ob die Aussage zutrifft, und er ersetzt keine fachliche Prüfung.

Juristische Auslegung hat keinen maschinell prüfbaren Wahrheitsmaßstab; sie ist streitig, und zwar berechtigt. Ein Verifier, der über Richtigkeit befände, würde eine Meinung zum Prüfergebnis erklären und damit falsche Sicherheit erzeugen, versehen mit einem Prüfsiegel. Belegtheit ist schwächer, aber prüfbar, und deshalb die einzige Zusage, die das Wiki macht.

## Befunde brauchen eine Gegenprobe

Der Verifikations-Pass erzeugt Befunde, die zum Handeln auffordern, und der Hard-Fail-Befund fordert zur sofortigen Entfernung auf. Genau deshalb braucht er eine Kontrollinstanz: **Ein Befund ist eine Behauptung über den Text, keine Feststellung.**

Der teuerste Fall aus dem Betrieb war kein übersehener Fehler, sondern ein erfundener. Ein Verifier meldete eine Autorenangabe im Wiki als falsch und stützte das auf das Autorenfeld der Literaturverwaltung. Der Volltext des Aufsatzes führte im Kolumnentitel durchgängig die Schreibweise des Wikis. Falsch war der Datensatz in der Literaturverwaltung, nicht der Text. Die ungeprüfte Umsetzung hätte korrekte Angaben in drei Dateien zerstört, und zwar unter der Überschrift „Hard Fail", also mit dem Anspruch besonderer Strenge.

Daraus zwei Regeln:

**Die Gegenprobe folgt der Rangordnung der Quellen.** Metadaten einer Literaturverwaltung sind abgeleitet und fehleranfällig; die Publikation selbst ist maßgeblich. Bei Normbezeichnungen entscheidet der amtliche Text, nicht die Sekundärliteratur, die ihn zitiert. Im selben Lauf bestätigte der amtliche Abgleich zwei gemeldete Normzweifel und widerlegte einen dritten.

**Nicht verifizierbares wird entfernt, nicht ersetzt.** Ließ sich ein bezweifeltes Datum aus der Arbeitsumgebung nicht klären, wird die Angabe gestrichen, nicht gegen eine zweite ungeprüfte ausgetauscht. Ein Aktenzeichen identifiziert eine Entscheidung auch ohne Datum.

Das ist dieselbe Disziplin, die für die mechanischen Prüfwerkzeuge gilt (siehe `tools/README.md`). Beim Verifikations-Pass wiegt sie schwerer, weil sein Befund autoritativ formuliert ist und zur Löschung auffordert, während ein Skript nur eine Liste ausgibt.

## Einführung im laufenden Bestand

Wer den Verifikations-Pass nicht am ersten Tag einführt, steht vor einem Altbestand, der ihn nie durchlaufen hat. Ihn nachträglich vollständig zu prüfen ist teuer: Ein Locator setzt voraus, die Quelle gelesen zu haben — das ist faktisch ein Re-Ingest jeder Seite. Bei einigen hundert Seiten sind das Wochen.

Die Versuchung ist, es trotzdem als Kampagne zu planen. Die bessere Regel besteht aus zwei Hälften, die nur zusammen tragen:

**Bestandsschutz.** Seiten, die vor dem Einführungsdatum zuletzt geändert wurden, werden nicht aktiv nachgezogen. Das ist keine Nachlässigkeit, sondern korrekte Kennzeichnung: Fehlt `verifiziert:`, gilt die Seite als ungeprüft — und genau das ist sie. Der Fehler wäre nicht, sie ungeprüft zu lassen, sondern sie für geprüft zu halten.

**Heben beim Anfassen.** Wird eine Altseite aus anderem Anlass inhaltlich geändert, verliert sie den Bestandsschutz und wird in derselben Bearbeitung gehoben: Locator, Verifikations-Pass, `verifiziert:`. Maßgeblich ist der Umfang der Seite, nicht der der Änderung.

Der Bestand konvergiert damit über die normale Arbeit statt über eine Sonderanstrengung — und in der richtigen Reihenfolge, denn was oft angefasst wird, wird zuerst geprüft. Seiten, die jahrelang niemand berührt, bleiben ungeprüft; das ist vertretbar, solange sie als ungeprüft ausgewiesen sind.

Zwei Abgrenzungen, ohne die die Regel kippt: Sprengt das Heben den Rahmen der Bearbeitung, bleibt `verifiziert:` **offen** und das Protokoll hält fest, was geprüft wurde und was nicht — ein halb geprüfter Stand darf nie als geprüft erscheinen. Und rein mechanische Läufe heben nicht: Sonst erzwingt ein Suchen-und-Ersetzen über 40 Dateien 40 Verifikations-Pässe.

## Ingest-Dekomposition

Der lineare Ingest lädt Volltext, Index und Schreibkontext in ein einziges Kontextfenster. Die Zerlegung in Sub-Agenten, die Daten ausschließlich über standardisierte JSON-Berichte austauschen und nie über geteilten Kontext, macht aus der Kontextgrenze eine Durchsatzfrage.

| Rolle | Eingabe | Ausgabe | Hält im Kontext |
|---|---|---|---|
| **Extraktor** | Zotero-Item | `extraktion.json` | nur die eine Quelle |
| **Kollisionsprüfer** | `extraktion.json` + `index.md` | `kollision.json` | nur Index + JSON |
| **Schreiber** (parallel, je Seite) | ein Eintrag aus `kollision.json` | `schreibbericht.json` | nur seine Seite |
| **Verifier** (frisch) | Seite + Locator | `verifikat.json` | nur Passagen |

Aktivierung erst ab **Bulk-Ingest mit mehr als 3 Quellen** oder **Einzelquelle mit mehr als ~50 Seiten Volltext** (Monografien, Kommentare, Sammelbände). Darunter bleibt der lineare Ablauf richtig, der Overhead lohnt nicht.

Ablage der JSONs in `/tmp/wiki-ingest/<citekey>/`, bewusst außerhalb des Vaults, damit Zwischenstände den Wissensbestand nicht verunreinigen. Der Orchestrator hält nur die JSONs, nie die PDFs. Bei Abbruch ist der Ordner der Wiederaufsetzpunkt.

## Benchmark

`lint wiki` misst Struktur, nicht Antwortqualität. Ohne Messung lässt sich nicht feststellen, ob eine Schema-Änderung überhaupt etwas verbessert hat. Datei: `[BENCHMARK-ORT]/benchmark.md`, also **außerhalb** des Wiki-Ordners, damit die antwortenden Agenten die Goldantworten nicht per Grep finden, Trigger `bench wiki`, Kadenz nach je 10 Ingests gemeinsam mit `lint wiki`.

1. **Wissensfragen:** Fragen, deren Antwort im Wiki nachweislich steht. Je Eintrag `Frage` · `Goldantwort` · `Belegseite` (Wikilink). Die Goldantworten werden aus den Wiki-Seiten abgeleitet, nicht aus dem Modellwissen formuliert.
2. **Out-of-Scope-Fragen:** Fragen zu Themen, die das Wiki nachweislich nicht führt. Korrekt ist hier die **Zurückweisung** („Dazu steht nichts im Wiki.").

**Der zweite Block ist der wichtigere.** Eine Wissensbasis, die Lücken mit plausiblem Modellwissen füllt, ist gefährlicher als eine, die schweigt, weil die erfundene Antwort wie belegtes Wiki-Wissen aussieht.

Jede Frage wird über `query wiki` gestellt, ohne dass die Goldantwort im Kontext liegt. Bewertet wird zweistufig: **inhaltlich korrekt** (ja/nein) und **korrekt belegt** (verweist auf die Belegseite). Eine inhaltlich richtige, aber unbelegte Antwort zählt als Teiltreffer und wird gesondert ausgewiesen.

```
- **Bench** — Wissen 13/15 korrekt (11 belegt), Out-of-Scope 5/5 zurückgewiesen
```

## Herkunft des Verfahrens

Verifikations-Pass, Dekomposition und Benchmark sind dem *test verifier–improver* aus Paper2Agent nachgebildet: Miao et al., „Reimagining research papers as interactive and reliable AI agents", *Nature* 2026, DOI [`10.1038/s41586-026-11044-y`](https://doi.org/10.1038/s41586-026-11044-y), Repo [`jmiao24/Paper2Agent`](https://github.com/jmiao24/Paper2Agent). Dort darf keine extrahierte Funktion in den fertigen MCP-Server, die nicht gegen die Quelle getestet wurde; was durchfällt, wird mit Fehlerkommentar ausgeschlossen statt behalten. Das Wiki überträgt diesen Grundsatz auf Aussagen: Was seine Quelle nicht trägt, bleibt nicht stillschweigend stehen.

## Weiter
→ `08-mcp-server.md` — der Wiki-MCP-Server, der `list_unverified` und `list_stale` als Tools bereitstellt.
