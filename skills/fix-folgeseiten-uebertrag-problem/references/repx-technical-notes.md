# Technischer Hintergrund: .repx-Dateiformat

## Dateiaufbau

Eine `.repx`-Datei ist XML, UTF-8 mit BOM (Byte Order Mark), mit CRLF (`\r\n`) als Zeilenende durchgehend in der ganzen Datei. Das eingebettete C#-Skript des Reports liegt als einziges großes Attribut `ScriptsSource` auf dem Root-Element `XtraReportsLayoutSerializer` — als HTML-Entity-escapeter Text. Innerhalb von `ScriptsSource` sind Zeilenumbrüche als `&#xD;&#xA;` kodiert (nicht nur `&#xA;`). Das ist eine Besonderheit dieses einen Attributs — andere mehrzeilige `Expression`-Attribute im Rest der Datei (z.B. Sichtbarkeits-Ausdrücke) verwenden nur `&#xA;`. Verwechsle die beiden nicht beim Escapen/Un-escapen.

**Verschachtelte Subreports haben eigene ScriptsSource-Attribute.** Ein Hauptreport kann `DetailReport`-Elemente enthalten (z.B. `DetailReport_SLKomponenten`, `DetailReport_Staffelpreise`, `Sub_Teilrechnungslogik_AN_AB`), die jeweils ihr eigenes, unabhängiges `ScriptsSource`-Attribut mit eigenem Methoden-Namensraum haben. Beim Prüfen, ob eine Methode "fehlt", immer zuerst feststellen, zu welchem `ScriptsSource`-Block eine `<Scripts>`-Referenz gehört — sonst produzierst du Fehlalarme.

## Sichere Bearbeitungs-Pipeline (Python)

1. Datei öffnen mit `encoding='utf-8-sig', newline=''` — das entfernt die BOM beim Lesen, lässt aber die CRLF-Sequenzen exakt im String stehen (kein automatisches Newline-Mapping). Das ist wichtig: mit Standard-Textmodus wird `\r\n` beim Lesen still zu `\n` normalisiert, wodurch jedes literale `\r\n`-Suchmuster stillschweigend nicht mehr matcht — ein Fehler, der leicht unbemerkt bleibt, weil kein Python-Fehler geworfen wird, nur 0 Treffer.
2. Den `ScriptsSource="..."`-Wert per Stringsuche extrahieren (siehe Abschnitt "Grenzmarkierungen" unten) und mit `html.unescape(...)` dekodieren, um lesbaren C#-Code zu bekommen.
3. Den Code normal mit einem Text-/Editier-Tool bearbeiten.
4. Beim Zurückschreiben in exakt dieser Reihenfolge escapen (Reihenfolge ist entscheidend, sonst entstehen doppelt/falsch escapte Zeichen):
   1. `&` → `&amp;` (muss zuerst passieren, sonst werden die `&` aus Schritt 2–4 selbst nochmal escaped)
   2. `<`, `>`, `"` escapen
   3. `\n` → `&#xD;&#xA;` (als Letztes)
5. Den re-escapten String zwischen den exakten Original-Grenzen zurücksplicen.
6. Datei schreiben mit `encoding='utf-8', newline=''` und die BOM (`'﻿'`) manuell vor den Inhalt setzen.

### Grenzmarkierungen für den Splice

Der Anfang ist `ScriptsSource="`. Als eindeutiger Endanker hat sich das Attribut `SnapGridSize="10"` bewährt, das (zumindest im ursprünglich bearbeiteten Report) genau einmal in der gesamten Datei vorkommt, direkt nach dem Ende von `ScriptsSource`. **Verifiziere das bei jeder neuen Report-Variante neu** (z.B. `content.count('SnapGridSize="10"')` sollte `1` sein) — verlass dich nicht blind darauf, dass es in jeder work4all-Report-Variante genauso ist. Falls der Anker nicht eindeutig ist, einen anderen eindeutigen Textblock suchen, der garantiert unmittelbar nach `ScriptsSource` folgt.

