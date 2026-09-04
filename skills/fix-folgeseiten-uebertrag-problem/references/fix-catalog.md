# Fix-Katalog

Jedes Muster ist **verhaltensbasiert** beschrieben — an dem, was der Code tut, nicht an konkreten Methodennamen oder `Ref`-IDs aus dem ursprünglich reparierten Report. Der Grund: die nächste Report-Variante wird andere Namen, andere IDs, vielleicht sogar leicht andere Bandstrukturen haben. Suche nach dem beschriebenen *Verhalten*, nicht nach einem Textmatch auf einen Eigennamen. Wo unten Beispielnamen aus dem ursprünglichen Report auftauchen (`GROUP_ERP_Nummer`, `Sub_POS`, ...), sind sie nur zur Illustration gemeint.

---

## Inhalt

- (a)
- (b)
- (c)
- (d)
- (e)
- (f)
- (g)
- (h)
- (i)
- (j)

## (a) · Unterpunkt-ID `DXJ0001.B` · BeforePrint-Sabotage der PrintOnPage-Logik

**Muster:** Ein `BeforePrint`-Handler eines Bands oder Subbands setzt `e.Cancel = true` oder `Visible = false`, basierend auf einem groben globalen Zähler (z.B. einer Variable, die einfach bei jedem Seitenumbruch hochgezählt wird), statt auf tatsächlichem Seiteninhalt. Im selben Band/Subband existiert daneben ein `PrintOnPage`-Handler, der eigentlich die richtige, feingranulare Sichtbarkeitsentscheidung treffen würde (z.B. anhand `e.PageIndex`, gecachten Werten pro Seite) — aber wegen des `Cancel`/`Visible=false` im `BeforePrint` nie zum Zug kommt.

**Ursache:** `BeforePrint` feuert vor der Paginierung; ein grober Zähler kann zu diesem Zeitpunkt nicht wissen, was tatsächlich auf welcher Seite landet. Das Abschalten via `BeforePrint` überstimmt die spätere, korrektere `PrintOnPage`-Entscheidung.

**Fix:** Den sabotierenden `BeforePrint`-Handler (und seine XML-Verdrahtung) entfernen, sodass die vorhandene `PrintOnPage`-Logik greifen kann.

**Automatisierungssicherheit:** *Automatisch sicher* — aber nur wenn zweifelsfrei nachgewiesen ist, dass (1) der Handler tatsächlich tot/redundant ist, weil eine funktionierende `PrintOnPage`-Alternative im selben Band bereits existiert, und (2) keine andere Logik im selben Band von dem Zähler/dem `Cancel` abhängt. Ist das nicht eindeutig zu belegen, stattdessen als *Vorschlag mit Rückfrage* behandeln.

---

## (b) · keine eigene Unterpunkt-ID (historisch, siehe `DXJ0001.G`) · KeepTogether=false auf einer Preiszeile bei sumCarryoverSum-Nutzung — **[ÜBERHOLT, siehe Muster (g)]**

> **Status seit dem zweiten Fix-Durchlauf (28.08., vom Kunden in Visual Studio getestet und bestätigt):** Dieser Ansatz gilt nicht mehr als Standardempfehlung für neue Fälle. In der Praxis hat `KeepTogether=true` auf Zeile + Band zu spürbar unerwünschtem Weißraum am Seitenende geführt und zudem nicht das eigentliche Symptom behoben, das den Kunden gestört hat (siehe Muster (g)). Der Kunde hat `KeepTogether` an beiden Stellen wieder zurückgenommen und stattdessen mit Mindesthöhen gearbeitet. Dieser Textabschnitt bleibt zu Diagnosezwecken stehen (z. B. um eine ältere, noch nach diesem Muster reparierte Report-Variante wiederzuerkennen), aber bei einer NEUEN Anwendung: nicht mehr dieses Muster vorschlagen, sondern direkt Muster (g) prüfen und anwenden.

**Muster:** Der Report verwendet `sumCarryoverSum(...)` für eine Übertragsberechnung, und die Tabellenzeile, die den Preis enthält (typischerweise eine Detail-/Sub-Band-Zeile wie `xrTableRow` innerhalb von `Sub_POS` oder vergleichbar), hat `KeepTogether="false"`.

**Ursache:** Ohne `KeepTogether` kann diese Zeile über einen Seitenumbruch aufgesplittet werden. `sumCarryoverSum` ist für vollständig gedruckte, nicht aufgesplittete Zeilen ausgelegt — wird eine Preiszeile gesplittet, kann der Übertragswert bereits auf der Seite, auf der die Zeile nur teilweise sichtbar ist, fälschlich den vollen (bereits inkludierten) Betrag zeigen.

**Fix:** `KeepTogether="true"` auf der betroffenen Zeile setzen. Zusätzlich empfehlenswert (siehe `known-issues.md`, Eintrag 3): `KeepTogether="true"` ALSO auf der übergeordneten Band-/SubBand-Ebene setzen, nicht nur auf der einzelnen Zeile. Das ist doppelte Absicherung mit vernachlässigbarem Risiko: Wird die Datei später vom Kunden im DevExpress-Designer geöffnet und gespeichert, kann dabei eine per XML gesetzte Zeilen-Eigenschaft verloren gehen (empirisch beobachtet) — die Band-Ebene hält den Inhalt in diesem Fall trotzdem zusammen.

**Automatisierungssicherheit:** *Vorschlag mit Rückfrage.* Das Ändern kann sichtbare Layout-Nebenwirkungen haben (z.B. mehr Weißraum am Seitenende, wenn eine Zeile komplett auf die nächste Seite verschoben wird, statt zu splitten). Nicht ohne Rückfrage automatisch anwenden, außer der Nutzer hat das Muster für diesen Report bereits explizit bestätigt.

**Wichtig bei einer bereits gefixten Datei, die zwischenzeitlich im Designer geöffnet war:** Nicht davon ausgehen, dass ein früher gesetztes `KeepTogether` noch vorhanden ist. Alle `KeepTogether`-Vorkommen in der Datei neu auflisten und mit dem erwarteten Zustand abgleichen (siehe `validation-checklist.md`).

