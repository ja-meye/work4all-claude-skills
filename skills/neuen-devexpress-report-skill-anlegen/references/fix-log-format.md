# work4all-skill-log — Format-Spezifikation

Diese Datei ist die verbindliche Spezifikation für den Log-Block, den jeder **Verbesserungs-Typ**-Skill (z.B. `fix-folgeseiten-uebertrag-problem`) ganz oben im eingebetteten C#-Skript einer `.repx`-Datei hinterlässt. Ziel: Jens (und später Kollegen) können auf einen Blick nachvollziehen, welcher Skill in welcher Version wann auf eine Datei angewendet wurde — kryptisch genug, um den Skriptcode nicht aufzublähen, aber lesbar genug, um es ohne Nachschlagen zu verstehen.

## Blockformat

```
// === work4all-skill-log (v1) ===
// <SkillID> | v<Version> | <ISO8601-Zeitstempel mit Offset> | <Skill-Name>
// === end work4all-skill-log ===
```

- `(v1)` in der Kopfzeile ist die Versionsnummer des Log-**Formats** selbst (nicht des Skills!) — falls das Format sich später ändert, wird hier hochgezählt und alte Blöcke bleiben lesbar.
- Pro Anwendung eines Skills genau eine Zeile. Mehrere Anwendungen (auch desselben Skills in unterschiedlichen Versionen, oder mehrerer verschiedener Fix-Skills) stehen als mehrere Zeilen **zwischen** der Kopf- und der Fußzeile, in der Reihenfolge ihrer Anwendung (älteste zuerst).
- `<SkillID>`: Format `DX<Kürzel><4-stellig>`, siehe `skill-id-registry.md`.
- `<Version>`: die Skill-Version zum Zeitpunkt der Anwendung (semver), nicht die Log-Format-Version.
- `<ISO8601-Zeitstempel mit Offset>`: z.B. `2026-08-30T14:22:05+02:00` (Europe/Berlin inkl. Sommer-/Winterzeit-Offset — niemals UTC ohne Offset, da die Session-Umgebung in UTC läuft und das sonst zu Verwirrung führt).
- `<Skill-Name>`: der Klarname des Skills (z.B. `fix-folgeseiten-uebertrag-problem`), damit der Block auch ohne Registry-Nachschlagen verständlich ist.

## Beispiel (mehrere Anwendungen)

```
// === work4all-skill-log (v1) ===
// DXJ0001 | v1.0.0 | 2026-08-28T16:03:11+02:00 | fix-folgeseiten-uebertrag-problem
// DXJ0001 | v1.1.0 | 2026-09-12T09:47:52+02:00 | fix-folgeseiten-uebertrag-problem
// === end work4all-skill-log ===
```

## Regeln

1. **Append-only.** Ein Skill darf niemals eine bestehende Zeile löschen, verändern oder überschreiben — auch nicht seine eigene ältere Zeile. Neue Anwendung = neue Zeile, immer direkt vor der Fußzeile eingefügt.
2. **Vor Anwendung eines Fixes: Idempotenz-Check.** Bevor ein Verbesserungs-Skill einen Fix anwendet, prüft er den bestehenden Log-Block: Ist die eigene Skill-ID bereits mit einer Version ≥ der aktuellen Skill-Version vorhanden? Falls ja, wird der Fix **nicht blind erneut angewendet** — stattdessen meldet Claude dies dem Nutzer ("Skill DXJ0001 v1.0.0 wurde laut Log bereits am ... angewendet — soll ich trotzdem erneut prüfen/anwenden?") und wartet auf Bestätigung.
3. **Schutz vor der Skript-Hygiene.** Die Skript-Hygiene-Aufräumroutine (siehe `fix-folgeseiten-uebertrag-problem`, Muster e) darf den `work4all-skill-log`-Block **niemals** entfernen, verschieben in der Reihenfolge der Zeilen verändern oder als "toter Kommentar" behandeln. Jeder Skill, der eine Skript-Hygiene-Passage enthält, muss diesen Block explizit von der Bereinigung ausnehmen (z.B. per Regex-Ausschluss auf den Bereich zwischen den beiden `===`-Markierungszeilen).
4. **Position im Skript.** Der Block steht immer als allererstes im eingebetteten C#-Skript, vor jedem anderen Code oder Kommentar (auch vor einer eventuell vorhandenen `using`-Direktive-Sektion, sofern das Scripting-Modell das zulässt — sonst direkt nach den `using`-Direktiven, aber vor jedem Event-Handler).
5. **Neuerstellungs-Skills seeden den Block.** Ein Neuerstellungs-Skill (z.B. `neuen-devexpress-listenreport-bauen`) erzeugt beim ersten Bau einer neuen `.repx` bereits den vollständigen Kopf- und Fußzeilen-Rahmen mit genau einer Zeile für sich selbst — damit jede neu gebaute Datei von Anfang an log-fähig ist und spätere Verbesserungs-Skills nur noch anhängen müssen.
6. **Kein Ersatz für Dokumentation.** Der Log-Block ersetzt nicht die ausführliche Änderungsdokumentation (siehe Pflichtbaustein 6 "Dokumentation" im Haupt-Skill) — er ist eine kompakte, maschinenlesbare Ergänzung direkt in der Datei, für den Fall, dass die Datei ohne Begleitdokumentation weitergegeben wird.

## Warum dieses Format

- Kompakt genug, um den Skriptcode nicht spürbar aufzublähen (3+n Zeilen reiner Kommentar).
- Lesbar ohne Tool: Jens kann die Datei in DevExpress-Designer öffnen, den Skriptteil ansehen und sofort erkennen, was wann gemacht wurde.
- Maschinell auswertbar: ein einfaches Regex-Muster (`^// (DX[A-Z]\d{4}) \| v([\d.]+) \| (\S+) \| (.+)$`) genügt, um den Block programmatisch zu parsen — nützlich, falls später ein Skill den Verlauf automatisiert auswerten soll.
