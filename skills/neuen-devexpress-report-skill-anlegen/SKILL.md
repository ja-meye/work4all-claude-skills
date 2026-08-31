---
name: neuen-devexpress-report-skill-anlegen
description: Legt einen neuen work4all-DevExpress-Report-Skill (Verbesserungs-Typ wie "fix-folgeseiten-uebertrag-problem" oder Neuerstellungs-Typ wie "neuen-devexpress-listenreport-bauen") strukturiert an und liefert ihn sowohl an das Cowork-Plugin als auch an das lokale GitHub-Repo C:\GitHub\work4all-claude-skills aus. Unbedingt verwenden, wenn der Nutzer einen neuen DevExpress-Skill anlegen, erweitern oder strukturieren möchte — auch bei kurzen Trigger-Sätzen wie "create new dx skill", "neuen DX Skill erstellen", "neuen Skill anlegen", "DX Skill Bauplan", "mach daraus einen skill" (im DevExpress/Report-Kontext), oder wenn der Nutzer nach Skill-ID, Versionierung, Fix-Log oder einer einheitlichen Struktur für Report-Skills fragt.
skill_id: DXJ0003
version: 0.2.1
---

# Neuen DevExpress-Report-Skill anlegen

Dieser Skill ist der "Bauplan" für alle weiteren work4all-DevExpress-Report-Skills in diesem Plugin. Er legt fest, aus welchen Bausteinen jeder Skill besteht, wie Skill-ID/Version/Fix-Log funktionieren, und wie ein fertiger Skill an beide Ablageorte (Cowork-Plugin + lokales GitHub-Repo) ausgeliefert wird.

Es gibt zwei Skill-Typen in diesem Ökosystem:

- **Verbesserungs-Typ** (Beispiel: `fix-folgeseiten-uebertrag-problem`): vergleicht eine bestehende `.repx` mit einer bestätigten Referenzdatei und wendet dokumentierte Korrekturanweisungen an.
- **Neuerstellungs-Typ** (Beispiel: `neuen-devexpress-listenreport-bauen`): baut aus Datenstruktur, Mockup und ggf. einer alten Query/Referenz eine komplett neue `.repx`.

Beide Typen teilen sich dieselben Pflichtbausteine (siehe unten) — nur "Schritte" und "Schlüsse" unterscheiden sich inhaltlich je nach Typ.

## Standing Rule: Übersicht zuerst

**Bevor ein neuer Skill inhaltlich geschrieben/gebaut wird**, muss Claude dem Nutzer immer zuerst eine kurze, leicht lesbare Übersicht geben — als Stichwortliste oder Inhaltsverzeichnis, ohne Detailtiefe:

- Skill-Name (Vorschlag) + Typ (Verbesserung/Neuerstellung)
- geplante Skill-ID (nächste freie Nummer aus `references/skill-id-registry.md`)
- Kurzbeschreibung der Trigger-Situation (wann soll der Skill anspringen?)
- grobe Gliederung der Schritte (Stichworte, keine Details)
- welche Referenzdateien geplant sind

Erst nach Bestätigung durch den Nutzer wird der Skill tatsächlich geschrieben. Diese Regel gilt für JEDEN neuen Skill, nicht nur für Skills, die mit diesem Meta-Skill selbst gebaut werden — sie ist ein permanenter Teil des Prozesses.

## Standing Rule: Rückfrage statt Annahme, kritische Prüfung statt Automatismus

Diese Regel gilt für **jeden** Report-Skill in diesem Plugin, bei **jedem** Schritt — nicht nur bei den unter Pflichtbaustein 3 beschriebenen Sicherheitsstufen für einzelne Feld-/Code-Änderungen, sondern auch für Prozessentscheidungen (z.B.: reicht die vorliegende Referenz wirklich aus? soll ein optionaler Schritt wie Skript-Hygiene laufen? ist eine Annahme über eine Datenbankstruktur wirklich abgesichert?):

- **Bei Unsicherheit wird immer nachgefragt, nie geraten oder halluziniert.** Nur bei 100%iger Sicherheit — d.h. eindeutig durch eine vorliegende Referenzdatei, Spezifikation oder Nutzeraussage belegt — darf eine Anpassung an Logik, Daten oder Struktur eigenständig vorgenommen werden. "Klingt plausibel" oder "ist in ähnlichen Reports üblich" reicht dafür nicht.
- **Kritisch prüfen, ob eine Anpassung überhaupt nötig ist, bevor sie vorgeschlagen wird.** Nicht jede technisch mögliche Änderung sollte gemacht werden, nur weil sie machbar ist — insbesondere bei Refactoring-artigen Vorschlägen (Skript-Hygiene, "sauberer" wirkende Alternativen) muss der tatsächliche Nutzen die Kosten (Regressionsrisiko, Review-Aufwand) rechtfertigen. Im Zweifel: nichts anfassen und stattdessen dem Nutzer die Beobachtung mitteilen.
- Diese Regel ersetzt nicht die dreistufige Einordnung aus Pflichtbaustein 3, sondern steht darüber: Sie gilt auch dort, wo Pflichtbaustein 3 keine explizite Stufe vorsieht (z.B. bei der Frage, ob überhaupt weitergemacht werden soll).

