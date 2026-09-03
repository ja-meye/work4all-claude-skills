# Validierungs-Checkliste

Verpflichtend vor jeder Auslieferung einer bearbeiteten `.repx`. Jeder einzelne Punkt hat in der Vergangenheit tatsächlich einen Fehler gefangen, der beim bloßen Lesen des Diffs nicht aufgefallen wäre — das ist keine reine Formalität.

1. **XML-Wohlgeformtheit.** Die komplette Datei mit einem XML-Parser laden (z.B. `xml.dom.minidom.parseString`). Ein Parse-Fehler bedeutet: nicht ausliefern, Fehler beheben.

2. **Keine doppelten `Ref="N"`-IDs.** Alle `Ref="..."`-Vorkommen in der Datei per Regex sammeln und zählen (z.B. mit `collections.Counter`). Jede ID darf nur einmal vorkommen. Duplikate deuten meist auf einen fehlerhaften Copy-Paste oder Splice-Fehler hin.

3. **Jede `<Scripts On*="Name">`-Referenz löst sich auf eine definierte Methode auf.** Wichtig: getrennt pro `ScriptsSource`-Block prüfen (Hauptreport und jeder Subreport haben eigene Namensräume, siehe `repx-technical-notes.md`). **Regex-Falle (28.08. beobachtet):** Suche `On\w+="(\w+)"` NUR innerhalb bereits isolierter `<Scripts ... />`-Elemente, nicht in der kompletten Roh-XML — sonst matchen fachliche Attribute wie `PrintOnEmptyDataSource="false"` versehentlich als vermeintliches Event und melden ein Phantom-„fehlendes Symbol" `false`, das mit Skript-Verdrahtung nichts zu tun hat (siehe `repx-technical-notes.md`, Abschnitt „XML/Skript-Paritätsregel"). Ein korrekt gescopter Check meldet auf einer sauberen Datei 0 fehlende Methoden — nicht `['false']`. Baseline vor der Bearbeitung erstellen (welche Namen fehlten schon *vorher* — typischerweise Subreport-Handler, die im falschen Namensraum gesucht werden, das sind keine echten Fehler) und nach der Bearbeitung nur auf **neu** fehlende Namen prüfen, die durch die eigene Bearbeitung entstanden sind.

4. **Klammern-Balance.** Anzahl `{` muss Anzahl `}` im bearbeiteten Skriptteil entsprechen. Einfache, aber wirksame Absicherung gegen einen abgeschnittenen oder falsch eingefügten Block.

5. **`<Summary Ref=...>`-Anzahl vor/nach vergleichen.** Diese Zahl darf sich durch die Bearbeitung **nie unbeabsichtigt ändern**. Siehe die `sumCarryoverSum`-Falle in `known-issues.md` — ein scheinbar redundantes `Summary`-Element zu entfernen hat dort bereits einmal eine Regression verursacht. Wenn sich die Zahl ändert, muss das eine bewusste, im Changelog explizit benannte Entscheidung sein, keine stille Nebenwirkung.

6. **Symmetrische Entfernung nach jeder Handler-Löschung.** Nach dem Entfernen einer Methode bestätigen: die Methode ist weder in der XML-Verdrahtung (`<Scripts On*="...">`) noch sonst irgendwo im Skript referenziert (z.B. nicht von einer anderen Methode aufgerufen). Eine Methode zu löschen, aber ihre `<Scripts>`-Referenz stehen zu lassen (oder umgekehrt), macht die Datei entweder ladeunfähig oder lässt toten Verweis-Ballast zurück.

7. **Changelog als nummerierte Liste erzeugen.** Jede einzelne Änderung als eigener Listenpunkt, auf Deutsch, mit kurzer Begründung — das Changelog ist die Grundlage, auf der work4all-Mitarbeiter (die den Report nicht selbst gebaut haben) nachvollziehen, was warum verändert wurde. Kein Punkt ohne Begründung, auch wenn sie nur ein halber Satz ist.

