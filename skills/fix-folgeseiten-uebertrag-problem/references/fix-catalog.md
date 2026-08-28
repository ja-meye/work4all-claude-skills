# Fix-Katalog

Jedes Muster ist **verhaltensbasiert** beschrieben — an dem, was der Code tut, nicht an konkreten Methodennamen oder `Ref`-IDs aus dem ursprünglich reparierten Report. Der Grund: die nächste Report-Variante wird andere Namen, andere IDs, vielleicht sogar leicht andere Bandstrukturen haben. Suche nach dem beschriebenen *Verhalten*, nicht nach einem Textmatch auf einen Eigennamen. Wo unten Beispielnamen aus dem ursprünglichen Report auftauchen (`GROUP_ERP_Nummer`, `Sub_POS`, ...), sind sie nur zur Illustration gemeint.

---

## (a) BeforePrint-Sabotage der PrintOnPage-Logik

**Muster:** Ein `BeforePrint`-Handler eines Bands oder Subbands setzt `e.Cancel = true` oder `Visible = false`, basierend auf einem groben globalen Zähler (z.B. einer Variable, die einfach bei jedem Seitenumbruch hochgezählt wird), statt auf tatsächlichem Seiteninhalt. Im selben Band/Subband existiert daneben ein `PrintOnPage`-Handler, der eigentlich die richtige, feingranulare Sichtbarkeitsentscheidung treffen würde (z.B. anhand `e.PageIndex`, gecachten Werten pro Seite) — aber wegen des `Cancel`/`Visible=false` im `BeforePrint` nie zum Zug kommt.

**Ursache:** `BeforePrint` feuert vor der Paginierung; ein grober Zähler kann zu diesem Zeitpunkt nicht wissen, was tatsächlich auf welcher Seite landet. Das Abschalten via `BeforePrint` überstimmt die spätere, korrektere `PrintOnPage`-Entscheidung.

**Fix:** Den sabotierenden `BeforePrint`-Handler (und seine XML-Verdrahtung) entfernen, sodass die vorhandene `PrintOnPage`-Logik greifen kann.

**Automatisierungssicherheit:** *Automatisch sicher* — aber nur wenn zweifelsfrei nachgewiesen ist, dass (1) der Handler tatsächlich tot/redundant ist, weil eine funktionierende `PrintOnPage`-Alternative im selben Band bereits existiert, und (2) keine andere Logik im selben Band von dem Zähler/dem `Cancel` abhängt. Ist das nicht eindeutig zu belegen, stattdessen als *Vorschlag mit Rückfrage* behandeln.

---

## (b) KeepTogether=false auf einer Preiszeile bei sumCarryoverSum-Nutzung — **[ÜBERHOLT, siehe Muster (g)]**

> **Status seit dem zweiten Fix-Durchlauf (28.08., vom Kunden in Visual Studio getestet und bestätigt):** Dieser Ansatz gilt nicht mehr als Standardempfehlung für neue Fälle. In der Praxis hat `KeepTogether=true` auf Zeile + Band zu spürbar unerwünschtem Weißraum am Seitenende geführt und zudem nicht das eigentliche Symptom behoben, das den Kunden gestört hat (siehe Muster (g)). Der Kunde hat `KeepTogether` an beiden Stellen wieder zurückgenommen und stattdessen mit Mindesthöhen gearbeitet. Dieser Textabschnitt bleibt zu Diagnosezwecken stehen (z. B. um eine ältere, noch nach diesem Muster reparierte Report-Variante wiederzuerkennen), aber bei einer NEUEN Anwendung: nicht mehr dieses Muster vorschlagen, sondern direkt Muster (g) prüfen und anwenden.

**Muster:** Der Report verwendet `sumCarryoverSum(...)` für eine Übertragsberechnung, und die Tabellenzeile, die den Preis enthält (typischerweise eine Detail-/Sub-Band-Zeile wie `xrTableRow` innerhalb von `Sub_POS` oder vergleichbar), hat `KeepTogether="false"`.

**Ursache:** Ohne `KeepTogether` kann diese Zeile über einen Seitenumbruch aufgesplittet werden. `sumCarryoverSum` ist für vollständig gedruckte, nicht aufgesplittete Zeilen ausgelegt — wird eine Preiszeile gesplittet, kann der Übertragswert bereits auf der Seite, auf der die Zeile nur teilweise sichtbar ist, fälschlich den vollen (bereits inkludierten) Betrag zeigen.