## Pflichtbausteine jedes Report-Skills

Jeder neue oder überarbeitete DevExpress-Report-Skill muss folgende Bausteine enthalten:

### 1. Frontmatter

```yaml
---
name: <skill-name>
description: <ausführliche Beschreibung inkl. Trigger-Formulierungen>
skill_id: DX<Autoren-Kürzel><4-stellige-Nummer>   # z.B. DXJ0001
version: <semver>                                  # z.B. 1.0.0
---
```

Details zu Skill-ID-Vergabe und Versionierung: siehe `references/skill-id-registry.md`.

### 2. Schritte (Steps)

Ein nummerierter Ablauf, typtypisch:

- **Verbesserungs-Typ**: Report entgegennehmen → Referenzdatei anfordern (Pflicht) → Befund melden vor Änderung → Fixes anwenden (nach Sicherheitsstufen, siehe unten) → Skript-Hygiene als separater Schritt → Validierung → Auslieferung mit Zeitstempel → Wissensdatenbank (`known-issues.md`) pflegen.
- **Neuerstellungs-Typ**: Mockup + Datenstruktur + Referenz-`.repx` entgegennehmen → Excel-Feldzuordnung erstellen und abstimmen → Query/Joins übernehmen → neue `.repx` bauen → Validierung → Auslieferung mit Zeitstempel.

### 3. Schlüsse / Entscheidungspunkte (Sicherheitsstufen)

Bevor eine Änderung überhaupt einer Stufe zugeordnet wird, steht die Frage aus der Standing Rule oben: **ist sie wirklich nötig?** Eine Änderung, die zwar korrekt und plausibel wäre, aber kein reales Problem löst oder keine gestellte Anforderung erfüllt, wird nicht vorgeschlagen — unabhängig davon, wie sicher sie technisch wäre.

Jede Änderung an einer bestehenden Datei (Verbesserungs-Typ) oder jede Annahme beim Neubau (Neuerstellungs-Typ), die diese Prüfung besteht, wird einer von drei Sicherheitsstufen zugeordnet:

1. **Automatisch sicher** — wird ohne Rückfrage angewendet, wenn eine bestätigte Referenz/Spezifikation eindeutig vorliegt.
2. **Vorschlag mit Rückfrage** — plausibel, aber nicht zweifelsfrei belegt; wird dem Nutzer zur Bestätigung vorgelegt, bevor es angewendet wird.
3. **Nur Verdacht / Platzhalter** — keine belastbare Quelle vorhanden (z.B. Feld ohne bestätigte DB-Zuordnung); wird sichtbar als Platzhalter markiert, niemals stillschweigend geraten.

### 4. Validierung

Eine skill-eigene `references/validierung-*.md` oder `validation-checklist.md` mit mindestens:

- XML-Wohlgeformtheit (`xml.etree.ElementTree.parse`)
- `Ref`-Eindeutigkeit + Auflösbarkeit aller `#Ref-x`-Verweise
- Base64-Datenquelle dekodiert und separat als XML geprüft
- alle `[Feldname]`-Expressions gegen `ResultSchema` abgeglichen
- BOM-Prüfung nach jedem Schreibschritt
- expliziter Hinweis: DevExpress-Designer-Laden + Testdaten-Rendering wird dadurch NICHT ersetzt und muss zusätzlich manuell erfolgen

### 5. Output-Konvention

Output ist immer eine neue `.repx`-Datei. Dateiname: `<Reportname>_<JJJJ-MM-TT>_<hh-mm>.repx`, Zeitstempel immer in Zeitzone Europe/Berlin erzeugen (Session-Umgebung läuft in UTC).

### 6. Dokumentation

- Ein "Änderungen dokumentiert"-Abschnitt bzw. eine `known-issues.md`, die neue Erkenntnisse, bekannte Grenzen und offene Punkte fortlaufend nummeriert festhält (für die spätere manuelle Code-Review durch den Nutzer).
- Bei jeder inhaltlichen Skill-Überarbeitung: Versionshistorie im Kopf des Skills oder in einer eigenen `CHANGELOG`-Notiz kurz vermerken (Version, Datum, was geändert wurde).

### 7. Skill-ID & Fix-Log

Vollständige Spezifikation: `references/fix-log-format.md`. Kurzfassung: jeder Skill bekommt eine Skill-ID (`references/skill-id-registry.md`), und jede Anwendung eines Verbesserungs-Skills auf eine `.repx` hinterlässt einen append-only Log-Eintrag ganz oben im eingebetteten C#-Skript der Datei.

### 8. Ablage-Konvention

