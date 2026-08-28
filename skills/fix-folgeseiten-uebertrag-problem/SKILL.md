---
name: fix-folgeseiten-uebertrag-problem
description: Diagnostiziert und repariert die Übertrag-/Folgeseiten-Unterdrückungslogik in DevExpress-XtraReports-.repx-Dateien vom work4all-Aio-Report-Typ (und strukturell ähnlichen Varianten). Unbedingt verwenden, wenn eine .repx-Datei hochgeladen wird und der Nutzer über eine fehlende oder falsche "Übertrag"-Zeile, verschwindende Tabellenüberschriften auf Folgeseiten, falsche sumCarryoverSum-Werte, Seitenumbruch-Probleme bei Positionstabellen, oder allgemein über "Report-Bugs"/"Fehler beim Druck von Angeboten/Rechnungen" bei work4all-Reports spricht — auch wenn nicht explizit "Übertrag" oder "Folgeseite" genannt wird, aber Symptome wie "Betrag stimmt nicht", "Kopfzeile fehlt auf Seite 2", "Summe zu früh/zu spät" beschrieben werden. Auch nutzen, wenn der Nutzer nach einer allgemeinen Aufräumung/Bereinigung ("Skript-Hygiene") des eingebetteten C#-Skripts in einer .repx-Datei fragt (tote Kommentare, leere Event-Handler).
---

# DevExpress .repx — Übertrag/Folgeseiten-Fix & Skript-Hygiene

## Worum es geht

work4all hat viele Varianten eines DevExpress-XtraReports-Angebots-/Rechnungsreports (`dxAio_template.repx` und strukturell gleich gebaute Ableger) im Feld, die alle dieselbe Familie von Schwächen in der Übertrag-/Folgeseiten-Logik geerbt haben. Diese Skill kapselt die Diagnose- und Fix-Methodik, die für den ersten reparierten Report erarbeitet wurde, damit sie sich wiederholt auf weitere Report-Varianten anwenden lässt — systematisch, aber nie blind automatisch. Jede .repx ist an einer anderen Stelle leicht anders gewachsen; die Aufgabe ist Muster erkennen und einordnen, nicht stur ein Diff von damals wiederholen.

Lies **`references/repx-technical-notes.md`** zuerst, bevor du irgendetwas am Skript änderst — dort steht die Dateiformat-Mechanik (Encoding, Escaping, Bandmodell) und die eine wirklich gefährliche Falle (`sumCarryoverSum` + `Summary`-Element), die schon einmal zu einer Regression geführt hat. Ohne dieses Hintergrundwissen sehen mehrere der Fixes unten harmloser aus, als sie sind.

## Was diese Skill konkret optimiert

Kurzfassung der Fixes, die aus dem ersten vollständig durchgefixten Report (`dxAio_template.repx`) hervorgegangen sind — Details und Erkennungsmuster jeweils in `references/fix-catalog.md`:

1. **Sabotierte Folgeseiten-Logik entfernen** — ein grober, seitenzähler-basierter `BeforePrint`-Handler, der ein Subband unabhängig vom tatsächlichen Seiteninhalt abschaltete und dadurch die eigentlich vorhandene, präzisere `PrintOnPage`-Logik nie zum Zug kommen ließ (Muster a).
2. **`KeepTogether` robust gegen Zeilen-Splitting** — verhindert, dass eine Position mit Preis über einen Seitenumbruch aufgesplittet wird, was `sumCarryoverSum` sonst verfälscht (zu früh nicht-null). Wird bewusst auf **zwei Ebenen** gesetzt (Zeile *und* übergeordnete Band-Ebene), weil ein Visual-Studio-Designer-Speichervorgang die Zeilen-Eigenschaft nachweislich wiederholt stillschweigend verwerfen kann — die Band-Ebene fängt das auf (Muster b, siehe auch `known-issues.md` Eintrag 3).
3. **Gesamtsummen-Rückfallbedingung** — unterscheidet zuverlässig zwischen „Beleg hat gar keine Position mit Preis" (Übertrag bleibt unterdrückt) und „Beleg hat einen Betrag, aber auf dieser Seite ist noch keine Position mit Preis gedruckt worden" (Übertrag wird trotzdem angezeigt, ggf. als 0,00) (Muster c).
4. **Detailbereich-Gate** — verhindert zusätzlich, dass Übertrag/Folgeseiten-Titel bereits angezeigt werden, wenn der Detailbereich (die eigentliche Positionstabelle) durch vorgelagerten Inhalt (langer Kopftext, optionale Titelübersicht) auf eine Folgeseite verschoben wurde, dort aber selbst noch gar nicht begonnen hat (Muster f).
5. **Batch-Sicherheits-Reset** — setzt sicherheitsrelevante Sichtbarkeits-/Zustandsvariablen beim Start jedes neuen Belegs zurück, damit bei Sammeldruck mehrerer Belege in einem Lauf kein Zustand vom vorherigen Beleg durchsickert (Muster d).
6. **Skript-Hygiene (optional)** — entfernt leere/wirkungslose Print-Event-Handler und rein auskommentierten toten Code, symmetrisch inkl. der zugehörigen XML-Verdrahtung, ohne wertvolle Begründungs-Kommentare zu verlieren (Muster e, nur auf ausdrücklichen Wunsch).
7. **Visuelle Fallstricke** — z.B. zu wenig Abstand zwischen Positionen/Titeln nach dem Entfernen einer Leerzeile: löst sich über `Padding`/Mindesthöhe der Tabellenzeile, nicht über das Zurückbringen der Leerzeile.