Berechne die Grenzen bei jedem Bearbeitungsschritt neu per direkter Stringsuche, statt gespeicherte Offsets aus einem früheren Lesevorgang wiederzuverwenden — Offsets verschieben sich bei jeder Änderung der Dateilänge, und ein stiller Off-by-N-Fehler produziert am Dateiende (oder -anfang) des gesplicten Blocks unbemerkten Datenmüll.

## DevExpress-Bandmodell (Kurzreferenz)

- `ReportHeaderBand` — einmalig am Dokumentanfang.
- `DetailBand` — pro Datensatz (hier: pro Position), kann verschachtelte `SubBand`s enthalten (z.B. `Sub_POS` für die Positionszeile).
- `PageHeaderBand` — wiederholt sich, kann aber durch `RepeatEveryPage`/Sichtbarkeits-Events gesteuert werden.
- `GroupHeaderBand` / `GroupFooterBand` mit `Level` — für Gruppierungen (z.B. pro Beleg bei Sammeldruck).
- Relevante Eigenschaften: `RepeatEveryPage` (Band auf jeder Seite wiederholen), `PrintAtBottom` (Band an den unteren Rand drucken statt im Fluss), `KeepTogether` (verhindert Aufsplittung eines Bands über einen Seitenumbruch — sofern der Inhalt überhaupt auf eine Seite passt; passt er nicht, splittet DevExpress trotzdem).

## `sumCarryoverSum([Feld])` — die "Carried Forward"-Summe

Eingebaute DevExpress-Summenfunktion (verfügbar ab v23.1) für Werte, die über eine Seite hinaus fortlaufend mitgeführt werden ("Übertrag"). Wird typischerweise an `RepeatEveryPage`-GroupHeader/GroupFooter-Bändern verwendet.

**Wichtige, in der offiziellen Doku so nicht klar dokumentierte Falle:** `sumCarryoverSum(...)` liefert nur dann tatsächlich einen Wert, wenn das Control zusätzlich ein `<Summary Running="Group" />`-XML-Element trägt. Ohne dieses Element bleibt das Feld leer, obwohl die Expression selbst syntaktisch korrekt aussieht und der Report anstandslos lädt — die Doku legt nahe, dass die Expression allein ausreicht, das stimmt in der Praxis nicht. Details und die konkrete Regressions-Geschichte dazu stehen in `known-issues.md`. Konsequenz für diese Skill: **`<Summary Running="Group">`-Elemente niemals automatisch entfernen**, selbst wenn sie auf den ersten Blick durch eine neuere Expression redundant aussehen.

## `BeforePrint` vs. `PrintOnPage`

- `BeforePrint` feuert während der Dokumentgenerierung, **vor** der finalen Paginierung. `e.PageIndex`/`e.PageCount` sind zu diesem Zeitpunkt nicht verlässlich.
- `PrintOnPage` feuert **nach** der Paginierung, mit verlässlichem `e.PageIndex`/`e.PageCount`. Das ist der richtige Ort für alles, was tatsächlich vom fertigen Seitenlayout abhängt (z.B. "ist dies die erste Seite, auf der eine bepreiste Position steht?").
- Setzt ein `BeforePrint`-Handler eines Eltern-Bands `e.Cancel = true` (oder `Visible = false`), feuert `PrintOnPage` der Kind-Controls in diesem Band **überhaupt nicht mehr**. Ein grober, globaler Zähler (z.B. `pageCounter`), der in einem `BeforePrint` benutzt wird, um pauschal "ab Seite X abschalten" zu entscheiden, sabotiert damit potenziell eine bereits vorhandene, präzisere `PrintOnPage`-Logik im selben Subband — das war die Ursache des ersten in dieser Skill-Familie behobenen Bugs. Siehe `fix-catalog.md`, Muster (a).

## XML/Skript-Paritätsregel

Jede `<Scripts On[Event]="MethodName" />`-Referenz im XML-Layout-Teil muss einer tatsächlich im zugehörigen `ScriptsSource` definierten Methode entsprechen. Fehlt sie, lädt der Report in DevExpress nicht mehr (oder zumindest nicht fehlerfrei). Nach jeder Methoden-Entfernung im Skript **immer symmetrisch die zugehörige XML-Verdrahtung anpassen** — siehe `validation-checklist.md`, Punkt 3 und 6.
