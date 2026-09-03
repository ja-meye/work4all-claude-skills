# Known Issues — lebendes Dokument

Diese Datei sammelt Fallen und Überraschungen, die über den generischen Fix-Katalog hinausgehen — Dinge, die sich erst beim tatsächlichen Bearbeiten/Testen konkreter Reports gezeigt haben. Bei jedem neuen Report-Lauf: erst hier nachsehen, ob ein beobachtetes Problem schon bekannt ist; am Ende eines Laufs: neue Erkenntnisse hier ergänzen (siehe SKILL.md, Schritt 9).

Format pro Eintrag: **Was passiert ist → Was man daraus lernt → Wie man es künftig vermeidet.**

---

## 1. `sumCarryoverSum()` benötigt zwingend das `<Summary Running="Group">`-Element (entgegen der Doku-Erwartung)

**Was passiert ist:** Beim ersten Fix-Durchlauf wurden vier `<Summary Ref="..." Running="Group" />`-XML-Elemente entfernt, die auf `lblCarryHelperUnten`, `lbllblUebertragUnten`, `lblCarryHelperOben` und `lb_UebertragOben` lagen. Die Begründung damals: die neuere `sumCarryoverSum([POS_GesPreis])`-Expression auf denselben Controls sah wie ein vollständiger Ersatz aus, und die offizielle DevExpress-Dokumentation zu `sumCarryoverSum` legt nahe, dass die Expression allein für den Carryover-Mechanismus ausreicht.

Nach Auslieferung meldete der Nutzer: das Wort "Übertrag €" erschien zwar korrekt (die Sichtbarkeits-Logik war ja separat repariert worden), aber der dazugehörige **Zahlenwert blieb leer** — auf mehreren Seiten, nicht nur den vorher fehlerhaften.

**Was man daraus lernt:** Die `Summary Running="Group"`-Elemente sind offenbar nicht redundant, sondern ein notwendiger, in der öffentlichen Doku nicht klar benannter Teil des Mechanismus, über den `sumCarryoverSum` seinen Wert überhaupt berechnet bzw. bereitstellt. Ohne dieses Element wird die Expression zwar weiterhin anstandslos geparst (kein Ladefehler, kein offensichtliches Warnsignal), liefert aber keinen Wert.

**Wie man es künftig vermeidet:** `<Summary>`-Elemente, die im Zusammenhang mit `sumCarryoverSum` stehen, **niemals automatisch entfernen** — auch nicht, wenn eine neuere Expression sie auf den ersten Blick zu ersetzen scheint. Diese Fixart gehört ausschließlich in die Kategorie "nur Verdacht — manueller Test nötig" (siehe `fix-catalog.md`): dokumentieren, dem Nutzer melden, aber nur nach explizitem Test im DevExpress Designer (Vorschau mit echten mehrseitigen Testdaten) tatsächlich entfernen. Die `validation-checklist.md`-Regel Nr. 5 (Summary-Anzahl vor/nach vergleichen) ist die technische Absicherung gegen ein Wiederholen dieses Fehlers — wenn sich die Zahl ändert, muss das eine bewusste, im Changelog explizit begründete Entscheidung sein.

**Behebung im Nachhinein:** Alle vier `Summary`-Elemente wurden unverändert wiederhergestellt; alle anderen Fixes (BeforePrint-Sabotage entfernt, KeepTogether korrigiert, neue Sichtbarkeitsbedingung mit Gesamtsumme) blieben bestehen. Nach Wiederherstellung: Übertragswert korrekt auf allen Seiten.

---

## 2. Gesamtsummen-Rückfallbedingung zeigt Übertrag an, bevor der Detailbereich überhaupt begonnen hat

**Was passiert ist:** Nach Auslieferung des ursprünglichen Fixes (inkl. der `_docGesamtGesPreis != 0`-Rückfallbedingung aus Muster (c) im Fix-Katalog) meldete der Nutzer in der Testphase zwei neue, verwandte Fälle:
- Ein über den Report-Parameter `ArgShowTitleOverview` gesteuerter Übersichtsbereich (mit einem verschachtelten Subreport, der u. a. Rabatt-/Zuschlagszeilen enthielt) war lang genug, um den Beginn des eigentlichen Detailbereichs auf eine Folgeseite zu verschieben. Übertrag erschien (mit leerem Wert) bereits am Ende der ersten Seite und am Anfang der Folgeseite — obwohl an beiden Stellen noch keine einzige Detailzeile gedruckt worden war.
- Ein sehr langer Kopftext allein (ganz ohne Übersichtsbereich) erzeugte dasselbe Symptom: Übertrag erschien leer auf Seiten, auf denen der Detailbereich noch gar nicht angefangen hatte.

**Was man daraus lernt:** Die Rückfallbedingung „Gesamtsumme des Belegs ungleich 0" ist notwendig (siehe Muster (c)), aber allein nicht hinreichend. Sie beantwortet nur „hat der Beleg überhaupt einen Betrag", nicht „ist der Detailbereich an dieser Stelle im Dokument schon dran". Jeder vorgelagerte Inhalt, der theoretisch mehrseitig werden kann (Kopftexte, optionale Übersichts-/Zusammenstellungs-Bereiche, verschachtelte Summen-Subreports), kann diese Lücke auslösen — nicht nur die ursprünglich gemeldeten zwei Fälle.

**Wie man es künftig vermeidet:** Bei JEDER Report-Variante, die eine Gesamtsummen-Rückfallbedingung für Übertrag/Folgeseiten-Sichtbarkeit verwendet, zusätzlich prüfen: Kann irgendein Inhalt VOR dem Detailbereich mehrseitig werden? Falls ja, ist Muster (f) im Fix-Katalog relevant — ein zusätzliches „Detailbereich hat begonnen"-Flag ergänzen, das über `PrintOnPage` an einer garantiert pro Detailzeile feuernden Kontrollzelle gesetzt wird, und alle Sichtbarkeitsbedingungen entsprechend erweitern.

---

## 3. Ein manueller Speichervorgang aus dem Visual-Studio-Designer kann per XML-Bearbeitung gesetzte Eigenschaften wieder verwerfen

**Was passiert ist:** Nachdem ein `KeepTogether="true"` per XML-Bearbeitung (nach der in `repx-technical-notes.md` beschriebenen Pipeline) auf einer Positionszeile gesetzt und ausgeliefert worden war, öffnete der Nutzer die Datei in Visual Studios DevExpress Report Designer, nahm dort eine unabhängige Layout-Änderung vor (Löschen einer ungenutzten Zeile in einer anderen Tabelle) und speicherte. Beim erneuten Hochladen war das zuvor gesetzte `KeepTogether="true"` auf der Positionszeile spurlos verschwunden (zurück auf Default `false`) — und der ursprüngliche Splitting-Bug (Übertrag wird zu früh mit vollem Wert angezeigt) trat dadurch erneut auf. Auffällig: bei diesem Speichervorgang wurden zusätzlich sämtliche `Ref`-IDs in der gesamten Datei neu durchnummeriert (Hinweis darauf, dass die Datei vollständig durch den Designer re-serialisiert wurde, nicht nur punktuell verändert).

