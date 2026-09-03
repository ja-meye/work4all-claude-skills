# Generische Validierungs-Checkliste (Minimum für jeden Korrektur-Skill)

Diese Checks gelten für **jede** `.repx`-Bearbeitung, unabhängig vom fachlichen Thema des Fixes. Sie sind das Minimum, das Pflichtbaustein 4 („Validierung") im Haupt-Skill (`SKILL.md`) verlangt — jeder Korrektur-Skill ergänzt sie um eigene fachliche Prüfpunkte in seiner eigenen `validation-checklist.md`, ersetzt sie aber nicht. Jeder einzelne Punkt hat in der Vergangenheit tatsächlich einen Fehler gefangen, der beim bloßen Lesen des Diffs nicht aufgefallen wäre — das ist keine reine Formalität.

1. **XML-Wohlgeformtheit.** Die komplette Datei mit einem XML-Parser laden (z. B. `xml.dom.minidom.parseString` oder `xml.etree.ElementTree.parse`). Ein Parse-Fehler bedeutet: nicht ausliefern, Fehler beheben.

2. **Keine doppelten `Ref="N"`-IDs.** Alle `Ref="..."`-Vorkommen in der Datei per Regex sammeln und zählen (z. B. mit `collections.Counter`). Jede ID darf nur einmal vorkommen. Duplikate deuten meist auf einen fehlerhaften Copy-Paste oder Splice-Fehler hin. Zusätzlich: alle `#Ref-x`-Verweise (inkl. `<Localization>`-Block, siehe `repx-format-basics.md`) müssen sich auf eine tatsächlich existierende `Ref`-ID auflösen.

3. **Jede `<Scripts On*="Name">`-Referenz löst sich auf eine definierte Methode auf.** Getrennt pro `ScriptsSource`-Block prüfen (Hauptreport und jeder Subreport haben eigene Namensräume, siehe `repx-format-basics.md`). Baseline vor der Bearbeitung erstellen (welche Namen fehlten schon *vorher* — typischerweise Subreport-Handler, die im falschen Namensraum gesucht werden, das sind keine echten Fehler) und nach der Bearbeitung nur auf **neu** fehlende Namen prüfen, die durch die eigene Bearbeitung entstanden sind.

4. **Klammern-Balance.** Anzahl `{` muss Anzahl `}` im bearbeiteten Skriptteil entsprechen. Einfache, aber wirksame Absicherung gegen einen abgeschnittenen oder falsch eingefügten Block.

5. **Symmetrische Entfernung nach jeder Handler-Löschung.** Nach dem Entfernen einer Methode bestätigen: die Methode ist weder in der XML-Verdrahtung (`<Scripts On*="...">`) noch sonst irgendwo im Skript referenziert (z. B. nicht von einer anderen Methode aufgerufen). Eine Methode zu löschen, aber ihre `<Scripts>`-Referenz stehen zu lassen (oder umgekehrt), macht die Datei entweder ladeunfähig oder lässt toten Verweis-Ballast zurück.

6. **Base64-Datenquelle dekodiert und separat als XML geprüft**, falls die Datei eine eingebettete Datenquelle in dieser Form enthält.

7. **BOM-Prüfung nach jedem Schreibschritt.** Die Datei muss nach dem Schreiben wieder mit BOM beginnen (siehe Schreib-Pipeline in `repx-format-basics.md`).

8. **`work4all-log`-Block bleibt unangetastet**, außer der eigenen neuen Zeile am Ende (siehe `fix-log-format.md`) — insbesondere darf eine Skript-Hygiene-Passage diesen Block niemals als „toten Kommentar" behandeln. (Bis Log-Format-Version v1 hieß der Block `work4all-skill-log` — ältere Blöcke mit diesem Namen sind gültig und bleiben unangetastet, siehe `fix-log-format.md`.)

9. **Changelog als nummerierte Liste erzeugen.** Jede einzelne Änderung als eigener Listenpunkt, auf Deutsch, mit kurzer Begründung — auch wenn sie nur ein halber Satz ist.

10. **Expliziter Hinweis in der Auslieferung:** DevExpress-Designer-Laden + Testdaten-Rendering wird durch diese Checks NICHT ersetzt und muss zusätzlich manuell durch den Nutzer erfolgen.

11. **Bei einer Datei, die zwischenzeitlich im DevExpress-Designer geöffnet/gespeichert war:** alle zuvor gezielt gesetzten Layout-Eigenschaften (z. B. `KeepTogether`, Höhen/Größen) neu auflisten und mit dem erwarteten Zustand abgleichen, statt anzunehmen, dass frühere Fixes automatisch erhalten geblieben sind. Ein Designer-Speichervorgang serialisiert die Datei komplett neu (erkennbar u. a. an durchgängig neu vergebenen `Ref`-IDs) und kann dabei per XML gesetzte Einzel-Eigenschaften stillschweigend verwerfen.

12. **Keine rohen `\r`/`\n`-Zeichen im re-escapten `ScriptsSource`-Attributwert (PFLICHT, seit 31.08.).** Nach dem Schreiben den rohen, noch escapten Attributwert (vor `html.unescape`) darauf prüfen, dass er keine literalen `\r`- oder `\n`-Zeichen mehr enthält — nur noch `&#xD;&#xA;`-Entities. **Bekannte Falle:** Fehlt vor dem finalen `\n` → `&#xD;&#xA;`-Kodierungsschritt die Normalisierung der Zeilenenden auf reines `\n` (siehe `repx-format-basics.md`, Bearbeitungs-Pipeline Schritt 4.3), bleibt bei jedem Zeilenumbruch im GESAMTEN Skript ein rohes `\r` unmittelbar vor dem neu kodierten `&#xD;&#xA;` stehen — sichtbar als Leerzeile nach jeder einzelnen Zeile beim Öffnen im Designer/Editor, aber unsichtbar in Punkt 1 (XML bleibt wohlgeformt) und in einem reinen Struktur-Diff. Betrifft potenziell jeden Korrektur-Skill, der Skript-Text zurückschreibt, nicht nur `fix-folgeseiten-uebertrag-problem` (siehe dessen `known-issues.md` Eintrag 13 für den konkreten Vorfall).

## Praktischer Hinweis

Diese Checks lassen sich alle als kurze Python-Snippets direkt gegen die extrahierte `.cs`-Datei bzw. die rohe `.repx`-XML laufen lassen — schneller und zuverlässiger, als jede Änderung einzeln von Hand nachzuverfolgen. Es lohnt sich, ein kleines Validierungsskript zu bauen (Parsing, Ref-Zählung, Methodenabgleich, Klammernzählung, Summary-/Log-Block-Zählung) und es nach *jeder* Bearbeitungsrunde erneut laufen zu lassen, nicht nur einmal ganz am Ende.

---

## Ergänzungen vom 04.09.2026 (Sitzung `dxAio_template`)

Diese vier Punkte gelten generisch für **jede** `.repx`-Bearbeitung, unabhängig vom Fach-Skill. Alle vier sind erst dadurch aufgefallen, dass der Kunde sie im Designer bzw. Testdruck gefunden hat — nicht durch die bis dahin bestehende Checkliste.

13. **`ItemN`-Sammlungen lückenlos halten.** DevExpress löst die Kinder einer Sammlung über die Element-Namen `Item1..ItemN` in lückenloser Folge auf. Wird ein Element entfernt oder eingefügt, muss die betroffene Sammlung neu durchnummeriert werden (Öffnungs- **und** Schließ-Tag). Alles hinter einer Lücke wird stillschweigend ignoriert — die Datei bleibt dabei wohlgeformtes XML und alle übrigen Checks grün. `Ref="N"`-Nummern dürfen dagegen Lücken haben.
14. **Phasentrennung BeforePrint / PrintOnPage respektieren.** Die PrintOnPage-Phase läuft für das gesamte Dokument erst, nachdem **alle** BeforePrint-Ereignisse durch sind. Eine Variable, die in einem PrintOnPage-Handler gesetzt wird, ist in **jedem** BeforePrint immer noch auf ihrem Initialwert — auch auf Control-Ebene, nicht nur auf Band-Ebene. In BeforePrint sind nur Größen verlässlich, die selbst ausschließlich aus BeforePrint-Ereignissen gespeist werden.
15. **Layout-relevante Eigenschaften nur in BeforePrint setzen.** `HeightF`/`SizeF`/`CanGrow` in einem PrintOnPage-Handler zu setzen ist wirkungslos, weil die Layoutberechnung dort bereits abgeschlossen ist. Wer Design-Höhen absenkt, muss die echten Höhen in BeforePrint wiederherstellen — an der Tabelle **und** an den darin verschachtelten Controls.
16b. **Serialisierungs-Reihenfolgen aus der Datei ableiten.** `Padding` ist `Left,Right,Top,Bottom,Dpi` (Top = Position 3). Solche Reihenfolgen nie aus einer Beschreibung übernehmen, sondern gegen vorhandene explizite Bindungen im Report selbst prüfen (`Padding.LeftF`/`Padding.RightF`) — Check `C17`.
16. **Element-gescopte Prüfungen statt Zählungen.** Ob ein bestimmtes Attribut an einem bestimmten Element gesetzt ist, wird immer über `Ref`/Name gescopet geprüft. Eine Zählung über die ganze Datei (`count(...)`, `grep -c`) beweist nichts über ein einzelnes Element — ein Zahlenunterschied zur Referenz kann von einer völlig anderen Stelle stammen.

## Ausführbarer Check-Index

Der Verbesserungs-Skill `fix-folgeseiten-uebertrag-problem` liefert diese Checkliste als lauffähiges Skript mit: `skills/fix-folgeseiten-uebertrag-problem/scripts/validate_repx.py` (Checks `C01`–`C19`, Exit-Code 1 bei FAIL). Es ist bewusst report-neutral gehalten und kann von jedem Skill dieses Plugins verwendet werden:

```bash
python3 "${CLAUDE_SKILL_DIR}/../fix-folgeseiten-uebertrag-problem/scripts/validate_repx.py" <bearbeitet.repx> --baseline <original.repx>
```

**Verbindlich für jeden Skill, der eine `.repx` verändert:** nach *jeder* Bearbeitungsrunde laufen lassen (nicht nur am Ende) und zusätzlich einmal auf einer verwendeten Referenzdatei (Selbst-Audit — eine Diagnose-Zwischenfassung als Referenz fällt dabei sofort auf). Fehlalarme werden durch Nachschärfen des Checks behoben, nicht durch Ignorieren des Befunds.