---

## (c) · Unterpunkt-ID `DXJ0001.A` (gemeinsam mit Muster (f)) · Übertrag-Sichtbarkeit ignoriert "Beleg hat Betrag, aber noch nicht auf dieser Seite gedruckt"

**Muster:** Eine Sichtbarkeitsbedingung für Übertrag-Zeile(n) oder Folgeseiten-Tabellenkopf hängt ausschließlich an `carry != 0` (bzw. äquivalent: der seitenbezogene `sumCarryoverSum`-Wert). Es gibt keine zusätzliche Berücksichtigung des Falls: der Beleg hat insgesamt einen Betrag > 0, aber auf der aktuellen Seite wurde bislang keine bepreiste Position gedruckt (z.B. weil ein langer Kopftext die erste Position auf Seite 2 verdrängt hat).

**Ursache:** `carry` (der seitenbezogene Übertrag) ist auf der betroffenen Seite noch 0, weil noch keine bepreiste Position lief — die Bedingung kann also nicht zwischen "Beleg hat wirklich gar keinen Betrag" (korrekt unterdrückt) und "Beleg hat einen Betrag, nur eben noch nicht auf dieser Seite gedruckt" (fälschlich unterdrückt) unterscheiden.

**Fix:** Ein zusätzliches, seitenunabhängiges Gesamtsummen-Feld einführen (z.B. über ein unsichtbares Hilfslabel gebunden an eine dokumentweite Summe wie `calcSumGesPreis`), und die Bedingung erweitern zu `carry != 0 || gesamtsumme != 0`.

**Automatisierungssicherheit:** *Vorschlag mit Rückfrage.* Erfordert ein neues Hilfsfeld/-label und eine Änderung an mehreren zusammengehörigen Sichtbarkeits-Handlern (Tabellenkopf, Übertrag oben, Übertrag unten) — sollte konsistent an allen betroffenen Stellen gleichzeitig gemacht werden, nicht nur an einer.

---

## (d) · Unterpunkt-ID `DXJ0001.H` · Fehlender Batch-Sicherheits-Reset bei Sammeldruck

**Muster:** Ein `GroupFooter`- oder vergleichbarer Handler setzt irgendwann `Visible = false` auf ein Element (z.B. um den Übertrag auf der letzten Seite eines Belegs auszublenden), aber es gibt keinen expliziten Reset auf `Visible = true` zu Beginn des *nächsten* Belegs im selben Reportlauf.

**Ursache:** Bei Sammeldruck mehrerer Belege in einem Lauf (mehrere Datensätze in derselben Reportgenerierung) kann der `Visible = false`-Zustand vom vorherigen Beleg auf den nächsten "durchsickern", weil DevExpress-Controls ihren Zustand zwischen Gruppenwechseln nicht automatisch zurücksetzen.

**Fix:** Im `BeforePrint`-Handler des GroupHeader-Bands, das einen neuen Beleg einleitet, explizit `Visible = true` auf dem betroffenen Element setzen.

**Automatisierungssicherheit:** *Vorschlag mit Rückfrage* beim ersten Auftreten in einer neuen Report-Variante (prüfen, ob der Report überhaupt für Sammeldruck genutzt wird — falls nicht, ist der Fix irrelevant). Wenn bereits an anderer Stelle im selben Report dasselbe Muster bestätigt gefixt wurde, kann ein identisches zweites Vorkommen als *automatisch sicher* behandelt werden.

---

## (e) · Unterpunkt-ID `DXJ0001.C` · Skript-Hygiene: leere Print-Event-Handler und toter auskommentierter Code

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
6. **Abgrenzung zu eigenständigen Funktionsumbauten:** Variablen/Methoden, die zu einer erkennbar anderen, aktiv genutzten Funktionalität gehören (z. B. eine parallele Steuertext-/Sachkonto-Berechnung), gehören NICHT zu diesem Muster — auch dann nicht, wenn eine Referenzdatei diese Funktionalität im Zuge eines separaten Umbaus (z. B. Ersatz durch einen neuen Subreport) mit entfernt hat. Das ist ein eigenständiger Funktionsumbau außerhalb des Auftragsumfangs, keine Hygiene (siehe `known-issues.md` Eintrag 8 für ein konkretes Beispiel dieser Abgrenzung).

