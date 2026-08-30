---
name: neuen-devexpress-listenreport-bauen
description: Baut aus einem Mockup (PDF/Bild) und einer bestehenden work4all-DevExpress-.repx-Vorlage einen neuen DevExpress-Listenreport (z.B. Kundenliste, Lieferantenliste, Artikelliste). Erstellt zuerst eine Excel-Feldzuordnungstabelle zur Abstimmung mit dem Fachbereich, übernimmt danach Joins/Query aus einer SQL- oder Crystal-Reports-Query in eine neue DevExpress-SqlDataSource und baut die neue .repx mit demselben Parameter-/ID-Filtermuster wie die Vorlage. Verwenden, wenn der Nutzer einen neuen work4all-Listenreport auf Basis eines Reports/Mockups bauen will, eine Excel-Feldzuordnung erstellen will, eine alte SQL-/Crystal-Reports-Query übernehmen möchte, oder "Report-Bauplan", "Feldzuordnung" oder "neuen Listenreport" erwähnt — auch ohne die Wörter "Skill" oder "DevExpress", z.B. "ich habe ein Mockup für einen neuen Report", "welche Felder kommen aus welcher Tabelle", "ich gebe dir die SQL von einem alten Report, bau das ein".
skill_id: DXJ0002
version: 1.0.0
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

## Skill-ID, Version & Fix-Log-Startpunkt

Diese Skill trägt die ID **DXJ0002** (aktuell Version **1.0.0**). Format und vollständige Registry sind zentral dokumentiert in `work4all-reporting-skills:neuen-devexpress-report-skill-anlegen`, `references/fix-log-format.md` und `references/skill-id-registry.md`.

Jede neu gebaute `.repx` bekommt in Schritt 4 (Layout bauen) ganz oben im eingebetteten Skript einen initialen Log-Block, der die Herkunft der Datei dokumentiert — damit spätere Fix-Skills (z.B. `fix-folgeseiten-uebertrag-problem`) wissen, dass diese Datei maschinell von dieser Skill erzeugt wurde, mit welcher Version und wann:

```
// === work4all-skill-log (v1) ===
// DXJ0002 | v1.0.0 | 2026-08-28T15:10:00+02:00 | neuen-devexpress-listenreport-bauen
// === end work4all-skill-log ===
```

Zeitstempel immer mit Zeitzone Europe/Berlin erzeugen (`TZ=Europe/Berlin date '+%Y-%m-%dT%H:%M:%S%z'` bzw. äquivalent in Python), nicht die UTC-Zeit der Session-Umgebung — das war schon beim Übertrag-Fix-Skill eine Fehlerquelle (siehe dort `known-issues.md` Eintrag 11).

## Referenzdateien im Überblick

- `references/repx-technische-notizen.md` — Base64-SqlDataSource-Mechanik, Ref-ID-Eindeutigkeit, XML-Escaping im eingebetteten SQL, Parameter-/Filtermuster, Farbformat-Hinweis.
- `references/excel-bauplan-vorlage.md` — Aufbau der Feldzuordnungs-Excel (Spalten, Legende, Beispielblock, Farbcodierung).
- `references/validierung-vor-auslieferung.md` — die Prüfungen, die vor jeder Auslieferung laufen müssen, inkl. wiederverwendbarem Python-Schnipsel.
