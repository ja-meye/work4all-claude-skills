---
name: neuen-devexpress-report-skill-anlegen
description: Legt einen neuen work4all-DevExpress-Report-Skill (Verbesserungs-Typ wie "fix-folgeseiten-uebertrag-problem" oder Neuerstellungs-Typ wie "neuen-devexpress-listenreport-bauen") strukturiert an und liefert ihn sowohl an das Cowork-Plugin als auch an das lokale GitHub-Repo C:\GitHub\work4all-claude-skills aus. Unbedingt verwenden, wenn der Nutzer einen neuen DevExpress-Skill anlegen, erweitern oder strukturieren möchte — auch bei kurzen Trigger-Sätzen wie "create new dx skill", "neuen DX Skill erstellen", "neuen Skill anlegen", "DX Skill Bauplan", "mach daraus einen skill" (im DevExpress/Report-Kontext), oder wenn der Nutzer nach Skill-ID, Versionierung, Fix-Log oder einer einheitlichen Struktur für Report-Skills fragt.
metadata:
  skill_id: DXJ0003
  version: 0.8.0
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

- **Verbesserungs-Typ**: Report entgegennehmen → Referenzdatei anfordern (Pflicht) → Befund melden vor Änderung → Fixes anwenden (nach Sicherheitsstufen, siehe unten) → Skript-Hygiene als separater Schritt → Validierung → **Auslieferung IMMER unter einem neuen, zeitgestempelten Dateinamen (Pflicht, siehe Baustein 9) — nie durch Überschreiben derselben Datei** → Wissensdatenbank (`known-issues.md`) pflegen.
- **Neuerstellungs-Typ**: Mockup + Datenstruktur + Referenz-`.repx` entgegennehmen → Excel-Feldzuordnung erstellen und abstimmen → Query/Joins übernehmen → neue `.repx` bauen → Validierung → Auslieferung mit Zeitstempel.

Beide Typen: Wird an einem Punkt des Ablaufs das eingebettete C#-Skript oder das rohe XML einer bestehenden `.repx` direkt gelesen oder verändert, ist vorher Baustein 10 (`references/repx-format-basics.md`) zu lesen — unabhängig vom fachlichen Thema des Skills.

### 3. Schlüsse / Entscheidungspunkte (Sicherheitsstufen)

Jede Änderung an einer bestehenden Datei (Verbesserungs-Typ) oder jede Annahme beim Neubau (Neuerstellungs-Typ) wird einer von drei Sicherheitsstufen zugeordnet:

1. **Automatisch sicher** — wird ohne Rückfrage angewendet, wenn eine bestätigte Referenz/Spezifikation eindeutig vorliegt.
2. **Vorschlag mit Rückfrage** — plausibel, aber nicht zweifelsfrei belegt; wird dem Nutzer zur Bestätigung vorgelegt, bevor es angewendet wird.
3. **Nur Verdacht / Platzhalter** — keine belastbare Quelle vorhanden (z.B. Feld ohne bestätigte DB-Zuordnung); wird sichtbar als Platzhalter markiert, niemals stillschweigend geraten.

### 4. Validierung

Verpflichtende Basis: **`references/validation-generic.md`** (dieser Meta-Skill) — die dort gelistete generische Checkliste (XML-Wohlgeformtheit, `Ref`-Eindeutigkeit + Auflösbarkeit aller `#Ref-x`-Verweise, Klammern-Balance, symmetrische Handler-Entfernung, BOM-Prüfung, Changelog-Format u. a.) gilt für **jede** `.repx`-Bearbeitung und wird nicht in jedem Fach-Skill neu geschrieben, sondern von dort referenziert.

Jeder Fach-Skill ergänzt diese Basis um eine eigene `references/validierung-*.md` oder `validation-checklist.md` mit den fachlich zusätzlichen Prüfpunkten, z. B.:

- Base64-Datenquelle dekodiert und separat als XML geprüft
- alle `[Feldname]`-Expressions gegen `ResultSchema` abgeglichen
- fachspezifische Invarianten (z. B. bestimmte `<Summary>`-Zählungen, die sich durch den Fix nicht ändern dürfen)