**Automatisierungssicherheit:** **Automatisch sicher und PFLICHT-Bestandteil jedes Fix-Laufs** (seit 28.08., siehe SKILL.md „Kundenvorgabe" — war ursprünglich optional/nur auf Wunsch, ist das nicht mehr), aber nur nachdem Regel 1–4 einzeln geprüft wurden. Vor dem Löschen jeder Variable/Methode per Textsuche verifizieren (nicht raten), dass sie außerhalb ihrer eigenen Deklaration nirgends mehr gelesen/aufgerufen wird — siehe `known-issues.md` Eintrag 8 für den Vorfall, der dazu geführt hat, dass dieser Schritt jetzt verbindlich ist.

### Erweiterte, konkrete Bereinigungsfälle (seit v1.2.0)

Vier zusätzliche, konkrete Unterfälle derselben Hygiene-Regel — gefunden am `dxAio_template`-Report, aber verhaltensbasiert genug formuliert, um auf andere Varianten übertragbar zu sein. Alle vier unterliegen denselben Regeln 1–4 oben (insbesondere: vor dem Entfernen per Textsuche verifizieren, dass wirklich nirgends mehr referenziert).

7. **work4all-interne Sonderparameter, die in einem Kunden-Report nichts verloren haben.** Manche Report-Varianten enthalten Variablen, die erkennbar nur für work4all-interne Zwecke gedacht sind, nicht für den eigentlichen Kundenreport — Muster: eine Variable mit einem Kommentar, der auf eine interne work4all-Struktur verweist (Artikel-Hauptgruppe/-Obergruppe, interne Gruppen-/Objektcodes o. ä.), ohne dass ein Kundenreport diese Unterscheidung fachlich braucht. Beispiel aus `dxAio_template`: `int Lizenz = 0;` und `int ArtikelServerHosting = 0;` (Kommentare verweisen auf work4all-interne Artikel-Hauptgruppen-/Obergruppen-Codes). **Fix:** Nach Verifikation, dass die Variable(n) nirgends mehr im Skript gelesen werden, entfernen. **Automatisierungssicherheit:** *Vorschlag mit Rückfrage* beim ersten Auftreten in einer neuen Report-Variante (es könnte in einer anderen Variante doch fachlich genutzt werden) — danach, sobald einmal für einen Report bestätigt, *automatisch sicher* bei identischem Namen/Kommentar-Muster.
8. **Ein Band, das ausschließlich einen alten, jetzt redundanten `pageCounter`-basierten Seite-1-Abstand erzeugt hat.** Muster: Ein eigenes SubBand mit Standardhöhe `0` und einer `BeforePrint`-Methode nach dem Schema `if (pageCounter != 1) { e.Cancel = true; }` (druckt also NUR auf Seite 1, mit Höhe 0 — kann de facto nie sichtbaren Inhalt erzeugen). Beispiel: `Sub_AbstandSeite1` mit `Sub_AbstandSeite1_BeforePrint`. **Bedingung für den Fix (beide müssen zutreffen, sonst nicht anfassen):** (a) die Standardhöhe des Bands ist `0` (direktes Attribut UND `<Localization>`-Block prüfen, siehe `repx-technical-notes.md`), UND (b) im Skript wird `HeightF` dieses Bands an keiner Stelle programmatisch erhöht. **Fix:** Band inkl. `BeforePrint`-Methode und XML-Verdrahtung vollständig entfernen (symmetrische Entfernung, siehe `validation-checklist.md` Punkt 6). **Automatisierungssicherheit:** *Vorschlag mit Rückfrage* — eine Bandentfernung ist strukturell eingreifender als eine reine Variablen-/Methoden-Löschung, deshalb trotz erfüllter Bedingung nicht automatisch scharf, sondern dem Nutzer als konkreter Vorschlag mit Begründung vorgelegt.
9. **Reine Debug-String-Ausgaben ohne produktiven Zweck.** Muster: Ein `_dbgHelper`-artiges Feld (oder vergleichbar benannt), das ausschließlich zu Diagnosezwecken während der Entwicklung befüllt wurde (typisches Muster: `string.Format("...", e.PageIndex + 1, ...)` mit rein diagnostischen Platzhaltern), aber von keinem sichtbaren Report-Element gelesen wird. **Fix:** Entfernen wie jeden anderen toten Code (Regel 1–4 oben). **Automatisierungssicherheit:** *Automatisch sicher*, sobald per Textsuche verifiziert ist, dass kein sichtbares Control den Wert liest — Debug-Ausgaben dieser Art sind per Definition nicht Teil der fachlichen Logik.
10. **Kommentare kürzen statt löschen.** Kein Löschfall, sondern eine Kürzungsregel: Lange, ausführliche Fließtext-Kommentare (mehrzeilige Prosa-Erklärungen) werden auf das Wesentliche gekürzt — Stichpunkt-artig, so dass die Kernaussage erhalten bleibt (Begründung/Architekturentscheidung, siehe Regel 4 oben), aber ohne wiederholende oder ausschmückende Formulierungen. Ziel: ein Kommentar soll knapp genug sein, dass ein Mensch oder eine KI ihn schnell erfassen und daraus die richtigen Schlüsse ziehen kann, ohne einen Prosa-Absatz lesen zu müssen. **Nicht kürzen:** der `work4all-log`-Block **und die Anker-Zeile** (siehe `fix-log-format.md`, Regeln 3 und 8) sowie Kommentare, die bereits knapp sind.

    > **Zwei-Wege-Regel, verbindlich seit 04.09.2026 (Meta-Skill Baustein 6):** Diese Kürzung gilt **nur für die produktive Live-Datei**, niemals für die Referenzdatei — dort sind die ausführlichen Kommentare die eigentliche Dokumentation und bleiben vollständig erhalten. Und sie ist ein **eigener, ausdrücklich angeforderter Arbeitsschritt**: sie läuft nie beiläufig innerhalb eines Fix-Laufs und nie im selben Schritt wie eine inhaltliche Änderung, damit im Diff trennbar bleibt, was Kürzung und was Fix war. Nach einer Kürzung wird der Vergleich gegen die Referenz **kommentar-unempfindlich** geführt (Kommentare vor dem Diff entfernen), und `scripts/validate_repx.py` muss weiterhin ohne FAIL durchlaufen — insbesondere `C15`/`C16` (Log-Block und Anker-Zeile unverändert vorhanden) und `C19` (Log-Block append-only). **Automatisierungssicherheit:** *Automatisch sicher* als Teil der Hygiene — Kürzung ist per Definition inhaltserhaltend, solange die Kernaussage stehen bleibt; im Zweifel (Kommentar enthält eine nicht eindeutig trennbare fachliche Detailinformation) lieber etwas länger lassen als eine relevante Information verlieren.

---

## (f) · Unterpunkt-ID `DXJ0001.A` (gemeinsam mit Muster (c)) · Übertrag/Folgeseiten-Sichtbarkeit ignoriert, ob der Detailbereich überhaupt schon begonnen hat

**Muster:** Die Sichtbarkeitsbedingung für Übertrag (oben/unten) bzw. Folgeseiten-Tabellenkopf stützt sich auf eine dokumentweite Gesamtsumme (siehe Muster (c) oben) als Rückfallbedingung — z. B. `carry != 0 || gesamtsumme != 0`. Diese Rückfallbedingung kann fälschlich auch dann `true` werden, wenn der eigentliche Detailbereich (die Positionstabelle) auf der aktuellen bzw. einer vorangehenden Seite **noch gar nicht begonnen hat zu drucken** — etwa weil vorgelagerter Inhalt (ein sehr langer Kopftext, oder eine optionale Übersichts-/Zusammenstellungs-Subband, die über einen Report-Parameter wie `ArgShowTitleOverview` gesteuert wird und selbst einen verschachtelten Subreport mit eigenen Summenzeilen enthalten kann) die Seite(n) vollständig einnimmt, bevor der Detailbereich überhaupt startet.

**Ursache:** Die dokumentweite Gesamtsumme ist über den ganzen Beleg konstant und sagt nichts darüber aus, WANN (auf welcher Seite, relativ zum Detailbereich) sie „freigegeben" werden darf. Sie unterscheidet zuverlässig zwischen „Beleg hat gar keinen Betrag" und „Beleg hat einen Betrag", aber nicht zwischen „Detailbereich läuft schon (nur eben ohne Preis auf dieser Seite)" und „Detailbereich hat noch nicht angefangen".

**Fix:** Ein zusätzliches Flag einführen (z. B. `_detailPrintedSoFar`, Standard `false`), das über einen `PrintOnPage`-Handler an einer bereits vorhandenen, in jeder Detailzeile zuverlässig vorkommenden Kontrollzelle (z. B. der Preis-Zelle) auf `true` gesetzt wird, sobald diese Zeile tatsächlich gedruckt wird. Alle Übertrag-/Folgeseiten-Sichtbarkeitsbedingungen um `&& detailFlag` erweitern. Das funktioniert zuverlässig, weil `PrintOnPage`-Ereignisse strikt in der Reihenfolge feuern, in der Inhalte tatsächlich gedruckt werden: eine Kopfzeile/Übertrag-oben-Kontrolle, die auf derselben physischen Seite VOR dem Detailbereich liegt, liest das Flag korrekt so, wie es am Ende der VORHERIGEN Seite stand; eine Fußzeile/Übertrag-unten-Kontrolle NACH dem Detailbereich derselben Seite liest es korrekt inklusive der Detailzeilen dieser Seite.

**Wichtige Nebenbedingung:** Wird ein solches Flag in einem `BeforePrint`-Handler (z. B. beim Start eines neuen Belegs/einer neuen Gruppe) zurückgesetzt, um Sammeldruck mehrerer Belege in einem Lauf abzusichern — bedenken, dass `BeforePrint` in der Generierungsphase läuft, die für das GESAMTE Dokument abgeschlossen ist, bevor die Druckphase (in der `PrintOnPage` und damit das Flag selbst gelesen/gesetzt wird) beginnt. Ein `BeforePrint`-Reset schützt daher zuverlässig nur den Normalfall „ein Beleg pro Reportlauf". Bei echtem Sammeldruck mehrerer Belege in einem einzigen Lauf kann der Reset zu spät greifen; das als bekannte Grenze dokumentieren statt stillschweigend als vollständig gelöst zu behandeln.

**Automatisierungssicherheit:** *Vorschlag mit Rückfrage.* Erfordert eine neue Variable und einen neuen (oder erweiterten) `PrintOnPage`-Handler an einer sorgfältig ausgewählten Kontrollzelle — die Wahl der richtigen Zelle (zuverlässig einmal pro Detailzeile, unabhängig vom Zeilentyp) ist entscheidend und sollte pro Report-Variante bestätigt werden, bevor der Fix angewendet wird.

---

## (g) · Unterpunkt-ID `DXJ0001.G` · Mindesthöhen statt KeepTogether gegen Weißraum und abgeschnittene Übertrag-Anzeige

**Ersetzt Muster (b) als aktuelle Standardempfehlung.** Vom Kunden in Visual Studio umgesetzt und in DevExpress bestätigt getestet (28.08.).

**Muster / Symptom:** Zwei zusammenhängende, aber getrennt zu behandelnde Symptome, die beide auftreten können, wenn Muster (b) (`KeepTogether=true` auf Preiszeile/Sub_POS-Band) bereits angewendet wurde oder wenn die Übertrag-oben-Tabelle generell zu knapp bemessen ist:

1. **Zu viel Weißraum am Seitenende.** `KeepTogether=true` auf der Preiszeile und/oder dem `Sub_POS`-Band verschiebt eine komplette Zeile (inkl. langer Artikelbeschreibung) auf die nächste Seite, sobald sie nicht mehr vollständig auf die aktuelle Seite passt — das erzeugt in der Praxis störend viel Leerraum am Ende der vorherigen Seite.
2. **Abgeschnittene/zu knapp wirkende Übertrag-oben-Anzeige.** Die Tabelle `tb_ÜbertragOben` (im `SubBand` `Sub_UebertragOben`) hat eine zu geringe Mindesthöhe (z. B. 40), wodurch ihr Inhalt in bestimmten Sprachvarianten (längere Texte in EN/FR/NL) oder bei zweizeiligem Inhalt abgeschnitten wirkt.

Zusätzlich, als verwandtes Symptom in manchen Report-Varianten: Die Positionstabelle `xrTable1` innerhalb von `Sub_POS` hat **zwei** Zeilen statt einer (eine vermutlich historische/überzählige erste Zeile plus die eigentliche Datenzeile), was zu Höhen- und Anzeigeproblemen führt.

**Ursache:** Die Kombination aus `KeepTogether=true` (Muster b) zur Absicherung von `sumCarryoverSum` und zu knapp bemessenen festen Höhen führt in Summe zu einem für den Kunden inakzeptablen Layout-Ergebnis. Der in `known-issues.md` Eintrag 4 als "kleineres Übel" akzeptierte Weißraum hat sich in der Praxis als zu störend herausgestellt.

**Fix (alle drei Teile zusammen anwenden):**

1. `KeepTogether` auf der Preiszeile (z. B. `xrTableRow1` in `Sub_POS`) UND auf dem `Sub_POS`-Band selbst wieder auf `false`/Standard zurücksetzen (Attribut entfernen oder explizit `"false"` setzen).
2. Mindesthöhe von `tb_ÜbertragOben` (und dem umgebenden `SubBand`, z. B. `Sub_UebertragOben`) auf **50** anheben — dabei **nur anheben, nie verringern**: ist bereits ein höherer Wert eingestellt (z. B. 60), diesen unverändert lassen.

   > **Verhältnis zu Muster (i), verbindlich seit 04.09.2026 — sonst widersprechen sich die beiden Muster:** Wird an derselben Stelle zusätzlich Muster (i) angewendet (bandeigenes `BeforePrint` mit `e.Cancel` gegen den Seite-1-Leerraum), dann **wandert die 50 vom Design in die Laufzeit**: der Design-Wert wird bewusst auf Mindestmaß abgesenkt (Muster (i), Punkt 4) und die echten 50 werden in einem `BeforePrint` wiederhergestellt (Muster (i), Punkt 3, Bedingung über `pageCounter`). Das „nie verringern" aus diesem Punkt gilt dann nur noch für den **wirksamen** Wert zur Druckzeit, nicht für den Design-Wert. Reihenfolge deshalb immer: erst prüfen, ob (i) zutrifft, dann (g) entsprechend als Laufzeitwert umsetzen — nicht beide Muster unabhängig voneinander auf denselben Design-Wert anwenden.
3. Falls `xrTable1` (in `Sub_POS`) zwei Zeilen enthält: die **obere** Zeile löschen, die verbleibende (Daten-)Zeile auf Höhe **55** setzen.

**Wichtiger technischer Hinweis zur Umsetzung:** Im Designer gesetzte `HeightF`-/`SizeF`-/`LocationFloat`-Werte landen nicht zwingend als direktes Attribut auf dem Element selbst, sondern häufig indirekt in einem separaten `<Localization>`-Block (`Component="#Ref-<ZielRef>"`). Vor dem Setzen einer Höhe IMMER auch dort nachsehen (siehe `known-issues.md`, Eintrag 6) — sonst wird eine vermeintlich fehlende Änderung übersehen oder ein neuer, redundanter Wert direkt am Element gesetzt, während der eigentlich wirksame Wert im `<Localization>`-Block unangetastet bleibt.

**Automatisierungssicherheit:**
- Punkt 1 (KeepTogether zurücknehmen) und Punkt 2 (Mindesthöhe 50): **Automatisch sicher, sobald eine bestätigte Referenzdatei vorliegt und denselben Zustand zeigt** (wie im bestätigten Fall vom 28.08.) — dann NICHT mehr als Vorschlag mit Rückfrage behandeln, sondern direkt umsetzen, ohne erneut nachzufragen. Nur wenn keine Referenz vorliegt oder sie dieses Muster nicht eindeutig bestätigt: *Vorschlag mit Rückfrage*.
- Punkt 3 (zweite Zeile in `xrTable1` löschen): ebenso **automatisch sicher bei bestätigter Referenz** — vor dem Löschen trotzdem gegenprüfen, dass die Referenz an derselben Tabelle (gleiche Zellnamen der Datenzeile, z. B. `tc_CellPos`) tatsächlich nur eine Zeile zeigt. Ohne Referenz: *Vorschlag mit Rückfrage*.

> **Wichtig, verbindlich seit 28.08. (siehe SKILL.md „Kundenvorgabe" und `known-issues.md` Eintrag 8):** Muster (g) wird in der Praxis besonders leicht vergessen, weil es NICHT im C#-Skript-Diff sichtbar ist — es lebt komplett in reinen XML-/Layout-Eigenschaften, teilweise indirekt im `<Localization>`-Block. Ein Fix-Lauf, der nur das Skript diffed und Muster (g) deshalb übersieht, gilt als unvollständig, selbst wenn der Skript-Teil für sich korrekt war. Bei jedem Lauf mit Referenzdatei ist deshalb die Pflicht-Checkliste aus SKILL.md Schritt 2 (KeepTogether auf allen Ebenen, Höhen inkl. Localization-Block, Zeilenanzahl kritischer Tabellen) verbindlich durchzugehen — unabhängig davon, ob der Skript-Diff bereits „sauber" aussah.

**Offene Frage / nicht abschließend geklärt:** Der genaue Kausal-Zusammenhang zwischen der Rücknahme von `KeepTogether` und dem ursprünglichen Muster-(b)-Risiko (aufgesplittete Preiszeile verfälscht `sumCarryoverSum`) ist nicht erneut aus der DevExpress-Rendering-Pipeline hergeleitet worden — dieser Eintrag dokumentiert den vom Kunden getesteten und für gut befundenen Zustand, nicht einen bewiesenen Mechanismus. Falls nach Anwendung dieses Fixes auf einer neuen Report-Variante ein falscher Übertragswert durch eine aufgesplittete Preiszeile auffällt, ist das ein Hinweis darauf, dass Muster (b) für DIESEN Report doch relevant bleibt und mit dem Kunden gemeinsam abgewogen werden sollte (Weißraum vs. korrekter Wert bei Seitenumbruch mitten in einer Position).

---

## (h) · Unterpunkt-ID `DXJ0001.E` · `AllowMarkupText` auf wachsender mehrzeiliger Zelle erzeugt Leerzeile — plus Folge-Padding auf nachfolgenden SubBands

**Vom Kunden in DevExpress bestätigt getestet (31.08.).** Siehe `known-issues.md` Einträge 14 und 15 für die vollständige Diagnose-Historie (inkl. widerlegter Zwischenhypothesen).

**Muster / Symptom:** Eine wachsende (`CanGrow`, kein `CanGrow="false"`), mehrzeilige (`Multiline="true"`) `XRTableCell`/`XRLabel` hat `AllowMarkupText="true"` gesetzt, obwohl die gebundene Expression keinerlei Markup-Tags erzeugt — oft zusammen mit einem nicht-standardmäßigen `LineSpacing`. Symptom beim Druck: eine zusätzliche Leerzeile/ein zu großer Abstand direkt NACH dem Ende dieser Zelle, bevor der nächste Inhalt beginnt. Charakteristisch: **kein** Zusammenhang mit Seitenumbrüchen (tritt auch bei vollständigem Druck auf einer einzigen Seite auf), aber ein **Schwellenwert-Zusammenhang mit der Zeilenanzahl** des Zelltexts (bei kurzem Text kein Effekt, ab einer gewissen Zeilenzahl — im bestätigten Fall ca. 8 Zeilen — deutlich sichtbar).

**Ursache:** DevExpress berechnet die automatische Wachstumshöhe (`CanGrow`) für mehrzeiligen Text im Markup-Modus (`AllowMarkupText="true"`) anders als im reinen Textmodus, mit einem Rundungsverhalten, das sich mit zunehmender Zeilenzahl zu einer vollen zusätzlichen Zeile aufsummieren kann.

**Fix:**
1. Prüfen, ob die Expression der betroffenen Zelle tatsächlich Markup-Tags erzeugt (`<b>`, `<br>`, `<color>` o. ä. im Expression-Text oder in den zugrundeliegenden Datenfeldern). Falls NICHT: `AllowMarkupText="true"` → `"false"` setzen (bzw. Attribut entfernen, da `false` Default ist).
2. Direkt anschließend prüfen, ob dadurch ein vorher (unbeabsichtigt) kompensierender Abstand zum nächsten Band/zur nächsten Zeile wegfällt (siehe `known-issues.md` Eintrag 15) — falls ja: `Padding` (Top) der ersten Zeile des/der unmittelbar nachfolgenden `SubBand`(s) moderat erhöhen, NICHT die übrigen Padding-Werte anfassen.

   > **Achtung, Positionsfalle (`known-issues.md` Eintrag 28):** `Padding` wird als **`Left,Right,Top,Bottom,Dpi`** serialisiert — der Top-Wert ist Position **3**. Die ursprüngliche Dokumentation dieses Punktes nannte die Änderung `10,0,0,0,254` → `10,10,0,0,254` einen „Top"-Fix; tatsächlich war das der **Right**-Wert und damit vertikal wirkungslos. Richtig ist z. B. `10,0,0,0,254` → `10,0,5,0,254`. Die Reihenfolge vor jeder Änderung mit Check `C17` (`scripts/validate_repx.py`) aus den `Padding.LeftF`/`Padding.RightF`-Bindungen der Datei selbst bestätigen lassen.

**Wichtiger technischer Hinweis:** Dieser Fehler ist weder im C#-Skript-Diff noch in einem reinen XML-Wohlgeformtheits-/Struktur-Check sichtbar — er betrifft eine einzelne, unscheinbare Attribut-Wert-Änderung mit rein visueller Auswirkung. Er lässt sich nicht durch Diff-Analyse allein erkennen, sondern nur durch das gemeldete Druckbild (oder testweises Ausprobieren bei Reports mit sehr langen mehrzeiligen Textfeldern).

> **Verbindlich seit 04.09.2026 (`known-issues.md` Eintrag 25):** Die beiden Punkte sind eine Einheit und werden **nur zusammen** angewendet. Punkt 2 ist die Kompensation für die durch Punkt 1 wegfallende Fehlhöhe — allein angewendet vergrößert er den Abstand zusätzlich und erzeugt genau das Symptom, das er beheben soll. Vor der Anwendung wird der Zustand von Punkt 1 **am konkreten Element** geprüft (`Ref`-gescopet, z. B. `Ref="228"` + `AllowMarkupText`), niemals über eine Zählung der Vorkommen in der ganzen Datei — ein Zahlenunterschied zur Referenz kann von einer völlig anderen Zelle stammen.

**Automatisierungssicherheit:** *Vorschlag mit Rückfrage* für beide Teile. Punkt 1 (AllowMarkupText) niemals blind scharf anwenden — immer erst als separate Diagnose-Testdatei ausliefern und den Nutzer die konkret auslösende (lange) Position testdrucken lassen, bevor ein produktiver Fix mit Backup/Changelog/work4all-log-Eintrag erfolgt. Punkt 2 (Padding) erst NACH bestätigtem Punkt 1 angehen, und die betroffenen Zellnamen/der genaue Top-Wert sind reportspezifisch — bei einer neuen Report-Variante neu bestätigen, nicht blind übertragen. Bei exakt diesem Report (`dxAio_template`) gelten beide Teile inzwischen als bestätigt und können bei erneutem Auftreten direkt angewendet werden.

---

## (i) · Unterpunkt-ID `DXJ0001.F` · Unterdrücktes Subband reserviert trotzdem Platz auf der Seite, auf der es unterdrückt wird

**Vom Kunden bestätigt getestet (02.–03.09., über eine sehr lange iterative Diagnose-Reihe).** Siehe `known-issues.md` Einträge 16–20 für die vollständige Diagnose-Historie inkl. widerlegter Zwischenhypothesen (u. a. eine anfänglich vermutete, nicht existente strukturelle DevExpress-Engine-Grenze, analog zu einem bekannten Crystal-Reports-Phänomen).

**Muster / Symptom:** Ein SubBand (typischerweise ein Folgeseiten-Tabellenkopf oder eine Übertrag-Zeile, die per `RepeatEveryPage`+Sichtbarkeitslogik nur ab Seite 2 gedruckt werden soll) wird auf Seite 1 zwar inhaltlich korrekt unterdrückt (kein sichtbarer Text/keine sichtbare Tabelle) — reserviert dort aber trotzdem seinen vollen Platz, sichtbar als ungewollter Leerraum. Charakteristisch: Die Unterdrückung selbst funktioniert (auf Folgeseiten erscheint der Inhalt korrekt), nur die Seite-1-Platzreservierung bleibt bestehen. Ein strukturell ähnliches, aber unauffälliges Nachbar-Subband (ohne dasselbe Symptom) kann fälschlich als Beweis für eine grundsätzliche, unvermeidbare Engine-Grenze missverstanden werden — meist liegt der eigentliche Unterschied stattdessen in einer der vier Ursachen unten.

**Ursache — vier zusammenwirkende, unabhängig auftretende Teilursachen (alle vier zusammen anwenden, nicht nur einzelne):**

1. **Bandeigenes `BeforePrint` fehlt.** Die Unterdrückung läuft ausschließlich über eine feingranulare `PrintOnPage`-Bedingung (z. B. Muster (a)/(c)/(f)) — die verhindert zwar den sichtbaren Inhalt, aber `PrintOnPage` feuert NACH der Platz-/Layoutberechnung, kann also keinen bereits reservierten Platz mehr zurückgeben.
2. **`CanGrow` dynamisch statt statisch umgeschaltet.** Wird `CanGrow` erst innerhalb von `PrintOnPage` gesetzt, hat das keine Wirkung mehr — die `CanGrow`-gesteuerte Layoutmessung ist zu diesem Zeitpunkt bereits abgeschlossen (siehe `repx-technical-notes.md`, Abschnitt „BeforePrint vs. PrintOnPage"). Wichtige Nebenerkenntnis: `CanGrow="true"` erlaubt nur WACHSEN über die zugewiesene Höhe hinaus, niemals SCHRUMPFEN darunter — für das Schrumpfen auf Seite 1 ist es also ohnehin der falsche Hebel.
3. **Verschachtelte Controls behalten ihre eigene, unabhängige Höhe.** Ein `XRLabel`/`XRTableCell` innerhalb des Subbands kann eine eigene, separat persistierte `HeightF`/`SizeF` tragen, die unabhängig von der Höhe der umgebenden Tabelle/des Bands ist — ein Schrumpfen der Tabelle allein lässt das Kind-Control auf seiner alten, größeren Höhe stehen.
4. **`HeightF` als direktes Attribut auf dem Band selbst ist wirkungslos.** Ein SubBand berechnet seine tatsächlich gedruckte Höhe aus seinem größten Kind-Element — ein direkt am Band gesetztes `HeightF`-Attribut wird von DevExpress beim Speichern schlicht verworfen (nicht mal mitgeschrieben). Der wirksame Weg, die Band-Standardhöhe zu setzen, ist ein `<Localization>`-Eintrag (`Path="HeightF"`), nicht das direkte Attribut — siehe `repx-technical-notes.md`, Abschnitt „Der `<Localization>`-Block".

**Fix (alle vier Teile zusammen anwenden — Teilfixe allein lösen das Symptom erfahrungsgemäß nicht vollständig):**

1. Das betroffene Subband strukturell in zwei Bänder aufteilen, falls es sowohl Berechnungscontrols (die auf JEDER Seite ungebremst feuern müssen, damit z. B. eine seitenübergreifende Summe weiterläuft) als auch reinen Anzeige-Inhalt enthält: ein Band behält nur die Berechnung (kein `e.Cancel`), ein zweites, neues Band bekommt nur den sichtbaren Inhalt plus ein **eigenes, bandeigenes** `BeforePrint` mit `e.Cancel = true`. Ist keine Berechnung betroffen (Band ist reiner Anzeige-Inhalt), genügt das bandeigene `BeforePrint` direkt am bestehenden Band, ohne Aufteilung.
2. Die Bedingung im bandeigenen `BeforePrint` MUSS auf einer seitenindex-unabhängigen, in `BeforePrint` bereits verlässlich verfügbaren Variable beruhen (z. B. einem einfachen, in einer anderen `BeforePrint`-Kette hochgezählten Seitenzähler wie `pageCounter`) — NICHT auf einer Variable, die erst in der `PrintOnPage`-Phase gesetzt wird (z. B. `_detailPrintedSoFar` aus Muster (f)): Diese ist auf Band-Ebene in `BeforePrint` nicht zuverlässig verfügbar, weil `PrintOnPage` der Kind-Controls dieses Bands zu diesem Zeitpunkt noch gar nicht gelaufen ist.
3. `CanGrow="true"` dauerhaft (statisch im XML, nicht dynamisch in `PrintOnPage`) auf den relevanten Zellen setzen. Verschachtelte Labels/Zellen, die selbst wachsen/schrumpfen sollen, bekommen ein **eigenes** `BeforePrint`, das ihre eigene `HeightF` passend zum Seitenzustand setzt (z. B. minimal, wenn noch nicht gedruckt werden soll, voller Wert sonst).

   > **Korrektur vom 04.09.2026 (`known-issues.md` Einträge 23 und 24), verbindlich:** Die Bedingung dieser Control-Handler MUSS ebenfalls `pageCounter` verwenden — nicht `_detailPrintedSoFar`. Die Phasen-Einschränkung aus Teilursache 1 gilt nicht nur für Bänder, sondern für **jedes** `BeforePrint`: ein erst in `PrintOnPage` gesetztes Flag ist dort immer `false`, die Controls blieben dann auf **allen** Seiten minimal und der Inhalt wäre nirgends sichtbar. Ebenso gilt: die Höhe der **Tabelle** wird in einem eigenen `BeforePrint` an der Tabelle gesetzt, nicht in ihrem `PrintOnPage`-Handler (dort ist das Layout bereits berechnet). Die vorhandene `PrintOnPage`-Logik bleibt als zweite, feinere Sicherheitsebene für `e.Cancel` unverändert bestehen.
   >
   > **Achtung bei Referenzdateien:** In der Diagnose-Zwischenfassung, aus der dieses Muster stammt, sind genau diese Control-Handler noch fehlerhaft (`_detailPrintedSoFar`). Sie dürfen nicht 1:1 übernommen werden — siehe `known-issues.md` Eintrag 27.
4. Die eigenen, separat persistierten Standardhöhen (`SizeF`/`HeightF`, ggf. im `<Localization>`-Block, siehe Ursache 4 und `known-issues.md` Eintrag 6) aller betroffenen verschachtelten Controls UND des äußeren Bands selbst auf einen kleinen Wert absenken. **Wichtig:** DevExpress erzwingt für `HeightF`/`H` einen Mindestwert von **5** — ein im Code gesetzter Wert unter 5 (z. B. `1`) wird beim Lesen/Anzeigen im Enduserdesigner-Properties-Panel stillschweigend auf 5 angehoben; direkt den erzwungenen Minimalwert 5 verwenden vermeidet eine unnötige, in der Praxis sichtbare Restunschärfe. **Praxiswert aus dem bestätigten Stand (04.09.2026):** dort stehen die verschachtelten Controls und die reinen Rechen-Bänder auf **1**, das sichtbare Anzeige-Band auf **5**. Beides ist in Ordnung — ein vorhandener Wert `1` wird nicht „korrigiert", er zeigt sich im Properties-Panel lediglich als 5.

**Wichtiger technischer Hinweis:** Dieser Fehler ist im reinen C#-Skript-Diff nur teilweise sichtbar (Fix-Teil 1 und 2 ja, Fix-Teil 3 und 4 nicht, wenn sie über den `<Localization>`-Block laufen) — ein vollständiger struktureller Diff (siehe `repx-technical-notes.md`, Abschnitt „Der `<Localization>`-Block") ist zwingend nötig, reiner Skript-Vergleich reicht nicht (vgl. `known-issues.md` Eintrag 8, dasselbe Muster wie bei Fix (g)).

**Automatisierungssicherheit:** *Vorschlag mit Rückfrage* für alle vier Teile — die Bandaufteilung (Teil 1) ist strukturell eingreifend genug, dass sie nicht ohne Bestätigung automatisch angewendet werden sollte, selbst bei vorliegender Referenzdatei. Automatisch sicher nur, wenn eine bestätigte Referenzdatei exakt denselben Bandaufbau (gleiche Aufteilung Berechnung/Anzeige) bereits zeigt.

---

## (j) · Unterpunkt-ID `DXJ0001.I` · Unsichtbarer Platzhalter mit falscher `Visible`-Localization verursacht Leerraum

**Vom Kunden bestätigt getestet (04.09.2026, Report `dxAio_template`, Sektion `Sub_Adresse`).** Siehe `known-issues.md` Einträge 29–31 für die Diagnose-Historie.

**Muster / Symptom:** Ein Steuerelement (im bestätigten Fall ein `XRLabel`, reiner Platzhalter ohne Anzeigezweck) soll unsichtbar sein und zeigt sich im Enduserdesigner-Properties-Panel trotzdem als `Visible = True`, obwohl das direkte XML-Attribut `Visible="false"` bereits korrekt gesetzt ist. Solange das Element sichtbar bleibt bzw. auch nur unsichtbar seinen alten Platz reserviert, entsteht bei wachsendem Nachbarinhalt (hier: eine wachsende Adresse) unnötiger Leerraum in der Sektion.

**Ursache:** Ein bereits vorhandener `<LocalizationItems>`-Eintrag für genau dieses Element (`Path="Visible"`, `Data="true"`) überschreibt das direkte `Visible`-Attribut — dieselbe Override-Mechanik, die für `HeightF`/`SizeF`/`LocationFloat` bereits bekannt ist (siehe `repx-technical-notes.md`, Abschnitt „Der `<Localization>`-Block"), hier erstmals konkret für `Visible` bestätigt. Ein einfaches Setzen des direkten Attributs allein reicht deshalb nicht aus. **Nicht zu verwechseln mit Eintrag 26:** Dort überschreibt ein `ExpressionBinding` den Design-Wert zur Laufzeit — hier überschreibt stattdessen ein `<LocalizationItems>`-Eintrag den Design-Wert bereits beim Laden/Anzeigen im Designer selbst. Beide Mechanismen vor einer Änderung getrennt prüfen, sie schließen sich nicht gegenseitig aus.

**Fix:**
1. Nicht nur das direkte `Visible`-Attribut setzen, sondern auch den zugehörigen `<LocalizationItems>`-Eintrag (`Path="Visible"`, `Component="#Ref-<RefDesElements>"`) auf denselben Wert (`Data="false"`) ändern — sonst bleibt die Designer-Anzeige/das Rendering beim alten Wert.
2. Reicht das reine Unsichtbarmachen nicht aus, um den reservierten Platz zurückzugeben (Platzhalter bleibt trotz `Visible="false"` raumgreifend, vgl. Muster (i) für dieselbe Grundproblematik bei Bändern statt einzelnen Controls): Das Platzhalter-Element komplett entfernen — inklusive aller zugehörigen Kind-Elemente (`ExpressionBindings`, `StylePriority` u. ä.) UND aller seiner eigenen `<LocalizationItems>`-Einträge. Anschließend die betroffenen `ItemN`-Sammlungen lückenlos neu nummerieren (siehe `known-issues.md` Eintrag 22 — sonst werden nachfolgende Einträge stillschweigend wirkungslos).
3. Den durch das Entfernen freigewordenen Platz gezielt einem oder mehreren fachlich sinnvollen Nachbar-Controls zuweisen, indem deren `<LocalizationItems>`-Eintrag für `SizeF`/`HeightF` (nicht das direkte Attribut, siehe Muster (i) Ursache 4) auf einen entsprechend größeren Wert gesetzt wird — bis maximal zur festen Höhe der umgebenden Sektion/des Bands.
4. Ergebnis strukturell gegen eine bestätigte Referenzdatei prüfen (name-basiert, `Ref`-Werte ignorieren, siehe `known-issues.md` Eintrag 29), nicht nur optisch im Designer.

**Wichtiger technischer Hinweis:** Dieser Fehler ist ohne den `<LocalizationItems>`-Abgleich nicht erkennbar — ein reiner Blick auf das direkte XML-Attribut täuscht einen bereits erfolgten Fix vor, obwohl die tatsächlich wirksame Eigenschaft (die Designer-Anzeige/das Rendering) noch den alten Wert nutzt. Kein automatisierter Check in `scripts/validate_repx.py` deckt diesen konkreten Fall ab (Kandidat für einen künftigen Check, der `Visible`-Attribute gegen `LocalizationItems`-Einträge desselben `Ref` abgleicht).

**Automatisierungssicherheit:** *Vorschlag mit Rückfrage.* Das komplette Entfernen eines Controls (Fix-Schritt 2) sowie das Vergrößern von Nachbar-Controls (Fix-Schritt 3) sind strukturell eingreifend und reportspezifisch — nicht ohne Bestätigung blind auf andere Reports/Sektionen übertragen. Bei exakt diesem Report (`dxAio_template`, Sektion `Sub_Adresse`) gilt der Fix inzwischen als bestätigt und kann bei erneutem Auftreten direkt angewendet werden.
