# work4all-log — Format-Spezifikation

Diese Datei ist die verbindliche Spezifikation für den Log-Block, den jeder **Verbesserungs-Typ**-Skill (z.B. `fix-folgeseiten-uebertrag-problem`) ganz oben im eingebetteten C#-Skript einer `.repx`-Datei hinterlässt. Ziel: Jens (und später Kollegen) können auf einen Blick nachvollziehen, welcher Skill in welcher Version wann auf eine Datei angewendet wurde — kryptisch genug, um den Skriptcode nicht aufzublähen, aber lesbar genug, um es ohne Nachschlagen zu verstehen.

## Blockformat

```
// === work4all-log (v2) ===
// <SkillID> | v<Version> | <Zeitstempel> | <Skill-Name> | <Ergebnis>
// === end work4all-log ===
```

- `(v2)` in der Kopfzeile ist die Versionsnummer des Log-**Formats** selbst (nicht des Skills!) — falls das Format sich später ändert, wird hier hochgezählt und alte Blöcke bleiben lesbar. **Seit v2 gibt es das 5. Feld `<Ergebnis>`** (siehe unten) — Grund: v1 kannte nur den Fall "Fix wurde angewendet" und ließ offen, ob ein Skill lief, aber nichts zu tun fand. Das machte es unmöglich, zwischen "Skill wurde nie auf diese Datei angewendet" und "Skill wurde angewendet, fand aber keinen Änderungsbedarf" zu unterscheiden — genau das soll dieser Block eigentlich belegen können.
- Pro **abgeschlossener** Anwendung eines Skills genau eine Zeile (was "abgeschlossen" heißt, siehe Regel 7 unten). Mehrere Anwendungen (auch desselben Skills in unterschiedlichen Versionen, oder mehrerer verschiedener Fix-Skills) stehen als mehrere Zeilen **zwischen** der Kopf- und der Fußzeile, in der Reihenfolge ihrer Anwendung (älteste zuerst).
- `<SkillID>`: Format `DX<Kürzel><4-stellig>`, siehe `skill-id-registry.md`.
- `<Version>`: die Skill-Version zum Zeitpunkt der Anwendung (semver), nicht die Log-Format-Version.
- `<Zeitstempel>`: ISO8601-Format ohne Offset-Suffix, z.B. `2026-08-30T14:22:05` — die lokale Wanduhrzeit Europe/Berlin (Sommer- oder Winterzeit, je nachdem was gerade gilt), **ohne** angehängte `+02:00`/`+01:00`. Die Session-Umgebung läuft in UTC; daher wird der Zeitstempel niemals mit einem bloßen `date`-Aufruf erzeugt, sondern immer explizit mit `TZ=Europe/Berlin` (z.B. `TZ=Europe/Berlin date '+%Y-%m-%dT%H:%M:%S'` bzw. äquivalent in Python) — der Offset wird dabei bewusst nicht mit ausgegeben, um den Log-Eintrag knapp und auf den ersten Blick lesbar zu halten.
- `<Skill-Name>`: der Klarname des Skills (z.B. `fix-folgeseiten-uebertrag-problem`), damit der Block auch ohne Registry-Nachschlagen verständlich ist.
- `<Ergebnis>`: eines von genau drei kontrollierten Werten (kein Freitext, damit das Feld maschinell auswertbar bleibt):
  - **`geändert`** — mindestens eine Anpassung an der Datei wurde vorgenommen.
  - **`keine Änderung nötig`** — der Skill wurde vollständig durchlaufen (Diagnose/Prüfung abgeschlossen), es gab aber nichts zu beheben bzw. anzupassen.
  - **`abgebrochen: <Kurzgrund>`** — die inhaltliche Diagnose hat bereits begonnen, der Lauf konnte aber nicht zu Ende geführt werden (siehe Regel 7 für die genaue Abgrenzung, wann das überhaupt geloggt wird). `<Kurzgrund>` ist wenige Worte, z.B. `abgebrochen: Rückfrage unbeantwortet` oder `abgebrochen: Struktur weicht zu stark ab`.

## Beispiel (mehrere Anwendungen, gemischte Ergebnisse)

```
// === work4all-log (v2) ===
// DXJ0001 | v1.0.0 | 2026-08-28T16:03:11 | fix-folgeseiten-uebertrag-problem | geändert
// DXJ0001 | v1.1.0 | 2026-09-12T09:47:52 | fix-folgeseiten-uebertrag-problem | keine Änderung nötig
// === end work4all-log ===
```

**Rückwärtskompatibilität zu v1:** Bestehende v1-Zeilen (ohne 5. Feld) werden nicht nachträglich umgeschrieben — sie bleiben stehen, genau wie sie sind (Regel 1, Append-only, gilt uneingeschränkt auch für das Format-Upgrade). Eine v1-Zeile ohne `<Ergebnis>` wird beim Lesen als `geändert` interpretiert, da das v1-Format ausschließlich für tatsächliche Fixes vorgesehen war. Trifft ein Skill auf einen bestehenden Block mit `(v1)`-Kopfzeile, hängt er seine neue Zeile im v2-Format (mit `<Ergebnis>`) an **und hebt dabei die Kopfzeile auf `(v2)`** — die Kopfzeile beschreibt damit immer das höchste in diesem Block verwendete Format, ein Block kann also unten alte v1-Zeilen und weiter unten neuere v2-Zeilen enthalten. Das ist beabsichtigt, kein Fehler.

## Regeln