**Was man daraus lernt:** Eine per XML-Bearbeitung gesetzte Eigenschaft ist nicht dauerhaft sicher, sobald die Datei erneut durch den Visual-Studio-Designer läuft — der Re-Serialisierungsprozess kann Properties verwerfen, die er aus irgendeinem Grund nicht als "explizit vom Nutzer im Designer gesetzt" erkennt. Das untergräbt punktuelle Einzel-Property-Fixes (wie `KeepTogether` auf genau einer Zeile), wenn der Kunde selbst regelmäßig im Designer weiterarbeitet.

**Wie man es künftig vermeidet:** Sicherheitskritische Layout-Eigenschaften wie `KeepTogether`, die für die Übertrag-Robustheit sorgen, nicht nur auf der einzelnen Zeile setzen, sondern zusätzlich auf der übergeordneten Band-/SubBand-Ebene (Bands unterstützen `KeepTogether` nachweislich auch direkt, siehe z. B. vorhandene `GroupFooterBand`-Elemente mit `KeepTogether="true"` in diesem Report). Das ist doppelte Absicherung mit vernachlässigbarem Risiko: Geht die Zeilen-Eigenschaft bei einem künftigen Designer-Speichervorgang erneut verloren, hält die Band-Ebene den Inhalt trotzdem zusammen. Bei jeder Übergabe einer bereits gefixten Datei, die der Kunde zwischenzeitlich selbst im Designer geöffnet hatte, routinemäßig die kompletten `KeepTogether`-Vorkommen in der Datei auflisten (nicht nur an der ursprünglich gefixten Stelle suchen) und mit dem erwarteten Zustand abgleichen, statt anzunehmen, dass frühere Fixes automatisch erhalten geblieben sind.

---

## 4. Freies Splitten langer Multiline-Texte über einen Seitenumbruch: Risiko von Rendering-Fehlern (Glyphen zerschnitten)