### 5. Output-Konvention

Output ist immer eine neue `.repx`-Datei. Dateiname: `<Reportname>_<JJJJ-MM-TT>_<hh-mm>.repx`, Zeitstempel immer in Zeitzone Europe/Berlin erzeugen (Session-Umgebung läuft in UTC).

### 6. Dokumentation

- Ein "Änderungen dokumentiert"-Abschnitt bzw. eine `known-issues.md`, die neue Erkenntnisse, bekannte Grenzen und offene Punkte fortlaufend nummeriert festhält (für die spätere manuelle Code-Review durch den Nutzer).
- Bei jeder inhaltlichen Skill-Überarbeitung: Versionshistorie im Kopf des Skills oder in einer eigenen `CHANGELOG`-Notiz kurz vermerken (Version, Datum, was geändert wurde).
- **Zwei-Wege-Kommentarregel (seit v0.5.1).** Kommentare im eingebetteten Skript haben in Referenz- und Live-Datei unterschiedliche Aufgaben und werden deshalb unterschiedlich behandelt:
  - **Referenzdatei:** Kommentare bleiben **vollständig** erhalten. Sie sind dort die eigentliche Dokumentation — sie erklären, warum eine Stelle so aussieht, und genau das braucht der nächste Lauf beim Strukturvergleich.
  - **Live-/Produktivdatei:** Kommentare **dürfen** gekürzt werden, aber nur als **eigener, ausdrücklich angeforderter Arbeitsschritt** — nie beiläufig innerhalb eines Fix-Laufs, und nie im selben Schritt wie eine inhaltliche Änderung (sonst ist im Diff nicht mehr trennbar, was Kürzung und was Fix war).
  - **Unantastbar in beiden Fällen:** der `work4all-log`-Block und die Anker-Zeile (`fix-log-format.md` Regeln 3 und 8).
  - **Konsequenz für den Referenz-Diff:** Sobald eine Live-Datei gekürzte Kommentare hat, wird der Vergleich gegen die Referenz **kommentar-unempfindlich** geführt (Kommentare vor dem Diff entfernen), sonst erzeugt die Kürzung Hunderte Scheinunterschiede und verdeckt echte Abweichungen.

### 7. Skill-ID & Fix-Log

Vollständige Spezifikation: `references/fix-log-format.md`. Kurzfassung: jeder Skill bekommt eine Skill-ID (`references/skill-id-registry.md`), und jede Anwendung eines Verbesserungs-Skills auf eine `.repx` hinterlässt einen append-only Log-Eintrag ganz oben im eingebetteten C#-Skript der Datei.

### 8. Ablage-Konvention

Vollständiger Ablauf: `references/ablage-und-versionierung.md`. Kurzfassung: jeder neue oder geänderte Skill wird IMMER an zwei Orten ausgeliefert — als Cowork-Plugin-Paket (`SendUserFile`) und im lokalen GitHub-Repo `C:\GitHub\work4all-claude-skills\skills\...` (via Device-Bridge: stage → SendUserFile → `device_commit_files`, da für dieses Gerät kein `device_bash` verfügbar ist). Dazu liefert Claude immer eine fertige Commit-Message (Titel + Grund + Änderungen-Liste) im etablierten Stil des Nutzers.

### 9. Auslieferung immer unter neuem Zeitstempel-Dateinamen — kein separates Backup mehr nötig

