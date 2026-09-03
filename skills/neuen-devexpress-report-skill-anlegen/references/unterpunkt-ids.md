# Unterpunkt-IDs für Verbesserungs-Typ-Skills

Spezifikation zu Pflichtbaustein 11 (siehe `SKILL.md`). Ziel: der Nutzer soll vor jedem Lauf eines Verbesserungs-Skills auf einen Blick sehen, aus welchen einzelnen, benennbaren Fixes der Skill besteht — und gezielt einzelne davon abwählen können, ohne den ganzen Lauf abzusagen. Später sollen diese IDs außerdem als Grundlage für ein skillübergreifendes Inhaltsverzeichnis dienen (`skill-inhaltsverzeichnis`, `DXJ0004`).

## Format

```
<Skill-ID>.<Buchstabe>
```

Beispiel: `DXJ0001.F`. Der Skill-ID-Teil ist die bereits vergebene Skill-ID aus `skill-id-registry.md` — es wird **kein separates, zweites ID-Schema** eingeführt. Der Buchstabe ist ein einzelner Großbuchstabe, `A` beginnend, pro Skill fortlaufend.

## Was bekommt eine eigene ID?

Jedes **eigenständige, für sich benennbare Fix-Muster** eines Verbesserungs-Skills — in der Praxis meist deckungsgleich mit einem Eintrag im jeweiligen `fix-catalog.md` (oder einem gleichwertigen fachlichen Katalog). Nicht jeder kleine Validierungsschritt oder jede technische Detailregel bekommt eine eigene ID — nur, was der Nutzer sinnvoll einzeln an- oder abwählen könnte. Ob ein Baustein diese Schwelle erreicht, entscheidet Claude im Zweifel zugunsten von "eigene ID", nicht dagegen — eine ID zu viel ist harmlos, eine fehlende ID nimmt dem Nutzer eine mögliche Abwahl-Option.

## Vergabe- und Stabilitätsregeln

1. **Append-only, wie Skill-IDs selbst.** Einmal vergebene Buchstaben werden nie neu vergeben oder umsortiert, auch wenn sich die Reihenfolge im Fix-Katalog später ändert (z. B. ein neues Muster alphabetisch "dazwischen" passen würde). Neue Buchstaben werden immer als nächster freier Buchstabe angehängt.
2. **Ein als "ÜBERHOLT"/superseded markiertes Muster behält seine ID**, bekommt aber im entsprechenden `SKILL.md`-Abschnitt einen Verweis auf die ablösende ID, statt gelöscht zu werden — das alte Muster kann in älteren, noch nicht migrierten Reports weiterhin relevant sein (Wiedererkennung), auch wenn es nicht mehr aktiv empfohlen wird.
3. **Zusammengehörige Mini-Fixes können sich eine ID teilen**, wenn sie in der Praxis immer gemeinsam auftreten und einzeln keinen sinnvollen Abwahl-Fall ergeben (Beispiel: die Gesamtsummen-Rückfallbedingung und das Detailbereich-Gate-Flag lösen zusammen ein einziges, vom Nutzer so wahrgenommenes Symptom — "fehlende Summe/Übertrag auf vorgelagerten Seiten" — und teilen sich deshalb eine ID).

## Pflichtablauf bei Anwendung eines Verbesserungs-Skills

Erweitert Schritt 3 ("Befund an den Nutzer melden") des jeweiligen Fach-Skills:

1. Nach abgeschlossener Diagnose (Schritt 2) alle **zutreffenden** Unterpunkt-IDs kurz auflisten — Format `<ID>: <ein Satz Kurzbeschreibung>`. Nicht zutreffende Muster werden nicht aufgeführt (kein Rauschen).
2. Der Nutzer kann einzelne IDs explizit abwählen, bevor Fixes angewendet werden (Schritt 4). Ohne Rückmeldung gilt: alle aufgeführten IDs werden wie in ihrer jeweiligen Sicherheitsstufe vorgesehen behandelt (automatisch sicher → angewendet, Vorschrag mit Rückfrage → wie gehabt einzeln nachgefragt, nur Verdacht → wie gehabt nur dokumentiert).
3. **Abwahl wird protokolliert.** Jede vom Nutzer abgewählte ID wird im `work4all-log`-Eintrag dieses Laufs vermerkt (siehe `fix-log-format.md`, Feld `<Übersprungen>`) — unabhängig davon, ob der Lauf ansonsten als `geändert` oder `keine Änderung nötig` protokolliert wird. Grund: ein Kollege, der die Datei später ohne Chat-Verlauf öffnet, soll erkennen können, dass ein bekanntes Muster bewusst NICHT angewendet wurde, statt anzunehmen, es sei übersehen worden.

## Migration bestehender Skills

Bestehende Verbesserungs-Skills (aktuell: `fix-folgeseiten-uebertrag-problem`) bekommen ihre Unterpunkt-IDs rückwirkend zugeteilt, sobald sie das nächste Mal inhaltlich überarbeitet werden — nicht per Sammel-Nachtrag ohne inhaltlichen Anlass. Die Zuordnung steht dann im jeweiligen `SKILL.md` unter einer eigenen Überschrift „Unterpunkt-IDs".
