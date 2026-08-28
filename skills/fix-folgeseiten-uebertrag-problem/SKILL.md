---
name: fix-folgeseiten-uebertrag-problem
description: Diagnostiziert und repariert die Übertrag-/Folgeseiten-Unterdrückungslogik in DevExpress-XtraReports-.repx-Dateien vom work4all-Aio-Report-Typ (und strukturell ähnlichen Varianten). Unbedingt verwenden, wenn eine .repx-Datei hochgeladen wird und der Nutzer über eine fehlende oder falsche "Übertrag"-Zeile, verschwindende Tabellenüberschriften auf Folgeseiten, falsche sumCarryoverSum-Werte, Seitenumbruch-Probleme bei Positionstabellen, oder allgemein über "Report-Bugs"/"Fehler beim Druck von Angeboten/Rechnungen" bei work4all-Reports spricht — auch wenn nicht explizit "Übertrag" oder "Folgeseite" genannt wird, aber Symptome wie "Betrag stimmt nicht", "Kopfzeile fehlt auf Seite 2", "Summe zu früh/zu spät" beschrieben werden. Auch nutzen, wenn der Nutzer nach einer allgemeinen Aufräumung/Bereinigung ("Skript-Hygiene") des eingebetteten C#-Skripts in einer .repx-Datei fragt (tote Kommentare, leere Event-Handler).
---

# DevExpress .repx — Übertrag/Folgeseiten-Fix & Skript-Hygiene

## Worum es geht

work4all hat viele Varianten eines DevExpress-XtraReports-Angebots-/Rechnungsreports (`dxAio_template.repx` und strukturell gleich gebaute Ableger) im Feld, die alle dieselbe Familie von Schwächen in der Übertrag-/Folgeseiten-Logik geerbt haben. Diese Skill kapselt die Diagnose- und Fix-Methodik, die für den ersten reparierten Report erarbeitet wurde, damit sie sich wiederholt auf weitere Report-Varianten anwenden lässt — systematisch, aber nie blind automatisch. Jede .repx ist an einer anderen Stelle leicht anders gewachsen; die Aufgabe ist Muster erkennen und einordnen, nicht stur ein Diff von damals wiederholen.

Lies **`references/repx-technical-notes.md`** zuerst, bevor du irgendetwas am Skript änderst — dort steht die Dateiformat-Mechanik (Encoding, Escaping, Bandmodell) und die eine wirklich gefährliche Falle (`sumCarryoverSum` + `Summary`-Element), die schon einmal zu einer Regression geführt hat. Ohne dieses Hintergrundwissen sehen mehrere der Fixes unten harmloser aus, als sie sind.

> **Verbindliche Kundenvorgabe (seit 28.08., nach zwei Nachbesserungsrunden am selben Report):** Ein Fix-Lauf ist erst dann fertig, wenn (1) **alle** anwendbaren Muster aus `fix-catalog.md` geprüft wurden — nicht nur die, die im C#-Skript-Diff auffallen, sondern ausdrücklich auch die reinen XML-/Layout-Eigenschaften (`KeepTogether` auf allen Ebenen, Höhen inkl. `<Localization>`-Block, doppelte Tabellenzeilen), (2) die Skript-Hygiene (Muster e) durchgeführt wurde — das ist **kein optionaler Schritt mehr**, sondern fester Bestandteil jedes Laufs, und (3) die komplette Validierungs-Checkliste **inklusive** eines Selbst-Audits der Referenzdatei durchlaufen wurde. „Es darf nichts vergessen werden" — ein Fix, der nur einen Teil der Muster behebt, gilt als unvollständig und damit als Fehler dieser Skill, nicht als akzeptables Teilergebnis. Siehe `known-issues.md`, Eintrag 8, für den konkreten Vorfall, der zu dieser Vorgabe geführt hat.

## Was diese Skill konkret optimiert

Kurzfassung der Fixes, die aus dem ersten vollständig durchgefixten Report (`dxAio_template.repx`) hervorgegangen sind — Details und Erkennungsmuster jeweils in `references/fix-catalog.md`:

