# Validierungs-Checkliste — ub-landscape-konfigurieren

Ergänzt die generische Basis-Checkliste `../../neuen-devexpress-report-skill-anlegen/references/validation-generic.md` (Pflichtbaustein 4 des Meta-Skills) um die fachlichen Prüfpunkte dieser Skill. Beide gelten zusammen, keine ersetzt die andere.

## Inhalt

1. Die drei Kern-Rezept-Attribute stehen zusammen und korrekt
2. Keine Leerseite durch doppelten Seitenumbruch (Falle 1)
3. Übertrag-/Folgeseiten-Logik im Hauptbericht unverändert (Falle 2)
4. Host-Band-Sichtbarkeit unverändert für alle anderen Dokumenttypen
5. Manueller Designer-Test bleibt Pflicht

---

1. **Die drei Kern-Rezept-Attribute stehen zusammen und korrekt.** `GenerateOwnPages="true"` auf dem `XRSubreport`-Host-Control, `Landscape="true"` im eingebetteten `ReportSource`, und `PageWidthF`/`PageHeightF` dort tatsächlich vertauscht (nicht nur `Landscape="true"` gesetzt, während die Maße noch Hochformat-Werte sind — das führt zu einem verzerrten oder abgeschnittenen Layout). Alle drei müssen an derselben `ReportSource`-Stelle stehen, nicht verteilt auf mehrere Ebenen.

2. **Keine Leerseite durch doppelten Seitenumbruch (Falle 1).** Die Host-Band des `XRSubreport` darf kein `PageBreak="BeforeBand"` mehr tragen, sofern sie neben dem Unterbericht nur unsichtbaren/Marker-Inhalt enthält. Bei Restzweifel: Testdruck mit mindestens zwei Seiten vor dem Unterbericht und prüfen, dass zwischen der letzten Hauptbericht-Seite und der ersten Unterbericht-Seite keine leere Seite liegt.

3. **Übertrag-/Folgeseiten-Logik im Hauptbericht unverändert (Falle 2).** Mit einem Testbeleg, der auf normalen Positionen echte, von Null verschiedene Preise hat (nicht nur auf Stücklistenkomponenten o.ä. — siehe `references/known-issues.md` Eintrag 1), mehrseitig testdrucken (mindestens 3 Seiten Positionstabelle) und als PDF exportieren oder in einer Vorschau prüfen, die den Hauptbericht im Querformat-Teil nicht abschneidet. Wiederholte Tabellenkopfzeile und Übertrag-Betrag müssen auf allen Folgeseiten der Positionstabelle korrekt erscheinen — auch auf Seiten, die zeitlich nach der Landscape-Unterbericht-Seite liegen. Zeigt sich hier ein Symptom: **nicht** direkt einen Workaround bauen, sondern zuerst mit der Version vor der Landscape-Umstellung denselben Testdruck vergleichen (siehe `references/known-issues.md` Eintrag 2), um eine echte Regression von einem Testdaten-/Vorschau-Artefakt zu unterscheiden.

4. **Host-Band-Sichtbarkeit unverändert für alle anderen Dokumenttypen.** Die Bedingung, unter der die Host-Band (und damit der Unterbericht) überhaupt gedruckt wird (z.B. `e.Cancel = ... == 0` im `BeforePrint` der Band), darf durch das Entfernen von `PageBreak="BeforeBand"` nicht verändert worden sein — mit einem Testdruck eines Dokumenttyps ohne die zugehörigen Daten (z.B. ohne Leistungsnachweis) bestätigen, dass die Band weiterhin korrekt übersprungen wird und keine Leerseite an ihrer Stelle entsteht.

5. **Manueller DevExpress-Designer-Test bleibt Pflicht**, wie in der generischen Basis-Checkliste festgehalten — diese Checkliste ersetzt kein Laden im Designer und keinen Testdruck.