**Fix:** `KeepTogether="true"` auf der betroffenen Zeile setzen. Zusätzlich empfehlenswert (siehe `known-issues.md`, Eintrag 3): `KeepTogether="true"` ALSO auf der übergeordneten Band-/SubBand-Ebene setzen, nicht nur auf der einzelnen Zeile. Das ist doppelte Absicherung mit vernachlässigbarem Risiko: Wird die Datei später vom Kunden im DevExpress-Designer geöffnet und gespeichert, kann dabei eine per XML gesetzte Zeilen-Eigenschaft verloren gehen (empirisch beobachtet) — die Band-Ebene hält den Inhalt in diesem Fall trotzdem zusammen.

**Automatisierungssicherheit:** *Vorschlag mit Rückfrage.* Das Ändern kann sichtbare Layout-Nebenwirkungen haben (z.B. mehr Weißraum am Seitenende, wenn eine Zeile komplett auf die nächste Seite verschoben wird, statt zu splitten). Nicht ohne Rückfrage automatisch anwenden, außer der Nutzer hat das Muster für diesen Report bereits explizit bestätigt.

**Wichtig bei einer bereits gefixten Datei, die zwischenzeitlich im Designer geöffnet war:** Nicht davon ausgehen, dass ein früher gesetztes `KeepTogether` noch vorhanden ist. Alle `KeepTogether`-Vorkommen in der Datei neu auflisten und mit dem erwarteten Zustand abgleichen (siehe `validation-checklist.md`).

---

## (c) Übertrag-Sichtbarkeit ignoriert "Beleg hat Betrag, aber noch nicht auf dieser Seite gedruckt"

**Muster:** Eine Sichtbarkeitsbedingung für Übertrag-Zeile(n) oder Folgeseiten-Tabellenkopf hängt ausschließlich an `carry != 0` (bzw. äquivalent: der seitenbezogene `sumCarryoverSum`-Wert). Es gibt keine zusätzliche Berücksichtigung des Falls: der Beleg hat insgesamt einen Betrag > 0, aber auf der aktuellen Seite wurde bislang keine bepreiste Position gedruckt (z.B. weil ein langer Kopftext die erste Position auf Seite 2 verdrängt hat).

**Ursache:** `carry` (der seitenbezogene Übertrag) ist auf der betroffenen Seite noch 0, weil noch keine bepreiste Position lief — die Bedingung kann also nicht zwischen "Beleg hat wirklich gar keinen Betrag" (korrekt unterdrückt) und "Beleg hat einen Betrag, nur eben noch nicht auf dieser Seite gedruckt" (fälschlich unterdrückt) unterscheiden.

**Fix:** Ein zusätzliches, seitenunabhängiges Gesamtsummen-Feld einführen (z.B. über ein unsichtbares Hilfslabel gebunden an eine dokumentweite Summe wie `calcSumGesPreis`), und die Bedingung erweitern zu `carry != 0 || gesamtsumme != 0`.

**Automatisierungssicherheit:** *Vorschlag mit Rückfrage.* Erfordert ein neues Hilfsfeld/-label und eine Änderung an mehreren zusammengehörigen Sichtbarkeits-Handlern (Tabellenkopf, Übertrag oben, Übertrag unten) — sollte konsistent an allen betroffenen Stellen gleichzeitig gemacht werden, nicht nur an einer.

---

## (d) Fehlender Batch-Sicherheits-Reset bei Sammeldruck

**Muster:** Ein `GroupFooter`- oder vergleichbarer Handler setzt irgendwann `Visible = false` auf ein Element (z.B. um den Übertrag auf der letzten Seite eines Belegs auszublenden), aber es gibt keinen expliziten Reset auf `Visible = true` zu Beginn des *nächsten* Belegs im selben Reportlauf.

**Ursache:** Bei Sammeldruck mehrerer Belege in einem Lauf (mehrere Datensätze in derselben Reportgenerierung) kann der `Visible = false`-Zustand vom vorherigen Beleg auf den nächsten "durchsickern", weil DevExpress-Controls ihren Zustand zwischen Gruppenwechseln nicht automatisch zurücksetzen.