8. **Bei einer Datei, die zwischenzeitlich im DevExpress-Designer geöffnet/gespeichert war: alle `KeepTogether`-Vorkommen (und andere zuvor gezielt gesetzte Layout-Eigenschaften) neu auflisten und mit dem erwarteten Zustand abgleichen**, statt anzunehmen, dass frühere Fixes automatisch erhalten geblieben sind. Ein Designer-Speichervorgang serialisiert die Datei komplett neu (erkennbar u. a. an durchgängig neu vergebenen `Ref`-IDs) und kann dabei per XML gesetzte Einzel-Eigenschaften stillschweigend verwerfen (siehe `known-issues.md`, Eintrag 3). Bei diesem Szenario nicht nur die eigene neue Änderung validieren, sondern auch die aus früheren Runden.

9. **BOM am Dateianfang erhalten (PFLICHT, seit 28.08.).** Nach jedem Bearbeitungsschritt prüfen, dass die Datei weiterhin mit dem UTF-8-BOM (`EF BB BF`) beginnt — z. B. `open(datei, 'rb').read(3) == b'\xef\xbb\xbf'`. **Bekannte Falle:** Wird eine Datei mit `encoding='utf-8-sig'` gelesen (das entfernt die BOM beim Lesen) und anschließend ohne die BOM wieder manuell voranzustellen zurückgeschrieben, geht sie in genau diesem Bearbeitungsschritt verloren — ohne Fehlermeldung, ohne dass ein Diff das automatisch anzeigt. Das ist bereits passiert (zwei ausgelieferte Dateien in Folge ohne BOM, erst beim dritten Lauf bemerkt) und muss nach **jedem einzelnen** Schreibschritt geprüft werden, nicht nur einmal am Ende der ganzen Kette.

10. **Vollständigkeits-Check gegen den Fix-Katalog (a)–(g) plus Skript-Hygiene (e), PFLICHT seit 28.08.** Vor der Auslieferung explizit gegenprüfen: Wurde für JEDES anwendbare Muster aus `fix-catalog.md` — nicht nur die im Skript sichtbaren — sowohl der Skript-Teil als auch die reinen XML-/Layout-Eigenschaften (KeepTogether, Höhen inkl. `<Localization>`-Block, Tabellenzeilen-Anzahl) mit der Referenz abgeglichen? Wurde die tote-Code-Hygiene durchgeführt? Ein „Ja" auf beide Fragen ist Voraussetzung für die Auslieferung, kein optionaler Bonus-Schritt. Siehe `known-issues.md` Eintrag 8.

11. **Selbst-Audit der Referenzdatei.** Punkte 1–6 zusätzlich auf die Referenzdatei selbst anwenden (nicht nur auf die reparierte Zieldatei). Findet sich dort ein echter Fehler: korrigieren, als neue, eigens gestempelte Datei ausliefern, und in Changelog + `known-issues.md` vermerken. Kein Fehler gefunden: das im Bericht ehrlich so festhalten.

12. **Keine rohen `\r`/`\n`-Zeichen im re-escapten `ScriptsSource`-Attributwert (PFLICHT, seit 31.08.).** Nach dem Schreiben den rohen, noch escapten Attributwert (vor `html.unescape`) darauf prüfen, dass er keine literalen `\r`- oder `\n`-Zeichen mehr enthält — nur noch `&#xD;&#xA;`-Entities (`raw_value.count('\r') == 0 and raw_value.count('\n') == 0`). **Bekannte Falle:** Fehlt vor dem finalen `\n` → `&#xD;&#xA;`-Schritt die Normalisierung der Zeilenenden auf reines `\n` (siehe `repx-technical-notes.md` Schritt 4.3), bleibt bei jedem Zeilenumbruch im GESAMTEN Skript ein rohes `\r` unmittelbar vor dem neu kodierten `&#xD;&#xA;` stehen — sichtbar als Leerzeile nach jeder einzelnen Zeile beim Öffnen im Designer/Editor, aber unsichtbar in Punkt 1 (XML bleibt wohlgeformt) und in einem reinen Struktur-Diff. Siehe `known-issues.md` Eintrag 13 für den konkreten Vorfall. Dieser Check hätte ihn vor der Auslieferung gefangen.

## 13.–16. Neue Pflichtpunkte seit 04.09.2026

