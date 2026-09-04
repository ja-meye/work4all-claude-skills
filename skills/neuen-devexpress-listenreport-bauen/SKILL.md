---
name: neuen-devexpress-listenreport-bauen
description: Baut aus einem Mockup (PDF/Bild) und einer bestehenden work4all-DevExpress-.repx-Vorlage einen neuen DevExpress-Listenreport (Kundenliste, Lieferantenliste, Artikelliste, o.ä.): Feldzuordnungs-Excel, SQL-/Query-Übernahme, Parameter-/ID-Filtermuster, Layout, Validierung. Verwenden bei "neuen Listenreport bauen", "Feldzuordnung", "Report-Bauplan", einem Mockup oder einer zu übernehmenden alten SQL-/Crystal-Reports-Query — auch ohne die Wörter "Skill" oder "DevExpress". Ebenfalls verwenden, wenn ein bestehender Listenreport nicht mehr lädt, aber eine funktionierende Parallelversion existiert, deren Inhalt/Query/Parameter ins Grundgerüst der funktionierenden Datei übernommen werden sollen.
metadata:
  skill_id: DXJ0002
  version: 1.3.1
---

# Neuen DevExpress-Listenreport aus Mockup + Vorlage bauen

## Worum es geht

work4all-Kunden möchten regelmäßig einen neuen Listenreport (Kundenliste, Lieferantenliste, Artikelliste, o.ä.), der optisch/inhaltlich einem Mockup entspricht, aber technisch auf denselben Mustern wie bestehende Reports aufsetzt: gleiche Parameterlogik (ID-Liste + Listenfilter), gleiche DevExpress-XtraReports-Mechanik (.repx = XML mit base64-kodierter SqlDataSource). Diese Skill kapselt den Prozess, der dafür erarbeitet und mit dem Kunden validiert wurde: Bauplan erfassen → Feldzuordnung mit dem Fachbereich abstimmen → SQL/Joins einbauen → neuen Report bauen → validieren → mit offenen Punkten ausliefern.

Wie bei der Schwester-Skill `fix-folgeseiten-uebertrag-problem` gilt: **Muster erkennen und anwenden, nicht blind Code von damals kopieren.** Jeder Report und jedes Mockup ist etwas anders.

Lies **`references/repx-technische-notizen.md`**, bevor du an einer .repx baust — dort steht die Dateiformat-Mechanik (Base64-SqlDataSource, Ref-ID-Eindeutigkeit, XML-Escaping im eingebetteten SQL) und die Fallstricke, die schon einmal Probleme gemacht haben.

## Referenz-.repx ist Pflicht

Genau wie beim Übertrag-Fix gilt: **frag aktiv nach einer bestehenden, funktionierenden .repx desselben Report-Typs (Listenreport)**, bevor du eine neue baust — auch wenn der Nutzer sie nicht von sich aus erwähnt. Diese Vorlage liefert die strukturellen Muster, die du 1:1 übernimmst, statt sie neu zu erfinden:

- den Aufbau von `<Parameters>`, `<Bands>`, `<ComponentStorage>`, `<Watermarks>`
- das Parameter-/Filtermuster für die ID-Liste (siehe unten)
- Seitenformat, Ränder, Schriftgrößen-Konventionen

Nur wenn der Nutzer explizit sagt, dass keine Vorlage existiert, fange bei null an — und weise im Bericht an den Nutzer darauf hin, dass dadurch mehr geraten werden musste.

## Kritische Prüfung statt Automatismus

Bei jeder Abweichung von der Referenz-.repx — ein zusätzliches Feld, ein anderer Join, ein neuer Parameter — zuerst fragen: **ist das wirklich nötig, um das Mockup korrekt abzubilden, oder ist es eine Annahme, die sich auch anders lösen ließe?** Nicht jede im Mockup sichtbare Nuance rechtfertigt eine strukturelle Änderung an der bewährten Vorlage. Und wie überall in diesem Skill-Ökosystem gilt: bei Unsicherheit wird nachgefragt, nicht geraten — insbesondere bei allem, was eine Datenbank-Feldzuordnung, einen Join oder eine Parameter-Bedeutung betrifft, wo eine falsche Annahme die Query beim Kunden zum Absturz bringen kann.

