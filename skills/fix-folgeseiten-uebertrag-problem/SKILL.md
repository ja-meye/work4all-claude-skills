---
name: fix-folgeseiten-uebertrag-problem
description: Diagnostiziert und repariert die Übertrag-/Folgeseiten-Unterdrückungslogik in DevExpress-XtraReports-.repx-Dateien vom work4all-Aio-Report-Typ (und strukturell ähnlichen Varianten). Unbedingt verwenden, wenn eine .repx-Datei hochgeladen wird und der Nutzer über eine fehlende oder falsche "Übertrag"-Zeile, verschwindende Tabellenüberschriften auf Folgeseiten, falsche sumCarryoverSum-Werte, Seitenumbruch-Probleme bei Positionstabellen, oder allgemein über "Report-Bugs"/"Fehler beim Druck von Angeboten/Rechnungen" bei work4all-Reports spricht — auch wenn nicht explizit "Übertrag" oder "Folgeseite" genannt wird, aber Symptome wie "Betrag stimmt nicht", "Kopfzeile fehlt auf Seite 2", "Summe zu früh/zu spät" beschrieben werden. Auch nutzen, wenn der Nutzer nach einer allgemeinen Aufräumung/Bereinigung ("Skript-Hygiene") des eingebetteten C#-Skripts in einer .repx-Datei fragt (tote Kommentare, leere Event-Handler).
skill_id: DXJ0001
version: 1.1.1
---

# DevExpress .repx — Übertrag/Folgeseiten-Fix & Skript-Hygiene

## Worum es geht

work4all hat viele Varianten eines DevExpress-XtraReports-Angebots-/Rechnungsreports (`dxAio_template.repx` und strukturell gleich gebaute Ableger) im Feld, die alle dieselbe Familie von Schwächen in der Übertrag-/Folgeseiten-Logik geerbt haben. Diese Skill kapselt die Diagnose- und Fix-Methodik, die für den ersten reparierten Report erarbeitet wurde, damit sie sich wiederholt auf weitere Report-Varianten anwenden lässt — systematisch, aber nie blind automatisch. Jede .repx ist an einer anderen Stelle leicht anders gewachsen; die Aufgabe ist Muster erkennen und einordnen, nicht stur ein Diff von damals wiederholen.

Lies **`references/repx-technical-notes.md`** zuerst, bevor du irgendetwas am Skript änderst — dort steht die Dateiformat-Mechanik (Encoding, Escaping, Bandmodell) und die eine wirklich gefährliche Falle (`sumCarryoverSum` + `Summary`-Element), die schon einmal zu einer Regression geführt hat. Ohne dieses Hintergrundwissen sehen mehrere der Fixes unten harmloser aus, als sie sind.

## Was diese Skill konkret optimiert

Kurzfassung der Fixes, die aus dem ersten vollständig durchgefixten Report (`dxAio_template.repx`) hervorgegangen sind — Details und Erkennungsmuster jeweils in `references/fix-catalog.md`:

1. **Sabotierte Folgeseiten-Logik entfernen** — ein grober, seitenzähler-basierter `BeforePrint`-Handler, der ein Subband unabhängig vom tatsächlichen Seiteninhalt abschaltete und dadurch die eigentlich vorhandene, präzisere `PrintOnPage`-Logik nie zum Zug kommen ließ (Muster a).
2. **`KeepTogether` robust gegen Zeilen-Splitting** — verhindert, dass eine Position mit Preis über einen Seitenumbruch aufgesplittet wird, was `sumCarryoverSum` sonst verfälscht (zu früh nicht-null). **[ÜBERHOLT seit 28.08., siehe Punkt 8 unten]** Ursprünglich wurde dafür bewusst auf **zwei Ebenen** `KeepTogether="true"` gesetzt (Zeile *und* übergeordnete Band-Ebene). Ein kundenseitiger Testlauf hat gezeigt, dass das inakzeptablen Weißraum verursachen kann; der Kunde hat diesen Ansatz durch die höhenbasierte Lösung in Muster (g) ersetzt. Muster (b) bleibt im Katalog dokumentiert (als Risiko-Hintergrund, siehe `known-issues.md` Eintrag 3), ist aber nicht mehr die empfohlene Standardlösung.
3. **Gesamtsummen-Rückfallbedingung** — unterscheidet zuverlässig zwischen „Beleg hat gar keine Position mit Preis" (Übertrag bleibt unterdrückt) und „Beleg hat einen Betrag, aber auf dieser Seite ist noch keine Position mit Preis gedruckt worden" (Übertrag wird trotzdem angezeigt, ggf. als 0,00) (Muster c).
4. **Detailbereich-Gate** — verhindert zusätzlich, dass Übertrag/Folgeseiten-Titel bereits angezeigt werden, wenn der Detailbereich (die eigentliche Positionstabelle) durch vorgelagerten Inhalt (langer Kopftext, optionale Titelübersicht) auf eine Folgeseite verschoben wurde, dort aber selbst noch gar nicht begonnen hat (Muster f).
5. **Batch-Sicherheits-Reset** — setzt sicherheitsrelevante Sichtbarkeits-/Zustandsvariablen beim Start jedes neuen Belegs zurück, damit bei Sammeldruck mehrerer Belege in einem Lauf kein Zustand vom vorherigen Beleg durchsickert (Muster d).
6. **Skript-Hygiene (optional)** — entfernt leere/wirkungslose Print-Event-Handler und rein auskommentierten toten Code, symmetrisch inkl. der zugehörigen XML-Verdrahtung, ohne wertvolle Begründungs-Kommentare zu verlieren (Muster e, nur auf ausdrücklichen Wunsch).
7. **Visuelle Fallstricke** — z.B. zu wenig Abstand zwischen Positionen/Titeln nach dem Entfernen einer Leerzeile: löst sich über `Padding`/Mindesthöhe der Tabellenzeile, nicht über das Zurückbringen der Leerzeile.
8. **Mindesthöhen statt `KeepTogether` gegen Weißraum/abgeschnittene Übertrag-Anzeige** — ersetzt den in Punkt 2 beschriebenen, überholten `KeepTogether`-Ansatz. `KeepTogether` wird auf Zeile/Band wieder auf `false` zurückgesetzt; stattdessen werden `tb_ÜbertragOben` und das umgebende Subband auf eine Mindesthöhe von 50 gebracht (bereits höhere Werte bleiben unangetastet) und eine ggf. vorhandene doppelte Kopfzeile in `xrTable1` entfernt (verbleibende Datenzeile auf Höhe 55). Wichtig: die Höhe kann zusätzlich indirekt im `<Localization>`-Block gespeichert sein, nicht nur als direktes Attribut — siehe `repx-technical-notes.md`, Abschnitt „Der `<Localization>`-Block" (Muster g, siehe auch `known-issues.md` Einträge 6 und 7).

**Referenzbeispiel (PFLICHT vor jedem inhaltlichen Fix):** Für diese Methodik existiert ein vollständig durchgefixter, vom Kunden in DevExpress getesteter und bestätigter Referenzreport (die jeweils aktuellste vom Kunden bestätigte Referenzversion) — ein Proof-of-Concept mit allen oben genannten Fixes bereits angewendet (Stand aktuellste Referenzversion: Muster (b) durch das höhenbasierte Muster (g) ersetzt, siehe Punkt 8). Diese Datei wird aus Vertraulichkeitsgründen nicht mit dieser Skill ausgeliefert und liegt nicht in diesem Repository.

Bevor irgendein inhaltlicher Fix (alles außer reiner Skript-Hygiene, Muster (e)) an einer neuen Report-Variante vorgenommen wird, MUSS der Nutzer explizit nach dieser bestätigten Referenz-`.repx` gefragt werden. Das ist **kein optionaler Diagnoseschritt mehr, sondern Pflicht** — unabhängig davon, ob die neue Variante auf den ersten Blick strukturell abweichend aussieht. Grund: ein direkter struktureller Diff (Bandnamen, Scripts-Verdrahtung, Sichtbarkeits-Bedingungen, `Summary`-Elemente, `KeepTogether`-Werte, betroffene Variablen/Felder) gegen eine bestätigt korrekte Referenz ist zuverlässiger als eine Re-Implementierung rein aus der Katalog-Beschreibung — `fix-catalog.md` und `known-issues.md` sind Prosa-Zusammenfassungen und verlieren zwangsläufig Details wie exakte Variablennamen, exakte Bedingungsformulierungen und genaue Code-Platzierung. Frag aktiv danach, auch wenn der Nutzer die Referenz nicht von sich aus erwähnt.