**Neuer Standard ab v0.8.0 (löst die bisherige separate Backup-Pflicht ab):** Jeder Skill, der eine **bestehende** `.repx`-Datei verändert (Verbesserungs-Typ; beim Neuerstellungs-Typ nur relevant, falls ausnahmsweise auf einer bestehenden Datei aufgebaut wird), liefert das Ergebnis **grundsätzlich als eine neue Datei mit neuem Zeitstempel im Dateinamen** aus (Format bereits in Baustein 5 „Output-Konvention" festgelegt: `<Reportname>_<JJJJ-MM-TT>_<hh-mm>.repx`) — **niemals durch Überschreiben der Originaldatei unter demselben Namen.**

Der Grund für die frühere separate Sicherungskopie (`<Reportname>_backup_<JJJJMMTT-hhmm>.repx`) entfällt damit: Wenn jede Auslieferung ohnehin einen eigenen, neuen Zeitstempel im Dateinamen trägt, IST die vorherige Version — unter ihrem eigenen, älteren Zeitstempel — bereits automatisch die Sicherungskopie. Ein zusätzliches, separates `_backup_...`-File wäre nur eine redundante dritte Kopie desselben Zustands und wird deshalb **nicht mehr** automatisch angelegt.

**Ausnahme — explizites Überschreiben auf Nutzerwunsch:** Nur wenn der Nutzer ausdrücklich verlangt, dieselbe Datei unter demselben Namen in-place zu überschreiben (z. B. weil ein externes System exakt diesen Dateinamen referenziert), UND dabei explizit KEINEN neuen Dateinamen wünscht, wird stattdessen vor dieser einen In-Place-Änderung automatisch — ohne separate Rückfrage — eine Sicherungskopie nach dem alten Schema angelegt:

```
<Reportname>_backup_<JJJJMMTT-hhmm>.repx
```

Das ist die einzige Situation, in der noch ein separates Backup-File entsteht — sie ist die Ausnahme, nicht der Regelfall.

Diese Ausliefer-Konvention ist keine der drei Sicherheitsstufen aus Baustein 3 (sie ist keine fachliche Änderungsentscheidung), sondern eine reine, immer ausgeführte Vorsichtsmaßnahme.

Hintergrund: Die ursprüngliche Backup-Pflicht (v0.2.0) entstand aus einer bereits projektweit geltenden Arbeitsweise-Vorgabe. In der praktischen Anwendung (Report `dxAio_template`, mehrere iterative Diagnoserunden am 03.–04.09.2026) hat sich gezeigt, dass eine separate Backup-Datei bei ohnehin durchgängig zeitgestempelten Auslieferungsnamen keinen zusätzlichen Schutz bietet, aber zusätzliche, leicht verwechselbare Dateien im Zielverzeichnis erzeugt. Der Nutzer hat daraufhin ausdrücklich verlangt, künftig grundsätzlich eine neue, zeitgestempelte Datei statt eines In-Place-Überschreibens auszuliefern, gerade damit kein separates Backup mehr nötig ist.

### 10. Gemeinsame .repx-Technik-Basis

Jeder Skill, der das eingebettete C#-Skript oder das rohe XML einer `.repx` direkt liest oder verändert — unabhängig vom fachlichen Thema —, **muss** vor der ersten Bearbeitung **`references/repx-format-basics.md`** (dieser Meta-Skill) lesen. Diese Datei enthält die format-technische Grundmechanik, die für alle diese Skills identisch gilt: Encoding/BOM/CRLF, die Escaping-/Splice-Pipeline, das DevExpress-Bandmodell, `BeforePrint` vs. `PrintOnPage`, die XML/Skript-Paritätsregel, den `<Localization>`-Block und die `<Summary>`-Falle.

Ein neuer Fach-Skill schreibt diese Mechanik **nicht erneut** in eine eigene Referenzdatei, sondern referenziert `repx-format-basics.md` und ergänzt in seiner eigenen Referenz nur das, was tatsächlich fachlich neu/spezifisch ist (z. B. die konkrete Übertrag-/Folgeseiten-Anwendung dieser Mechanik). Ziel: dieselbe Falle wird nicht in jedem neuen Skill unabhängig neu entdeckt, übersehen oder anders (und ggf. falsch) beschrieben.

Bestehende Skills, deren eigene Referenz diese Mechanik bereits vollständig enthält (z. B. `fix-folgeseiten-uebertrag-problem/references/repx-technical-notes.md`), werden dadurch nicht automatisch geändert — der Verweis auf die zentrale Basis gilt ab v0.2.0 für neu angelegte oder inhaltlich überarbeitete Skills.

### 11. Unterpunkt-IDs für Verbesserungs-Typ-Skills

Vollständige Spezifikation: `references/unterpunkt-ids.md`. Kurzfassung: Jedes eigenständige Fix-Muster eines Verbesserungs-Typ-Skills bekommt zusätzlich zur Skill-ID eine eigene Unterpunkt-ID (`<Skill-ID>.<Buchstabe>`, z. B. `DXJ0001.F`). Vor Anwendung eines Fixes (erweitert Schritt „Befund melden") zeigt Claude dem Nutzer alle zutreffenden IDs mit je einem Satz Kurzbeschreibung — der Nutzer kann einzelne davon gezielt abwählen, ohne den ganzen Lauf abzusagen. Eine Abwahl wird verpflichtend im `work4all-log`-Eintrag vermerkt (Feld `<Übersprungen>`, siehe `references/fix-log-format.md` v3).

Grund für diesen Baustein: Diese IDs sind die Grundlage für ein skillübergreifendes Inhaltsverzeichnis (siehe Dokumentations-Typ-Skill `skill-inhaltsverzeichnis`, `DXJ0004`), das dem Nutzer einen Gesamtüberblick über alle behobenen Einzelprobleme gibt, ohne jedes `fix-catalog.md` einzeln lesen zu müssen.

**Dritter Skill-Typ ab hier:** Neben Verbesserungs- und Neuerstellungs-Typ gibt es seit `DXJ0004` einen **Dokumentations-Typ** (Beispiel: `skill-inhaltsverzeichnis`) — kein Report-Fix-Skill im eigentlichen Sinn, sondern ein Skill, der bestehendes Skill-Wissen (hier: alle Unterpunkt-IDs) für den Nutzer aufbereitet. Pflichtbausteine 1, 6, 7 und 8 gelten auch für diesen Typ; Bausteine 2 (Schritte), 3 (Sicherheitsstufen), 5 (Output-Konvention: `.repx`) und 9/10 (repx-spezifisch) sind für ihn nicht einschlägig, da er keine `.repx`-Dateien liest oder verändert.

### 12. Spec-Konformität (offizielle Agent-Skills-Vorgaben)

Jeder Skill dieses Plugins hält die offiziellen Vorgaben ein. Sie sind nicht kosmetisch: Verstöße gegen die ersten vier führen dazu, dass ein Upload abgelehnt wird oder der Skill gar nicht erst gefunden wird.

| Regel | Vorgabe |
|----|----|
| Frontmatter-Keys | Nur `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. **Eigene Felder wie `skill_id` und `version` gehören unter `metadata:`** — als Top-Level-Key werden sie beim claude.ai-Upload und beim Packaging als „unexpected key" abgelehnt. |
| `name` | Kleinbuchstaben/Ziffern/Bindestriche, max. 64 Zeichen, ohne „claude"/„anthropic". |
| `description` | Max. 1.024 Zeichen, dritte Person, nennt **was** der Skill tut **und wann** er greift; wichtigster Anwendungsfall zuerst. |
| SKILL.md-Umfang | Max. 500 Zeilen — und darüber hinaus knapp halten: die Datei wird bei **jedem** Trigger vollständig geladen. Details gehören in `references/`, die nur bei Bedarf gelesen werden. |
| Referenz-Tiefe | Verweise aus `SKILL.md` gehen **eine Ebene tief**; skillübergreifende Verweise mit vollständigem relativem Pfad (`../<anderer-skill>/references/...`), sonst zeigt der Pfad ins Leere. |
| Referenzdateien >100 Zeilen | Bekommen ein `## Inhalt`-Verzeichnis, damit beim Anlesen der volle Umfang sichtbar ist. |
| Skript-Aufrufe | Immer mit `${CLAUDE_SKILL_DIR}` dokumentieren — ein relativer Pfad bricht, sobald das Arbeitsverzeichnis ein anderes ist. |
| Pfadtrenner | Nur Forward-Slashes in skill-internen Pfaden. |
| Evaluations | Mindestens drei Szenarien je Verbesserungs-Skill, abgeleitet aus real aufgetretenen Fehlerfällen, in `evals/`. |
| Eine Quelle je Information | Dieselbe Aussage steht an **einer** Stelle. Wo eine Kopie unvermeidbar ist (z. B. das Inhaltsverzeichnis in `DXJ0004`), wird sie maschinell gegen die Quelle geprüft. Prosa-Zusammenfassungen, die einen Katalog oder eine Tabelle nacherzählen, werden nicht angelegt — sie laufen erfahrungsgemäß auseinander und widersprechen dann der verbindlichen Stelle. |
| SKILL.md-Umfang | Die Datei darf so ausführlich sein, wie der Ablauf es braucht: **Qualität geht vor Token-Zahl.** Gemeldet wird nur unkontrolliertes Wachstum, nicht jede Überschreitung eines Richtwerts. |

**Automatisierte Prüfung:** `python3 "${CLAUDE_SKILL_DIR}/scripts/lint_skills.py"` prüft alle Skills des Plugins gegen diese Regeln (`S01`–`S12`, Exit-Code 1 bei FAIL) — darunter `S11` (Unterpunkt-IDs stimmen über alle Dateien überein) und `S12` (Versionsangaben stimmen über Frontmatter, Registry und Inhaltsverzeichnis überein). Vor jedem Ausliefern eines geänderten Skills laufen lassen — analog zu `validate_repx.py` bei Report-Dateien.

## Versionierung dieses Meta-Skills

- v0.8.0 — Baustein 9 grundlegend geändert (Nutzerwunsch nach Abschluss der Diagnose-Reihe am Report `dxAio_template`, 04.09.2026): Die bisherige Pflicht, vor jeder Änderung automatisch ein separates `<Reportname>_backup_<JJJJMMTT-hhmm>.repx` anzulegen, entfällt als Regelfall. Neuer Standard: jede Auslieferung erfolgt grundsätzlich unter einem neuen, zeitgestempelten Dateinamen (bereits in Baustein 5 festgelegtes Format) statt durch Überschreiben der Originaldatei — die jeweils vorherige, unter ihrem eigenen Zeitstempel erhalten bleibende Version übernimmt dadurch automatisch die Rolle der Sicherungskopie, ein zusätzliches separates Backup-File ist überflüssig. Die alte Backup-Konvention bleibt als Ausnahme bestehen, ausschließlich wenn der Nutzer ausdrücklich ein In-Place-Überschreiben derselben Datei unter demselben Namen verlangt. Baustein 2 (Schritte, Verbesserungs-Typ) entsprechend angepasst: der bisherige erste Schritt „Backup mit Zeitstempel anlegen" ist entfallen, die Auslieferung mit neuem Zeitstempel ist jetzt explizit als Pflicht markiert. Zusätzlich `references/repx-format-basics.md` (Baustein 10, Abschnitt „Der `<Localization>`-Block") um die am selben Report bestätigte, themenneutrale Erkenntnis ergänzt, dass der Override-Mechanismus auch für `Visible` gilt, nicht nur für Höhen-/Größen-/Positions-Properties — Details und die fachspezifische Ausprägung in `fix-folgeseiten-uebertrag-problem` (`DXJ0001` v1.8.0).
- v0.1.0 — Erstfassung: Bauplan mit den 8 Pflichtbausteinen, Übersicht-zuerst-Regel, Skill-ID-Format `DX<Kürzel><4-stellig>`.
- v0.2.0 — Zwei fehlende, wiederkehrend benötigte Bausteine ergänzt, damit künftige Korrektur-Skills keine bereits gelösten Probleme erneut lösen oder Regeln vergessen: Baustein 9 (Backup-Pflicht vor jeder Änderung, bisher nur Projekt-Instruction, jetzt Skill-Pflichtbaustein) und Baustein 10 (gemeinsame, themenneutrale `.repx`-Technik-Basis in `references/repx-format-basics.md`, damit Encoding-/Escaping-/Bandmodell-Wissen nicht pro Skill dupliziert wird). Baustein 4 (Validierung) verweist jetzt auf eine neue generische Basis-Checkliste (`references/validation-generic.md`), die jeder Fach-Skill um eigene Punkte ergänzt statt sie neu zu schreiben.
- v0.2.1 — Fehlerkorrektur in `repx-format-basics.md`, Bearbeitungs-Pipeline Schritt 4.3: Zeilenenden werden jetzt explizit auf reines `\n` normalisiert, BEVOR `\n` → `&#xD;&#xA;` kodiert wird — sonst blieb bei jedem Zeilenumbruch im gesamten Skript ein rohes `\r` stehen (sichtbar als Leerzeile nach jeder Zeile, siehe `fix-folgeseiten-uebertrag-problem/references/known-issues.md` Eintrag 13). Neuer Pflicht-Validierungspunkt 12 in `references/validation-generic.md` ergänzt. Stale Verweise auf `work4all-skill-log` auf den aktuellen Blocknamen `work4all-log` korrigiert.
- v0.3.0 — Neuer Baustein 11 (Unterpunkt-IDs für Verbesserungs-Typ-Skills, `references/unterpunkt-ids.md`): jedes eigenständige Fix-Muster bekommt eine ID (`<Skill-ID>.<Buchstabe>`), wird dem Nutzer vor Anwendung zur gezielten Abwahl gezeigt, Abwahl wird im `work4all-log` vermerkt. Dazu `fix-log-format.md` auf `(v3)` erweitert (neues Feld `<Übersprungen>`, rückwärtskompatibel zu v1/v2). Dritter Skill-Typ „Dokumentations-Typ" eingeführt (Beispiel: `skill-inhaltsverzeichnis`, `DXJ0004`) — nutzt Skill-IDs und Unterpunkt-IDs, aber keine `.repx`-spezifischen Bausteine.
- v0.7.0 — Baustein 12 um zwei Regeln erweitert, die aus einem Selbst-Check hervorgingen: **„Eine Quelle je Information"** (unvermeidbare Kopien werden maschinell gegen die Quelle geprüft, Prosa-Nacherzählungen von Katalogen werden nicht angelegt) und die ausdrückliche Klarstellung, dass **Qualität vor Token-Zahl** geht — der Umfangs-Check meldet nur noch unkontrolliertes Wachstum. Neue Checks `S11` (Unterpunkt-ID-Konsistenz) und `S12` (Versionskonsistenz) in `scripts/lint_skills.py`. Anlass: In `DXJ0001` beschrieb eine Prosa-Zusammenfassung die Skript-Hygiene noch als optional, während der Ablauf derselben Datei sie als Pflicht führte, und die Versionsangabe im Inhaltsverzeichnis war zum zweiten Mal veraltet — beides fand der Linter, nicht ein Mensch.
- v0.6.0 — Neuer Baustein 12 (Spec-Konformität) plus `scripts/lint_skills.py` (`S01`–`S10`): die offiziellen Agent-Skills-Vorgaben sind jetzt Teil des Bauplans und maschinell prüfbar. Anlass war ein Abgleich mit der offiziellen Dokumentation, der zwei harte Verstöße im Bestand fand: `skill_id`/`version` standen als Top-Level-Frontmatter-Keys (beim claude.ai-Upload als „unexpected key" abgelehnt — jetzt unter `metadata:`), und mehrere `SKILL.md` verwiesen auf `references/fix-log-format.md` bzw. `references/unterpunkt-ids.md`, die in **diesem** Skill liegen, nicht im verweisenden — die Pfade zeigten ins Leere und sind jetzt vollständig relativ. Dazu: Inhaltsverzeichnisse in allen Referenzdateien >100 Zeilen, Skript-Aufrufe über `${CLAUDE_SKILL_DIR}`, und die Versionshistorie von DXJ0001 aus der `SKILL.md` in `../fix-folgeseiten-uebertrag-problem/references/skill-changelog.md` ausgelagert (Progressive Disclosure, rund 1.800 Tokens weniger pro Trigger).
- v0.5.1 — Baustein 6 (Dokumentation) um die Zwei-Wege-Kommentarregel ergänzt: die Referenzdatei behält ihre vollständigen Begründungs-Kommentare, die produktive Live-Datei darf gekürzte Kommentare haben; die Kürzung ist ein eigener, ausdrücklich angeforderter Arbeitsschritt und nie Teil eines Fix-Laufs. Konsequenz für den Referenz-Diff: kommentar-unempfindlich vergleichen. Stale Verweise (`C01`–`C16`, „vier Fehlerklassen") korrigiert.
- v0.5.0 — Baustein 4 (Validierung) um einen **ausführbaren Check-Index** erweitert: `validation-generic.md` bekommt die generischen Pflichtpunkte 13–16 (lückenlose `ItemN`-Nummerierung; dokumentweite Phasentrennung BeforePrint/PrintOnPage; layout-relevante Eigenschaften nur in BeforePrint; element-gescopte Prüfungen statt Zählungen) und verweist auf das lauffähige Skript `fix-folgeseiten-uebertrag-problem/scripts/validate_repx.py` (Checks `C01`–`C18`), das nach jeder Bearbeitungsrunde und zusätzlich als Selbst-Audit auf der Referenzdatei zu laufen hat. `repx-format-basics.md` um zwei Abschnitte ergänzt (`ItemN`-Mechanik, dokumentweite Phasentrennung). Anlass: Sitzung 03./04.09.2026 am Report `dxAio_template`, in der fünf Fehlerklassen nacheinander erst durch den Kunden im Designer/Testdruck gefunden wurden, obwohl alle bis dahin bestehenden Checks grün waren — Details in `fix-folgeseiten-uebertrag-problem/references/known-issues.md` Einträge 22–28.
- v0.4.0 — `references/fix-log-format.md` um neuen Abschnitt „Überlebensfähigkeit bei einem Designer-Speichervorgang" ergänzt: bestätigter Befund (Report `dxArticleList`, 03.09.2026), dass ein rein aus Kommentaren bestehender `work4all-log`-Block beim Speichern aus dem DevExpress Report Designer restlos aus der Datei verschwindet (`ScriptsSource`/`ScriptLanguage`-Attribute werden entfernt, nicht nur geleert). Neue, noch unverifizierte Mitigation: eine harmlose Anker-Zeile (`private static readonly string _work4allLogAnchor = ...`) direkt nach der Log-Fußzeile, damit der kompilierte Skript-Code nicht leer ist. Neue Regel 8 (Anker-Zeile bei fehlender Anker-Zeile in Altdateien nachrüsten), Regeln 3–5 entsprechend ergänzt. Betroffene Skills `fix-folgeseiten-uebertrag-problem` (DXJ0001) und `neuen-devexpress-listenreport-bauen` (DXJ0002) im selben Zug aktualisiert.

## Referenzdateien im Überblick

- `references/skill-id-registry.md` — Tabelle aller vergebenen Skill-IDs (Name, Autor, Datum, Version).
- `references/fix-log-format.md` — vollständige Spezifikation des `work4all-log`-Blocks, Schutzregel, Idempotenz-Check.
- `references/ablage-und-versionierung.md` — Ablauf für die doppelte Auslieferung (Cowork-Plugin + lokales GitHub-Repo), Versionsbump-Regeln, Commit-Message-Vorlage.
- `references/repx-format-basics.md` — themenneutrale `.repx`-Technik-Basis (Encoding, Escaping/Splice-Pipeline, Bandmodell, `Localization`-Block, bekannte generische Fallen). Pflichtlektüre vor jeder direkten Skript-/XML-Bearbeitung (Baustein 10).
- `references/validation-generic.md` — generische Validierungs-Mindestcheckliste für jede `.repx`-Bearbeitung (Baustein 4).
- `references/unterpunkt-ids.md` — Format, Vergabe- und Stabilitätsregeln für Unterpunkt-IDs (Baustein 11).
- `scripts/lint_skills.py` — prüft alle Skills des Plugins gegen die offiziellen Spec-Vorgaben (Baustein 12).
