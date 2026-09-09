# Known Issues — lebendes Dokument

Diese Datei sammelt Fallen und Überraschungen zur Kurz-/Langtext-Umschaltung, die über `SKILL.md` und `validierung-kurz-langtext.md` hinausgehen — Dinge, die sich erst bei der Anwendung auf konkrete weitere Reports zeigen. Bei jedem neuen Lauf: erst hier nachsehen, ob ein beobachtetes Problem schon bekannt ist; am Ende eines Laufs: neue Erkenntnisse hier ergänzen (siehe `SKILL.md`, Schritt 10).

Format pro Eintrag: **Was passiert ist → Was man daraus lernt → Wie man es künftig vermeidet.**

---

## Inhalt

- 1. Entwicklungsgeschichte der Formeln — mehrfach invertierte Bedingung als Warnbeispiel
- 2. Ausgangspunkt war eine ältere, umfassendere ArtikelArt-Liste

---

### 1. Entwicklungsgeschichte der Formeln — mehrfach invertierte Bedingung als Warnbeispiel

**Was passiert ist:** Bei der Erarbeitung dieser Lösung (Report `dxAio_template`, September 2026) wurde die Bedeutung von `?ArgKurzLangtext` im Gespräch mehrfach vertauscht — u.a. einmal mit fehlendem `Not` vor dem Parameter, wodurch sich `True`/`False` genau umgekehrt verhielten, und mehrfach unterschiedliche Annahmen darüber, ob der Parameter in der Sub_POS-Formel oder nur im unteren Band wirken soll.

**Was man daraus lernt:** Eine Formulierung wie "wenn Parameter=True dann X" ist erst dann verlässlich, wenn sie an einer konkreten Wahrheitstabelle mit allen Kombinationen durchgespielt wurde — Prosa-Beschreibungen von bedingter Logik mit mehreren verschachtelten `Iif`s laufen in einem Gespräch leicht auseinander, ohne dass es einer Seite auffällt.

**Wie man es künftig vermeidet:** Bei jeder neuen Anwendung dieser Skill auf einen weiteren Report: die Wahrheitstabelle aus `validierung-kurz-langtext.md` Punkt 2 dem Nutzer vor der Umsetzung zur Bestätigung vorlegen (nicht nur die Formeln), besonders wenn der Zielreport strukturell vom Referenzfall abweicht und die Formeln nicht 1:1 übernommen werden können.

### 2. Ausgangspunkt war eine ältere, umfassendere ArtikelArt-Liste

**Was passiert ist:** Die ursprüngliche Kurztext-Formel des Reports nutzte die Liste `(0, -10, -2, -3, -12, -13)`. Im Zuge dieser Erweiterung wurde einvernehmlich mit dem Nutzer auf die engere Liste `(0, -10, -24)` gewechselt — ohne, dass zunächst geklärt war, ob das eine bewusste fachliche Einschränkung oder ein Versehen war.

**Was man daraus lernt:** Eine Artikelart-Liste, die in mehreren Formeln eines Reports wiederkehrt, kann sich über die Zeit fachlich weiterentwickelt haben (neue ArtikelArt `-24` hinzugekommen, andere bewusst ausgeschlossen) — sie 1:1 aus einer älteren Formel zu übernehmen ist keine sichere Annahme.

**Wie man es künftig vermeidet:** Bei jedem Zielreport die dort **aktuell** verwendete ArtikelArt-Liste explizit erfragen bzw. aus dem bestehenden Kurztext-Ausdruck ablesen, statt automatisch `(0, -10, -24)` zu übernehmen (siehe `SKILL.md`, Sicherheitsstufe 2).