**Ausnahme:** Nur wenn der Nutzer explizit angibt, keine Referenzdatei zu haben oder sie nicht bereitstellen zu können/wollen, darf ohne Referenz weitergearbeitet werden — anhand der dokumentierten Muster in `references/fix-catalog.md`, `references/known-issues.md` und `references/repx-technical-notes.md`. In diesem Fall im Bericht an den Nutzer UND im finalen Changelog (Schritt 8) ausdrücklich vermerken, dass ohne Referenzvergleich gearbeitet wurde und das Ergebnis dadurch ein geringeres Vertrauensniveau hat als ein referenzverifizierter Fix.

**Liegt eine Referenzdatei vor:** Extrahiere sie genauso wie die zu reparierende Datei (siehe Schritt 1) und führe einen strukturellen Diff durch (Bandnamen, Scripts-Verdrahtung, Sichtbarkeits-Bedingungen, `Summary`-Elemente, `KeepTogether`-Werte, betroffene Variablen/Felder). Wo die neue Variante strukturell dem Referenz-Report entspricht oder sehr ähnlich ist, die dort bestätigt funktionierenden Werte/Formulierungen bevorzugt 1:1 übernehmen (angepasst an ggf. abweichende Namen), statt sie unabhängig neu zu erfinden.

## Skill-ID, Version & Fix-Log

Diese Skill trägt die ID **DXJ0001** (aktuell Version **1.1.1**). Format und vollständige Spezifikation des `work4all-log`-Blocks (inkl. `<Ergebnis>`-Feld, Idempotenz-Check, Rückwärtskompatibilität zu einem älteren `(v1)`-Block) sind zentral dokumentiert in `work4all-reporting-skills:neuen-devexpress-report-skill-anlegen`, `references/fix-log-format.md` — dort auch die vollständige Registry aller vergebenen IDs (`references/skill-id-registry.md`). Wann und wie diese Skill den Block liest und beschreibt: siehe Schritt 7 „Log-Eintrag schreiben" im Arbeitsablauf unten.

**Wichtig für Schritt 5 (Skript-Hygiene):** Der `work4all-log`-Block sieht wie ein Kommentarblock aus, ist aber KEIN toter Kommentar — er darf von der Hygiene-Routine niemals entfernt werden, auch nicht als vermeintlich "wirkungsloser" Kommentar. Vor jeder Hygiene-Passage explizit prüfen, dass der Block (erkennbar an der festen Marker-Zeile `=== work4all-log`) unangetastet bleibt.

## Bekannte Grenzen