1. **Sabotierte Folgeseiten-Logik entfernen** — ein grober, seitenzähler-basierter `BeforePrint`-Handler, der ein Subband unabhängig vom tatsächlichen Seiteninhalt abschaltete und dadurch die eigentlich vorhandene, präzisere `PrintOnPage`-Logik nie zum Zug kommen ließ (Muster a).
2. **`KeepTogether` robust gegen Zeilen-Splitting** — verhindert, dass eine Position mit Preis über einen Seitenumbruch aufgesplittet wird, was `sumCarryoverSum` sonst verfälscht (zu früh nicht-null). **[ÜBERHOLT seit 28.08., siehe Punkt 8 unten]** Ursprünglich wurde dafür bewusst auf **zwei Ebenen** `KeepTogether="true"` gesetzt (Zeile *und* übergeordnete Band-Ebene). Ein kundenseitiger Testlauf hat gezeigt, dass das inakzeptablen Weißraum verursachen kann; der Kunde hat diesen Ansatz durch die höhenbasierte Lösung in Muster (g) ersetzt. Muster (b) bleibt im Katalog dokumentiert (als Risiko-Hintergrund, siehe `known-issues.md` Eintrag 3), ist aber nicht mehr die empfohlene Standardlösung.
3. **Gesamtsummen-Rückfallbedingung** — unterscheidet zuverlässig zwischen „Beleg hat gar keine Position mit Preis" (Übertrag bleibt unterdrückt) und „Beleg hat einen Betrag, aber auf dieser Seite ist noch keine Position mit Preis gedruckt worden" (Übertrag wird trotzdem angezeigt, ggf. als 0,00) (Muster c).
4. **Detailbereich-Gate** — verhindert zusätzlich, dass Übertrag/Folgeseiten-Titel bereits angezeigt werden, wenn der Detailbereich (die eigentliche Positionstabelle) durch vorgelagerten Inhalt (langer Kopftext, optionale Titelübersicht) auf eine Folgeseite verschoben wurde, dort aber selbst noch gar nicht begonnen hat (Muster f).
5. **Batch-Sicherheits-Reset** — setzt sicherheitsrelevante Sichtbarkeits-/Zustandsvariablen beim Start jedes neuen Belegs zurück, damit bei Sammeldruck mehrerer Belege in einem Lauf kein Zustand vom vorherigen Beleg durchsickert (Muster d).
6. **Skript-Hygiene (PFLICHT seit 28.08.)** — entfernt leere/wirkungslose Print-Event-Handler und rein auskommentierten toten Code, symmetrisch inkl. der zugehörigen XML-Verdrahtung, ohne wertvolle Begründungs-Kommentare zu verlieren (Muster e). War ursprünglich optional/nur auf Wunsch — ist jetzt fester Bestandteil jedes Laufs, siehe Kundenvorgabe oben und `known-issues.md` Eintrag 8.
7. **Visuelle Fallstricke** — z.B. zu wenig Abstand zwischen Positionen/Titeln nach dem Entfernen einer Leerzeile: löst sich über `Padding`/Mindesthöhe der Tabellenzeile, nicht über das Zurückbringen der Leerzeile.
8. **Mindesthöhen statt `KeepTogether` gegen Weißraum/abgeschnittene Übertrag-Anzeige** — ersetzt den in Punkt 2 beschriebenen, überholten `KeepTogether`-Ansatz. `KeepTogether` wird auf Zeile/Band wieder auf `false` zurückgesetzt; stattdessen werden `tb_ÜbertragOben` und das umgebende Subband auf eine Mindesthöhe von 50 gebracht (bereits höhere Werte bleiben unangetastet) und eine ggf. vorhandene doppelte Kopfzeile in `xrTable1` entfernt (verbleibende Datenzeile auf Höhe 55). Wichtig: die Höhe kann zusätzlich indirekt im `<Localization>`-Block gespeichert sein, nicht nur als direktes Attribut — siehe `repx-technical-notes.md`, Abschnitt „Der `<Localization>`-Block" (Muster g, siehe auch `known-issues.md` Einträge 6 und 7).

