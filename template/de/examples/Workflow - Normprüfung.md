---
type: wiki-workflow
thema: [Methodik]
created: 2026-09-23
updated: 2026-09-23
---

# Workflow: Normprüfung

> **Beispielseite (Workflow).** Zeigt den Aufbau einer aufrufbaren Verfahrensseite (`type: wiki-workflow`). Im laufenden Vault liegt sie in `[WIKI-ORDNER]/Workflows/`. Beim Nachbau durch eigene Verfahren ersetzen oder ergänzen.

## Zweck

Eine einzelne Norm systematisch erschließen, bevor sie in einer Wiki-Seite, einem Gutachten oder einem Lehrtext verwendet wird. Der Workflow beantwortet eine Frage: Was genau ordnet diese Norm für wen an, ab wann, und was folgt daraus? Er ersetzt weder die Subsumtion im Einzelfall noch die fachliche Prüfung durch einen Menschen.

**Aufruf:** `workflow: Normprüfung`

## Schritte

Die Schritte werden in dieser Reihenfolge abgearbeitet. Jeder Schritt endet mit einer Prüffrage; wird sie nicht beantwortet, geht es nicht weiter, sondern zurück zur Quelle.

1. **Anwendungsbereich bestimmen.** Vier Dimensionen getrennt führen:
   - sachlich: welche Sachverhalte und Gegenstände erfasst die Norm
   - persönlich: wer ist Normadressat, wer ist begünstigt
   - räumlich: welches Territorium, gilt ein Marktort- oder Auswirkungsprinzip
   - zeitlich: `in_kraft:`, `wirksam_ab:`, Übergangsrecht

   *Prüffrage:* Lässt sich für jede der vier Dimensionen ein Satz mit Normverweis formulieren?

2. **Normfunktion klassifizieren.** Die Norm einem oder mehreren Werten des `normtyp:`-Vokabulars zuordnen (Gebot, Verbot, Erlaubnis, Anspruchsnorm, Freiheitsrecht, Kompetenznorm, Gestaltungsrecht, Immunität, Definitionsnorm, Qualifikationsnorm). Kombinationen sind der Normalfall, nicht die Ausnahme.

   *Prüffrage:* Welche Rechtsposition etabliert die Norm, und für wen ist sie die korrelative Belastung?

3. **Tatbestandsmerkmale zerlegen.** Jedes Merkmal einzeln benennen, Legaldefinitionen aus dem Definitionsartikel des Gesetzes zuordnen, unbestimmte Rechtsbegriffe markieren und offene Auslegungsfragen als solche kennzeichnen.

   *Prüffrage:* Ist jedes Merkmal entweder legaldefiniert oder durch eine Leitentscheidung konkretisiert, und liegt dafür ein Locator vor?

4. **Rechtsfolge bestimmen.** Zwischen gebundener Entscheidung und Ermessen unterscheiden. Ansprüche, Sanktionen, Unwirksamkeitsfolgen und Verfahrenspflichten getrennt führen, weil sie unterschiedliche Durchsetzungswege haben.

   *Prüffrage:* Wer kann was von wem verlangen, und wer setzt es durch?

5. **Normverhältnis klären.** Vorrang, Verdrängung, Spezialität und Ergänzung zu benachbarten Normen mit dem typisierten Relationsvokabular ausdrücken (setzt um, verdrängt, konkretisiert, wendet an, wirkt nach). Umsetzungs- und Öffnungsklauseln gesondert vermerken.

   *Prüffrage:* Gibt es eine höherrangige oder spätere Norm, die diese hier ganz oder teilweise verdrängt?

6. **Dokumentieren.** Ergebnis in den Normknoten schreiben:
   - Frontmatter: `rang:`, `normtyp:`, `in_kraft:`, `wirksam_ab:`, `normen:`, `rechtsstand:`
   - `[!recht]`-Callout mit `Beleg:`-Zeile für jede ausgelegte Aussage
   - Wikilinks auf betroffene Konzeptseiten und Leitentscheidungen

   *Prüffrage:* Trägt jede ausgelegte Aussage einen Locator, und ist der Verifikations-Pass gelaufen?

## Abbruchkriterien

- Die Norm ist zum Prüfungszeitpunkt weder in Kraft noch anwendbar: Prüfung aussetzen, Stand im Normknoten vermerken, erwartetes Inkrafttreten führen.
- Der amtliche Normtext liegt nicht vor: keine Rekonstruktion aus dem Gedächtnis, stattdessen Abbruch mit Vermerk `[kein Volltext]` im Log.
- Die Norm ist vollständig aufgehoben oder für nichtig erklärt: Prüfung abbrechen, Callout nach dem Muster für abgelöste Normen kennzeichnen, Nachwirkung für Altfälle prüfen.
- Die Auslegung eines Merkmals ist offen streitig: Streitstand darstellen statt entscheiden, Gegenansichten mit eigenem Locator führen.
- Es geht erkennbar um einen konkreten Einzelfall: abbrechen und an die fachliche Bearbeitung verweisen. Dieser Workflow erschließt Normen, er berät nicht.

## Verwandte Knoten

[[DSGVO Art. 6]] · [[EuGH C-300-21 (Österreichische Post)]] · [[Beispielkonzept (Datenminimierung)]]
