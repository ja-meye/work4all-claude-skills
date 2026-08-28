# Known Issues — lebendes Dokument

Diese Datei sammelt Fallen und Überraschungen, die über den generischen Fix-Katalog hinausgehen — Dinge, die sich erst beim tatsächlichen Bearbeiten/Testen konkreter Reports gezeigt haben. Bei jedem neuen Report-Lauf: erst hier nachsehen, ob ein beobachtetes Problem schon bekannt ist; am Ende eines Laufs: neue Erkenntnisse hier ergänzen (siehe SKILL.md, Schritt 8).

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

## (Platzhalter für künftige Einträge)

Beim nächsten Report-Lauf, der etwas Neues zutage fördert, hier als Eintrag Nr. 8 ergänzen — gleiches Format: Was passiert ist / Was man daraus lernt / Wie man es künftig vermeidet.