## Sonderfall: bestehenden Report reparieren, der nicht lädt (Content-Transplantation)

Manchmal ist die Aufgabe keine Neuerstellung nach Mockup, sondern eine Reparatur: Eine bestehende `.repx` lädt nicht mehr im Programm, aber der Nutzer hat bereits eine zweite, strukturell einfachere Version desselben Report-Typs (z.B. neu in der App angelegt), die nachweislich lädt. In diesem Fall **nicht** von null neu bauen, sondern den Inhalt der defekten Datei in das Grundgerüst der funktionierenden Datei übertragen:

1. **Grundgerüst der funktionierenden Datei nicht verändern.** Das Root-Element (`Name`, `ScriptLanguage`, `SnappingMode`, `DataSource`, etc.) der funktionierenden Datei 1:1 übernehmen — es enthält oft unbemerkt genau die Einstellung, die den Unterschied zwischen "lädt" und "lädt nicht" ausmacht.
2. **Connection Name als erste Fehlerquelle vergleichen.** Beide `SqlDataSource`-Blöcke (Base64 im `ComponentStorage` dekodieren) gegenüberstellen und den `<Connection Name="...">`-Wert exakt vergleichen — auch scheinbar triviale Abweichungen wie ein angehängtes Leerzeichen + Zahl (`"...Connection"` vs. `"...Connection 1"`) sind ein sehr wahrscheinlicher Kandidat für den Ladefehler: Der Report referenziert dann eine Connection, die unter diesem exakten Namen nicht (mehr) existiert.
3. **Inhalt aus der defekten Datei übernehmen:** `<Parameters>`, `<Bands>`, `<StyleSheet>`, `<ParameterPanelLayoutItems>`, `<Watermarks>` komplett aus der defekten Datei in die neue Datei kopieren; die Ref-Nummerierung dieser Blöcke bleibt dabei unverändert (sie ist in sich schon eindeutig) — es werden die entsprechenden Blöcke der funktionierenden Datei komplett ersetzt, nicht beide Sätze gemischt.
4. **SqlDataSource neu zusammensetzen:** Query, Parameter und ResultSchema aus der defekten Datei übernehmen, aber die `<Connection Name="...">` auf den in Schritt 2 bestätigten, funktionierenden Wert setzen. Anschließend neu Base64-kodieren.
5. **Skript nicht anfassen, solange unklar ist, ob Scripts in der Zielumgebung aktiviert sind.** Kein `ScriptsSource`/`work4all-log`-Block wird ergänzt, solange der Nutzer das nicht ausdrücklich bestätigt — nur die Report-/Datenquellen-Definition wird migriert.
6. **Validieren wie in Schritt 5 des normalen Ablaufs** (`references/validierung-vor-auslieferung.md`), zusätzlich einen gezielten Root-Attribut-Abgleich zwischen alter defekter Datei und neuer Datei, um sicherzustellen, dass wirklich nur der beabsichtigte Inhalt übertragen wurde und nicht versehentlich auch Grundgerüst-Attribute mit übernommen wurden.

Bestätigt an `dxArticleList` → `dxArticleListV2` (04.09.2026, siehe `docs/lessons-learned.md`): Ursache des Ladefehlers war eine abweichende Connection Name (fehlendes `" 1"`-Suffix). Nach Übernahme des Inhalts mit korrigierter Connection lud die Datei sowohl im Programm als auch nach einem Re-Export aus Visual Studio erfolgreich.

## Arbeitsablauf

### Schritt 1 — Mockup lesen und Bauplan als Excel erfassen

Lies das Mockup (PDF/Bild) vollständig — auch mehrseitige Beispiele, damit du echte Beispielwerte pro Spalte hast, nicht nur die Kopfzeile. Trenne dabei zwei Arten von Feldern:

- **Detailfelder**: wiederholen sich pro Datensatz/Zeile (z.B. Firma, Straße, PLZ).
- **Kopf-/Parameterfelder**: erscheinen einmal pro Reportlauf, nicht pro Zeile (Sortierung, Filtertext, Datensatzanzahl, Zeitstempel, Seitenzahl, Logo). Diese sind später meist keine 1:1-DB-Feld-Zuordnung, sondern Report-Parameter oder Ausdrücke — das muss dem Nutzer klar kommuniziert werden, sonst wird beim Ausfüllen des Bauplans versucht, dafür ein DB-Feld zu finden, das es so nicht gibt.

Baue daraus eine Excel-Tabelle (`xlsx`-Skill nutzen) nach dem Muster in `references/excel-bauplan-vorlage.md`: eine Zeile pro Feld, Spalten für Beispielwert, Typ (Detail/Kopf), und leere, gelb markierte Spalten DB-Tabelle/DB-Feld zum Ausfüllen durch den Nutzer. Trage bereits bekannte Zuordnungen ein (aus Schritt 2, falls die SQL/Query schon vorliegt), lass unbekannte Felder frei, und formuliere bei mehrdeutigen Feldern (z.B. "ist 'Nr.' die Zeilennummer oder die echte Kundennummer?") eine konkrete Rückfrage in der Anmerkung-Spalte statt einfach zu raten.

### Schritt 2 — SQL/Joins übernehmen, wenn vorhanden

Wenn der Nutzer eine bestehende SQL- oder Crystal-Reports-Query mitliefert (Crystal-`.rpt`-Dateien sind binäre proprietäre Dateien — sag das dem Nutzer offen, wenn er eine `.rpt` hochlädt, und bitte stattdessen um den SQL-Text oder einen PDF-Ausdruck), nutze deren Joins als Grundlage, nicht als bloße Inspiration. Dabei:

- **Nie einen DB-Feldnamen erfinden**, der in der gegebenen Quelle nicht vorkommt, nur weil ihn das Mockup zeigt (z.B. eine Status- oder Klassifizierungsspalte, die im Mockup sichtbar ist, aber in der gelieferten Query fehlt). Baue stattdessen im Report-Layout eine sichtbare Platzhalterzelle (z.B. Text `TODO: DB-Feld?`, keine `ExpressionBindings`) statt einer Bindung auf einen geratenen Feldnamen — ein falscher Feldname bringt die Query beim Ausführen zum Absturz, ein sichtbarer Platzhalter nicht. Liste diese Lücken explizit im Bericht an den Nutzer und in der Excel-Kontrollliste auf.
- **Namenskollisionen auflösen**: Wenn zwei selektierte Spalten aus unterschiedlichen Tabellen gleich heißen (z.B. `Kunden."E-Mail"` und `KAnsprechp."E-Mail"`), vergib eindeutige Aliase (`KundenEMail`, `AnsprechpartnerEMail`) — sonst kollidiert das ResultSchema.
- **1:n-Join-Risiko prüfen**: Ein Join auf eine Tabelle, die mehrere Zeilen pro Hauptdatensatz liefern kann (z.B. mehrere Ansprechpartner pro Kunde), erzeugt Duplikate in der Liste, wenn das Mockup eigentlich eine Zeile pro Hauptdatensatz zeigt. Das aktiv ansprechen statt stillschweigend zu übernehmen oder stillschweigend zu "reparieren" — frag nach einem Auswahlkriterium (z.B. Hauptansprechpartner-Kennzeichen) oder biete eine `EXISTS`-Variante als Alternative an, wenn nur geprüft werden soll, ob überhaupt ein verknüpfter Datensatz existiert.
- **Datenbank-/Schema-Namen abgleichen**: Eine alte Query nennt die Datenbank oft explizit (dreiteiliger Bezeichner `"Datenbank"."dbo"."Tabelle"`), während die Ziel-.repx meist über eine benannte, aus der App-Konfiguration aufgelöste Connection zweiteilig referenziert (`"dbo"."Tabelle"`). Übernimm die Zweiteiligkeit der Vorlage, aber weise den Nutzer explizit darauf hin, dass er prüfen muss, ob die Connection wirklich auf dieselbe Datenbank zeigt wie die alte Query.

