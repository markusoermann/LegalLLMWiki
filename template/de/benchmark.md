---
type: wiki-benchmark
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Wiki-Benchmark

Gerüst für den Gold-Benchmark. Trigger: `bench wiki`. Kadenz: nach je 10 Ingests, gemeinsam mit `lint wiki`. Spezifikation in `wiki-schema.md`, Abschnitt *Benchmark-Spezifikation*.

Diese Datei ist bewusst leer ausgeliefert. Die Fragen müssen aus dem eigenen Wiki stammen, sonst misst der Benchmark nichts. Die beiden Einträge je Block sind reine Formatmuster und werden beim ersten echten Lauf ersetzt.

**Zielgröße:** 30 Wissensfragen, 10 Out-of-Scope-Fragen. Kleiner ist möglich, macht die Quote aber grob.

## Block 1: Wissensfragen

Fragen, deren Antwort im Wiki nachweislich steht. Die Goldantwort wird **aus der Belegseite abgeleitet** und nicht aus dem Modellwissen formuliert. Ändert sich die Belegseite inhaltlich, wird die Goldantwort mitgezogen.

### W01

- **Frage:** [Frage, die eine Wiki-Seite eindeutig beantwortet]
- **Gold:** [Kurze Antwort in ein bis zwei Sätzen, abgeleitet aus der Belegseite]
- **Beleg:** [[Seitenname]]

### W02

- **Frage:** [Frage, die zwei Seiten zusammenführen muss]
- **Gold:** [Kurze Antwort; nennt beide Teilaspekte]
- **Beleg:** [[Seitenname 1]], [[Seitenname 2]]

## Block 2: Out-of-Scope-Fragen

Fragen zu Themen, die das Wiki nachweislich *nicht* führt. Die korrekte Antwort ist die **Zurückweisung**, nicht eine plausible Antwort aus dem Modellwissen. Dieser Block ist der wichtigere: Eine Wissensbasis, die Lücken mit Modellwissen füllt, ist gefährlicher als eine, die schweigt, weil die Antwort wie belegtes Wiki-Wissen aussieht.

**Vor der Aufnahme prüfen:** Jede Frage per Grep über den Wiki-Ordner auf Trefferfreiheit testen. Findet sich einschlägiges Material, gehört die Frage nicht in diesen Block, sondern in Block 1.

### O01

- **Frage:** [Frage zu einem Thema, das im Wiki nicht vorkommt]
- **Erwartet:** Zurückweisung („Dazu steht nichts im Wiki.")
- **Grep-Check:** `[Suchbegriff]` → 0 Treffer, geprüft am YYYY-MM-DD

### O02

- **Frage:** [Frage, die einem im Wiki geführten Thema oberflächlich ähnelt, aber daneben liegt]
- **Erwartet:** Zurückweisung, ggf. mit Hinweis auf das benachbarte, tatsächlich geführte Thema
- **Grep-Check:** `[Suchbegriff]` → 0 Treffer, geprüft am YYYY-MM-DD

## Bewertungsregeln

- Jede Frage wird über `query wiki` gestellt, ohne dass die Goldantwort im Kontext liegt.
- Bewertet wird zweistufig: **inhaltlich korrekt** (ja/nein) und **korrekt belegt** (verweist auf die Belegseite).
- Eine inhaltlich richtige, aber unbelegte Antwort zählt als **Teiltreffer** und wird gesondert ausgewiesen.
- Eine Antwort auf eine Out-of-Scope-Frage gilt nur dann als korrekt, wenn sie zurückweist. Eine sachlich zutreffende Antwort aus dem Modellwissen ist hier ein **Fehler**, kein Teiltreffer.
- Bei Abweichung zwischen Antwort und Goldantwort zuerst prüfen, ob die Belegseite inzwischen geändert wurde. Dann die Goldantwort korrigieren, nicht die Bewertung.

## Auswertung

```
## Bench YYYY-MM-DD

Wissensfragen:     N/30 inhaltlich korrekt, davon N belegt (N Teiltreffer)
Out-of-Scope:      N/10 korrekt zurückgewiesen
Auffälligkeiten:   [Fragen, die durchgefallen sind, mit Kurzdiagnose]
```

Eintrag in `log.md`:

```
- **Bench** — Wissen N/30 korrekt (N belegt), Out-of-Scope N/10 zurückgewiesen
```