**Referenzbeispiel (PFLICHT vor jedem inhaltlichen Fix):** Für diese Methodik existiert ein vollständig durchgefixter, vom Kunden in DevExpress getesteter und bestätigter Referenzreport (die jeweils aktuellste vom Kunden bestätigte Referenzversion) — ein Proof-of-Concept mit allen oben genannten Fixes bereits angewendet (Stand aktuellste Referenzversion: Muster (b) durch das höhenbasierte Muster (g) ersetzt, siehe Punkt 8). Diese Datei wird aus Vertraulichkeitsgründen nicht mit dieser Skill ausgeliefert und liegt nicht in diesem Repository.

Bevor irgendein inhaltlicher Fix (alles außer reiner Skript-Hygiene, Muster (e)) an einer neuen Report-Variante vorgenommen wird, MUSS der Nutzer explizit nach dieser bestätigten Referenz-`.repx` gefragt werden. Das ist **kein optionaler Diagnoseschritt mehr, sondern Pflicht** — unabhängig davon, ob die neue Variante auf den ersten Blick strukturell abweichend aussieht. Grund: ein direkter struktureller Diff (Bandnamen, Scripts-Verdrahtung, Sichtbarkeits-Bedingungen, `Summary`-Elemente, `KeepTogether`-Werte, betroffene Variablen/Felder) gegen eine bestätigt korrekte Referenz ist zuverlässiger als eine Re-Implementierung rein aus der Katalog-Beschreibung — `fix-catalog.md` und `known-issues.md` sind Prosa-Zusammenfassungen und verlieren zwangsläufig Details wie exakte Variablennamen, exakte Bedingungsformulierungen und genaue Code-Platzierung. Frag aktiv danach, auch wenn der Nutzer die Referenz nicht von sich aus erwähnt.

**Ausnahme:** Nur wenn der Nutzer explizit angibt, keine Referenzdatei zu haben oder sie nicht bereitstellen zu können/wollen, darf ohne Referenz weitergearbeitet werden — anhand der dokumentierten Muster in `references/fix-catalog.md`, `references/known-issues.md` und `references/repx-technical-notes.md`. In diesem Fall im Bericht an den Nutzer UND im finalen Changelog (Schritt 7) ausdrücklich vermerken, dass ohne Referenzvergleich gearbeitet wurde und das Ergebnis dadurch ein geringeres Vertrauensniveau hat als ein referenzverifizierter Fix.

**Liegt eine Referenzdatei vor:** Extrahiere sie genauso wie die zu reparierende Datei (siehe Schritt 1) und führe einen strukturellen Diff durch (Bandnamen, Scripts-Verdrahtung, Sichtbarkeits-Bedingungen, `Summary`-Elemente, `KeepTogether`-Werte, betroffene Variablen/Felder). Wo die neue Variante strukturell dem Referenz-Report entspricht oder sehr ähnlich ist, die dort bestätigt funktionierenden Werte/Formulierungen bevorzugt 1:1 übernehmen (angepasst an ggf. abweichende Namen), statt sie unabhängig neu zu erfinden.

## Warum Vorsicht wichtiger ist als Vollständigkeit — UND warum Vollständigkeit trotzdem Pflicht ist

Der ursprüngliche Auftrag für diese Skill entstand aus einer echten Regression: ein scheinbar redundantes `<Summary Running="Group" />`-Element wurde entfernt, weil eine neuere Expression es angeblich ersetzt hatte — laut offizieller DevExpress-Doku hätte das funktionieren müssen. In der Praxis blieb der Übertrag-Wert danach leer. Das ist der Grund, warum diese Skill zwischen drei Sicherheitsstufen unterscheidet (siehe `references/fix-catalog.md`): **automatisch sicher**, **Vorschlag mit Rückfrage**, und **nur Verdacht — manueller Test nötig**. Behandle diese Einstufung ernst. Ein Fix, der in der Theorie richtig aussieht, kann in DevExpress' tatsächlicher Rendering-Pipeline trotzdem falsch sein, und ein produktiver Report, der beim Kunden bricht, ist teurer als eine Rückfrage.