Diese Skill wurde bisher ausschließlich an Reports erprobt, die strukturell nah an der bestätigten Referenzdatei liegen (siehe „Referenzbeispiel" oben) — also an vergleichsweise jungen, wenig abweichenden Varianten von `dxAio_template.repx`. Es gibt im Feld auch deutlich ältere Reports mit stärker abweichender Struktur, die diese Skill noch nicht kennt und bei denen ein Fix voraussichtlich tiefer eingreifen muss (z. B. eigene Berechnungsfelder, abweichende Bandnamen oder komplett andere Übertrag-Mechanik). Diese Fälle kommen laut Kunde nach und nach dazu. Bei einer .repx, die schon in Schritt 1 stark von den bekannten Bandnamen/Mustern abweicht: das offen ansprechen, nicht versuchen, den bestehenden Fix-Katalog gewaltsam passend zu machen — stattdessen wie eine neue Grundstruktur behandeln, vorsichtiger vorgehen als sonst, und nach Abschluss einen neuen Eintrag in `known-issues.md` sowie ggf. ein neues Muster im Fix-Katalog ergänzen, damit die nächste ähnliche Variante nicht wieder bei null anfängt.

## Warum Vorsicht wichtiger ist als Vollständigkeit

Der ursprüngliche Auftrag für diese Skill entstand aus einer echten Regression: ein scheinbar redundantes `<Summary Running="Group" />`-Element wurde entfernt, weil eine neuere Expression es angeblich ersetzt hatte — laut offizieller DevExpress-Doku hätte das funktionieren müssen. In der Praxis blieb der Übertrag-Wert danach leer. Das ist der Grund, warum diese Skill zwischen drei Sicherheitsstufen unterscheidet (siehe `references/fix-catalog.md`): **automatisch sicher**, **Vorschlag mit Rückfrage**, und **nur Verdacht — manueller Test nötig**. Behandle diese Einstufung ernst. Ein Fix, der in der Theorie richtig aussieht, kann in DevExpress' tatsächlicher Rendering-Pipeline trotzdem falsch sein, und ein produktiver Report, der beim Kunden bricht, ist teurer als eine Rückfrage.

## Arbeitsablauf

### Schritt 1 — Report entgegennehmen und Rohdaten extrahieren

Kopiere die hochgeladene `.repx` in ein Arbeitsverzeichnis (z.B. `/tmp/repx_work/`). Öffne sie mit `encoding='utf-8-sig', newline=''`, damit BOM sauber abgetrennt wird, aber die CRLF-Zeilenenden exakt erhalten bleiben (Details dazu und zur `ScriptsSource`-Extraktion in `references/repx-technical-notes.md`). Dekodiere das eingebettete C#-Skript und speichere es separat als lesbare `.cs`-Datei, damit du es normal durchsuchen und lesen kannst.

Prüfe direkt zu Beginn, ob es sich überhaupt um einen strukturell verwandten Report handelt (Bandnamen wie `Sub_POS`, `GROUP_ERP_Nummer`, `GroupFooter_Uebertrag`, Verwendung von `sumCarryoverSum`). Falls die Struktur stark abweicht oder sich die Datei nicht sauber öffnen/parsen lässt, sag das dem Nutzer offen und brich hier ab — die Muster unten generalisieren nur begrenzt auf komplett andere Reports. Ein Abbruch an dieser Stelle (vor Schritt 2) bekommt **keinen** Eintrag im `work4all-log` — es wurde noch nichts inhaltlich geprüft (siehe `references/fix-log-format.md`, Regel 7). Melde den Abbruch stattdessen klar im Chat, inkl. Grund, damit gemeinsam das weitere Vorgehen abgestimmt werden kann.

### Schritt 2 — Referenz-.repx anfordern (PFLICHT) und Diagnose gegen den Fix-Katalog

Bevor du in die eigentliche Diagnose einsteigst: frag den Nutzer aktiv nach der bestätigten Referenz-`.repx` (siehe Abschnitt „Referenzbeispiel" oben) — das ist Pflicht, kein optionaler Zwischenschritt, und gilt unabhängig davon, wie ähnlich oder unähnlich die neue Datei auf den ersten Blick wirkt. Nur wenn der Nutzer explizit sagt, dass er keine Referenz hat oder bereitstellen kann, machst du ohne sie weiter (und vermerkst das später im Bericht/Changelog, siehe Ausnahme-Regel oben). Liegt eine Referenzdatei vor, extrahiere sie wie in Schritt 1 beschrieben und halte sie für den strukturellen Diff bereit.

Lies `references/fix-catalog.md`. Gehe die dort beschriebenen Muster (a) bis (e) systematisch durch — jedes ist **musterbasiert** beschrieben (welches Verhalten/welche Codestruktur zu suchen ist), nicht an konkrete Methodennamen oder `Ref`-IDs aus dem ursprünglichen Report gebunden, weil die nächste Report-Variante andere Namen haben wird. Notiere für jeden Fund, welchem Muster er entspricht und welche Sicherheitsstufe laut Katalog gilt. Liegt eine Referenzdatei vor, führe zusätzlich den strukturellen Diff gegen sie durch (siehe „Referenzbeispiel" oben) und bevorzuge dort bestätigt funktionierende Werte/Formulierungen gegenüber einer eigenen Neu-Interpretation des Katalogs.

Prüfe außerdem gegen `references/known-issues.md` — dort sammeln sich Fallen, die in früheren Läufen entdeckt wurden (aktuell v.a. die `sumCarryoverSum`/`Summary`-Falle). Diese Datei ist ein lebendes Dokument: wenn du in diesem Lauf etwas Neues entdeckst, das über den bisherigen Katalog hinausgeht, ergänze sie am Ende (Schritt 9).

**Es ist ein vollständig gültiges Ergebnis dieses Schritts, dass kein einziges Muster zutrifft.** Wenn die Diagnose sauber durchlaufen wurde (auch nach einem strukturellen Diff gegen eine vorliegende Referenzdatei) und keiner der Katalog-Einträge greift, wird nichts konstruiert, um trotzdem etwas zu "finden" — das Ergebnis ist dann `keine Änderung nötig` (siehe Schritt 7) und genauso wertvoll wie ein gefundener Fix, weil es dem Nutzer bestätigt, dass die Datei geprüft wurde.

### Schritt 3 — Befund an den Nutzer melden, bevor automatisch etwas verändert wird

Fasse zusammen, was gefunden wurde, gruppiert nach Sicherheitsstufe. Auch bei eindeutigen Fällen: kurz benennen, was verändert wird und warum, bevor du loslegst — der Nutzer soll nachvollziehen können, was passiert, auch wenn er nicht bei jedem Einzelpunkt gefragt wird. Wurde ohne Referenzdatei gearbeitet (siehe Ausnahme-Regel im Abschnitt „Referenzbeispiel"), weise an dieser Stelle explizit auf das dadurch geringere Vertrauensniveau hin.

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

Konnte ein einzelner Validierungs-Check aus irgendeinem Grund nicht durchgeführt werden (z.B. technische Einschränkung der Umgebung), wird das **nicht stillschweigend übersprungen** — als offener Punkt im Statusbericht in Schritt 8 aufführen.

### Schritt 7 — Log-Eintrag schreiben

Schreibe **unabhängig vom Ergebnis** eine Zeile in den `work4all-log`-Block im eingebetteten Skript, sobald Schritt 2 (Diagnose) tatsächlich abgeschlossen wurde — Format und Ergebnis-Werte: `references/fix-log-format.md`.

- Vor dem Schreiben: Idempotenz-Check aus `fix-log-format.md` Regel 2 durchführen (nur relevant, wenn im Block bereits eine `geändert`-Zeile dieser Skill-ID mit ≥ aktueller Version steht).
- Wurden in Schritt 4 Fixes tatsächlich angewendet: Ergebnis `geändert`.
- Wurde die Diagnose vollständig durchlaufen, aber kein Muster traf zu (siehe Hinweis in Schritt 2): Ergebnis `keine Änderung nötig`. Das gilt auch, wenn ausschließlich Skript-Hygiene lief oder ausschließlich "Nur Verdacht"-Funde dokumentiert wurden, ohne dass eine Datei-Anpassung vorgenommen wurde.
- Existiert noch kein Block (erstmaliger Lauf dieser Skill-Familie auf dieser Datei), lege Kopf- und Fußzeile im `(v2)`-Format neu an.
- Falls die Datei bereits einen `(v1)`-Block hat: neue Zeile im v2-Format anhängen und Kopfzeile auf `(v2)` anheben (siehe `fix-log-format.md`).

### Schritt 8 — Auslieferung

Liefere die reparierte `.repx` zusammen mit einem Changelog aus. Das Changelog ist für work4all-Mitarbeiter gedacht, die den Report nicht selbst gebaut haben — schreibe es auf Deutsch, als nummerierte Liste, mit einem kurzen Satz pro Änderung: was, wo, warum. Kein Fachjargon ohne Erklärung; die Übertrag-Logik in ein bis zwei Sätzen einordnen, falls die Änderung nicht selbsterklärend ist. Auch wenn das Ergebnis `keine Änderung nötig` war, liefere einen kurzen Abschlussbericht statt gar nichts — das bestätigt dem Nutzer, dass geprüft wurde.

**Dateibenennung — PFLICHT:** Jede ausgelieferte `.repx`-Datei (die reparierte Datei ebenso wie jede neu erstellte Referenz-`.repx`) bekommt vor der Auslieferung einen Zeit-/Datumsstempel an den Dateinamen angehängt, Format `_JJJJ-MM-TT_hh-mm` (aktuelle Systemzeit, z.B. per `date '+%Y-%m-%d_%H-%M'` ermittelt), unmittelbar vor der Dateiendung. Grund: bei mehreren Läufen mit ähnlichen Dateinamen (z.B. mehrere Referenzversionen im zeitlichen Verlauf) lässt sich sonst nicht mehr zweifelsfrei nachvollziehen, welche Datei aus welchem Lauf stammt — das ist in der Praxis bereits zu Verwechslungen beim Vergleich von Läufen an unterschiedlichen Tagen gekommen. Dies ist kein optionaler Stil-Punkt, sondern fester Teil der Auslieferung.

Halte den Basisnamen dabei bewusst KURZ (kurzer Report-Name + ggf. Versionskürzel, keine ausführliche Beschreibung des Inhalts im Dateinamen) — ein langer Basisname lässt den Zeitstempel am Ende in der UI/Downloadliste abgeschnitten wirken oder gar nicht mehr sichtbar sein, was den eigentlichen Zweck des Stempels zunichtemacht. Ausführliche Beschreibungen gehören ins Changelog, nicht in den Dateinamen. Beispiel: `dxAio_template_REFERENZ_v2_2026-08-28_10-29.repx` (nicht `dxAio_template_REFERENZ_v2_KeepTogetherFalse_Mindesthoehe_2026-08-28_10-29.repx`).

Schließe **immer** mit einem kurzen Statusblock ab, welche Teile dieses Skills in diesem Lauf **nicht** ausgeführt wurden und warum (z.B. "Skript-Hygiene nicht durchgeführt — nicht angefragt", "Validierungs-Check X übersprungen, weil kein Hinweis auf einen zwischenzeitlichen Designer-Speichervorgang vorlag", "Referenzdatei nicht verfügbar — Diagnose ausschließlich anhand Fix-Katalog/known-issues.md"). Gab es keine Auslassungen, reicht ein kurzer positiver Vermerk. Ziel: der Nutzer soll aus dem Bericht allein erkennen können, worüber noch gesprochen werden müsste.

### Schritt 9 — `known-issues.md` pflegen

Wenn in diesem Lauf ein neues Muster, eine neue Falle oder eine überraschende DevExpress-Eigenheit auffällt (etwas, das nicht bereits im Fix-Katalog oder in known-issues.md steht), ergänze `references/known-issues.md` um einen neuen Eintrag nach demselben Format wie die bestehenden. So wird die Skill mit jedem bearbeiteten Report robuster, statt bei jedem Lauf wieder bei null anzufangen.

## Referenzdateien im Überblick

- `references/repx-technical-notes.md` — Dateiformat, Encoding/Escaping-Pipeline, DevExpress-Bandmodell, Event-Timing (BeforePrint vs. PrintOnPage), XML/Skript-Paritätsregel. Lies das zuerst.
- `references/fix-catalog.md` — die bekannten Problem-Muster, ihre Ursache, der empfohlene Fix, und wie sicher es ist, ihn automatisch anzuwenden.
- `references/validation-checklist.md` — die Checks, die vor jeder Auslieferung durchlaufen werden müssen.
- `references/known-issues.md` — lebendes Dokument bekannter Fallen und Überraschungen, wächst mit jedem Lauf.
- `references/fix-log-format.md` (in `neuen-devexpress-report-skill-anlegen`) — Spezifikation des `work4all-log`-Blocks inkl. Ergebnis-Werten (`geändert` / `keine Änderung nötig` / `abgebrochen: ...`) und der vollständigen Skill-ID-Registry, maßgeblich für Schritt 7.

## Versionierung dieses Skills

- v1.0.0 — Erstfassung plus nachträgliche Erweiterungen vor Einführung dieser Versionshistorie (Registry-Eintrag `DXJ0001`, 2026-08-28): Diagnose-/Fix-Methodik mit drei Sicherheitsstufen (Muster a-f), optionale Skript-Hygiene, Validierungs-Checkliste, `known-issues.md` als lebendes Dokument; danach ergänzt um Muster (g) „Mindesthöhen statt KeepTogether", die verpflichtende Referenz-.repx-Anforderung vor jedem inhaltlichen Fix, und die Sektion „Bekannte Grenzen".
- v1.1.0 — Neuer Schritt 7 „Log-Eintrag schreiben" ergänzt: schreibt jetzt bei jedem abgeschlossenen Lauf einen Eintrag im `work4all-skill-log`-Block, auch ohne Änderung (`keine Änderung nötig`), gemäß `fix-log-format.md` v2. Schritt 8 „Auslieferung" um einen verpflichtenden Statusbericht zu nicht ausgeführten Teilen ergänzt. Schritt 1 und 2 um explizite Abbruch- bzw. Notwendigkeits-Klarstellung ergänzt. Abschnitt „Skill-ID, Version & Fix-Log" auf das neue `(v2)`-Log-Format samt `<Ergebnis>`-Feld aktualisiert und auf Schritt 7 verweisend gekürzt (statt Detail-Duplikat).
- v1.1.1 — Dokumentationskorrektur: Log-Block in `work4all-log` umbenannt (vorher `work4all-skill-log`), Versionskennzeichnung `(v2)` in der Kopfzeile bleibt erhalten. Zeitstempel-Vorgabe in `fix-log-format.md` korrigiert: kein UTC-Offset (`+02:00`) mehr im Zeitstempel-Feld — nur noch die lokale Wanduhrzeit Europe/Berlin ohne Offset-Suffix. Alle Verweise auf den Blocknamen in dieser Datei entsprechend angepasst.