**Fix:** Im `BeforePrint`-Handler des GroupHeader-Bands, das einen neuen Beleg einleitet, explizit `Visible = true` auf dem betroffenen Element setzen.

**Automatisierungssicherheit:** *Vorschlag mit Rückfrage* beim ersten Auftreten in einer neuen Report-Variante (prüfen, ob der Report überhaupt für Sammeldruck genutzt wird — falls nicht, ist der Fix irrelevant). Wenn bereits an anderer Stelle im selben Report dasselbe Muster bestätigt gefixt wurde, kann ein identisches zweites Vorkommen als *automatisch sicher* behandelt werden.

---

## (e) Skript-Hygiene: leere Print-Event-Handler und toter auskommentierter Code

**Muster:** Zwei Unterfälle:
- Ein Event-Handler (`BeforePrint`, `AfterPrint`, `PrintOnPage`, ...) hat einen Rumpf, der ausschließlich aus Kommentaren besteht oder komplett leer ist — keine aktive Anweisung.
- Ein Block reinen, auskommentierten Codes (keine aktive Zeile darin) steht im Skript, oft mit einem Kommentar, der erklärt, wodurch er ersetzt wurde.

**Ursache:** Historisch gewachsener Code — frühere Lösungsversuche, die durch eine neuere Variante abgelöst wurden, aber nie aufgeräumt wurden.

**Fix:** Entfernen. Dabei gilt zwingend:

1. Der Handler-Rumpf muss nachweislich frei von aktiver Logik sein (nur Kommentare oder leer) — im Zweifel NICHT entfernen.
2. **Immer symmetrisch auf Geschwister-Events am selben Control/Band prüfen.** Beispiel: `OnBeforePrint` mit echter Logik + `OnAfterPrint` leer am selben Element → nur die `OnAfterPrint`-Verdrahtung entfernen, `OnBeforePrint` bleibt unangetastet.
3. War der entfernte Handler die **einzige** Verdrahtung an diesem Element, das komplette `<Scripts>`-Element entfernen. Gab es daneben noch andere `On*`-Attribute mit Logik, nur das jeweils betroffene `On*`-Attribut entfernen.
4. Begründungs-Kommentare, die eine Architekturentscheidung dokumentieren (z.B. "X über Expression gelöst, weil Y zum Zeitpunkt von BeforePrint noch nicht verfügbar ist"), **nicht ersatzlos löschen** — als knapper Einzeiler erhalten, oder zum inhaltlich nächstgelegenen Handler mit aktiver Logik verschieben, wenn sich der Kommentar eigentlich auf dessen Verhalten bezieht.
5. Reine `if(false)`-Zweige oder ähnliche tote, aber *nicht auskommentierte* (also weiterhin vom Compiler gesehene) Logik gehören **nicht** zu diesem Muster — das ist aktiver, wenn auch ungenutzter Code, und damit potenziell eigenständiges Refactoring mit eigener Rückfrage, nicht Teil dieser Hygiene-Bereinigung.

**Automatisierungssicherheit:** *Automatisch sicher*, aber nur nachdem Regel 1–4 einzeln geprüft wurden, und nur wenn der Nutzer diesen Schritt für den aktuellen Lauf überhaupt angefordert hat (siehe SKILL.md, Schritt 5 — dieser Schritt ist optional und nicht automatisch Teil jedes Fix-Laufs).

---

## (f) Übertrag/Folgeseiten-Sichtbarkeit ignoriert, ob der Detailbereich überhaupt schon begonnen hat

**Muster:** Die Sichtbarkeitsbedingung für Übertrag (oben/unten) bzw. Folgeseiten-Tabellenkopf stützt sich auf eine dokumentweite Gesamtsumme (siehe Muster (c) oben) als Rückfallbedingung — z. B. `carry != 0 || gesamtsumme != 0`. Diese Rückfallbedingung kann fälschlich auch dann `true` werden, wenn der eigentliche Detailbereich (die Positionstabelle) auf der aktuellen bzw. einer vorangehenden Seite **noch gar nicht begonnen hat zu drucken** — etwa weil vorgelagerter Inhalt (ein sehr langer Kopftext, oder eine optionale Übersichts-/Zusammenstellungs-Subband, die über einen Report-Parameter wie `ArgShowTitleOverview` gesteuert wird und selbst einen verschachtelten Subreport mit eigenen Summenzeilen enthalten kann) die Seite(n) vollständig einnimmt, bevor der Detailbereich überhaupt startet.

