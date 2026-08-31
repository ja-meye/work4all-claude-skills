# .repx-Format — technische Basis (für alle Korrektur-Skills)

## Zweck

Diese Datei bündelt die generische `.repx`-Dateiformat-Mechanik, die für **jeden** Skill gilt, der eine bestehende `.repx`-Datei liest, ihr eingebettetes C#-Skript bearbeitet oder ihr rohes XML verändert — unabhängig vom fachlichen Thema des jeweiligen Fixes. Jeder Korrektur-Skill (Verbesserungs-Typ) **muss** diese Datei vor der ersten inhaltlichen `.repx`-Bearbeitung lesen, statt die Mechanik neu zu erarbeiten, aus dem Gedächtnis zu rekonstruieren oder unabhängig zu duplizieren. So wird eine einmal gefundene Falle (z. B. der `<Localization>`-Block, die Escaping-Reihenfolge) nicht in jedem neuen Skill erneut übersehen.

Fachlich-spezifisches Wissen (z. B. die Übertrag-/Folgeseiten-Logik, konkrete Bug-Muster) gehört weiterhin in die Referenzdateien des jeweiligen Fach-Skills, nicht hierher. Diese Datei bleibt bewusst themenneutral.

## Dateiaufbau

Eine `.repx`-Datei ist XML, UTF-8 mit BOM (Byte Order Mark), mit CRLF (`\r\n`) als Zeilenende durchgehend in der ganzen Datei. Das eingebettete C#-Skript des Reports liegt als einziges großes Attribut `ScriptsSource` auf dem Root-Element `XtraReportsLayoutSerializer` — als HTML-Entity-escapeter Text. Innerhalb von `ScriptsSource` sind Zeilenumbrüche als `&#xD;&#xA;` kodiert (nicht nur `&#xA;`). Das ist eine Besonderheit dieses einen Attributs — andere mehrzeilige `Expression`-Attribute im Rest der Datei (z. B. Sichtbarkeits-Ausdrücke) verwenden nur `&#xA;`. Verwechsle die beiden nicht beim Escapen/Un-escapen.

**Verschachtelte Subreports haben eigene `ScriptsSource`-Attribute.** Ein Hauptreport kann `DetailReport`-Elemente enthalten (z. B. `DetailReport_SLKomponenten`, `DetailReport_Staffelpreise`, `Sub_Teilrechnungslogik_AN_AB`), die jeweils ihr eigenes, unabhängiges `ScriptsSource`-Attribut mit eigenem Methoden-Namensraum haben. Beim Prüfen, ob eine Methode „fehlt", immer zuerst feststellen, zu welchem `ScriptsSource`-Block eine `<Scripts>`-Referenz gehört — sonst entstehen Fehlalarme.

## Sichere Bearbeitungs-Pipeline (Python)

