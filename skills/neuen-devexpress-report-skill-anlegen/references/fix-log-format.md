# work4all-log — Format-Spezifikation

Diese Datei ist die verbindliche Spezifikation für den Log-Block, den jeder **Verbesserungs-Typ**-Skill (z.B. `fix-folgeseiten-uebertrag-problem`) ganz oben im eingebetteten C#-Skript einer `.repx`-Datei hinterlässt. Ziel: Jens (und später Kollegen) können auf einen Blick nachvollziehen, welcher Skill in welcher Version wann auf eine Datei angewendet wurde — kryptisch genug, um den Skriptcode nicht aufzublähen, aber lesbar genug, um es ohne Nachschlagen zu verstehen.

## Blockformat

```
// === work4all-log (v3) ===
// <SkillID> | v<Version> | <Zeitstempel> | <Skill-Name> | <Ergebnis> | <Übersprungen>
// === end work4all-log ===
```

- `(v3)` in der Kopfzeile ist die Versionsnummer des Log-**Formats** selbst (nicht des Skills!) — falls das Format sich später ändert, wird hier hochgezählt und alte Blöcke bleiben lesbar. **Seit v2 gibt es das 5. Feld `<Ergebnis>`** (siehe unten) — Grund: v1 kannte nur den Fall "Fix wurde angewendet" und ließ offen, ob ein Skill lief, aber nichts zu tun fand. Das machte es unmöglich, zwischen "Skill wurde nie auf diese Datei angewendet" und "Skill wurde angewendet, fand aber keinen Änderungsbedarf" zu unterscheiden. **Seit v3 gibt es zusätzlich das 6. Feld `<Übersprungen>`** (siehe unten, gehört zu Meta-Skill-Baustein 11 „Unterpunkt-IDs") — Grund: ohne dieses Feld war nicht sichtbar, ob ein bekanntes Fix-Muster bewusst vom Nutzer abgewählt wurde, oder ob es schlicht nicht zutraf/übersehen wurde.
- Pro **abgeschlossener** Anwendung eines Skills genau eine Zeile (was "abgeschlossen" heißt, siehe Regel 7 unten). Mehrere Anwendungen (auch desselben Skills in unterschiedlichen Versionen, oder mehrerer verschiedener Fix-Skills) stehen als mehrere Zeilen **zwischen** der Kopf- und der Fußzeile, in der Reihenfolge ihrer Anwendung (älteste zuerst).
- `<SkillID>`: Format `DX<Kürzel><4-stellig>`, siehe `skill-id-registry.md`.
- `<Version>`: die Skill-Version zum Zeitpunkt der Anwendung (semver), nicht die Log-Format-Version.
- `<Zeitstempel>`: ISO8601-Format ohne Offset-Suffix, z.B. `2026-08-30T14:22:05` — die lokale Wanduhrzeit Europe/Berlin (Sommer- oder Winterzeit, je nachdem was gerade gilt), **ohne** angehängte `+02:00`/`+01:00`. Die Session-Umgebung läuft in UTC; daher wird der Zeitstempel niemals mit einem bloßen `date`-Aufruf erzeugt, sondern immer explizit mit `TZ=Europe/Berlin` (z.B. `TZ=Europe/Berlin date '+%Y-%m-%dT%H:%M:%S'` bzw. äquivalent in Python) — der Offset wird dabei bewusst nicht mit ausgegeben, um den Log-Eintrag knapp und auf den ersten Blick lesbar zu halten.
- `<Skill-Name>`: der Klarname des Skills (z.B. `fix-folgeseiten-uebertrag-problem`), damit der Block auch ohne Registry-Nachschlagen verständlich ist.
- `<Ergebnis>`: eines von genau drei kontrollierten Werten (kein Freitext, damit das Feld maschinell auswertbar bleibt):
  - **`geändert`** — mindestens eine Anpassung an der Datei wurde vorgenommen.
  - **`keine Änderung nötig`** — der Skill wurde vollständig durchlaufen (Diagnose/Prüfung abgeschlossen), es gab aber nichts zu beheben bzw. anzupassen.
  - **`abgebrochen: <Kurzgrund>`** — die inhaltliche Diagnose hat bereits begonnen, der Lauf konnte aber nicht zu Ende geführt werden (siehe Regel 7 für die genaue Abgrenzung, wann das überhaupt geloggt wird). `<Kurzgrund>` ist wenige Worte, z.B. `abgebrochen: Rückfrage unbeantwortet` oder `abgebrochen: Struktur weicht zu stark ab`.
- `<Übersprungen>` (seit v3, Feld 6): Komma-getrennte Liste der Unterpunkt-IDs (siehe `references/unterpunkt-ids.md`), die zwar zutrafen, aber auf ausdrücklichen Wunsch des Nutzers NICHT angewendet wurden — z.B. `Übersprungen: DXJ0001.C, DXJ0001.H`. Traf kein zutreffendes Muster zu oder wurde nichts abgewählt: Feld weglassen (nicht `Übersprungen: -` oder leer schreiben — ein fehlendes 6. Feld ist gleichbedeutend mit "nichts abgewählt", siehe Rückwärtskompatibilität unten).

## Beispiel (mehrere Anwendungen, gemischte Ergebnisse, eine mit Abwahl)

```
// === work4all-log (v3) ===
// DXJ0001 | v1.0.0 | 2026-08-28T16:03:11 | fix-folgeseiten-uebertrag-problem | geändert
// DXJ0001 | v1.1.0 | 2026-09-12T09:47:52 | fix-folgeseiten-uebertrag-problem | keine Änderung nötig
// DXJ0001 | v1.2.0 | 2026-09-20T11:15:40 | fix-folgeseiten-uebertrag-problem | geändert | Übersprungen: DXJ0001.C
// === end work4all-log ===
```

**Rückwärtskompatibilität zu v1/v2:** Bestehende v1-Zeilen (ohne 5. Feld) und v2-Zeilen (ohne 6. Feld) werden nicht nachträglich umgeschrieben — sie bleiben stehen, genau wie sie sind (Regel 1, Append-only, gilt uneingeschränkt auch für jedes Format-Upgrade). Eine v1-Zeile ohne `<Ergebnis>` wird beim Lesen als `geändert` interpretiert. Eine v2-Zeile ohne `<Übersprungen>` wird beim Lesen als "nichts abgewählt" interpretiert (nicht als "unbekannt"), da v2 noch keine Unterpunkt-IDs kannte. Trifft ein Skill auf einen bestehenden Block mit `(v1)`- oder `(v2)`-Kopfzeile, hängt er seine neue Zeile im jeweils aktuellen Format an **und hebt dabei die Kopfzeile auf das höchste im Block verwendete Format** (aktuell `(v3)`) — die Kopfzeile beschreibt damit immer das höchste verwendete Format, ein Block kann also unten alte v1-/v2-Zeilen und weiter unten neuere v3-Zeilen enthalten. Das ist beabsichtigt, kein Fehler.

## Überlebensfähigkeit bei einem Designer-Speichervorgang — Anker-Zeile (Pflicht seit 2026-09-03)

**Bestätigter Befund (Report `dxArticleList`, 03.09.2026):** Ein `work4all-log`-Block, der ausschließlich aus Kommentarzeilen besteht, wird vom DevExpress Report Designer beim Speichern vollständig aus der Datei entfernt — nicht nur geleert. Der Vorher/Nachher-Vergleich einer Datei, die nur diesen reinen Kommentarblock als `ScriptsSource` hatte, zeigte nach einem einzigen Speichervorgang im Designer: das komplette `ScriptsSource`-Attribut war weg, ebenso (ohne erkennbaren inhaltlichen Zusammenhang) das `ScriptLanguage`-Attribut. Alle anderen Attribute, Controls und Expression-Bindings blieben exakt gleich. Vermutete Ursache: Der Designer kompiliert `ScriptsSource` beim Laden/Speichern; ein reiner Kommentarblock kompiliert zu leerem Code, und beim Re-Serialisieren wird ein leeres Kompilat offenbar als "kein Skript vorhanden" behandelt und das Attribut ganz weggelassen. Verwandtes, aber älteres Phänomen: `fix-folgeseiten-uebertrag-problem/references/known-issues.md` Eintrag 3 (Designer-Re-Serialisierung kann Properties verwerfen, die er nicht als "im Designer gesetzt" erkennt) — hier trifft es aber nicht eine einzelne Property, sondern den gesamten Log-Mechanismus samt Audit-Historie.

**Mitigation (Sicherheitsstufe 2 — Vorschlag, NOCH NICHT durch einen echten Designer-Round-Trip verifiziert):** Direkt nach der `end work4all-log`-Fußzeile eine harmlose, syntaktisch echte C#-Anweisung ergänzen, die keine Wirkung hat, aber dafür sorgt, dass der kompilierte Code nicht leer ist:

```
// === work4all-log (v2) ===
// DXJ0002 | v1.1.1 | 2026-09-03T13:53:07 | neuen-devexpress-listenreport-bauen | geändert
// === end work4all-log ===
private static readonly string _work4allLogAnchor = "keep-scriptssource-alive";
```

- Die Anker-Zeile ist Teil des geschützten Blocks (siehe Regel 3 unten) — sie wird von keiner Hygiene-Routine entfernt und nicht mitgezählt als "toter Code".
- Sie trägt keine Nutzdaten und wird nie verändert — falls künftig eine bessere Absicherung gefunden wird, wird sie ersetzt, nicht ergänzt.
- **Migration bestehender Dateien:** Trifft ein Skill (gleich welcher Typ) beim Schreiben einer neuen Log-Zeile auf einen bestehenden Block, dem die Anker-Zeile fehlt (ältere, vor dem 03.09.2026 gebaute Dateien), ergänzt er sie im selben Arbeitsschritt direkt nach der Fußzeile — das ist keine eigene, im Log protokollierte "Änderung" im fachlichen Sinn, sondern eine stille technische Nachrüstung, analog zur Kopfzeilen-Anhebung bei einem Formatsprung (siehe Rückwärtskompatibilität oben).
- **Ausdrücklich als ungetestete Hypothese kennzeichnen, bis verifiziert:** Bei der nächsten Gelegenheit, bei der eine so geseedete Datei tatsächlich im DevExpress Report Designer geöffnet und gespeichert wird, prüfen: Ist `ScriptsSource` (inkl. Log-Block und Anker-Zeile) danach noch vorhanden? Ergebnis bitte hier und in `fix-folgeseiten-uebertrag-problem/references/known-issues.md` nachtragen — dieser Abschnitt wird dann von "Vorschlag" auf "bestätigt" (oder auf eine korrigierte Mitigation) aktualisiert.

## Regeln

1. **Append-only.** Ein Skill darf niemals eine bestehende Zeile löschen, verändern oder überschreiben — auch nicht seine eigene ältere Zeile. Neue Anwendung = neue Zeile, immer direkt vor der Fußzeile eingefügt.
2. **Vor Anwendung eines Fixes: Idempotenz-Check — nur relevant bei `geändert`.** Bevor ein Verbesserungs-Skill einen Fix anwendet, prüft er den bestehenden Log-Block: Ist die eigene Skill-ID bereits mit dem Ergebnis `geändert` und einer Version ≥ der aktuellen Skill-Version vorhanden? Falls ja, wird der Fix **nicht blind erneut angewendet** — stattdessen meldet Claude dies dem Nutzer ("Skill DXJ0001 v1.0.0 hat diese Datei laut Log bereits am ... geändert — soll ich trotzdem erneut prüfen/anwenden?") und wartet auf Bestätigung. Findet sich stattdessen nur eine frühere Zeile mit `keine Änderung nötig` oder `abgebrochen: ...`, greift der Idempotenz-Block **nicht** — es gibt in diesem Fall nichts, was "erneut angewendet" würde, also läuft die Diagnose ganz normal neu (die Datei könnte sich seither geändert haben, z.B. durch einen Designer-Speichervorgang).
3. **Schutz vor der Skript-Hygiene.** Die Skript-Hygiene-Aufräumroutine (siehe `fix-folgeseiten-uebertrag-problem`, Muster e) darf den `work4all-log`-Block **und die Anker-Zeile** (siehe oben) **niemals** entfernen, verschieben in der Reihenfolge der Zeilen verändern oder als "toter Kommentar"/"toter Code" behandeln. Jeder Skill, der eine Skript-Hygiene-Passage enthält, muss Block und Anker-Zeile explizit von der Bereinigung ausnehmen (z.B. per Regex-Ausschluss auf den Bereich zwischen den beiden `===`-Markierungszeilen zzgl. der unmittelbar folgenden Anker-Zeile).
4. **Position im Skript.** Block und Anker-Zeile stehen immer als allererstes im eingebetteten C#-Skript, vor jedem anderen Code oder Kommentar (auch vor einer eventuell vorhandenen `using`-Direktive-Sektion, sofern das Scripting-Modell das zulässt — sonst direkt nach den `using`-Direktiven, aber vor jedem Event-Handler).
5. **Neuerstellungs-Skills seeden den Block.** Ein Neuerstellungs-Skill (z.B. `neuen-devexpress-listenreport-bauen`) erzeugt beim ersten Bau einer neuen `.repx` bereits den vollständigen Kopf- und Fußzeilen-Rahmen mit genau einer Zeile für sich selbst **und der Anker-Zeile direkt danach** — damit jede neu gebaute Datei von Anfang an log-fähig UND designer-speicher-fest ist und spätere Verbesserungs-Skills nur noch anhängen müssen.
6. **Kein Ersatz für Dokumentation.** Der Log-Block ersetzt nicht die ausführliche Änderungsdokumentation (siehe Pflichtbaustein 6 "Dokumentation" im Haupt-Skill) — er ist eine kompakte, maschinenlesbare Ergänzung direkt in der Datei, für den Fall, dass die Datei ohne Begleitdokumentation weitergegeben wird.
7. **Wann ein abgebrochener Lauf eine Zeile bekommt — und wann nicht.** Nicht jeder nicht zu Ende geführte Lauf ist eine Log-Zeile wert; die Grenze liegt daran, ob schon inhaltlich an/mit der Datei gearbeitet wurde:
   - **Kein Eintrag**, wenn der Skill bereits in der Rohdaten-Extraktion/Struktur­erkennung (typischerweise Schritt 1 des jeweiligen Skills) abbricht — z.B. weil die Datei nicht zum erwarteten Reporttyp passt, nicht geöffnet/geparst werden konnte, oder der Nutzer den Lauf vor jeder inhaltlichen Prüfung zurückzieht. In diesem Fall wurde faktisch noch nichts auf die Datei angewendet; das gehört ausschließlich in den Chat-Bericht an den Nutzer (siehe Pflichtbaustein "Nicht ausgeführte Teile melden" im Haupt-Skill), nicht in die Datei.
   - **Ein Eintrag mit `abgebrochen: <Kurzgrund>`**, wenn die inhaltliche Diagnose (Schritt 2 o.ä.) bereits gelaufen ist — es also einen Befund gibt — der Lauf aber danach nicht mehr zu Ende geführt werden konnte (z.B. der Nutzer antwortet nicht mehr auf eine offene Rückfrage, die Session endet vorzeitig). Begründung: Hier hat eine echte Prüfung stattgefunden, deren Ergebnis sonst nirgends in der Datei selbst sichtbar wäre — ein Kollege, der die Datei später ohne den Chat-Verlauf öffnet, soll nicht denken, sie sei nie angefasst worden.
   - Im Zweifel, welcher der beiden Fälle vorliegt: Claude fragt beim Nutzer nach, statt selbst zu entscheiden — das betrifft in der Praxis eher seltene Grenzfälle.
8. **Anker-Zeile nachrüsten (seit 2026-09-03).** Jeder Skill, der eine neue Log-Zeile in einen bestehenden Block schreibt, prüft zuerst, ob die Anker-Zeile (siehe Abschnitt „Überlebensfähigkeit bei einem Designer-Speichervorgang" oben) unmittelbar nach der Fußzeile vorhanden ist. Fehlt sie, wird sie im selben Arbeitsschritt ergänzt — unabhängig davon, ob der eigentliche Skill-Lauf inhaltlich etwas an der Datei ändert oder nicht (diese Nachrüstung zählt nicht als eigene `<Ergebnis>`-Zeile, siehe oben).

## Warum dieses Format

- Kompakt genug, um den Skriptcode nicht spürbar aufzublähen (3+n Zeilen reiner Kommentar).
- Lesbar ohne Tool: Jens kann die Datei in DevExpress-Designer öffnen, den Skriptteil ansehen und sofort erkennen, was wann gemacht wurde.
- Maschinell auswertbar: ein einfaches Regex-Muster genügt, um den Block programmatisch zu parsen — nützlich, falls später ein Skill den Verlauf automatisiert auswerten soll:
  - v3-Zeilen (mit Ergebnis + optional Übersprungen): `^// (DX[A-Z]\d{4}) \| v([\d.]+) \| (\S+) \| ([^|]+) \| ([^|]+?)(?: \| Übersprungen: (.+))?$`
  - v2-Zeilen (mit Ergebnis, kein Übersprungen-Feld): `^// (DX[A-Z]\d{4}) \| v([\d.]+) \| (\S+) \| ([^|]+) \| (.+)$`
  - v1-Zeilen (ohne Ergebnis, Altbestand): `^// (DX[A-Z]\d{4}) \| v([\d.]+) \| (\S+) \| (.+)$` — matcht eine v1-Zeile aber auch fälschlich als v2-/v3-Zeile mit dem Skill-Namen im Ergebnis-Feld; ein Parser muss daher zuerst auf das v3-Muster, dann auf das v2-Muster prüfen und nur bei beidem Nichttreffer auf das v1-Muster zurückfallen, nicht umgekehrt.
