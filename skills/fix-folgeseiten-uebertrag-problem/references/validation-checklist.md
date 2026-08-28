# Validierungs-Checkliste

Verpflichtend vor jeder Auslieferung einer bearbeiteten `.repx`. Jeder einzelne Punkt hat in der Vergangenheit tatsächlich einen Fehler gefangen, der beim bloßen Lesen des Diffs nicht aufgefallen wäre — das ist keine reine Formalität.

1. **XML-Wohlgeformtheit.** Die komplette Datei mit einem XML-Parser laden (z.B. `xml.dom.minidom.parseString`). Ein Parse-Fehler bedeutet: nicht ausliefern, Fehler beheben.

2. **Keine doppelten `Ref="N"`-IDs.** Alle `Ref="..."`-Vorkommen in der Datei per Regex sammeln und zählen (z.B. mit `collections.Counter`). Jede ID darf nur einmal vorkommen. Duplikate deuten meist auf einen fehlerhaften Copy-Paste oder Splice-Fehler hin.

3. **Jede `<Scripts On*="Name">`-Referenz löst sich auf eine definierte Methode auf.** Wichtig: getrennt pro `ScriptsSource`-Block prüfen (Hauptreport und jeder Subreport haben eigene Namensräume, siehe `repx-technical-notes.md`). Baseline vor der Bearbeitung erstellen (welche Namen fehlten schon *vorher* — typischerweise Subreport-Handler, die im falschen Namensraum gesucht werden, das sind keine echten Fehler) und nach der Bearbeitung nur auf **neu** fehlende Namen prüfen, die durch die eigene Bearbeitung entstanden sind.

4. **Klammern-Balance.** Anzahl `{` muss Anzahl `}` im bearbeiteten Skriptteil entsprechen. Einfache, aber wirksame Absicherung gegen einen abgeschnittenen oder falsch eingefügten Block.

5. **`<Summary Ref=...>`-Anzahl vor/nach vergleichen.** Diese Zahl darf sich durch die Bearbeitung **nie unbeabsichtigt ändern**. Siehe die `sumCarryoverSum`-Falle in `known-issues.md` — ein scheinbar redundantes `Summary`-Element zu entfernen hat dort bereits einmal eine Regression verursacht. Wenn sich die Zahl ändert, muss das eine bewusste, im Changelog explizit benannte Entscheidung sein, keine stille Nebenwirkung.

6. **Symmetrische Entfernung nach jeder Handler-Löschung.** Nach dem Entfernen einer Methode bestätigen: die Methode ist weder in der XML-Verdrahtung (`<Scripts On*="...">`) noch sonst irgendwo im Skript referenziert (z.B. nicht von einer anderen Methode aufgerufen). Eine Methode zu löschen, aber ihre `<Scripts>`-Referenz stehen zu lassen (oder umgekehrt), macht die Datei entweder ladeunfähig oder lässt toten Verweis-Ballast zurück.

7. **Changelog als nummerierte Liste erzeugen.** Jede einzelne Änderung als eigener Listenpunkt, auf Deutsch, mit kurzer Begründung — das Changelog ist die Grundlage, auf der work4all-Mitarbeiter (die den Report nicht selbst gebaut haben) nachvollziehen, was warum verändert wurde. Kein Punkt ohne Begründung, auch wenn sie nur ein halber Satz ist.

8. **Bei einer Datei, die zwischenzeitlich im DevExpress-Designer geöffnet/gespeichert war: alle `KeepTogether`-Vorkommen (und andere zuvor gezielt gesetzte Layout-Eigenschaften) neu auflisten und mit dem erwarteten Zustand abgleichen**, statt anzunehmen, dass frühere Fixes automatisch erhalten geblieben sind. Ein Designer-Speichervorgang serialisiert die Datei komplett neu (erkennbar u. a. an durchgängig neu vergebenen `Ref`-IDs) und kann dabei per XML gesetzte Einzel-Eigenschaften stillschweigend verwerfen (siehe `known-issues.md`, Eintrag 3). Bei diesem Szenario nicht nur die eigene neue Änderung validieren, sondern auch die aus früheren Runden.

## Praktischer Hinweis

Diese Checks lassen sich alle als kurze Python-Snippets direkt gegen die extrahierte `.cs`-Datei bzw. die rohe `.repx`-XML laufen lassen — schneller und zuverlässiger, als jede Änderung einzeln von Hand nachzuverfolgen. Es lohnt sich, ein kleines Validierungsskript zu bauen (Parsing, Ref-Zählung, Methodenabgleich, Klammernzählung, Summary-Zählung) und es nach *jeder* Bearbeitungsrunde erneut laufen zu lassen, nicht nur einmal ganz am Ende.
