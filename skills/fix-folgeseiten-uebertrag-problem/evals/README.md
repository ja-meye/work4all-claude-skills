# Evaluations — `fix-folgeseiten-uebertrag-problem`

Sechs Szenarien, jedes aus einem **real aufgetretenen** Fehlerfall dieses Skills abgeleitet
(Sitzung 03./04.09.2026, Report `dxAio_template`; Hintergrund je Fall in `references/known-issues.md`,
Einträge 22–31). Jedes Szenario beschreibt in `expected_behavior`, woran ein korrekter Lauf zu
erkennen ist — nicht, welche Formulierung er benutzt.

| Datei | Prüft | known-issues |
|----|----|----|
| `01-referenz-ist-diagnosefassung.json` | Referenz wird vorgeprüft statt blind kopiert | 27 |
| `02-elemente-entfernt-itemn.json` | Lückenlose `ItemN`-Nummerierung nach Entfernungen | 22 |
| `03-hoehen-und-laufzeit.json` | Phasentrennung und Höhen-Wiederherstellung | 23, 24 |
| `04-padding-position.json` | Padding-Position aus der Datei ableiten, Muster (h) vollständig | 25, 28 |
| `05-kein-muster-trifft-zu.json` | „keine Änderung nötig" ist ein gültiges Ergebnis | — |
| `06-visible-localization-override.json` | `LocalizationItems` übersteuert `Visible`, Muster (j) vollständig inkl. binärsicherer Bearbeitung | 29, 30, 31 |

**Verwendung:** Mit dem `skill-creator`-Skill als Eval-Suite ausführen, oder manuell: Szenario-Query
mit einer passenden Testdatei stellen und das Ergebnis gegen `expected_behavior` abgleichen.
Nach jeder inhaltlichen Skill-Änderung mindestens die Szenarien laufen lassen, die den geänderten
Bereich betreffen.
