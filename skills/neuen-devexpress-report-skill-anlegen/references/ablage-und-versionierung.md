# Ablage & Versionierung

Verbindlicher Ablauf für jede Erstellung oder Änderung eines DevExpress-Report-Skills in diesem Plugin. Jeder neue oder geänderte Skill wird immer an **beiden** Orten ausgeliefert — Cowork-Plugin und lokales GitHub-Repo — nie nur an einem.

## Die zwei Ablageorte

1. **Cowork-Plugin** (`work4all-reporting-skills`) — hier lebt der Skill "aktiv" für die Cowork-Session; Auslieferung an den Nutzer erfolgt als gepacktes `.plugin`-Paket über `SendUserFile`.
2. **Lokales GitHub-Repo** — `C:\GitHub\work4all-claude-skills\skills\...` auf dem Windows-Rechner des Nutzers, für Team-Zugriff (Kollegen, spätere eigene Sessions) und Versionskontrolle via Git. Auslieferung über die Device-Bridge (stage → `SendUserFile` → `device_commit_files`), da für dieses Gerät kein `device_bash`-Tool verfügbar ist.

Hinweis zur Struktur: das lokale Repo besitzt aktuell nur eine `.claude-plugin/marketplace.json`, keine `plugin.json` — beim Sync ins lokale Repo wird also nur `marketplace.json` aktualisiert, keine `plugin.json` dort neu angelegt (außer der Nutzer bittet ausdrücklich darum).

## Ablauf Schritt für Schritt

1. **Skill-Dateien schreiben/ändern** in der Cowork-Plugin-Struktur (`skills/<skill-name>/SKILL.md` + `references/...`).
2. **Skill-ID-Registry aktualisieren** (`neuen-devexpress-report-skill-anlegen/references/skill-id-registry.md`) — neue Zeile bzw. Versionsspalte anpassen.
3. **`plugin.json` und `marketplace.json` (Cowork-Plugin) aktualisieren** — neuen Skill-Pfad in beide `skills`-Arrays eintragen.
4. **Validieren**: `claude plugin validate <pfad-zu-plugin.json>` ausführen, Warnungen/Fehler beheben.
5. **Cowork-Plugin packen** (`.plugin`-Zip) und per `SendUserFile` an den Nutzer ausliefern.
6. **Lokales Repo spiegeln**: für jede neue/geänderte Datei — via Device-Bridge staged/gesendet/committed:
   - neue/geänderte `SKILL.md`- und `references/*.md`-Dateien
   - aktualisierte `marketplace.json` (lokales Repo)
7. **Commit-Message vorschlagen** im etablierten Stil des Nutzers (siehe Vorlage unten) — Claude committet nicht selbst (kein `device_bash` verfügbar), sondern liefert Titel + Beschreibung zum manuellen Einfügen in GitHub Desktop / Git.

## Versionsbump-Regeln

`version:` im Frontmatter jedes Skills folgt Semver:

- **patch** (`x.y.Z`): kleine Korrektur, kein neues Verhalten (Tippfehler, Klarstellung, kleiner Bugfix im Skill-Text selbst).
- **minor** (`x.Y.0`): neue Fähigkeit/neuer Abschnitt, bestehendes Verhalten bleibt kompatibel (z.B. neues Muster als "automatisch sicher" eingestuft, neue Referenzdatei ergänzt).
- **major** (`X.0.0`): strukturelle Neufassung, die bestehende Abläufe grundlegend ändert (z.B. neuer Skill-Typ, komplett neue Schritt-Reihenfolge).

Bei jedem Versionsbump: `plugin.json` (Cowork, top-level `version`, falls vorhanden) im selben Zug mitziehen, und die Skill-ID-Registry-Zeile des betroffenen Skills auf die neue Version aktualisieren.

## Commit-Message-Vorlage (Stil des Nutzers)

```
Skill: <Kurztitel der Änderung>

<Grund-Absatz: was war der Anlass, welches Problem/welche Lücke wurde behoben>.

Änderungen:

- <Änderung 1>
- <Änderung 2>
  - <Unterpunkt, falls nötig>
- <Änderung 3>

<optionaler Abschlusssatz, z.B. Hinweis ob ein funktionaler Fix an einer
.repx enthalten ist oder es sich um reine Skill-/Dokumentationsarbeit handelt>.
```

Beobachtete Stilmerkmale (aus `.git/COMMIT_EDITMSG`): deutschsprachig, Titelzeile beginnt meist mit `Skill: `, Grund wird als Fließtext-Absatz erklärt (nicht als Liste), Änderungen als Bulletpunkte mit optionaler Verschachtelung, letzter Satz ordnet oft ein, ob ein funktionaler `.repx`-Fix enthalten war oder nicht.