**Ursache:** Die dokumentweite Gesamtsumme ist über den ganzen Beleg konstant und sagt nichts darüber aus, WANN (auf welcher Seite, relativ zum Detailbereich) sie „freigegeben" werden darf. Sie unterscheidet zuverlässig zwischen „Beleg hat gar keinen Betrag" und „Beleg hat einen Betrag", aber nicht zwischen „Detailbereich läuft schon (nur eben ohne Preis auf dieser Seite)" und „Detailbereich hat noch nicht angefangen".

**Fix:** Ein zusätzliches Flag einführen (z. B. `_detailPrintedSoFar`, Standard `false`), das über einen `PrintOnPage`-Handler an einer bereits vorhandenen, in jeder Detailzeile zuverlässig vorkommenden Kontrollzelle (z. B. der Preis-Zelle) auf `true` gesetzt wird, sobald diese Zeile tatsächlich gedruckt wird. Alle Übertrag-/Folgeseiten-Sichtbarkeitsbedingungen um `&& detailFlag` erweitern. Das funktioniert zuverlässig, weil `PrintOnPage`-Ereignisse strikt in der Reihenfolge feuern, in der Inhalte tatsächlich gedruckt werden: eine Kopfzeile/Übertrag-oben-Kontrolle, die auf derselben physischen Seite VOR dem Detailbereich liegt, liest das Flag korrekt so, wie es am Ende der VORHERIGEN Seite stand; eine Fußzeile/Übertrag-unten-Kontrolle NACH dem Detailbereich derselben Seite liest es korrekt inklusive der Detailzeilen dieser Seite.

**Wichtige Nebenbedingung:** Wird ein solches Flag in einem `BeforePrint`-Handler (z. B. beim Start eines neuen Belegs/einer neuen Gruppe) zurückgesetzt, um Sammeldruck mehrerer Belege in einem Lauf abzusichern — bedenken, dass `BeforePrint` in der Generierungsphase läuft, die für das GESAMTE Dokument abgeschlossen ist, bevor die Druckphase (in der `PrintOnPage` und damit das Flag selbst gelesen/gesetzt wird) beginnt. Ein `BeforePrint`-Reset schützt daher zuverlässig nur den Normalfall „ein Beleg pro Reportlauf". Bei echtem Sammeldruck mehrerer Belege in einem einzigen Lauf kann der Reset zu spät greifen; das als bekannte Grenze dokumentieren statt stillschweigend als vollständig gelöst zu behandeln.

**Automatisierungssicherheit:** *Vorschlag mit Rückfrage.* Erfordert eine neue Variable und einen neuen (oder erweiterten) `PrintOnPage`-Handler an einer sorgfältig ausgewählten Kontrollzelle — die Wahl der richtigen Zelle (zuverlässig einmal pro Detailzeile, unabhängig vom Zeilentyp) ist entscheidend und sollte pro Report-Variante bestätigt werden, bevor der Fix angewendet wird.

---

## (g) Mindesthöhen statt KeepTogether gegen Weißraum und abgeschnittene Übertrag-Anzeige

**Ersetzt Muster (b) als aktuelle Standardempfehlung.** Vom Kunden in Visual Studio umgesetzt und in DevExpress bestätigt getestet (28.08.).

**Muster / Symptom:** Zwei zusammenhängende, aber getrennt zu behandelnde Symptome, die beide auftreten können, wenn Muster (b) (`KeepTogether=true` auf Preiszeile/Sub_POS-Band) bereits angewendet wurde oder wenn die Übertrag-oben-Tabelle generell zu knapp bemessen ist:

1. **Zu viel Weißraum am Seitenende.** `KeepTogether=true` auf der Preiszeile und/oder dem `Sub_POS`-Band verschiebt eine komplette Zeile (inkl. langer Artikelbeschreibung) auf die nächste Seite, sobald sie nicht mehr vollständig auf die aktuelle Seite passt — das erzeugt in der Praxis störend viel Leerraum am Ende der vorherigen Seite.
2. **Abgeschnittene/zu knapp wirkende Übertrag-oben-Anzeige.** Die Tabelle `tb_ÜbertragOben` (im `SubBand` `Sub_UebertragOben`) hat eine zu geringe Mindesthöhe (z. B. 40), wodurch ihr Inhalt in bestimmten Sprachvarianten (längere Texte in EN/FR/NL) oder bei zweizeiligem Inhalt abgeschnitten wirkt.