**Referenzbeispiel:** Für diese Methodik existiert ein vollständig durchgefixter, vom Kunden in DevExpress getesteter und bestätigter Referenzreport (`dxAio_template_REFERENZ_KORRIGIERT.repx`) — ein Proof-of-Concept mit allen oben genannten Fixes bereits angewendet (inkl. beider `KeepTogether`-Ebenen). Diese Datei wird aus Vertraulichkeitsgründen nicht mit dieser Skill ausgeliefert und liegt nicht in diesem Repository. Wenn für die Diagnose ein struktureller Vergleich (Bandnamen, Scripts-Verdrahtung, Sichtbarkeits-Handler) gegen diese Referenz sinnvoll ist, bitte den Nutzer, die Referenz-`.repx` zusätzlich im Chat hochzuladen. Ohne Referenzdatei anhand der dokumentierten Muster in `references/fix-catalog.md`, `references/known-issues.md` und `references/repx-technical-notes.md` arbeiten.

## Warum Vorsicht wichtiger ist als Vollständigkeit

Der ursprüngliche Auftrag für diese Skill entstand aus einer echten Regression: ein scheinbar redundantes `<Summary Running="Group" />`-Element wurde entfernt, weil eine neuere Expression es angeblich ersetzt hatte — laut offizieller DevExpress-Doku hätte das funktionieren müssen. In der Praxis blieb der Übertrag-Wert danach leer. Das ist der Grund, warum diese Skill zwischen drei Sicherheitsstufen unterscheidet (siehe `references/fix-catalog.md`): **automatisch sicher**, **Vorschlag mit Rückfrage**, und **nur Verdacht — manueller Test nötig**. Behandle diese Einstufung ernst. Ein Fix, der in der Theorie richtig aussieht, kann in DevExpress' tatsächlicher Rendering-Pipeline trotzdem falsch sein, und ein produktiver Report, der beim Kunden bricht, ist teurer als eine Rückfrage.

## Arbeitsablauf

### Schritt 1 — Report entgegennehmen und Rohdaten extrahieren

Kopiere die hochgeladene `.repx` in ein Arbeitsverzeichnis (z.B. `/tmp/repx_work/`). Öffne sie mit `encoding='utf-8-sig', newline=''`, damit BOM sauber abgetrennt wird, aber die CRLF-Zeilenenden exakt erhalten bleiben (Details dazu und zur `ScriptsSource`-Extraktion in `references/repx-technical-notes.md`). Dekodiere das eingebettete C#-Skript und speichere es separat als lesbare `.cs`-Datei, damit du es normal durchsuchen und lesen kannst.

Prüfe direkt zu Beginn, ob es sich überhaupt um einen strukturell verwandten Report handelt (Bandnamen wie `Sub_POS`, `GROUP_ERP_Nummer`, `GroupFooter_Uebertrag`, Verwendung von `sumCarryoverSum`). Falls die Struktur stark abweicht, sag das dem Nutzer offen — die Muster unten generalisieren nur begrenzt auf komplett andere Reports.

### Schritt 2 — Diagnose gegen den Fix-Katalog

Lies `references/fix-catalog.md`. Gehe die dort beschriebenen Muster (a) bis (e) systematisch durch — jedes ist **musterbasiert** beschrieben (welches Verhalten/welche Codestruktur zu suchen ist), nicht an konkrete Methodennamen oder `Ref`-IDs aus dem ursprünglichen Report gebunden, weil die nächste Report-Variante andere Namen haben wird. Notiere für jeden Fund, welchem Muster er entspricht und welche Sicherheitsstufe laut Katalog gilt.

Prüfe außerdem gegen `references/known-issues.md` — dort sammeln sich Fallen, die in früheren Läufen entdeckt wurden (aktuell v.a. die `sumCarryoverSum`/`Summary`-Falle). Diese Datei ist ein lebendes Dokument: wenn du in diesem Lauf etwas Neues entdeckst, das über den bisherigen Katalog hinausgeht, ergänze sie am Ende (Schritt 8).