13. **`ItemN`-Sammlungen lückenlos.** Nach jedem Entfernen/Einfügen eines Sammlungs-Kindes muss jede `<...>`-Sammlung ihre Kinder lückenlos als `Item1..ItemN` benennen. Eine Lücke führt dazu, dass DevExpress alles dahinter still ignoriert — die Datei bleibt dabei wohlgeformt und alle anderen Checks grün. Siehe `known-issues.md` Eintrag 22.
14. **Kein in `PrintOnPage` gesetztes Flag wird in einem `BeforePrint`-Handler gelesen.** Die PrintOnPage-Phase läuft für das gesamte Dokument nach allen BeforePrint-Ereignissen; solche Flags sind dort immer `false`. Schreibzugriffe (Reset) sind erlaubt. Siehe `known-issues.md` Eintrag 23.
15. **Keine `HeightF`-Zuweisung in einem `PrintOnPage`-Handler**, und umgekehrt: abgesenkte Design-Höhen brauchen zwingend eine Wiederherstellung in `BeforePrint`. Siehe `known-issues.md` Eintrag 24.
16. **Kein Diagnose-/Debug-Code in der Auslieferung** (`_dbgHelper`-artige Felder, Debug-Label, `Diagnose-Test`-Kommentare) — auch dann nicht, wenn er aus einer Referenzdatei stammt. Siehe `known-issues.md` Eintrag 27.

17. **Padding-Positionen aus der Datei ableiten, nicht aus der Doku.** `Padding` ist `Left,Right,Top,Bottom,Dpi` — Top ist Position 3. Vor jeder Padding-Änderung die Reihenfolge gegen die vorhandenen `Padding.LeftF`/`Padding.RightF`-Bindungen prüfen (Check `C17`). Check `C18` benennt zusätzlich jede Padding-Änderung gegenüber der Baseline im Klartext (`Right 0->10`) — diese Zeile vor der Auslieferung lesen und gegen die Absicht abgleichen. Siehe `known-issues.md` Eintrag 28.

## Automatisierter Check-Index: `scripts/validate_repx.py`

Alle Punkte dieser Checkliste sind in `scripts/validate_repx.py` als ausführbare Checks `C01`–`C19` hinterlegt. Aufruf:

```bash
python3 scripts/validate_repx.py <bearbeitet.repx> --baseline <original.repx>
```

Das Skript gibt eine Tabelle mit `OK`/`FAIL`/`WARN` je Check aus und liefert Exit-Code 1, sobald ein FAIL auftritt. **Verbindlich:** nach *jeder* Bearbeitungsrunde laufen lassen, nicht nur einmal am Ende — und zusätzlich einmal **auf der Referenzdatei selbst** (Punkt 11, Selbst-Audit). Ein FAIL wird behoben oder im Bericht ausdrücklich als bewusste Abweichung begründet; ein `WARN` mindestens gelesen.

Schlägt ein Check an, ohne dass ein echter Fehler vorliegt (Fehlalarm), wird **der Check nachgeschärft** und die Verschärfung hier vermerkt — nicht der Befund ignoriert.

## Praktischer Hinweis

Diese Checks lassen sich alle als kurze Python-Snippets direkt gegen die extrahierte `.cs`-Datei bzw. die rohe `.repx`-XML laufen lassen — schneller und zuverlässiger, als jede Änderung einzeln von Hand nachzuverfolgen. Es lohnt sich, ein kleines Validierungsskript zu bauen (Parsing, Ref-Zählung, Methodenabgleich mit korrektem `<Scripts>`-Scoping, Klammernzählung, Summary-Zählung, BOM-Check) und es nach *jeder* Bearbeitungsrunde erneut laufen zu lassen, nicht nur einmal ganz am Ende.

**Zeitstempel für Dateinamen:** Immer mit expliziter Zeitzone erzeugen, z. B. `TZ=Europe/Berlin date '+%Y-%m-%d_%H-%M'`. Die Session-Umgebung läuft oft in UTC — ein bloßes `date` ohne `TZ=` erzeugt einen für den Kunden falschen (meist 1–2h abweichenden) Zeitstempel. Siehe SKILL.md Schritt 7 und `known-issues.md` Eintrag 11.