### Schritt 3 — Parameter-/Filterlogik der Vorlage übernehmen

Übernimm das Parametermuster der Referenz-.repx unverändert (typischerweise: ein Multi-Value-Parameter für eine ID-Liste, z.B. `keys`, der serverseitig über einen XML-Split-Trick aus einem kommagetrennten String in eine `IN (...)`-Liste umgewandelt wird, plus ein reiner Anzeige-Parameter für den aktuellen Listenfilter). Ändere nur das gefilterte Feld auf das vom Nutzer genannte ID-Feld des neuen Reports (z.B. `Kunden.Code` statt `ERP_Code`) — nicht die Mechanik selbst neu erfinden.

### Schritt 4 — Layout bauen

Baue die neue .repx auf Basis der Referenzdatei (siehe `references/repx-technische-notizen.md` für die Mechanik: Base64-Blob decodieren, SQL/ResultSchema darin ersetzen, wieder encodieren, Ref-IDs durchgängig eindeutig vergeben). Richte dich am Mockup aus für:

- Spaltenbreiten/-reihenfolge der Detailzeile (relative `Weight`-Werte, die die visuellen Proportionen des Mockups annähern)
- eine sich wiederholende Spaltenkopfzeile (meist im `PageHeaderBand`, das sich automatisch pro Seite wiederholt)
- Kopfbereich mit Logo-Platzhalter, Titel, Sortier-/Filterzeile, Datensatzanzahl/Zeitstempel/Seitenzahl (Summary-Element mit `Func="Count"` für Anzahl, `Now()`-Expression für Zeitstempel, `XRPageInfo` für Seitenzahl — siehe technische Notizen)
- Fußzeile analog zur Vorlage

Für Farben nur benannte .NET-Farben verwenden (z.B. `MidnightBlue`, `Gainsboro`, `Gray`), keine geratenen RGB/ARGB-Zahlenformate — deren exaktes Serialisierungsformat lässt sich ohne Beispiel aus einer echten Datei nicht zuverlässig bestätigen, und ein falsches Format kann die Datei brechen.

### Schritt 5 — Validieren, bevor ausgeliefert wird

Arbeite die Prüfungen aus `references/validierung-vor-auslieferung.md` ab (wohlgeformtes XML, eindeutige `Ref`-IDs, alle `#Ref-x`-Verweise aufgelöst, Base64-Blob separat dekodiert und als XML geprüft, jede `ExpressionBindings`-Feldreferenz gegen das `ResultSchema` abgeglichen). Das ersetzt **nicht** den echten Test: sag dem Nutzer klar, dass ein Laden im DevExpress Report Designer und ein Renderdurchlauf gegen Testdaten vor dem produktiven Einsatz weiterhin nötig sind — das kann in dieser Umgebung nicht durchgeführt werden.

### Schritt 6 — Ausliefern

Liefere aus:

1. die neue `.repx`
2. die (ggf. aktualisierte) Excel-Feldzuordnung als Kontrollliste
3. eine klare, kurze Zusammenfassung aller offenen Punkte (fehlende Felder, 1:n-Join-Risiken, Datenbank-Namens-Annahmen, angenommene Datentypen) — nicht verschweigen, sondern aktiv benennen, damit der Nutzer gezielt nachliefern kann.
4. einen kurzen Statusblock, welche Teile dieses Skills in diesem Lauf **nicht** ausgeführt werden konnten und warum (z.B. "keine Referenz-.repx vorhanden — Layout stärker als sonst geraten", "SQL/Query fehlt noch — Excel-Bauplan ohne befüllte DB-Spalten ausgeliefert", "Designer-Laden/Testdaten-Rendering kann in dieser Umgebung nicht durchgeführt werden"). Gab es keine Auslassungen, reicht ein kurzer positiver Vermerk.

