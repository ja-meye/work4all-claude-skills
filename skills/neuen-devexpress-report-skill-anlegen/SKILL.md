---
name: neuen-devexpress-report-skill-anlegen
description: Legt einen neuen work4all-DevExpress-Report-Skill (Verbesserungs-Typ wie "fix-folgeseiten-uebertrag-problem" oder Neuerstellungs-Typ wie "neuen-devexpress-listenreport-bauen") strukturiert an und liefert ihn sowohl an das Cowork-Plugin als auch an das lokale GitHub-Repo C:\GitHub\work4all-claude-skills aus. Unbedingt verwenden, wenn der Nutzer einen neuen DevExpress-Skill anlegen, erweitern oder strukturieren möchte — auch bei kurzen Trigger-Sätzen wie "create new dx skill", "neuen DX Skill erstellen", "neuen Skill anlegen", "DX Skill Bauplan", "mach daraus einen skill" (im DevExpress/Report-Kontext), oder wenn der Nutzer nach Skill-ID, Versionierung, Fix-Log oder einer einheitlichen Struktur für Report-Skills fragt.
skill_id: DXJ0003
version: 0.1.0
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

- **Verbesserungs-Typ**: Report entgegennehmen → Referenzdatei anfordern (Pflicht) → Befund melden vor Änderung → Fixes anwenden (nach Sicherheitsstufen, siehe unten) → Skript-Hygiene als separater Schritt → Validierung → Auslieferung mit Zeitstempel → Wissensdatenbank (`known-issues.md`) pflegen.
- **Neuerstellungs-Typ**: Mockup + Datenstruktur + Referenz-`.repx` entgegennehmen → Excel-Feldzuordnung erstellen und abstimmen → Query/Joins übernehmen → neue `.repx` bauen → Validierung → Auslieferung mit Zeitstempel.

### 3. Schlüsse / Entscheidungspunkte (Sicherheitsstufen)

Jede Änderung an einer bestehenden Datei (Verbesserungs-Typ) oder jede Annahme beim Neubau (Neuerstellungs-Typ) wird einer von drei Sicherheitsstufen zugeordnet:

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

## Versionierung dieses Meta-Skills

- v0.1.0 — Erstfassung: Bauplan mit den 8 Pflichtbausteinen, Übersicht-zuerst-Regel, Skill-ID-Format `DX<Kürzel><4-stellig>`.

## Referenzdateien im Überblick

- `references/skill-id-registry.md` — Tabelle aller vergebenen Skill-IDs (Name, Autor, Datum, Version).
- `references/fix-log-format.md` — vollständige Spezifikation des `work4all-skill-log`-Blocks, Schutzregel, Idempotenz-Check.
- `references/ablage-und-versionierung.md` — Ablauf für die doppelte Auslieferung (Cowork-Plugin + lokales GitHub-Repo), Versionsbump-Regeln, Commit-Message-Vorlage.