Das ist aber **kein Freibrief, Muster wegzulassen**, die bereits als sicher eingestuft und/oder durch eine bestätigte Referenz belegt sind. Die beiden Ziele widersprechen sich nicht, wenn man sie sauber trennt:

- **Unsicherheit über die RICHTIGKEIT eines Fixes** (z. B. ein neues, im Katalog noch nicht dokumentiertes Verhalten) → weiterhin zurückhaltend behandeln, einstufen, ggf. Rückfrage oder „nur Verdacht".
- **Vollständigkeit der ANWENDUNG bereits bekannter, bestätigter Muster** (a)–(g) **plus Skript-Hygiene (e)** → das ist **keine Ermessensfrage mehr**, sobald eine bestätigte Referenzdatei vorliegt oder das Muster im Katalog als „automatisch sicher" bzw. „vom Kunden für diesen Report bereits bestätigt" markiert ist. Hier gilt: **alle** zutreffenden Muster **müssen** angewendet werden, nicht nur die, die im C#-Skript-Diff auffallen. Ein Lauf, der z. B. nur den Skript-Fix macht, aber die dazugehörigen `KeepTogether`-/Höhen-/Tabellenzeilen-Anpassungen (Muster g) vergisst, ist **unvollständig**, selbst wenn der Skript-Teil für sich genommen korrekt war. Siehe `known-issues.md` Eintrag 8 für den konkreten Fall, an dem genau das passiert ist.

Praktische Konsequenz: **Schritt 2 verlangt immer einen vollständigen strukturellen Diff (Skript UND reine XML-/Layout-Eigenschaften)**, nicht nur einen Diff des eingebetteten Skripts — siehe die Pflicht-Checkliste in Schritt 2.

## Arbeitsablauf

### Schritt 1 — Report entgegennehmen und Rohdaten extrahieren

Kopiere die hochgeladene `.repx` in ein Arbeitsverzeichnis (z.B. `/tmp/repx_work/`). Öffne sie mit `encoding='utf-8-sig', newline=''`, damit BOM sauber abgetrennt wird, aber die CRLF-Zeilenenden exakt erhalten bleiben (Details dazu und zur `ScriptsSource`-Extraktion in `references/repx-technical-notes.md`). Dekodiere das eingebettete C#-Skript und speichere es separat als lesbare `.cs`-Datei, damit du es normal durchsuchen und lesen kannst.

Prüfe direkt zu Beginn, ob es sich überhaupt um einen strukturell verwandten Report handelt (Bandnamen wie `Sub_POS`, `GROUP_ERP_Nummer`, `GroupFooter_Uebertrag`, Verwendung von `sumCarryoverSum`). Falls die Struktur stark abweicht, sag das dem Nutzer offen — die Muster unten generalisieren nur begrenzt auf komplett andere Reports.

### Schritt 2 — Referenz-.repx anfordern (PFLICHT) und Diagnose gegen den Fix-Katalog

