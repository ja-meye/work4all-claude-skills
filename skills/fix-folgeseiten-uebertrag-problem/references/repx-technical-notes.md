# Technischer Hintergrund: .repx-Dateiformat

## Dateiaufbau

Eine `.repx`-Datei ist XML, UTF-8 mit BOM (Byte Order Mark), mit CRLF (`\r\n`) als Zeilenende durchgehend in der ganzen Datei. Das eingebettete C#-Skript des Reports liegt als einziges großes Attribut `ScriptsSource` auf dem Root-Element `XtraReportsLayoutSerializer` — als HTML-Entity-escapeter Text. Innerhalb von `ScriptsSource` sind Zeilenumbrüche als `&#xD;&#xA;` kodiert (nicht nur `&#xA;`). Das ist eine Besonderheit dieses einen Attributs — andere mehrzeilige `Expression`-Attribute im Rest der Datei (z.B. Sichtbarkeits-Ausdrücke) verwenden nur `&#xA;`. Verwechsle die beiden nicht beim Escapen/Un-escapen.

**Verschachtelte Subreports haben eigene ScriptsSource-Attribute.** Ein Hauptreport kann `DetailReport`-Elemente enthalten (z.B. `DetailReport_SLKomponenten`, `DetailReport_Staffelpreise`, `Sub_Teilrechnungslogik_AN_AB`), die jeweils ihr eigenes, unabhängiges `ScriptsSource`-Attribut mit eigenem Methoden-Namensraum haben. Beim Prüfen, ob eine Methode "fehlt", immer zuerst feststellen, zu welchem `ScriptsSource`-Block eine `<Scripts>`-Referenz gehört — sonst produzierst du Fehlalarme.

## Sichere Bearbeitungs-Pipeline (Python)

1. Datei öffnen mit `encoding='utf-8-sig', newline=''` — das entfernt die BOM beim Lesen, lässt aber die CRLF-Sequenzen exakt im String stehen (kein automatisches Newline-Mapping). Das ist wichtig: mit Standard-Textmodus wird `\r\n` beim Lesen still zu `\n` normalisiert, wodurch jedes literale `\r\n`-Suchmuster stillschweigend nicht mehr matcht — ein Fehler, der leicht unbemerkt bleibt, weil kein Python-Fehler geworfen wird, nur 0 Treffer.
2. Den `ScriptsSource="..."`-Wert per Stringsuche extrahieren (siehe Abschnitt "Grenzmarkierungen" unten) und mit `html.unescape(...)` dekodieren, um lesbaren C#-Code zu bekommen. **Wichtig:** Danach enthält der String an jedem Zeilenumbruch ein echtes `\r\n` (CR+LF), keine reinen `\n` — das ist für Schritt 4 entscheidend, siehe dort.
3. Den Code normal mit einem Text-/Editier-Tool bearbeiten. Eigene neu eingefügte Zeilen können mit reinem `\n` geschrieben werden — die Normalisierung in Schritt 4.3 vereinheitlicht ohnehin alles.
4. Beim Zurückschreiben in exakt dieser Reihenfolge escapen (Reihenfolge ist entscheidend, sonst entstehen doppelt/falsch escapte Zeichen):
   1. `&` → `&amp;` (muss zuerst passieren, sonst werden die `&` aus Schritt 2–4 selbst nochmal escaped)
   2. `<`, `>`, `"` escapen
   3. **Zeilenenden normalisieren, bevor kodiert wird:** zuerst `\r\n` → `\n` und verbleibende einzelne `\r` → `\n` vereinheitlichen, danach erst `\n` → `&#xD;&#xA;`. **Bekannter Fehler, wenn dieser Normalisierungsschritt fehlt:** Wird stattdessen direkt `\n` → `&#xD;&#xA;` auf dem Ergebnis von Schritt 2 angewendet (das noch echte `\r\n`-Paare enthält), bleibt das `\r` jeder Zeile als rohes, nicht escapetes Zeichen unmittelbar VOR dem neuen `&#xD;&#xA;` stehen. Das erzeugt bei JEDEM Zeilenumbruch im gesamten Skript (nicht nur an bearbeiteten Stellen) eine zusätzliche Leerzeile, sichtbar sobald jemand das Skript im DevExpress-Designer oder einem Code-Editor öffnet. Der Fehler ist im rohen XML-Diff leicht zu übersehen, weil die Datei trotzdem wohlgeformtes XML bleibt und lädt — sichtbar wird er erst beim Betrachten des dekodierten Skripts. Siehe `known-issues.md` für den konkreten Vorfall.