### Schritt 3 — Befund an den Nutzer melden, bevor automatisch etwas verändert wird

Fasse zusammen, was gefunden wurde, gruppiert nach Sicherheitsstufe. Auch bei eindeutigen Fällen: kurz benennen, was verändert wird und warum, bevor du loslegst — der Nutzer soll nachvollziehen können, was passiert, auch wenn er nicht bei jedem Einzelpunkt gefragt wird.

### Schritt 4 — Fixes anwenden

- **Automatisch sicher**: direkt umsetzen, ohne extra nachzufragen.
- **Vorschlag mit Rückfrage**: dem Nutzer den konkreten Fix vorschlagen (mit möglichen Nebenwirkungen, z.B. Layout-Whitespace bei `KeepTogether`), und erst nach Zustimmung umsetzen.
- **Nur Verdacht**: NICHT automatisch anfassen. Dokumentieren, im Bericht an den Nutzer erwähnen, empfehlen, es im DevExpress Designer manuell zu testen.

Halte dich bei jeder Skript-Änderung an die Bearbeitungs-Pipeline aus `references/repx-technical-notes.md` (insbesondere die exakte Reihenfolge beim Re-Escaping und die eindeutigen Grenzmarkierungen beim Zurücksplicen) — ein falsch reihenfolgtes Escaping oder ein falscher Splice-Punkt erzeugt eine Datei, die zwar wohlgeformtes XML sein kann, aber in DevExpress nicht mehr lädt oder falsch layoutet.

### Schritt 5 — Optionale Skript-Hygiene

Nur durchführen, wenn der Nutzer das für diesen Lauf ausdrücklich wünscht (entweder direkt gefragt, oder weil er es explizit zusammen mit dem eigentlichen Fix beauftragt hat) — es ist reine Kosmetik ohne funktionale Wirkung und verdient eine eigene bewusste Entscheidung, kein automatischer Nebeneffekt jedes Laufs.

Wenn gewünscht: entferne leere/wirkungslose Print-Event-Handler und rein auskommentierte tote Codepassagen nach den Regeln in Muster (e) von `references/fix-catalog.md`. Kurzfassung der wichtigsten Regel dabei: bei Geschwister-Events am selben Element (z.B. `OnBeforePrint` mit echter Logik neben leerem `OnAfterPrint`) nur die leere Verdrahtung entfernen, die mit Logik behalten — und Begründungs-Kommentare, die eine Architekturentscheidung dokumentieren, nicht ersatzlos löschen, sondern knapp erhalten oder zum nächstgelegenen aktiven Handler verschieben.

### Schritt 6 — Validierung

Arbeite `references/validation-checklist.md` vollständig ab, bevor irgendetwas ausgeliefert wird. Das ist nicht optional — mehrere der Fehler, die in früheren Läufen passiert sind (verwaiste XML-Verdrahtung, versehentlich entfernte Summary-Elemente), wurden ausschließlich durch diese Checks gefangen, nicht durch bloßes Lesen des Diffs.

### Schritt 7 — Auslieferung

Liefere die reparierte `.repx` zusammen mit einem Changelog aus. Das Changelog ist für work4all-Mitarbeiter gedacht, die den Report nicht selbst gebaut haben — schreibe es auf Deutsch, als nummerierte Liste, mit einem kurzen Satz pro Änderung: was, wo, warum. Kein Fachjargon ohne Erklärung; die Übertrag-Logik in ein bis zwei Sätzen einordnen, falls die Änderung nicht selbsterklärend ist.

### Schritt 8 — `known-issues.md` pflegen

Wenn in diesem Lauf ein neues Muster, eine neue Falle oder eine überraschende DevExpress-Eigenheit auffällt (etwas, das nicht bereits im Fix-Katalog oder in known-issues.md steht), ergänze `references/known-issues.md` um einen neuen Eintrag nach demselben Format wie die bestehenden. So wird die Skill mit jedem bearbeiteten Report robuster, statt bei jedem Lauf wieder bei null anzufangen.

## Referenzdateien im Überblick

- `references/repx-technical-notes.md` — Dateiformat, Encoding/Escaping-Pipeline, DevExpress-Bandmodell, Event-Timing (BeforePrint vs. PrintOnPage), XML/Skript-Paritätsregel. Lies das zuerst.
- `references/fix-catalog.md` — die bekannten Problem-Muster, ihre Ursache, der empfohlene Fix, und wie sicher es ist, ihn automatisch anzuwenden.
- `references/validation-checklist.md` — die Checks, die vor jeder Auslieferung durchlaufen werden müssen.
- `references/known-issues.md` — lebendes Dokument bekannter Fallen und Überraschungen, wächst mit jedem Lauf.