Bevor du in die eigentliche Diagnose einsteigst: frag den Nutzer aktiv nach der bestätigten Referenz-`.repx` (siehe Abschnitt „Referenzbeispiel" oben) — das ist Pflicht, kein optionaler Zwischenschritt, und gilt unabhängig davon, wie ähnlich oder unähnlich die neue Datei auf den ersten Blick wirkt. Nur wenn der Nutzer explizit sagt, dass er keine Referenz hat oder bereitstellen kann, machst du ohne sie weiter (und vermerkst das später im Bericht/Changelog, siehe Ausnahme-Regel oben). Liegt eine Referenzdatei vor, extrahiere sie wie in Schritt 1 beschrieben und halte sie für den strukturellen Diff bereit.

Lies `references/fix-catalog.md`. Gehe die dort beschriebenen Muster (a) bis (g) systematisch durch — jedes ist **musterbasiert** beschrieben (welches Verhalten/welche Codestruktur zu suchen ist), nicht an konkrete Methodennamen oder `Ref`-IDs aus dem ursprünglichen Report gebunden, weil die nächste Report-Variante andere Namen haben wird. Notiere für jeden Fund, welchem Muster er entspricht und welche Sicherheitsstufe laut Katalog gilt. Liegt eine Referenzdatei vor, führe zusätzlich den strukturellen Diff gegen sie durch (siehe „Referenzbeispiel" oben) und bevorzuge dort bestätigt funktionierende Werte/Formulierungen gegenüber einer eigenen Neu-Interpretation des Katalogs.

**Pflicht-Checkliste für den strukturellen Diff (PFLICHT, nicht nur das Skript diffen):** Ein reiner Diff des dekodierten C#-Skripts reicht NICHT aus — mehrere der Muster (insbesondere g) leben ausschließlich in reinen XML-/Layout-Eigenschaften, die im Skript-Diff unsichtbar bleiben. Gehe bei jedem Lauf mit Referenzdatei explizit auch diese Punkte durch, jeweils Ziel-Datei gegen Referenz:

1. **`KeepTogether`-Vorkommen (alle, nicht nur die vom letzten Lauf):** Jedes `KeepTogether="..."`-Attribut in der ganzen Datei auflisten (Element + Wert) und mit der Referenz abgleichen — auf Zeilen-, Tabellen- UND Band-/SubBand-Ebene. Nicht nur an der einen Stelle suchen, die aus einem früheren Lauf bekannt ist.
2. **Höhen/Größen, INKLUSIVE des `<Localization>`-Blocks:** Für jedes Element, das in einem Muster eine Mindesthöhe braucht (z. B. `tb_ÜbertragOben`, `Sub_UebertragOben`), sowohl das direkte Attribut (`HeightF`, `SizeF`) als auch `Component="#Ref-<Ziel>"`-Einträge im `<Localization>`-Block prüfen (siehe `repx-technical-notes.md`, Abschnitt „Der `<Localization>`-Block", und `known-issues.md` Einträge 6/7). Ein Diff, der nur das Element selbst anschaut, übersieht hier gesetzte Werte systematisch.
3. **Zeilenanzahl in kritischen Tabellen** (z. B. `xrTable1` in `Sub_POS`): Anzahl der `XRTableRow`-Kinder gegen die Referenz vergleichen. Eine überzählige/doppelte Zeile fällt in einem reinen Skript-Diff nicht auf.
4. **`Summary`-Element-Anzahl** vor Bearbeitung festhalten (siehe `validation-checklist.md`, Punkt 5).
5. **Tote/unverdrahtete Methoden und Variablen** (Muster e) — siehe Schritt 5, jetzt Pflichtbestandteil dieses Schritts, nicht mehr optional.

Prüfe außerdem gegen `references/known-issues.md` — dort sammeln sich Fallen, die in früheren Läufen entdeckt wurden (aktuell v.a. die `sumCarryoverSum`/`Summary`-Falle sowie der unvollständige Diff aus Eintrag 8). Diese Datei ist ein lebendes Dokument: wenn du in diesem Lauf etwas Neues entdeckst, das über den bisherigen Katalog hinausgeht, ergänze sie am Ende (Schritt 8).

### Schritt 3 — Befund an den Nutzer melden, bevor automatisch etwas verändert wird

Fasse zusammen, was gefunden wurde, gruppiert nach Sicherheitsstufe. Auch bei eindeutigen Fällen: kurz benennen, was verändert wird und warum, bevor du loslegst — der Nutzer soll nachvollziehen können, was passiert, auch wenn er nicht bei jedem Einzelpunkt gefragt wird. Wurde ohne Referenzdatei gearbeitet (siehe Ausnahme-Regel im Abschnitt „Referenzbeispiel"), weise an dieser Stelle explizit auf das dadurch geringere Vertrauensniveau hin.

### Schritt 4 — Fixes anwenden

- **Automatisch sicher**: direkt umsetzen, ohne extra nachzufragen.
- **Vorschlag mit Rückfrage**: dem Nutzer den konkreten Fix vorschlagen (mit möglichen Nebenwirkungen, z.B. Layout-Whitespace bei `KeepTogether`), und erst nach Zustimmung umsetzen.
- **Nur Verdacht**: NICHT automatisch anfassen. Dokumentieren, im Bericht an den Nutzer erwähnen, empfehlen, es im DevExpress Designer manuell zu testen.

Halte dich bei jeder Skript-Änderung an die Bearbeitungs-Pipeline aus `references/repx-technical-notes.md` (insbesondere die exakte Reihenfolge beim Re-Escaping und die eindeutigen Grenzmarkierungen beim Zurücksplicen) — ein falsch reihenfolgtes Escaping oder ein falscher Splice-Punkt erzeugt eine Datei, die zwar wohlgeformtes XML sein kann, aber in DevExpress nicht mehr lädt oder falsch layoutet.

### Schritt 5 — Skript-Hygiene (PFLICHT seit 28.08.)

**Immer durchführen, als fester Bestandteil jedes Laufs** — nicht mehr davon abhängig, ob der Nutzer das separat erwähnt. Das ist ausdrücklich als Kundenvorgabe festgelegt worden, nachdem in einem früheren Lauf tote Variablen/Methoden stehen geblieben waren, obwohl die Referenzdatei sie bereits bereinigt hatte (siehe `known-issues.md` Eintrag 8).

Entferne leere/wirkungslose Print-Event-Handler und rein auskommentierte tote Codepassagen nach den Regeln in Muster (e) von `references/fix-catalog.md`. Kurzfassung der wichtigsten Regeln dabei:

- Vor dem Löschen einer Variable/Methode **verifizieren, nicht raten**: per Textsuche zählen, ob sie außerhalb ihrer eigenen Deklaration/Definition noch irgendwo gelesen/aufgerufen wird (auch von anderem, selbst totem Code aus — dann gehört dieser ggf. mit dazu, siehe Muster e).
- Bei Geschwister-Events am selben Element (z.B. `OnBeforePrint` mit echter Logik neben leerem `OnAfterPrint`) nur die leere Verdrahtung entfernen, die mit Logik behalten.
- Begründungs-Kommentare, die eine Architekturentscheidung dokumentieren, nicht ersatzlos löschen, sondern knapp erhalten oder zum nächstgelegenen aktiven Handler verschieben.
- **Nicht** anfassen: Variablen/Methoden, die zu einer erkennbar eigenständigen, anderen Funktionalität gehören (z. B. eine parallele Steuertext-/Sachkonto-Berechnung), auch wenn die Referenzdatei diese im Zuge eines separaten Umbaus mit entfernt hat — das ist kein Hygiene-Fall, sondern ein eigenständiger Funktionsumbau außerhalb des Auftragsumfangs (siehe `known-issues.md` Eintrag 8 für ein konkretes Beispiel dieser Abgrenzung).

### Schritt 6 — Validierung (inkl. Selbst-Audit der Referenzdatei)

Arbeite `references/validation-checklist.md` **vollständig** ab, bevor irgendetwas ausgeliefert wird. Das ist nicht optional — mehrere der Fehler, die in früheren Läufen passiert sind (verwaiste XML-Verdrahtung, versehentlich entfernte Summary-Elemente, verlorenes BOM), wurden ausschließlich durch diese Checks gefangen, nicht durch bloßes Lesen des Diffs. „Der Output muss fehlerfrei sein" ist die Vorgabe — die Checkliste ist der Nachweis dafür, nicht eine Formalität.

**Neu (PFLICHT): Lauf dieselbe Checkliste zusätzlich gegen die Referenzdatei selbst.** Die Referenz ist vom Kunden bestätigt, aber nicht unfehlbar — prüfe sie genauso auf Wohlgeformtheit, doppelte `Ref`-IDs, Scripts-Parität, Klammern-Balance, Summary-Anzahl und BOM. Findest du dort einen echten Fehler: (1) korrigieren, (2) als eigene, neu gestempelte Datei ausliefern (klar als „korrigierte Referenz" gekennzeichnet, siehe Schritt 7), (3) im Changelog UND in `known-issues.md` explizit vermerken, was an der Referenz falsch war. Findest du keinen Fehler: das im Bericht an den Nutzer kurz und ehrlich so festhalten (nicht verschweigen, aber auch keinen Fehler erfinden, um „etwas gefunden zu haben").

### Schritt 7 — Auslieferung

Liefere die reparierte `.repx` zusammen mit einem Changelog aus. Das Changelog ist für work4all-Mitarbeiter gedacht, die den Report nicht selbst gebaut haben — schreibe es auf Deutsch, als nummerierte Liste, mit einem kurzen Satz pro Änderung: was, wo, warum. Kein Fachjargon ohne Erklärung; die Übertrag-Logik in ein bis zwei Sätzen einordnen, falls die Änderung nicht selbsterklärend ist.

**Dateibenennung — PFLICHT:** Jede ausgelieferte `.repx`-Datei (die reparierte Datei ebenso wie jede neu erstellte oder korrigierte Referenz-`.repx`) bekommt vor der Auslieferung einen Zeit-/Datumsstempel an den Dateinamen angehängt, Format `_JJJJ-MM-TT_hh-mm`, unmittelbar vor der Dateiendung.

**Zeitzone — PFLICHT, immer Europe/Berlin:** Die Session-Umgebung läuft typischerweise in UTC, nicht in der Zeitzone des Nutzers — `date` ohne Zeitzonenangabe liefert also die FALSCHE Uhrzeit für den Zeitstempel (im Sommer 2h, im Winter 1h daneben). Immer explizit die Zielzeitzone erzwingen, z. B. `TZ=Europe/Berlin date '+%Y-%m-%d_%H-%M'` — niemals bloßes `date` ohne `TZ=`. Das ist keine Kleinigkeit: ein falscher Zeitstempel führt bei mehreren Läufen am selben Tag zu genau der Verwechslungsgefahr, die dieser Abschnitt eigentlich verhindern soll (siehe `known-issues.md` Eintrag 11 für den Vorfall, der das aufgedeckt hat). Grund für den Zeitstempel überhaupt: bei mehreren Läufen mit ähnlichen Dateinamen (z.B. mehrere Referenzversionen im zeitlichen Verlauf) lässt sich sonst nicht mehr zweifelsfrei nachvollziehen, welche Datei aus welchem Lauf stammt — das ist in der Praxis bereits zu Verwechslungen beim Vergleich von Läufen an unterschiedlichen Tagen gekommen. Dies ist kein optionaler Stil-Punkt, sondern fester Teil der Auslieferung.

Halte den Basisnamen dabei bewusst KURZ (kurzer Report-Name + ggf. Versionskürzel, keine ausführliche Beschreibung des Inhalts im Dateinamen) — ein langer Basisname lässt den Zeitstempel am Ende in der UI/Downloadliste abgeschnitten wirken oder gar nicht mehr sichtbar sein, was den eigentlichen Zweck des Stempels zunichtemacht. Ausführliche Beschreibungen gehören ins Changelog, nicht in den Dateinamen. Beispiel: `dxAio_template_REFERENZ_v2_2026-08-28_10-29.repx` (nicht `dxAio_template_REFERENZ_v2_KeepTogetherFalse_Mindesthoehe_2026-08-28_10-29.repx`).

### Schritt 8 — `known-issues.md` pflegen

Wenn in diesem Lauf ein neues Muster, eine neue Falle oder eine überraschende DevExpress-Eigenheit auffällt (etwas, das nicht bereits im Fix-Katalog oder in known-issues.md steht), ergänze `references/known-issues.md` um einen neuen Eintrag nach demselben Format wie die bestehenden. So wird die Skill mit jedem bearbeiteten Report robuster, statt bei jedem Lauf wieder bei null anzufangen.

## Referenzdateien im Überblick

- `references/repx-technical-notes.md` — Dateiformat, Encoding/Escaping-Pipeline, DevExpress-Bandmodell, Event-Timing (BeforePrint vs. PrintOnPage), XML/Skript-Paritätsregel. Lies das zuerst.
- `references/fix-catalog.md` — die bekannten Problem-Muster, ihre Ursache, der empfohlene Fix, und wie sicher es ist, ihn automatisch anzuwenden.
- `references/validation-checklist.md` — die Checks, die vor jeder Auslieferung durchlaufen werden müssen.
- `references/known-issues.md` — lebendes Dokument bekannter Fallen und Überraschungen, wächst mit jedem Lauf.