5. Den re-escapten String zwischen den exakten Original-Grenzen zurücksplicen.
6. Datei schreiben mit `encoding='utf-8', newline=''` und die BOM (`'﻿'`) manuell vor den Inhalt setzen.
7. **Validierung (neu, PFLICHT):** Im rohen, noch escapten `ScriptsSource`-Attributwert der geschriebenen Datei prüfen, dass keine literalen `\r`- oder `\n`-Zeichen mehr vorkommen (`raw_value.count('\r') == 0 and raw_value.count('\n') == 0`) — nur noch `&#xD;&#xA;`-Entities. Ein Treffer > 0 bedeutet: Schritt 4.3 wurde nicht (oder falsch) angewendet.

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

**Vorsicht bei der Automatisierung dieser Prüfung — Regex muss auf `<Scripts>`-Elemente scopen:** Ein naiver Check der Form „suche `On\w+=\"(\w+)\"` in der gesamten XML" liefert Falsch-Positive, weil `On` als Substring auch in fachlichen Attributen vorkommt, die nichts mit Event-Verdrahtung zu tun haben — z. B. `PrintOnEmptyDataSource="false"` (ein `ReportPrintOptions`-Attribut) matcht versehentlich als vermeintliches Event `OnEmptyDataSource="false"` mit Methode `false`. Das ist beobachtet worden (28.08.) und hat zunächst wie ein fehlendes Skript-Symbol ausgesehen, war aber ein reines Regex-Artefakt, in Ziel- UND Referenzdatei identisch vorhanden. **Fix für den Check:** Erst alle `<Scripts ... />`-Elemente per eigenem Pattern (`<Scripts\b[^/]*/>`) isolieren, und NUR innerhalb dieser Treffer nach `On\w+="(\w+)"` suchen — nicht auf der kompletten Roh-XML. Ein derart korrekt gescopter Check sollte auf einer sauberen Datei (Ziel wie Referenz) 0 fehlende Methoden melden; bleibt dort `false` als „fehlend" stehen, ist der Check selbst falsch aufgebaut, nicht die Datei.

## Der `<Localization>`-Block — indirekte Speicherung von Designer-Werten

Nicht jede im DevExpress-Designer manuell geänderte Eigenschaft landet als direktes XML-Attribut auf dem betroffenen Element. Insbesondere `HeightF`, `SizeF`, `LocationFloat` und teils `Visible` werden häufig stattdessen indirekt in einem separaten `<Localization>`-Element weiter oben in der Datei abgelegt, als Liste von Einträgen der Form:

```xml
<Item354 Ref="2991" Component="#Ref-1931" Culture="Default" Path="HeightF" Data="40" />
```

`Component="#Ref-N"` verweist dabei über die `Ref`-Nummer auf das eigentliche Ziel-Element (Band, Table, Control, ...); `Path` ist der Eigenschaftsname; `Data` der aktuell gesetzte Wert. `Culture` ist meist `Default`, kann bei mehrsprachigen Reports aber auch `en`/`fr`/`nl` (o. ä.) sein — dann existieren ggf. MEHRERE Einträge für denselben `Component`-Ref mit unterschiedlicher `Culture`, die unabhängig voneinander gepflegt werden müssen.

**Praktische Konsequenz:** Bei jeder Höhen-/Größen-/Positions-Änderung, die per Diff gegen eine im Designer bearbeitete Datei nachvollzogen werden soll:

1. Zuerst das Ziel-Element selbst auf ein direktes Attribut prüfen (`HeightF="..."`, `SizeF="..."`, etc.).
2. Zusätzlich IMMER nach `Component="#Ref-<RefDesElements>"` im gesamten Dokument suchen — dort kann der eigentlich wirksame (oder überschreibende) Wert stehen, unabhängig vom direkten Attribut.
3. Beim eigenen Setzen einer neuen Höhe entsprechend nicht nur das Element-Attribut setzen, sondern auch prüfen/setzen, ob ein passender `<Localization>`-Eintrag existiert bzw. angelegt werden muss.

Ein reiner Element-für-Element-Vergleich der vermuteten Stelle kann diese Änderungen komplett übersehen (weil weder vorher noch nachher ein direktes Attribut existiert) — zuverlässiger ist ein vollständiger, positionsweiser Baumvergleich der GESAMTEN Datei (alle Elemente in Dokumentreihenfolge, `Ref`-Werte beim Vergleich ignorieren), der solche indirekten Änderungen automatisch mit erfasst. Details und ein konkretes Beispiel dazu in `known-issues.md`, Einträge 6 und 7 (dort auch: nicht jede so gefundene Verschiebung ist eine echte Änderung — manche sind harmlose, rein designtime-relevante Umsortierungen).