## Skill-ID, Version & Fix-Log-Startpunkt

Diese Skill trägt die ID **DXJ0002** (aktuell Version **1.3.1**). Format und vollständige Registry sind zentral dokumentiert in `work4all-reporting-skills:neuen-devexpress-report-skill-anlegen`, `../neuen-devexpress-report-skill-anlegen/references/fix-log-format.md` und `../neuen-devexpress-report-skill-anlegen/references/skill-id-registry.md`.

Jede neu gebaute `.repx` bekommt in Schritt 4 (Layout bauen) ganz oben im eingebetteten Skript einen initialen Log-Block im aktuellen Format `(v2)`, der die Herkunft der Datei dokumentiert — damit spätere Fix-Skills (z.B. `fix-folgeseiten-uebertrag-problem`) wissen, dass diese Datei maschinell von dieser Skill erzeugt wurde, mit welcher Version, wann und mit welchem Ergebnis. **Seit v1.2.0 gehört die Anker-Zeile direkt danach zwingend dazu** (siehe `fix-log-format.md`, Abschnitt „Überlebensfähigkeit bei einem Designer-Speichervorgang") — ohne sie kann ein ScriptsSource-Block, der nur aus Kommentaren besteht, beim ersten Speichern im DevExpress Report Designer restlos verschwinden:

```
// === work4all-log (v2) ===
// DXJ0002 | v1.1.0 | 2026-08-28T15:10:00 | neuen-devexpress-listenreport-bauen | geändert
// === end work4all-log ===
private static readonly string _work4allLogAnchor = "keep-scriptssource-alive";
```

Beim Erstbau ist das Ergebnis immer `geändert` (es wird ja eine neue Datei erzeugt). Wird diese Skill **erneut** auf einen bereits von ihr gebauten Report angewendet — z.B. ein Korrekturlauf, nachdem der Fachbereich Rückmeldung zur Feldzuordnung gegeben hat — gilt dieselbe Ergebnis-Konvention wie bei Verbesserungs-Skills: `geändert`, wenn tatsächlich etwas am Layout/an der Query angepasst wurde, `keine Änderung nötig`, wenn die Prüfung ergab, dass alles bereits passt. Der Sonderfall "bestehenden Report reparieren" oben (Content-Transplantation) schreibt **keinen** neuen Log-Block, solange nicht ausdrücklich bestätigt ist, dass Scripts in der Zielumgebung aktiviert sind. Vollständige Regeln inkl. Idempotenz-Check: `../neuen-devexpress-report-skill-anlegen/references/fix-log-format.md`.

Zeitstempel immer mit Zeitzone Europe/Berlin erzeugen (`TZ=Europe/Berlin date '+%Y-%m-%dT%H:%M:%S'` bzw. äquivalent in Python — ohne `%z`, der Log-Zeitstempel wird bewusst **ohne** UTC-Offset-Suffix geschrieben, siehe `fix-log-format.md`), nicht die UTC-Zeit der Session-Umgebung — das war schon beim Übertrag-Fix-Skill eine Fehlerquelle (siehe dort `known-issues.md` Eintrag 11).

## Referenzdateien im Überblick

- `references/repx-technische-notizen.md` — Base64-SqlDataSource-Mechanik, Ref-ID-Eindeutigkeit, XML-Escaping im eingebetteten SQL, Parameter-/Filtermuster, Farbformat-Hinweis.
- `references/excel-bauplan-vorlage.md` — Aufbau der Feldzuordnungs-Excel (Spalten, Legende, Beispielblock, Farbcodierung).
- `references/validierung-vor-auslieferung.md` — die Prüfungen, die vor jeder Auslieferung laufen müssen, inkl. wiederverwendbarem Python-Schnipsel.
- `../neuen-devexpress-report-skill-anlegen/references/fix-log-format.md` (in `neuen-devexpress-report-skill-anlegen`) — Spezifikation des `work4all-log`-Blocks, maßgeblich für Schritt 4 und für Korrekturläufe.

## Versionierung dieses Skills

- v1.0.0 — Erstfassung (Registry-Eintrag `DXJ0002`, 2026-08-28): Bauplan-Excel, SQL/Join-Übernahme, Parametermuster, Layout-Bau, Validierung, Auslieferung mit initialem Log-Block.
- v1.1.0 — Neuer Abschnitt "Kritische Prüfung statt Automatismus" ergänzt. Schritt 6 um verpflichtenden Statusbericht zu nicht ausgeführten Teilen erweitert. Log-Startpunkt auf Format `(v2)` inkl. Ergebnis-Feld gehoben; Ergebnis-Konvention für spätere Korrekturläufe auf bereits gebaute Reports ergänzt.
- v1.1.1 — Dokumentationskorrektur: Log-Block in `work4all-log` umbenannt (vorher `work4all-skill-log`), Versionskennzeichnung `(v2)` bleibt erhalten. Beispiel-Log-Zeile und Zeitstempel-Erzeugungsbefehl korrigiert: kein UTC-Offset (`+02:00`/`%z`) mehr, nur noch die lokale Wanduhrzeit Europe/Berlin.
- v1.2.0 — Bestätigter Befund (Report `dxArticleList`, 03.09.2026): ein rein aus Kommentaren bestehender `work4all-log`-Block wird beim Speichern aus dem DevExpress Report Designer restlos entfernt (`ScriptsSource`/`ScriptLanguage` verschwinden komplett, nicht nur der Inhalt). Schritt 4 seedet den Block jetzt zusätzlich mit einer harmlosen Anker-Zeile direkt nach der Fußzeile (`private static readonly string _work4allLogAnchor = ...`), damit der kompilierte Skript-Code beim Speichern nicht leer ist — Mitigation laut `fix-log-format.md` noch nicht durch einen echten Designer-Round-Trip verifiziert, daher beim nächsten Testdruck gezielt gegenprüfen.
- v1.2.1 — Frontmatter-Konformität hergestellt: `skill_id` und `version` waren Top-Level-Frontmatter-Keys (von der offiziellen Agent-Skills-Spezifikation nicht erlaubt) und stehen jetzt unter `metadata:`.
- v1.3.0 — Neuer Sonderfall-Abschnitt "bestehenden Report reparieren, der nicht lädt (Content-Transplantation)" ergänzt: Vorgehen, wenn eine defekte `.repx` nicht lädt, aber eine strukturell einfachere Parallelversion desselben Report-Typs nachweislich funktioniert — Grundgerüst der funktionierenden Datei unverändert lassen, Connection Name als erste geprüfte Fehlerquelle, restlichen Inhalt (Parameters/Bands/StyleSheet/ParameterPanelLayoutItems/Watermarks/Query) aus der defekten Datei übernehmen, Skript dabei nicht anfassen, wenn Skript-Aktivierung in der Zielumgebung unklar ist. Bestätigt an `dxArticleList` → `dxArticleListV2` (04.09.2026): Ursache war eine abweichende Connection Name (fehlendes `" 1"`-Suffix); nach Übernahme des Inhalts mit korrigierter Connection lud die Datei sowohl im Programm als auch nach einem Re-Export aus Visual Studio erfolgreich. Trigger-Beschreibung im Frontmatter um diesen Reparatur-Fall erweitert.
- v1.3.1 — Frontmatter-`description` war mit ~1.320 Zeichen deutlich zu lang; auf ~690 Zeichen gekürzt (Beispielsätze und Wiederholungen entfernt, beide Trigger-Szenarien — Neubau und Reparatur-Sonderfall — bleiben erkennbar). Rein redaktionell, keine inhaltliche/funktionale Änderung.