**Was passiert ist:** Als Alternative zu `KeepTogether="true"` (das gelegentlich Leerflächen am Seitenende erzeugt, wenn eine lange Beschreibung nicht mehr passt) wurde erwogen, die lange Beschreibung in eine eigene, frei splittende Zeile ohne `KeepTogether` auszulagern, damit nur der kurze Preis-Teil zusammengehalten werden muss. Der Kunde wies darauf hin, dass er genau das in der Vergangenheit bereits versucht hatte: Wird eine Multiline-Zelle/ein Label ohne `KeepTogether` über einen Seitenumbruch hinweg von DevExpress automatisch aufgeteilt, kann es zu fehlerhaftem Rendering kommen — einzelne Buchstaben wurden mitten in der Glyphe zerschnitten (z. B. bei „Building": der obere Teil von B und die i-Punkte auf einer Seite, der untere Teil des Wortes auf der nächsten).

**Was man daraus lernt:** DevExpress' eingebautes automatisches Text-Splitting über Seitenumbrüche (bei `Multiline`-Controls ohne `KeepTogether`) ist nicht garantiert sauber — es kann in bestimmten Konstellationen (Schriftart, Zellgröße, DevExpress-Version) zu visuell fehlerhaftem Rendering führen, nicht nur zu einem harmlosen Zeilenumbruch an unglücklicher Stelle. Das ist ein eigenständiges Risiko, unabhängig davon, ob der Text vorher im Skript manuell vorsortiert/aufgeteilt wurde oder nicht — sobald IRGENDEIN Multiline-Control ohne `KeepTogether` lang genug wird, um über die Seite zu laufen, greift derselbe DevExpress-interne Splitting-Mechanismus.

**Wie man es künftig vermeidet:** Bei der Abwägung „`KeepTogether=true` (mögliche Leerfläche) vs. frei splitten lassen (mögliches Rendering-Risiko)" ist `KeepTogether=true` die sicherere Standardempfehlung, sofern der Kunde nicht ausdrücklich bereit ist, den Splitting-Ansatz gezielt mit Testfällen (inkl. sehr langem Text, mehreren Schriftarten) in der DevExpress-Vorschau zu verifizieren, BEVOR er produktiv geht. Diese Fixart gehört in die Kategorie „nur Verdacht — manueller Test nötig" aus `fix-catalog.md`: nicht automatisch vorschlagen, geschweige denn automatisch umsetzen, ohne den Kunden explizit auf dieses konkrete Rendering-Risiko hinzuweisen (nicht nur auf die Leerflächen-Kosmetik). In diesem Fall hat sich der Kunde nach Abwägung bewusst für `KeepTogether=true` und gegen das Splitting-Risiko entschieden — Leerfläche gilt hier als das kleinere Übel gegenüber potenziell zerstörten Zeichen.

---

## 5. Ein direkter Diff gegen die Referenz ersetzt NICHT die XML/Skript-Paritätsprüfung — auch bei sonst strukturell fast identischen Dateien

**Was passiert ist:** Beim ersten Lauf mit Pflicht-Referenzvergleich (siehe Abschnitt „Referenzbeispiel" in SKILL.md) wurde das komplette Haupt-Skript 1:1 aus der bestätigten Referenzdatei übernommen, weil ein Zeile-für-Zeile-Diff zeigte, dass Zielskript-plus-Fix exakt der Referenz entspricht. Die Referenzdatei hatte dabei zwei Methoden komplett entfernt (`GROUP_ERP_Nummer_AfterPrint`, `GroupFooter_Summen_AfterPrint`, beide vorher nur auskommentierten Code ohne aktive Logik). Beim reinen Skript-Diff sah das sauber aus. Erst die Validierungs-Checkliste (Punkt 3/6: Scripts-On*-Referenzen gegen tatsächlich vorhandene Methoden) deckte auf, dass die Ziel-XML an zwei Stellen (`GROUP_ERP_Nummer`-Band, `GroupFooter_Summen`-Band) noch die alte `OnAfterPrint="..."`-Verdrahtung auf genau diese jetzt gelöschten Methoden trug — die Referenzdatei hatte an denselben Stellen offenbar in einem früheren, nicht separat dokumentierten Schritt auch die XML-Wiring entfernt, aber das ging aus dem reinen Skript-Diff nicht hervor, weil Skript und XML-Wiring in der .repx an komplett unterschiedlichen Stellen der Datei liegen.

**Was man daraus lernt:** Ein direkter Diff der Referenz-Datei gegen die neue Variante — selbst wenn beide strukturell nahezu identisch sind und der Diff für sich genommen sauber aussieht — deckt nur das ab, was tatsächlich verglichen wurde. Wird nur das Skript diff-verglichen und übernommen (weil es sich um den offensichtlich fixierten Teil handelt), können an anderer Stelle (hier: XML-Bandverdrahtung) Altlasten zurückbleiben, die in der Referenzdatei bereits bereinigt waren, aber nicht Teil des betrachteten Diffs waren.

**Wie man es künftig vermeidet:** Die Validierungs-Checkliste (`validation-checklist.md`, insbesondere Punkt 3 „Scripts-On*-Referenzen lösen sich auf eine definierte Methode auf" und Punkt 6 „Symmetrische Entfernung nach jeder Handler-Löschung") ist PFLICHT und ersetzt NICHT der Referenzvergleich, sondern ergänzt ihn — auch wenn ein Referenzvergleich vorliegt und der Skript-Diff sauber aussieht. Baseline-vs-Fixed-Vergleich der „fehlenden Methoden"-Liste (siehe Checkliste Punkt 3) fängt genau diese Art von Lücke zuverlässig ab, bevor ausgeliefert wird.

---

## 6. DevExpress speichert manche im Designer gesetzten Werte NICHT als direktes XML-Attribut, sondern in einem separaten `<Localization>`-Block

**Was passiert ist:** Der Kunde hat in Visual Studio die Höhe von `tb_ÜbertragOben` (Band `Sub_UebertragOben`) manuell von 40 auf 50 erhöht und danach gespeichert. Ein Diff der Elemente selbst (`tb_ÜbertragOben`, `Sub_UebertragOben`) zeigte dabei zunächst KEINE Änderung — `HeightF`/`SizeF` standen an keiner Stelle direkt als Attribut auf diesen Elementen, weder vorher noch nachher. Erst ein vollständiger, positionsweiser Baumvergleich der gesamten Datei (nicht nur der vermuteten Elemente) deckte die tatsächliche Änderung auf: Sie steckte in einem separaten `<Localization>`-Element weiter oben in der Datei, in Einträgen der Form `<ItemN Ref="..." Component="#Ref-<ZielRef>" Culture="Default" Path="HeightF" Data="40" />` (bzw. `Data="50"` nachher) sowie einem analogen Eintrag mit `Path="SizeF" Data="1750,40"` → `Data="1750,50"`. `#Ref-<ZielRef>` verweist dabei per `Ref`-Nummer auf das eigentliche Element (hier `Sub_UebertragOben` bzw. `tb_ÜbertragOben`).

**Was man daraus lernt:** DevExpress serialisiert offenbar bestimmte im Designer manuell überschriebene Eigenschaften (u. a. `HeightF`, `SizeF`, `LocationFloat`, teils auch `Visible`) nicht zwingend als Attribut direkt am Element, sondern als indirekten Eintrag in einem globalen `<Localization>`-Block, der über `Component="#Ref-N"` auf das Ziel-Element zeigt (Culture ist dabei i. d. R. `Default`, kann aber auch `en`/`fr`/`nl` für sprachspezifische Overrides sein — bei mehrsprachigen Reports IMMER alle Culture-Varianten für denselben `Component`-Ref prüfen, nicht nur `Default`). Wer nur das vermutete Element selbst nach einer Höhen-/Positionsänderung durchsucht, findet nichts und schließt fälschlich, es gäbe keine Änderung.

**Wie man es künftig vermeidet:** Bei JEDER Höhen-/Größen-/Positions-Änderung, die im Designer vorgenommen wurde (erkennbar am Dateinamen oder an der Aussage des Nutzers, „das habe ich in Visual Studio geändert"): zusätzlich zum direkten Element-Attribut-Vergleich IMMER auch nach `Component="#Ref-<RefDesElements>"` im gesamten Dokument suchen, bevor man „keine Änderung gefunden" meldet. Noch zuverlässiger: einen vollständigen positionsweisen Baumvergleich der GESAMTEN Datei durchführen (alle Elemente in Dokumentreihenfolge paarweise vergleichen, `Ref`-Werte dabei ignorieren) statt nur gezielt einzelne vermutete Elemente zu diffen — das deckt genau solche indirekten Speicherorte zuverlässig auf. Beim Anwenden eines Höhen-Fixes auf eine neue Report-Variante entsprechend NICHT nur ein Attribut auf dem Element setzen, sondern prüfen, ob in dieser Variante ein `<Localization>`-Eintrag für dasselbe Element/dieselbe Eigenschaft existiert, und ggf. dort den Wert setzen (oder einen neuen Eintrag anlegen, falls noch keiner existiert).

---

## 7. Ein Visual-Studio-Speichervorgang kann rein kosmetische Einträge in der `<Localization>`-Sektion umsortieren, ohne dass sich Inhalt oder Verhalten ändert

**Was passiert ist:** Beim selben Speichervorgang wie in Eintrag 6 wurden zusätzlich acht `<Localization>`-Einträge mit `Path="Title"` umsortiert — es handelt sich um die Anzeige-Kategorienamen der Report-Parameter im Designer-Parameter-Panel (Werte wie „MwSt", „SettingsLogo", „CurrentTenant", „Design", „General" u. Ä.). Die acht Einträge blieben inhaltlich als Menge exakt gleich, wurden aber unterschiedlichen `Component`-/`Ref`-Nummern zugeordnet als vorher — ein Diff auf Basis fixer `Ref`-Zuordnung meldet hier acht „Änderungen", obwohl sich am gedruckten Report-Ergebnis nichts geändert hat.

**Was man daraus lernt:** Nicht jede vom Designer beim Speichern verursachte Verschiebung ist eine Regression im Sinne von `known-issues.md` Eintrag 3 (verlorene Eigenschaft). Manche Verschiebungen sind reine Neuordnung rein designtime-relevanter Metadaten (hier: Kategorie-Beschriftungen im Parameter-Panel), die keinerlei Auswirkung auf den gedruckten Report haben.

**Wie man es künftig vermeidet:** Bei einem `Ref`-wertbasierten Vergleich nach dem Speichern in Visual Studio nicht vorschnell von einer Regression ausgehen, nur weil sich `Ref`-Zuordnungen innerhalb einer kleinen, lokal zusammenhängenden Gruppe von `<Localization>`-Einträgen mit `Path="Title"` verschoben haben. Prüfen, ob es sich um reine Parameter-Kategorie-Beschriftungen handelt (erkennbar an `Path="Title"` und Klartext-Kategorienamen als `Data`-Wert) — wenn ja, als harmlos einstufen und nicht melden, sofern die Wertemenge unverändert bleibt. Bei `Path`-Werten mit Layout-Bezug (`HeightF`, `SizeF`, `LocationFloat`, `Visible`) dagegen immer genau hinschauen (siehe Eintrag 6).

---

## 8. Ein reiner Skript-Diff übersieht Muster (g) komplett — Fix-Lauf war unvollständig, obwohl der Skript-Teil korrekt war

**Was passiert ist:** Im ersten Durchlauf mit Pflicht-Referenzvergleich wurde die Diagnose ausschließlich über einen Diff des dekodierten C#-Hauptskripts geführt (Muster a, c, d, f wurden dabei korrekt erkannt und behoben, inkl. sauberer Validierung). Der Fix wurde als „fertig" ausgeliefert. Der Kunde meldete danach im Test: `tb_ÜbertragOben` hatte weiterhin Höhe 40 statt 50, `xrTable1` in `Sub_POS` hatte weiterhin zwei Zeilen statt einer (`xrTableRow18` war nicht gelöscht), und `Sub_POS` trug weiterhin `KeepTogether="true"`. Alle drei Punkte waren in der bestätigten Referenzdatei bereits korrekt (Muster g) — sie wurden schlicht nicht geprüft, weil sie im Skript-Diff nicht auftauchen: `KeepTogether` ist ein XML-Attribut auf Zeile/Band, die beiden Höhen steckten indirekt im `<Localization>`-Block (siehe Eintrag 6), und die doppelte Zeile ist eine reine Tabellenstruktur-Frage. Nach Nachbesserung (separater Lauf) fiel dem Kunden zusätzlich auf, dass gegenüber der Referenz auch etliche tote Variablen und drei unverdrahtete „Trials"-Methoden im Skript stehen geblieben waren — die Skript-Hygiene (Muster e) war schlicht nicht durchgeführt worden, weil sie zu diesem Zeitpunkt als optional gegolten hatte.

**Was man daraus lernt:** „Ich habe die Referenz mit dem Skript verglichen" ist NICHT dasselbe wie „ich habe die Referenz strukturell vollständig verglichen". Ein Fix-Katalog-Muster kann komplett außerhalb des Skripts leben (reine XML-/Layout-Eigenschaften) und wird von einem reinen Skript-Diff dann grundsätzlich nicht gefunden, egal wie sorgfältig dieser Diff war. Ebenso: Skript-Hygiene als „optional, nur auf Wunsch" einzustufen führt in der Praxis dazu, dass sie in einem hektischen oder fokussierten Lauf schlicht vergessen wird, obwohl die Referenz sie längst enthält.

**Wie man es künftig vermeidet (verbindliche Konsequenz, siehe SKILL.md „Kundenvorgabe"):**
1. Bei JEDEM Lauf mit Referenzdatei zusätzlich zum Skript-Diff explizit die Pflicht-Checkliste aus SKILL.md Schritt 2 abarbeiten: alle `KeepTogether`-Vorkommen auflisten und abgleichen, alle Höhen/Größen inkl. `<Localization>`-Block der relevanten Elemente abgleichen, Zeilenanzahl kritischer Tabellen abgleichen.
2. Skript-Hygiene (Muster e) ist ab sofort PFLICHT-Bestandteil jedes Laufs, nicht mehr optional — aber mit klarer Abgrenzung: nur Variablen/Methoden entfernen, die nachweislich (per Textsuche verifiziert) nirgends mehr aktiv gelesen/aufgerufen werden. Variablen, die zu einer erkennbar eigenständigen, anderen Funktionalität gehören (im konkreten Fall: `sum_EKTO_4a/4b/13b/3a` für eine Steuertext-/Sachkonto-Berechnung, die die Referenz durch einen komplett neuen Subreport ersetzt hatte), gehören NICHT zur Hygiene, sondern zu einem eigenständigen, hier bewusst ausgeklammerten Funktionsumbau — diese Abgrenzung muss bei jedem Lauf neu bewusst getroffen werden, nicht pauschal "alles was die Referenz auch entfernt hat" übernehmen.
3. Ein Fix-Lauf gilt erst als abgeschlossen, wenn beide Punkte (voller struktureller Diff UND Hygiene) durchlaufen wurden — nicht schon, wenn der Skript-Teil sauber validiert.

---

## 9. Verlust des UTF-8-BOM bei einem reinen XML-Bearbeitungsschritt (kein Skript-Reencoding)

**Was passiert ist:** Nach dem ersten Fix-Lauf (Skript-Änderungen, korrekt inkl. BOM zurückgeschrieben) wurden in zwei nachfolgenden Läufen zusätzliche reine XML-Änderungen vorgenommen (KeepTogether-Attribut entfernen, Localization-Werte ändern, eine Tabellenzeile löschen — alles ohne den Skript-Reencoding-Schritt). Dabei wurde die Datei mit `encoding='utf-8-sig'` gelesen (das entfernt beim Lesen automatisch die BOM) und anschließend mit `open(..., 'w', encoding='utf-8', newline='')` zurückgeschrieben, OHNE die BOM manuell wieder voranzustellen. Zwei komplette, an den Kunden ausgelieferte Dateien in Folge hatten dadurch kein BOM mehr (Datei begann direkt mit `<?xml...` statt mit den BOM-Bytes `EF BB BF`). Erst beim dritten Lauf (nach einer erneuten reinen Skript-Änderung, bei der die BOM-Zeile im Code zufällig wieder vorhanden war) fiel per Stichprobenprüfung auf, dass die beiden vorherigen Dateien das BOM verloren hatten.

**Was man daraus lernt:** Der BOM-Verlust passiert lautlos — kein Parse-Fehler, keine sichtbare Diff-Auffälligkeit im Skript- oder XML-Inhalt selbst, weil nur das allererste Zeichen der Datei betroffen ist. Er passiert nicht beim eigentlichen Skript-Escaping-Schritt (der aus `repx-technical-notes.md` bereits die BOM-Regel kennt), sondern gerade bei "kleinen", rein XML-fokussierten Nachbesserungs-Läufen, bei denen man das BOM-Handling leicht vergisst, weil man "ja nur eine Kleinigkeit im XML ändert".

**Wie man es künftig vermeidet:** Nach JEDEM Schreibschritt (nicht nur nach Skript-Änderungen) programmatisch prüfen: `open(datei, 'rb').read(3) == b'\xef\xbb\xbf'`. Diese Prüfung ist jetzt fester Bestandteil der Validierungs-Checkliste (Punkt 9) und muss nach jedem einzelnen Zwischenstand laufen, nicht nur einmal ganz am Ende der Bearbeitungskette. Beim Schreiben selbst: `f.write('﻿' + content)` explizit in jedem Schreibschritt, der aus einer mit `utf-8-sig` gelesenen Zwischendatei erzeugt wird — unabhängig davon, ob dieser Schritt das Skript oder nur die reine XML anfasst.

---

## 10. Falsch-Positiv bei der Scripts-Paritätsprüfung durch ungescopte Regex

**Was passiert ist:** Ein Validierungs-Check der Form „suche `On\w+=\"(\w+)\"` in der kompletten Roh-XML (außerhalb der `ScriptsSource`-Werte)" meldete sowohl in der Zieldatei als auch in der unabhängig davon bestätigten Referenzdatei ein vermeintlich fehlendes Methoden-Symbol namens `false`. Bei näherer Untersuchung stellte sich heraus: Das Attribut `PrintOnEmptyDataSource="false"` auf einem `ReportPrintOptions`-Element enthält als Teilstring zufällig `On...="false"` und wurde von der ungescopten Regex fälschlich als Event-Verdrahtung interpretiert.

**Was man daraus lernt:** Weil der Fund in BEIDEN Dateien (Ziel und Referenz) identisch auftrat, war er kein Hinweis auf einen echten Fehler — aber das ist Glück, kein verlässliches Kriterium. Eine Prüfung, die nicht syntaktisch auf den tatsächlichen Kontext (`<Scripts .../>`-Elemente) beschränkt ist, kann durch zufällige Namensüberschneidungen sowohl Fehlalarme als auch (im ungünstigeren Fall) tatsächliche Lücken verdecken.

**Wie man es künftig vermeidet:** Die Scripts-Paritätsprüfung IMMER zweistufig aufbauen: zuerst alle `<Scripts ... />`-Elemente per eigenem Pattern isolieren, dann NUR innerhalb dieser Treffer nach `On\w+="(\w+)"` suchen. Ein so gescopter Check sollte auf einer sauberen Datei 0 fehlende Methoden melden. Siehe `repx-technical-notes.md`, Abschnitt „XML/Skript-Paritätsregel", und `validation-checklist.md` Punkt 3.

---

## 11. Zeitstempel im Dateinamen war falsch, weil die Session-Umgebung in UTC läuft, nicht in der Zeitzone des Kunden

**Was passiert ist:** Der in SKILL.md vorgeschriebene Zeitstempel wurde mit einem bloßen `date '+%Y-%m-%d_%H-%M'`-Aufruf ohne Zeitzonenangabe erzeugt. Die Session-Umgebung lief dabei in UTC, der Kunde aber in Europe/Berlin (zu diesem Zeitpunkt UTC+2, Sommerzeit) — die erzeugten Zeitstempel waren dadurch durchgängig zwei Stunden zu früh gegenüber der tatsächlichen Uhrzeit beim Kunden.

**Was man daraus lernt:** `date` ohne explizite Zeitzone spiegelt die Zeitzone der Ausführungsumgebung wider, nicht die des Nutzers — das ist bei einer Cloud-Sandbox nicht automatisch dieselbe Zeitzone, auch wenn man es beim Arbeiten leicht annimmt. Der Fehler fällt nicht durch einen Parse- oder Validierungsfehler auf, sondern nur durch einen Soll-Ist-Abgleich der Uhrzeit mit dem Kunden.

**Wie man es künftig vermeidet:** Zeitstempel für Dateinamen IMMER mit expliziter Zielzeitzone erzeugen: `TZ=Europe/Berlin date '+%Y-%m-%d_%H-%M'`. Niemals bloßes `date` ohne `TZ=`-Präfix verwenden, auch wenn die Session-Uhrzeit auf den ersten Blick plausibel wirkt. Siehe SKILL.md Schritt 8.

---

## 12. Skill kennt bisher nur referenznahe Reports — stärker abweichende, ältere Varianten sind ein bekannter blinder Fleck

**Was passiert ist:** Der Kunde hat explizit darauf hingewiesen (28.08.2026, ohne dass es an einem konkreten Report aufgefallen wäre): Alle bisherigen Fix-Läufe dieser Skill betrafen Reports, die strukturell nah an der bestätigten Referenzdatei liegen. Es gibt im Feld daneben deutlich ältere Reports mit wesentlich stärker abweichender Struktur, die noch nicht durch diese Skill gelaufen sind. Bei diesen wird ein Fix voraussichtlich tiefer eingreifen müssen — z. B. müssen eigene Berechnungsfelder mit eingearbeitet werden, die es in der Referenz so nicht gibt, oder Bandnamen/Mechanik weichen stärker ab, als der aktuelle Fix-Katalog vorsieht.

**Was man daraus lernt:** Der Fix-Katalog und diese known-issues.md sind bisher ausschließlich aus Läufen an referenznahen Reports entstanden — sie sind kein Nachweis dafür, dass die Muster auch auf strukturell stark abweichende, ältere Reports zutreffen. Das ist kein Fehler, der schon aufgetreten ist, sondern eine bekannte, vom Kunden selbst benannte Lücke im bisherigen Abdeckungsgrad der Skill.

**Wie man es künftig vermeidet:** Bei jeder neuen `.repx`, die in Schritt 1 (Rohdaten extrahieren) schon strukturell deutlich von den bekannten Bandnamen/Mustern abweicht (siehe SKILL.md „Bekannte Grenzen"): das dem Nutzer proaktiv melden, nicht versuchen, den bestehenden Fix-Katalog gewaltsam passend zu machen. Langsamer und vorsichtiger vorgehen als bei einem referenznahen Report, explizit mehr Rückfragen stellen statt „automatisch sicher" einzustufen, und nach Abschluss unbedingt einen neuen Eintrag hier sowie ggf. ein neues Muster im Fix-Katalog ergänzen — nur so wächst die Abdeckung schrittweise, wie vom Kunden angekündigt ("das wird nach und nach kommen").

---

## 13. Fehlende `\r`-Normalisierung vor dem finalen Escaping erzeugt eine Leerzeile nach JEDER Skriptzeile

**Was passiert ist:** Beim Zurückschreiben eines bearbeiteten Skripts wurde die Escaping-Pipeline aus `repx-technical-notes.md` Schritt 4 angewendet, aber Schritt 4.3 wurde direkt als `script.replace('\n', '&#xD;&#xA;')` auf dem Ergebnis von Schritt 2 (`html.unescape(...)`) ausgeführt. Nach `html.unescape` enthält der Skript-String an jedem ursprünglichen Zeilenumbruch aber ein echtes `\r\n`-Paar (CR+LF), keine reinen `\n`. Die direkte Ersetzung traf also nur das `\n` jedes Paares und ließ das zugehörige `\r` als rohes, nicht escapetes Zeichen unmittelbar vor dem neu erzeugten `&#xD;&#xA;` stehen. Ausgeliefert wurden zwei `.repx`-Dateien (Ziel- und Referenzdatei), bei denen dadurch **jede einzelne Zeile des gesamten Skripts** (nicht nur die bearbeiteten Stellen) beim Öffnen im Editor/Designer von einer Leerzeile gefolgt war — weil beim Zurückschreiben immer der komplette Skript-Attributwert neu escaped wird, nicht nur der geänderte Teil. Der Kunde hat das per Screenshot des dekodierten Skripts gemeldet.

**Was man daraus lernt:** Die Datei blieb trotz des Fehlers wohlgeformtes XML und lud anstandslos — ein reiner XML-Well-formedness-Check (Validierungspunkt 1) fängt diesen Fehler nicht ab, weil ein rohes `\r` in einem Attributwert syntaktisch gültig ist. Der Fehler zeigt sich ausschließlich beim Betrachten des dekodierten Skripts (Designer oder Code-Editor), nicht im rohen XML-Diff gegen die Vorversion, wenn dieser nur auf Wohlgeformtheit und Strukturgleichheit prüft. Das macht ihn besonders tückisch: Alle bisherigen Validierungspunkte (Ref-Duplikate, Scripts-Parität, Klammernbalance, Summary-Anzahl, BOM) wären hier grün gewesen.

**Wie man es künftig vermeidet:** Zeilenenden direkt nach dem Unescapen (Schritt 2) oder spätestens unmittelbar vor der finalen Kodierung (Schritt 4.3) einmalig auf reines `\n` normalisieren (`text.replace('\r\n', '\n').replace('\r', '\n')`), sodass zum Zeitpunkt von `\n` → `&#xD;&#xA;` garantiert keine rohen `\r`-Zeichen mehr im String vorkommen. Siehe `repx-technical-notes.md` Schritt 4.3 (aktualisiert) für die korrigierte Pipeline. Zusätzlich als eigenständigen Validierungs-Check ergänzt (siehe `validation-checklist.md` Punkt 12): nach dem Schreiben den rohen, noch escapten `ScriptsSource`-Wert auf verbliebene literale `\r`/`\n`-Zeichen prüfen — muss 0 sein, sonst wurde die Normalisierung nicht oder falsch angewendet. Dieser Check hätte den Fehler vor der Auslieferung gefangen.

---

## 14. `AllowMarkupText="true"` + custom `LineSpacing` auf einer wachsenden (`CanGrow`) mehrzeiligen `XRTableCell` erzeugt eine zusätzliche Leerzeile — CONFIRMED (31.08., vom Kunden testgedruckt und bestätigt)

**Was passiert ist:** Der Kunde meldete eine Leerzeile/einen zu großen Abstand unmittelbar VOR der "Rabatt 10 %"-Zeile — aber nur bei Positionen mit langer, mehrzeiliger Bezeichnung (beobachtet ab ca. 8 Zeilen; bei ~3 Zeilen kein Effekt) und ausdrücklich auch dann, wenn die Position komplett auf einer Seite gedruckt wurde (Seitenumbruch damit als Ursache ausgeschlossen). Erste Hypothese (eine eigene, immer sichtbare `Detail`-Band-Höhe im Summen-Subreport) wurde durch genau diese Beobachtung widerlegt, da sie einen konstanten, textlängen-unabhängigen Effekt vorhergesagt hätte.

Strukturanalyse ergab: Die Bezeichnungszelle `tbl00` (in `Sub_POS` → `xrTable1` → `xrTableRow1`, gebunden an das Berechnungsfeld `_BezeichnungAndArtNrPOS`) hatte `AllowMarkupText="true"` zusammen mit einem nicht-standardmäßigen `LineSpacing="1.1"` gesetzt — obwohl der Expression-Text (ArtikelNr + Bezeichnung + optionale interne Bemerkung, per `NewLine()` getrennt) keinerlei Markup-Tags erzeugt. Diese Kombination ist ein bekannter DevExpress-Fallstrick: Die automatische Höhenberechnung (`CanGrow`) für mehrzeiligen Text rechnet im Markup-Modus anders (mit Rundungsfehlern) als im reinen Textmodus, und der Fehler akkumuliert bzw. wird erst ab einer bestimmten Zeilenzahl als volle zusätzliche Leerzeile sichtbar — passt exakt zum beobachteten Schwellenwert-Verhalten.

Ein Nebenverdacht (`tc_GPreis` hat `RowSpan="3"` in einer `xrTable1`, die jetzt nur noch 1 Zeile hat) wurde geprüft und verworfen: Dieser Zustand ist in Ziel- UND Referenzdatei byte-identisch vorhanden, also kein Unterschied und keine plausible Ursache für ein Symptom, das (soweit bekannt) nur in der Zieldatei auftrat.

**Fix (vom Kunden per Testdruck bestätigt):** `AllowMarkupText="true"` → `"false"` auf `tbl00` gesetzt (bzw. beim erneuten Speichern im DevExpress-Designer wird das Attribut, da `false` der Default ist, teilweise ganz aus der XML entfernt — funktional identisch). `LineSpacing="1.1"` unverändert gelassen (nicht Teil der Ursache, nur der Auslöser in Kombination mit `AllowMarkupText`). Ergebnis: Leerzeile vollständig verschwunden, keine sichtbare Veränderung an der Bezeichnung selbst.

**Was man daraus lernt:** `AllowMarkupText="true"` auf einer wachsenden, mehrzeiligen `XRTableCell`/`XRLabel` sollte grundsätzlich hinterfragt werden, wenn die dahinterliegende Expression keine Markup-Tags erzeugt — es ist dann reines, unnötiges Risiko für genau diese Art von höhenabhängigem Rendering-Fehler. Der Fehler ist rein visuell/Layout-seitig, erzeugt keinen XML- oder Skript-Diff-Auffälligkeit (Attribut-Wert-Änderung an einer unscheinbaren Stelle) und wird von keinem der bisherigen Validierungspunkte (1–12) erfasst.

**Wie man es künftig vermeidet:** Bei JEDER wachsenden (`CanGrow`, kein explizites `CanGrow="false"`), mehrzeiligen (`Multiline="true"`) Text-/Tabellenzelle mit gesetztem `AllowMarkupText="true"`: prüfen, ob die gebundene Expression tatsächlich Markup-Tags (`<b>`, `<br>`, `<color>` o. ä.) erzeugt. Falls nicht: `AllowMarkupText` auf `false` als Verdachtsmoment notieren, nicht automatisch scharf ändern (siehe Automatisierungssicherheit unten), aber bei einem gemeldeten Symptom "Leerzeile/Abstand bei langem Text, unabhängig von Seitenumbruch" als ersten Kandidaten prüfen. Neuer Fix-Katalog-Eintrag: siehe `fix-catalog.md` Muster (h).

**Automatisierungssicherheit:** *Vorschlag mit Rückfrage* — vor dem scharfen Anwenden immer erst als reine Diagnose-Testdatei (kein produktives Update, kein Log-Eintrag) ausliefern und vom Nutzer per Testdruck der auslösenden (langen) Position gegenprüfen lassen, wie in diesem Fall geschehen. Erst nach Bestätigung als produktiver Fix mit Backup/Changelog/work4all-log übernehmen.

---

## 15. Folgefund: Nach Behebung von Eintrag 14 sitzt die nächste `SubBand`-Zeile (Rabatt/Rabatt2/Liefertermin/Zolltarifnummer) zu eng am vorherigen Text

**Was passiert ist:** Unmittelbar nachdem der Fix aus Eintrag 14 bestätigt getestet war ("Leerzeile ist jetzt komplett weg"), meldete der Kunde ein neues, direkt anschließendes Symptom: Die Rabatt-Zeile sitzt jetzt sehr nah am vorherigen Text — der Wegfall der (fehlerhaften) zusätzlichen Höhe hat offenbar einen Abstand mit entfernt, der visuell als "ausreichend Luft" gewirkt hatte, obwohl er eigentlich Symptom des Fehlers war.

**Was man daraus lernt:** Ein Höhenberechnungs-Fix an einer wachsenden Zelle kann einen vorher (unbeabsichtigt) kompensierenden Abstand mit entfernen. Das ist kein neuer, unabhängiger Fehler, sondern eine direkte, erwartbare Nebenwirkung des vorherigen Fixes — nach jedem Höhen-/Wachstums-Fix an einer Zelle bewusst auch die unmittelbar nachfolgenden Bänder/Zeilen auf ihren Abstand zum vorherigen Inhalt hin gegenprüfen, nicht nur die reparierte Zelle selbst isoliert betrachten.

**Fix (vom Kunden selbst im DevExpress-Designer ermittelt und bestätigt):** `Padding` (Top) von `0` auf `10` erhöht, auf den Zellen der jeweils ersten Zeile der vier direkt auf `Sub_POS` folgenden `SubBands`:
- `Sub_Rabatt` → `xrTableRow4` → `xrTableCell18` ("Rabatt")
- `Sub_Rabatt2` → `xrTableRow13` → `xrTableCell48` ("Rabatt 2")
- `Sub_LieferterminPOS` → `xrTableRow39` → `xrTableCell185` ("LTDatumPOS")
- `Sub_ZollinformationenPOS` → `xrTableRow55` → `xrTableCell191` ("Zolltarifnummer")

Padding-Format ist `Left,Top,Right,Bottom,Dpi` — nur der zweite Wert (Top) wird geändert, die übrigen Werte bleiben unangetastet (in der Zieldatei z. B. `10,0,10,0,254` → `10,10,10,0,254`; in der Referenzdatei war der Right-Wert bereits `0` statt `10` — dieser vorbestehende Unterschied zwischen Ziel- und Referenzdatei ist NICHT Teil dieses Fixes und wurde bewusst unverändert gelassen).

**Wie man es künftig vermeidet:** Diese vier Zellen sind für DIESEN Report konkret bestätigt — bei einer neuen Report-Variante mit strukturell anderen Namen ist das Muster (Top-Padding der ersten Zeile jedes direkt auf `Sub_POS` folgenden `SubBand`) zu übertragen, aber die betroffenen Zellnamen und der genaue Top-Wert müssen für den jeweiligen Report neu bestätigt werden, nicht blind mit `10` übernommen werden. Siehe `fix-catalog.md` Muster (h) für die verhaltensbasierte Beschreibung.

**Automatisierungssicherheit:** *Vorschlag mit Rückfrage*, außer bei exakt diesem Report + exakt diesen vier Zellnamen, wo es nach dieser Bestätigung als **automatisch sicher** gelten kann (analog zur Regelung bei Muster (g)).

---

## 16. `CanGrow="true"` erlaubt nur Wachsen über die zugewiesene Höhe, niemals Schrumpfen darunter

**Was passiert ist:** Bei dem Versuch, ein Subband auf Seite 1 möglichst klein zu halten, wurde `CanGrow` dynamisch in `PrintOnPage` auf `false`/`true` umgeschaltet, in der Annahme, dass `CanGrow="false"` dabei hilft, eine Zelle auf ihre aktuell zugewiesene (kleine) Höhe zu zwingen. Ergebnis: Der sichtbare Inhalt auf Folgeseiten verschwand teilweise, ohne dass sich am Seite-1-Leerraum etwas änderte.

**Was man daraus lernt:** `CanGrow="true"` ist eine reine Wachstums-Erlaubnis nach OBEN (der Inhalt darf mehr Platz einnehmen, als die zugewiesene Höhe vorsieht, falls nötig) — es hat keine symmetrische Schrumpf-Wirkung nach unten. Eine Zelle mit `CanGrow="true"` schrumpft nie unter ihre zugewiesene Höhe, unabhängig davon, wie kurz/leer der tatsächliche Inhalt ist. Für „auf Seite 1 klein halten" ist `CanGrow` also grundsätzlich der falsche Hebel — das eigentliche Schrumpfen muss über die zugewiesene `HeightF`/`SizeF` selbst passieren (siehe Eintrag 6 zum `<Localization>`-Block).

**Wie man es künftig vermeidet:** `CanGrow` als reines Wachstums-Flag behandeln, statisch im XML setzen (nicht dynamisch in `PrintOnPage` umschalten — siehe Eintrag 17, wirkt ohnehin zu spät). Für die eigentliche Höhensteuerung pro Seitenzustand die tatsächliche `HeightF` der betroffenen Controls in einem bandeigenen `BeforePrint` selbst setzen (siehe `fix-catalog.md` Muster (i)).

---

## 17. `e.PageIndex` ist in `BeforePrint` unzuverlässig — nur in `PrintOnPage` verlässlich verfügbar

**Was passiert ist:** Ein Versuch, `CanGrow`/`HeightF` dynamisch anhand von `e.PageIndex` innerhalb von `PrintOnPage` zu steuern, zeigte in der Diagnose korrekte, plausible Werte beim Auslesen — aber keine sichtbare Wirkung im tatsächlichen Druckbild. Ursache wurde über einen bereits im Skript vorhandenen Entwickler-Kommentar gefunden: `PrintOnPage` feuert NACH der finalen Paginierung, aber die layoutrelevante Höhen-/Wachstumsmessung (die `CanGrow` steuert) ist zu diesem Zeitpunkt bereits abgeschlossen — eine dort vorgenommene Änderung kommt für die aktuelle Seite zu spät, auch wenn die Eigenschaft selbst korrekt gesetzt und zurückgelesen werden kann.

**Was man daraus lernt:** `BeforePrint` feuert VOR der Paginierung — `e.PageIndex`/`e.PageCount` sind dort nicht verlässlich. `PrintOnPage` feuert NACH der Paginierung mit verlässlichem `e.PageIndex`, aber nach dem Zeitpunkt, an dem layoutrelevante Größen (`CanGrow`-gesteuertes Wachstum, Platzreservierung) bereits feststehen. Für alles, was tatsächlich Platz auf der Seite beeinflussen soll (Höhen, `e.Cancel`), ist `BeforePrint` der richtige Ort — aber dort muss die Entscheidungsgrundlage seitenindex-UNABHÄNGIG sein, weil `e.PageIndex` dort nicht zuverlässig ist.

**Wie man es künftig vermeidet:** Für Platz-/Höhenentscheidungen, die auf der aktuellen Seite wirken sollen, immer `BeforePrint` verwenden — mit einer Bedingung, die NICHT auf `e.PageIndex` beruht, sondern auf einem seitenindex-unabhängigen Signal, das in der `BeforePrint`-Phase bereits verlässlich gesetzt ist (siehe Eintrag 19 für ein konkretes Beispiel und dessen Fallstrick). Für alles, was tatsächlich vom fertigen Seitenlayout abhängt (z. B. „ist dies die erste Seite mit einer bepreisten Position"), bleibt `PrintOnPage` richtig — beide Phasen haben unterschiedliche Zwecke, keine ersetzt die andere.

---

## 18. DevExpress erzwingt einen Mindestwert von 5 für `HeightF`/`H` — ein programmatisch gesetzter kleinerer Wert wird beim Lesen stillschweigend angehoben

**Was passiert ist:** Über die gesamte Diagnose hinweg wurde `HeightF`/`SizeF` diverser Controls per Code auf `1` (praktisch minimal) gesetzt. Jeder Diagnose-Readback (sowohl im eigenen Debug-String als auch im Enduserdesigner-Properties-Panel) zeigte aber durchgängig `5` statt `1` — was zunächst wie ein Fehler in der eigenen Logik aussah. Der Kunde stellte über eigene Tests fest: Der Enduserdesigner lässt sich `H` gar nicht unter `5` setzen, auch nicht manuell.

**Was man daraus lernt:** DevExpress hat einen intern erzwungenen Mindestwert von `5` für Höhen (`HeightF`, Properties-Panel-Feld „H"). Ein per Code/XML gesetzter kleinerer Wert (z. B. `1`) wird nicht als Fehler abgelehnt, aber beim Lesen/Rendern stillschweigend auf `5` angehoben — das ist normales, erwartetes Verhalten, kein Bug in der eigenen Logik. Bei ~0,05 mm (5 Einheiten bei üblichem DPI) ist die Differenz zum eigentlich gewünschten Minimalwert visuell vernachlässigbar.

**Wie man es künftig vermeidet:** Beim Schrumpfen einer Höhe auf ein Minimum direkt `5` als Zielwert verwenden, nicht `1` oder `0` — das vermeidet die (in der Praxis geringe, aber sichtbare) Restunschärfe zwischen gesetztem und tatsächlich wirksamem Wert und erspart eine verwirrende Diagnosephase, in der ein Readback-Wert fälschlich als Fehler interpretiert wird.

---

## 19. Ein bandeigenes `BeforePrint` darf sich nicht auf eine erst in `PrintOnPage` gesetzte Variable stützen

**Was passiert ist:** Ein neues, bandeigenes `BeforePrint` (siehe `fix-catalog.md` Muster (i)) wurde zunächst mit der Bedingung `if (!_detailPrintedSoFar) { e.Cancel = true; }` gebaut — `_detailPrintedSoFar` ist ein bereits etabliertes, funktionierendes Flag (siehe Muster (f)), allerdings wird es ausschließlich in der `PrintOnPage`-Phase einer Kontrollzelle gesetzt. Ergebnis: Auf Seite 1 verschwand der gewünschte Leerraum korrekt, aber ab diesem Zeitpunkt wurde auf GAR KEINER Seite mehr etwas gedruckt, auch nicht auf echten Folgeseiten.

**Was man daraus lernt:** `_detailPrintedSoFar` wird in der `PrintOnPage`-Phase gesetzt — für ein bandeigenes `BeforePrint` auf SubBand-Ebene ist dieser Wert zum Zeitpunkt der eigenen Auswertung nicht zuverlässig verfügbar, weil `PrintOnPage` der relevanten Kind-Controls dieses Bands zu diesem Zeitpunkt im Ablauf noch gar nicht gelaufen ist — anders als bei einem `BeforePrint` direkt auf einem einzelnen, tief verschachtelten Label (dort funktioniert es nachweislich, siehe Muster (f)). Ein SubBand mit `RepeatEveryPage` trifft seine `BeforePrint`-Entscheidung offenbar in einem anderen, früheren Durchlauf als ein einzelnes Label innerhalb eines bereits platzierten Bandes.

**Wie man es künftig vermeidet:** Für ein bandeigenes `BeforePrint` ausschließlich Variablen verwenden, die selbst aus einer anderen `BeforePrint`-Kette gespeist werden (z. B. ein einfacher, in `PageFooter_BeforePrint` o. ä. hochgezählter Seitenzähler wie `pageCounter`) — nicht aus `PrintOnPage`. Vor dem Einsatz einer Variable in einem neuen bandeigenen `BeforePrint` immer prüfen, in welcher Event-Phase sie gesetzt wird, nicht nur, ob sie „im Prinzip die richtige Bedeutung" hat.

---

## 20. Verschachtelte Controls behalten ihre eigene, unabhängig von der Elterntabelle persistierte Höhe

**Was passiert ist:** Nachdem eine Tabelle erfolgreich auf eine kleine Höhe geschrumpft wurde, blieb der sichtbare Leerraum auf Seite 1 dennoch teilweise bestehen. Der Kunde stellte im Enduserdesigner fest: Ein Label innerhalb der Tabellenzelle hatte weiterhin seine eigene, alte, größere Höhe (`H=40`) — obwohl die Tabelle selbst bereits korrekt auf `H=5` stand.

**Was man daraus lernt:** Ein verschachteltes Control (Label in einer Tabellenzelle) trägt seine eigene, separat persistierte Standardhöhe, unabhängig von der Höhe seines Elter-Controls. Das Schrumpfen der äußeren Tabelle/Zelle allein genügt nicht — das innere Control behält seine alte Höhe, bis diese ebenfalls explizit angepasst wird. Dieselbe Regel gilt in beide Richtungen: Auch das Wieder-Vergrößern (z. B. auf Folgeseiten) muss auf JEDER betroffenen Verschachtelungsebene einzeln passieren, nicht nur auf der äußersten.

**Wie man es künftig vermeidet:** Bei jedem Höhen-Fix an einer Tabelle/einem Band IMMER auch alle direkt verschachtelten Controls (Labels, Zellen-Inhalte) auf eigene, unabhängig gesetzte Höhen prüfen — sowohl als direktes Attribut als auch im `<Localization>`-Block (siehe Eintrag 6). Ein Fix, der nur das äußerste Element behandelt, ist erfahrungsgemäß unvollständig.

---

## (Platzhalter für künftige Einträge)

Beim nächsten Report-Lauf, der etwas Neues zutage fördert, hier als Eintrag Nr. 21 ergänzen — gleiches Format: Was passiert ist / Was man daraus lernt / Wie man es künftig vermeidet.