1. Datei öffnen mit `encoding='utf-8-sig', newline=''` — das entfernt die BOM beim Lesen, lässt aber die CRLF-Sequenzen exakt im String stehen (kein automatisches Newline-Mapping). Wichtig: im Standard-Textmodus wird `\r\n` beim Lesen still zu `\n` normalisiert, wodurch jedes literale `\r\n`-Suchmuster unbemerkt nicht mehr matcht — ein Fehler ohne Python-Exception, nur 0 Treffer.
2. Den `ScriptsSource="..."`-Wert per Stringsuche extrahieren (siehe „Grenzmarkierungen" unten) und mit `html.unescape(...)` dekodieren, um lesbaren C#-Code zu bekommen. **Wichtig:** Danach enthält der String an jedem Zeilenumbruch ein echtes `\r\n` (CR+LF), keine reinen `\n` — entscheidend für Schritt 4.
3. Den Code normal mit einem Text-/Editier-Tool bearbeiten. Eigene neu eingefügte Zeilen können mit reinem `\n` geschrieben werden — die Normalisierung in Schritt 4.3 vereinheitlicht ohnehin alles.
4. Beim Zurückschreiben in exakt dieser Reihenfolge escapen (Reihenfolge ist entscheidend, sonst entstehen doppelt/falsch escapte Zeichen):
   1. `&` → `&amp;` (muss zuerst passieren, sonst werden `&`-Zeichen aus den folgenden Schritten selbst nochmal escaped)
   2. `<`, `>`, `"` escapen
   3. **Zeilenenden normalisieren, bevor kodiert wird:** zuerst `\r\n` → `\n` und verbleibende einzelne `\r` → `\n` vereinheitlichen, danach erst `\n` → `&#xD;&#xA;`. **Bekannter Fehler, wenn dieser Normalisierungsschritt fehlt:** Direktes `\n` → `&#xD;&#xA;` auf dem noch `\r\n`-haltigen String aus Schritt 2 lässt das `\r` jeder Zeile als rohes, nicht escapetes Zeichen vor dem neuen `&#xD;&#xA;` stehen — das erzeugt bei JEDEM Zeilenumbruch im gesamten Skript eine zusätzliche Leerzeile, sichtbar erst beim Öffnen des dekodierten Skripts (im rohen XML-Diff leicht zu übersehen, da die Datei trotzdem wohlgeformt bleibt und lädt). Siehe `fix-folgeseiten-uebertrag-problem/references/known-issues.md` für den konkreten Vorfall.
5. Den re-escapten String zwischen den exakten Original-Grenzen zurücksplicen.
6. Datei schreiben mit `encoding='utf-8', newline=''` und die BOM (`'﻿'`) manuell vor den Inhalt setzen.
7. **Validierung (PFLICHT):** Im rohen, noch escapten `ScriptsSource`-Attributwert prüfen, dass keine literalen `\r`- oder `\n`-Zeichen mehr vorkommen — nur noch `&#xD;&#xA;`-Entities.

### Grenzmarkierungen für den Splice

Der Anfang ist `ScriptsSource="`. Als Endanker eignet sich ein Attribut, das garantiert eindeutig und unmittelbar nach dem Ende von `ScriptsSource` folgt (in bisher bearbeiteten Reports z. B. `SnapGridSize="10"`). **Verifiziere den gewählten Anker bei jeder neuen Report-Variante neu** (z. B. `content.count('SnapGridSize="10"')` sollte `1` sein) — verlass dich nicht blind darauf, dass er in jeder work4all-Report-Variante gleich eindeutig ist. Falls nicht eindeutig, einen anderen garantiert eindeutigen Textblock direkt nach `ScriptsSource` suchen.

Berechne die Grenzen bei jedem Bearbeitungsschritt neu per direkter Stringsuche, statt gespeicherte Offsets aus einem früheren Lesevorgang wiederzuverwenden — Offsets verschieben sich bei jeder Änderung der Dateilänge, und ein stiller Off-by-N-Fehler produziert am Dateiende (oder -anfang) des gesplicten Blocks unbemerkten Datenmüll.

## DevExpress-Bandmodell (Kurzreferenz)

- `ReportHeaderBand` — einmalig am Dokumentanfang.
- `DetailBand` — pro Datensatz (z. B. pro Position), kann verschachtelte `SubBand`s enthalten.
- `PageHeaderBand` — wiederholt sich, kann aber durch `RepeatEveryPage`/Sichtbarkeits-Events gesteuert werden.
- `GroupHeaderBand` / `GroupFooterBand` mit `Level` — für Gruppierungen (z. B. pro Beleg bei Sammeldruck).
- Relevante Eigenschaften: `RepeatEveryPage` (Band auf jeder Seite wiederholen), `PrintAtBottom` (Band an den unteren Rand drucken statt im Fluss), `KeepTogether` (verhindert Aufsplittung eines Bands über einen Seitenumbruch — sofern der Inhalt überhaupt auf eine Seite passt; passt er nicht, splittet DevExpress trotzdem).

## `BeforePrint` vs. `PrintOnPage`

- `BeforePrint` feuert während der Dokumentgenerierung, **vor** der finalen Paginierung. `e.PageIndex`/`e.PageCount` sind zu diesem Zeitpunkt nicht verlässlich.
- `PrintOnPage` feuert **nach** der Paginierung, mit verlässlichem `e.PageIndex`/`e.PageCount`. Das ist der richtige Ort für alles, was tatsächlich vom fertigen Seitenlayout abhängt.
- Setzt ein `BeforePrint`-Handler eines Eltern-Bands `e.Cancel = true` (oder `Visible = false`), feuert `PrintOnPage` der Kind-Controls in diesem Band **überhaupt nicht mehr**. Ein grober, globaler Zähler, der in einem `BeforePrint` pauschal „ab Seite X abschalten" entscheidet, kann damit eine bereits vorhandene, präzisere `PrintOnPage`-Logik im selben Subband sabotieren.

## XML/Skript-Paritätsregel

Jede `<Scripts On[Event]="MethodName" />`-Referenz im XML-Layout-Teil muss einer tatsächlich im zugehörigen `ScriptsSource` definierten Methode entsprechen. Fehlt sie, lädt der Report in DevExpress nicht mehr (oder zumindest nicht fehlerfrei). Nach jeder Methoden-Entfernung im Skript **immer symmetrisch die zugehörige XML-Verdrahtung anpassen** — siehe `references/validation-generic.md`, Punkte 3 und 5.

## Der `<Localization>`-Block — indirekte Speicherung von Designer-Werten

Nicht jede im DevExpress-Designer manuell geänderte Eigenschaft landet als direktes XML-Attribut auf dem betroffenen Element. Insbesondere `HeightF`, `SizeF`, `LocationFloat` und teils `Visible` werden häufig stattdessen indirekt in einem separaten `<Localization>`-Element weiter oben in der Datei abgelegt, als Liste von Einträgen der Form:

```xml
<Item354 Ref="2991" Component="#Ref-1931" Culture="Default" Path="HeightF" Data="40" />
```

`Component="#Ref-N"` verweist über die `Ref`-Nummer auf das eigentliche Ziel-Element (Band, Table, Control, …); `Path` ist der Eigenschaftsname; `Data` der aktuell gesetzte Wert. `Culture` ist meist `Default`, kann bei mehrsprachigen Reports aber auch `en`/`fr`/`nl` sein — dann existieren ggf. mehrere Einträge für denselben `Component`-Ref mit unterschiedlicher `Culture`, die unabhängig voneinander gepflegt werden müssen.

**Praktische Konsequenz** bei jeder Höhen-/Größen-/Positions-Änderung, die per Diff gegen eine im Designer bearbeitete Datei nachvollzogen werden soll:

1. Zuerst das Ziel-Element selbst auf ein direktes Attribut prüfen (`HeightF="..."`, `SizeF="..."`, etc.).
2. Zusätzlich immer nach `Component="#Ref-<RefDesElements>"` im gesamten Dokument suchen — dort kann der eigentlich wirksame (oder überschreibende) Wert stehen, unabhängig vom direkten Attribut.
3. Beim eigenen Setzen einer neuen Höhe entsprechend nicht nur das Element-Attribut setzen, sondern auch prüfen/setzen, ob ein passender `<Localization>`-Eintrag existiert bzw. angelegt werden muss.

Ein reiner Element-für-Element-Vergleich der vermuteten Stelle kann diese Änderungen komplett übersehen (weil weder vorher noch nachher ein direktes Attribut existiert) — zuverlässiger ist ein vollständiger, positionsweiser Baumvergleich der gesamten Datei (alle Elemente in Dokumentreihenfolge, `Ref`-Werte beim Vergleich ignorieren), der solche indirekten Änderungen automatisch mit erfasst.

## Bekannte generische Falle: `<Summary Running="...">`-Elemente

DevExpress-Summenfunktionen, die über eine Seite hinaus fortlaufend Werte mitführen (z. B. `sumCarryoverSum(...)`, verfügbar ab v23.1), liefern häufig nur dann tatsächlich einen Wert, wenn das Control zusätzlich ein passendes `<Summary Running="..." />`-XML-Element trägt — auch wenn die offizielle DevExpress-Doku das nicht klar herausstellt und die Expression allein syntaktisch korrekt aussieht und der Report anstandslos lädt. **Konsequenz: `<Summary>`-Elemente niemals automatisch entfernen, nur weil sie auf den ersten Blick durch eine neuere Expression redundant aussehen** — das hat in der Praxis bereits zu einer stillen Regression geführt (leeres Feld statt Fehler). Die konkrete Übertrag-spezifische Ausprägung dieser Falle inkl. Regressions-Geschichte steht in `fix-folgeseiten-uebertrag-problem/references/known-issues.md`.

## Verweis auf fachspezifische Vertiefung

Für die themenspezifische Anwendung dieser Mechanik (z. B. Übertrag-/Folgeseiten-Muster) siehe die Referenzdateien des jeweiligen Fach-Skills, z. B. `fix-folgeseiten-uebertrag-problem/references/repx-technical-notes.md` und `fix-catalog.md`. Diese Datei hier wird bei neuen Erkenntnissen nur ergänzt, wenn die Erkenntnis wirklich themenneutral/generisch ist — fachspezifische Funde gehören in die Referenz des jeweiligen Fach-Skills.
