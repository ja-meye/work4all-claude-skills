# Known Issues — lebendes Dokument

Diese Datei sammelt Fallen und Überraschungen zur Landscape-Umstellung von Unterberichten, die über `SKILL.md` und `validierung-ub-landscape.md` hinausgehen — Dinge, die sich erst bei der Anwendung auf konkrete weitere Reports zeigen. Bei jedem neuen Lauf: erst hier nachsehen, ob ein beobachtetes Problem schon bekannt ist; am Ende eines Laufs: neue Erkenntnisse hier ergänzen (siehe `SKILL.md`, Schritt 10).

Format pro Eintrag: **Was passiert ist → Was man daraus lernt → Wie man es künftig vermeidet.**

---

## Inhalt

- 1. Vermeintlich fehlender Übertrag war ein Testdaten- und Vorschau-Artefakt, kein Bug
- 2. Ein vollständig durchgebauter PageHeader-Workaround stellte sich als unnötig heraus
- 3. Doppelter Seitenumbruch vor dem Unterbericht (Leerseite)

---

### 1. Vermeintlich fehlender Übertrag war ein Testdaten- und Vorschau-Artefakt, kein Bug

**Was passiert ist:** Nach der Landscape-Umstellung von `SubReport_Leistungsnachweis` wurde bei einer Rechnung mit Leistungsnachweis auf Folgeseiten der Positionstabelle weder die wiederholte Tabellenkopfzeile noch der Übertrag-Betrag angezeigt. Das sah zunächst wie eine Bestätigung des dokumentierten DevExpress-Risikos aus (`GenerateOwnPages` stört `RepeatEveryPage` dokumentweit) und löste eine mehrtägige Diagnose- und Workaround-Sitzung aus (siehe Eintrag 2). Am Ende stellte sich heraus: (a) die normalen Positionen im verwendeten Testbeleg hatten schlicht keinen `GesPreis`-Wert (nur Stücklistenkomponenten hatten Preise) — ein Übertrag von 0 wurde also korrekt unterdrückt, das war kein Bug; und (b) die Druckvorschau schneidet den Hauptbericht im Querformat-Layout rechts ab, wodurch die `GesPreis`-Spalte gar nicht sichtbar war und das Fehlen der Preise in den Testdaten nicht auffiel.

**Was man daraus lernt:** Ein leerer/fehlender Übertrag ist nur dann ein belastbares Bug-Symptom, wenn zuvor bestätigt ist, dass die zugrunde liegenden Positionen tatsächlich echte, von Null verschiedene Preise haben — und dass die verwendete Ansicht (Vorschau vs. PDF-Export) den relevanten Bereich überhaupt vollständig zeigt.

**Wie man es künftig vermeidet:** Vor jeder Diagnose eines vermeintlichen Übertrag-Bugs nach einer Landscape-Umstellung: (1) im Testbeleg mit echten Preisen auf normalen Positionen drucken, nicht mit einem beliebigen Testdatensatz; (2) als PDF exportieren oder eine Vorschau verwenden, die den Hauptbericht im Querformat nicht rechts abschneidet, bevor "Spalte/Betrag fehlt" als Bug gewertet wird.

### 2. Ein vollständig durchgebauter PageHeader-Workaround stellte sich als unnötig heraus

**Was passiert ist:** Ausgehend vom Symptom in Eintrag 1 wurde ein kompletter Workaround entwickelt und mehrfach iteriert: Tabellenkopf und Übertrag wurden als Kopie in eine eigene `PageHeaderBand`-SubBand dupliziert, mit manueller C#-Nachbildung der Summenbildung (da `sumCarryoverSum()` im PageHeader-Kontext bzw. dokumentweit in diesem Report 0 lieferte). Mehrere Versionen scheiterten an unterschiedlichen Detailproblemen (Timing von `BeforePrint` vs. `PrintOnPage`, doppeltes Zählen von `pageCounter`, ein zweiter, gleichnamiger Zellenname in einem anderen Unterbericht). Erst ein direkter Vergleichstest mit der **unveränderten** Ursprungsdatei (ganz ohne PageHeader-Workaround) zeigte: Die Original-Logik funktionierte die ganze Zeit korrekt — das Symptom war Eintrag 1, kein echter Bug.

**Was man daraus lernt:** Ein aufwendiger Workaround für ein DevExpress-Risiko, das nur *dokumentiert möglich*, aber am konkreten Report noch nicht *bestätigt* ist, sollte nicht gebaut werden, bevor ein einfacher Kontrolltest (unveränderte Datei mit sauberen Testdaten) das Symptom tatsächlich als Regression bestätigt hat.

**Wie man es künftig vermeidet:** Vor Beginn eines PageHeader-Kopie-Workarounds (oder eines strukturell ähnlichen Eingriffs) immer zuerst: mit der unveränderten Datei (vor der Landscape-Umstellung, oder mit `GenerateOwnPages` testweise wieder entfernt) denselben Testdruck machen. Zeigt sich das Symptom dort NICHT, ist die Landscape-Umstellung nicht die Ursache, und es muss zuerst die eigentliche Ursache (siehe Eintrag 1) gefunden werden, bevor irgendein Workaround begonnen wird.

### 3. Doppelter Seitenumbruch vor dem Unterbericht (Leerseite)

**Was passiert ist:** Nach Anwendung des Kern-Rezepts (siehe `SKILL.md`) erschien vor der ersten Seite des Unterberichts eine leere Seite. Ursache: die Host-`SubBand` hatte zusätzlich `PageBreak="BeforeBand"` gesetzt — vermutlich ein Überbleibsel aus der Zeit, in der der Unterbericht noch im Hochformat eingebettet war. In Kombination mit `GenerateOwnPages="true"` entstanden zwei Seitenumbrüche hintereinander.

**Was man daraus lernt:** `GenerateOwnPages="true"` allein erzwingt bereits einen neuen Seitenanfang — ein zusätzlicher manueller `PageBreak="BeforeBand"` auf derselben Host-Band ist danach fast immer redundant und erzeugt eine Leerseite, wenn die Host-Band selbst außer dem `XRSubreport` keinen nennenswerten sichtbaren Inhalt hat.

**Wie man es künftig vermeidet:** Ist in `SKILL.md` als Falle 1 mit automatischem Fix (Sicherheitsstufe 1, sofern die Host-Band nur unsichtbaren/Marker-Inhalt neben dem `XRSubreport` enthält) fest verankert — dieser Prüfschritt gehört bei jeder Anwendung dieser Skill zum Standardablauf, nicht nur bei einem beobachteten Symptom.