Zusätzlich, als verwandtes Symptom in manchen Report-Varianten: Die Positionstabelle `xrTable1` innerhalb von `Sub_POS` hat **zwei** Zeilen statt einer (eine vermutlich historische/überzählige erste Zeile plus die eigentliche Datenzeile), was zu Höhen- und Anzeigeproblemen führt.

**Ursache:** Die Kombination aus `KeepTogether=true` (Muster b) zur Absicherung von `sumCarryoverSum` und zu knapp bemessenen festen Höhen führt in Summe zu einem für den Kunden inakzeptablen Layout-Ergebnis. Der in `known-issues.md` Eintrag 4 als "kleineres Übel" akzeptierte Weißraum hat sich in der Praxis als zu störend herausgestellt.

**Fix (alle drei Teile zusammen anwenden):**

1. `KeepTogether` auf der Preiszeile (z. B. `xrTableRow1` in `Sub_POS`) UND auf dem `Sub_POS`-Band selbst wieder auf `false`/Standard zurücksetzen (Attribut entfernen oder explizit `"false"` setzen).
2. Mindesthöhe von `tb_ÜbertragOben` (und dem umgebenden `SubBand`, z. B. `Sub_UebertragOben`) auf **50** anheben — dabei **nur anheben, nie verringern**: ist bereits ein höherer Wert eingestellt (z. B. 60), diesen unverändert lassen.
3. Falls `xrTable1` (in `Sub_POS`) zwei Zeilen enthält: die **obere** Zeile löschen, die verbleibende (Daten-)Zeile auf Höhe **55** setzen.

**Wichtiger technischer Hinweis zur Umsetzung:** Im Designer gesetzte `HeightF`-/`SizeF`-/`LocationFloat`-Werte landen nicht zwingend als direktes Attribut auf dem Element selbst, sondern häufig indirekt in einem separaten `<Localization>`-Block (`Component="#Ref-<ZielRef>"`). Vor dem Setzen einer Höhe IMMER auch dort nachsehen (siehe `known-issues.md`, Eintrag 6) — sonst wird eine vermeintlich fehlende Änderung übersehen oder ein neuer, redundanter Wert direkt am Element gesetzt, während der eigentlich wirksame Wert im `<Localization>`-Block unangetastet bleibt.

**Automatisierungssicherheit:**
- Punkt 1 (KeepTogether zurücknehmen) und Punkt 2 (Mindesthöhe 50): *Vorschlag mit Rückfrage*, außer der Kunde hat für DIESEN Report bereits explizit bestätigt, auf dieses Vorgehen umzusteigen (dann *automatisch sicher*, wie im bestätigten Fall vom 28.08.).
- Punkt 3 (zweite Zeile in `xrTable1` löschen): *Vorschlag mit Rückfrage* — vor dem Löschen prüfen, ob die obere Zeile wirklich keine eigenständige Funktion hat (z. B. durch Vergleich mit einer bestätigten Referenz, die dieselbe Situation bereits bereinigt hat), nicht blind die erste Zeile löschen nur weil zwei vorhanden sind.

**Offene Frage / nicht abschließend geklärt:** Der genaue Kausal-Zusammenhang zwischen der Rücknahme von `KeepTogether` und dem ursprünglichen Muster-(b)-Risiko (aufgesplittete Preiszeile verfälscht `sumCarryoverSum`) ist nicht erneut aus der DevExpress-Rendering-Pipeline hergeleitet worden — dieser Eintrag dokumentiert den vom Kunden getesteten und für gut befundenen Zustand, nicht einen bewiesenen Mechanismus. Falls nach Anwendung dieses Fixes auf einer neuen Report-Variante ein falscher Übertragswert durch eine aufgesplittete Preiszeile auffällt, ist das ein Hinweis darauf, dass Muster (b) für DIESEN Report doch relevant bleibt und mit dem Kunden gemeinsam abgewogen werden sollte (Weißraum vs. korrekter Wert bei Seitenumbruch mitten in einer Position).