Vollständiger Ablauf: `references/ablage-und-versionierung.md`. Kurzfassung: jeder neue oder geänderte Skill wird IMMER an zwei Orten ausgeliefert — als Cowork-Plugin-Paket (`SendUserFile`) und im lokalen GitHub-Repo `C:\GitHub\work4all-claude-skills\skills\...` (via Device-Bridge: stage → SendUserFile → `device_commit_files`, da für dieses Gerät kein `device_bash` verfügbar ist). Dazu liefert Claude immer eine fertige Commit-Message (Titel + Grund + Änderungen-Liste) im etablierten Stil des Nutzers.

**Umgebungs-Hinweis:** Steht in der aktuellen Session keine Device-Bridge zur Verfügung (z.B. normale Claude.ai-Chat-Umgebung ohne `SendUserFile`/`device_commit_files`), kann dieser Baustein nicht automatisch ausgeführt werden. In dem Fall gilt Pflichtbaustein 10 ("Nicht ausgeführte Teile melden"): Claude liefert die geänderten Dateien als herunterladbare Datei(en) plus die fertige Commit-Message, weist aber explizit darauf hin, dass die eigentliche Ablage an beiden Orten manuell durch den Nutzer (oder in einer späteren Cowork-Session mit Device-Zugriff) erfolgen muss.

### 9. Ausführungsprotokoll auch ohne Änderung

Jeder Verbesserungs-Typ-Skill hinterlässt bei **jeder abgeschlossenen Anwendung** einen Log-Eintrag im `work4all-log`-Block — nicht nur, wenn tatsächlich etwas geändert wurde. Vollständige Spezifikation inkl. der drei zulässigen Ergebnis-Werte (`geändert`, `keine Änderung nötig`, `abgebrochen: <Kurzgrund>`) und der genauen Abgrenzung, wann ein nicht zu Ende geführter Lauf überhaupt eine Zeile bekommt: `references/fix-log-format.md`, Regel 7.

Zweck: Ohne diesen Eintrag lässt sich aus der Datei allein nicht unterscheiden, ob ein Skill auf sie angewendet wurde und nichts fand, oder ob er nie angewendet wurde. Beides sieht ohne Protokoll identisch aus — genau das soll dieser Baustein verhindern.

### 10. Nicht ausgeführte Teile melden

Jeder Skill-Lauf schließt mit einem kurzen, expliziten Status ab, welche im Skill vorgesehenen Teile **nicht** ausgeführt wurden — unabhängig davon, ob der Grund harmlos ist (z.B. optionale Skript-Hygiene nicht angefragt) oder eine echte Lücke (z.B. Referenzdatei fehlte, ein Validierungsschritt konnte technisch nicht laufen, die Device-Bridge war nicht verfügbar). Für jeden übersprungenen Teil: **was** wurde übersprungen, **warum**, und was das für das weitere Vorgehen bedeutet — damit der Nutzer gezielt entscheiden kann, wie es weitergeht, statt eine Lücke erst später zufällig zu bemerken. Ein Lauf ohne jede Auslassung darf das kurz und positiv vermerken ("alle Schritte vollständig durchlaufen"); es muss keine leere Liste erzwungen werden.

## Versionierung dieses Meta-Skills

- v0.1.0 — Erstfassung: Bauplan mit den 8 Pflichtbausteinen, Übersicht-zuerst-Regel, Skill-ID-Format `DX<Kürzel><4-stellig>`.
- v0.2.0 — Standing Rule "Rückfrage statt Annahme, kritische Prüfung statt Automatismus" ergänzt (gilt übergreifend, nicht nur für Feld-/Code-Entscheidungen). Pflichtbaustein 3 verweist jetzt explizit auf die Notwendigkeitsprüfung vor der Stufen-Einordnung. Zwei neue Pflichtbausteine ergänzt: 9 "Ausführungsprotokoll auch ohne Änderung" (verweist auf `fix-log-format.md` v2 mit `<Ergebnis>`-Feld) und 10 "Nicht ausgeführte Teile melden". Pflichtbaustein 8 um einen Umgebungs-Hinweis ergänzt (Device-Bridge nicht überall verfügbar).
- v0.2.1 — Dokumentationskorrektur: Log-Block in `work4all-log` umbenannt (vorher `work4all-skill-log`), Versionskennzeichnung `(v2)` bleibt erhalten. Referenz auf die korrigierte Zeitstempel-Vorgabe (kein UTC-Offset) in `fix-log-format.md` ergänzt.

## Referenzdateien im Überblick

- `references/skill-id-registry.md` — Tabelle aller vergebenen Skill-IDs (Name, Autor, Datum, Version).
- `references/fix-log-format.md` — vollständige Spezifikation des `work4all-log`-Blocks, Schutzregel, Idempotenz-Check.
- `references/ablage-und-versionierung.md` — Ablauf für die doppelte Auslieferung (Cowork-Plugin + lokales GitHub-Repo), Versionsbump-Regeln, Commit-Message-Vorlage.