1. **Append-only.** Ein Skill darf niemals eine bestehende Zeile löschen, verändern oder überschreiben — auch nicht seine eigene ältere Zeile. Neue Anwendung = neue Zeile, immer direkt vor der Fußzeile eingefügt.
2. **Vor Anwendung eines Fixes: Idempotenz-Check — nur relevant bei `geändert`.** Bevor ein Verbesserungs-Skill einen Fix anwendet, prüft er den bestehenden Log-Block: Ist die eigene Skill-ID bereits mit dem Ergebnis `geändert` und einer Version ≥ der aktuellen Skill-Version vorhanden? Falls ja, wird der Fix **nicht blind erneut angewendet** — stattdessen meldet Claude dies dem Nutzer ("Skill DXJ0001 v1.0.0 hat diese Datei laut Log bereits am ... geändert — soll ich trotzdem erneut prüfen/anwenden?") und wartet auf Bestätigung. Findet sich stattdessen nur eine frühere Zeile mit `keine Änderung nötig` oder `abgebrochen: ...`, greift der Idempotenz-Block **nicht** — es gibt in diesem Fall nichts, was "erneut angewendet" würde, also läuft die Diagnose ganz normal neu (die Datei könnte sich seither geändert haben, z.B. durch einen Designer-Speichervorgang).
3. **Schutz vor der Skript-Hygiene.** Die Skript-Hygiene-Aufräumroutine (siehe `fix-folgeseiten-uebertrag-problem`, Muster e) darf den `work4all-log`-Block **niemals** entfernen, verschieben in der Reihenfolge der Zeilen verändern oder als "toter Kommentar" behandeln. Jeder Skill, der eine Skript-Hygiene-Passage enthält, muss diesen Block explizit von der Bereinigung ausnehmen (z.B. per Regex-Ausschluss auf den Bereich zwischen den beiden `===`-Markierungszeilen).
4. **Position im Skript.** Der Block steht immer als allererstes im eingebetteten C#-Skript, vor jedem anderen Code oder Kommentar (auch vor einer eventuell vorhandenen `using`-Direktive-Sektion, sofern das Scripting-Modell das zulässt — sonst direkt nach den `using`-Direktiven, aber vor jedem Event-Handler).
5. **Neuerstellungs-Skills seeden den Block.** Ein Neuerstellungs-Skill (z.B. `neuen-devexpress-listenreport-bauen`) erzeugt beim ersten Bau einer neuen `.repx` bereits den vollständigen Kopf- und Fußzeilen-Rahmen mit genau einer Zeile für sich selbst — damit jede neu gebaute Datei von Anfang an log-fähig ist und spätere Verbesserungs-Skills nur noch anhängen müssen.
6. **Kein Ersatz für Dokumentation.** Der Log-Block ersetzt nicht die ausführliche Änderungsdokumentation (siehe Pflichtbaustein 6 "Dokumentation" im Haupt-Skill) — er ist eine kompakte, maschinenlesbare Ergänzung direkt in der Datei, für den Fall, dass die Datei ohne Begleitdokumentation weitergegeben wird.
7. **Wann ein abgebrochener Lauf eine Zeile bekommt — und wann nicht.** Nicht jeder nicht zu Ende geführte Lauf ist eine Log-Zeile wert; die Grenze liegt daran, ob schon inhaltlich an/mit der Datei gearbeitet wurde:
   - **Kein Eintrag**, wenn der Skill bereits in der Rohdaten-Extraktion/Struktur­erkennung (typischerweise Schritt 1 des jeweiligen Skills) abbricht — z.B. weil die Datei nicht zum erwarteten Reporttyp passt, nicht geöffnet/geparst werden konnte, oder der Nutzer den Lauf vor jeder inhaltlichen Prüfung zurückzieht. In diesem Fall wurde faktisch noch nichts auf die Datei angewendet; das gehört ausschließlich in den Chat-Bericht an den Nutzer (siehe Pflichtbaustein "Nicht ausgeführte Teile melden" im Haupt-Skill), nicht in die Datei.
   - **Ein Eintrag mit `abgebrochen: <Kurzgrund>`**, wenn die inhaltliche Diagnose (Schritt 2 o.ä.) bereits gelaufen ist — es also einen Befund gibt — der Lauf aber danach nicht mehr zu Ende geführt werden konnte (z.B. der Nutzer antwortet nicht mehr auf eine offene Rückfrage, die Session endet vorzeitig). Begründung: Hier hat eine echte Prüfung stattgefunden, deren Ergebnis sonst nirgends in der Datei selbst sichtbar wäre — ein Kollege, der die Datei später ohne den Chat-Verlauf öffnet, soll nicht denken, sie sei nie angefasst worden.
   - Im Zweifel, welcher der beiden Fälle vorliegt: Claude fragt beim Nutzer nach, statt selbst zu entscheiden — das betrifft in der Praxis eher seltene Grenzfälle.

## Warum dieses Format

- Kompakt genug, um den Skriptcode nicht spürbar aufzublähen (3+n Zeilen reiner Kommentar).
- Lesbar ohne Tool: Jens kann die Datei in DevExpress-Designer öffnen, den Skriptteil ansehen und sofort erkennen, was wann gemacht wurde.
- Maschinell auswertbar: ein einfaches Regex-Muster genügt, um den Block programmatisch zu parsen — nützlich, falls später ein Skill den Verlauf automatisiert auswerten soll:
  - v2-Zeilen (mit Ergebnis): `^// (DX[A-Z]\d{4}) \| v([\d.]+) \| (\S+) \| ([^|]+) \| (.+)$`
  - v1-Zeilen (ohne Ergebnis, Altbestand): `^// (DX[A-Z]\d{4}) \| v([\d.]+) \| (\S+) \| (.+)$` — matcht eine v1-Zeile aber auch fälschlich als v2-Zeile mit dem Skill-Namen im Ergebnis-Feld; ein Parser muss daher zuerst auf das v2-Muster prüfen und nur bei Nichttreffer auf das v1-Muster zurückfallen, nicht umgekehrt.
