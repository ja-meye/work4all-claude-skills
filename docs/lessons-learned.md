# Lessons Learned — work4all DevExpress-Report-Skills

Fachlich unkritische, projektübergreifende Erkenntnisse aus der Report-/Skill-Entwicklung. Kundenbezogene oder sonst intern sensible Details (konkrete Report-Inhalte, DB-Felder mit Kundenbezug) gehören NICHT hierher, sondern bleiben lokal unter `Referenz\`.

Format pro Eintrag: **Datum — Kontext → Befund → Konsequenz.**

---

## 2026-09-04 — Ein nicht ladbarer Report lässt sich reparieren, indem sein Inhalt in das Grundgerüst einer funktionierenden Parallelversion übertragen wird; Connection Name ist eine unterschätzte Fehlerquelle

**Kontext:** Ein bestehender Listenreport (`neuen-devexpress-listenreport-bauen`, DXJ0002) lud nicht mehr im Programm. Der Nutzer hatte bereits eine zweite, strukturell viel einfachere Version desselben Report-Typs neu in der App angelegt, die nachweislich lud. Aufgabe: Elemente, Logik, Query und Parameter aus der defekten Datei übernehmen, ohne das Grundgerüst der funktionierenden Datei zu verändern, und ohne das eingebettete Skript anzufassen (unklar, ob Scripts in der Zielumgebung überhaupt aktiviert sind).

**Befund:** Root-Element und Datenquellen-Mechanik beider Dateien waren strukturell identisch, bis auf einen einzigen, leicht zu übersehenden Unterschied: Der `<Connection Name="...">`-Wert in der defekten Datei unterschied sich von dem der funktionierenden Datei nur um ein angehängtes Leerzeichen plus Ziffer (z.B. `"...Connection"` vs. `"...Connection 1"`). Eine rein strukturelle Validierung (wohlgeformtes XML, eindeutige Ref-IDs, aufgelöste Verweise, Feld-Abgleich gegen das ResultSchema) hätte diesen Unterschied nicht gefunden, weil beide Varianten für sich genommen syntaktisch gültig sind — er fällt nur beim gezielten Attribut-Abgleich zwischen defekter und bekannt funktionierender Referenzdatei auf. Das reiht sich ein in die bereits dokumentierte Lehre vom 2026-09-03 ("Root-Attribute müssen konsistent zur restlichen Datei sein, nicht nur syntaktisch gültig") — hier trifft es allerdings nicht ein Root-Attribut, sondern einen Wert innerhalb der eingebetteten Datenquelle.

Die gewählte Reparaturstrategie — Grundgerüst der funktionierenden Datei unverändert lassen, nur `<Parameters>`, `<Bands>`, `<StyleSheet>`, `<ParameterPanelLayoutItems>`, `<Watermarks>` und die Datenquelle (Query/Parameter/ResultSchema) aus der defekten Datei übernehmen, dabei aber die Connection auf den bestätigt funktionierenden Wert umstellen — hat sich doppelt bestätigt: einmal beim Laden im Programm, ein zweites Mal, weil der Nutzer die reparierte Datei zusätzlich in sein Visual-Studio-Projekt geladen und von dort neu exportiert hat, ohne dass sich am Inhalt etwas änderte (nur BOM/Zeilenumbrüche unterschieden sich, der Inhalt war byteidentisch).

**Konsequenz:** `neuen-devexpress-listenreport-bauen` (DXJ0002, → v1.3.0) bekam einen neuen Sonderfall-Abschnitt "bestehenden Report reparieren, der nicht lädt (Content-Transplantation)" mit den obigen Schritten, inkl. dem expliziten Hinweis, die Connection Name als erste Fehlerquelle zu prüfen, bevor eine aufwändigere Diagnose begonnen wird. Die Trigger-Beschreibung im Frontmatter wurde erweitert, damit dieser Reparatur-Fall künftig auch ohne expliziten Verweis auf den Skill-Namen erkannt wird.

---

## 2026-09-03 — Ein `work4all-log`-Block aus reinen Kommentaren übersteht keinen Designer-Speichervorgang

**Kontext:** Beim Bau des Reports `dxArticleList` (Skill `neuen-devexpress-listenreport-bauen`, DXJ0002) wurden zunächst zwei unabhängige Bugs behoben, die das Laden im DevExpress Report Designer verhinderten: ein falsches `Version`-Attribut (`25.2` statt `25.1`, inkonsistent zur referenzierten Assembly `v25.1`) und ein falsches `ScriptLanguage`-Attribut (`VisualBasic` statt `CSharp`, inkonsistent zum tatsächlich verwendeten `//`-Kommentarstil und zu allen anderen produktiven Reports). Nach Behebung beider Punkte lud die Datei erfolgreich. Der Nutzer öffnete sie im Designer und speicherte sie dort einmal.

**Befund:** Der Vorher/Nachher-Vergleich zeigte: alle Controls, Expression-Bindings und sonstigen Attribute blieben exakt gleich — aber das komplette `ScriptsSource`-Attribut war verschwunden, mit ihm der `work4all-log`-Audit-Block (Skill-ID, Version, Zeitstempel), sowie ohne erkennbaren Zusammenhang auch `ScriptLanguage` und `SnappingMode`. Nicht geleert, sondern das Attribut existierte nicht mehr — eine Suche nach der Skill-ID im Dateiinhalt ergab null Treffer. Vermutete Ursache: Der Designer kompiliert `ScriptsSource` beim Laden/Speichern; ein reiner Kommentarblock kompiliert zu leerem Code, und ein leeres Kompilat wird beim Re-Serialisieren offenbar als "kein Skript vorhanden" behandelt und ganz weggelassen statt leer geschrieben.

Das ist eine schärfere Ausprägung eines bereits bekannten, allgemeineren Phänomens (`fix-folgeseiten-uebertrag-problem/references/known-issues.md`, Eintrag 3): Designer-Re-Serialisierung kann Properties verwerfen, die er nicht als "im Designer explizit gesetzt" erkennt. Neu und für die Skill-Architektur besonders relevant: hier trifft es nicht eine einzelne Layout-Property, sondern den gesamten Audit-Log-Mechanismus, auf dessen Append-only-Garantie sich alle Report-Skills verlassen — der Log kann sich durch ganz gewöhnliche, im Alltag unvermeidbare Designer-Nutzung selbst löschen, ohne dass es jemand beabsichtigt oder bemerkt.

**Konsequenz:** `neuen-devexpress-report-skill-anlegen/references/fix-log-format.md` bekam eine neue Regel 8 samt Abschnitt „Überlebensfähigkeit bei einem Designer-Speichervorgang": Direkt nach der `end work4all-log`-Fußzeile steht künftig eine harmlose, aber syntaktisch echte C#-Zeile (`private static readonly string _work4allLogAnchor = "keep-scriptssource-alive";`), damit der kompilierte Skript-Code nie leer ist. Betroffene Skills wurden im selben Zug aktualisiert: `neuen-devexpress-listenreport-bauen` (DXJ0002, → v1.2.0, seedet die Anker-Zeile beim Erstbau), `fix-folgeseiten-uebertrag-problem` (DXJ0001, → v1.3.0, rüstet die Anker-Zeile bei älteren Dateien nach, sobald er ohnehin einen Log-Eintrag schreibt), Meta-Skill `neuen-devexpress-report-skill-anlegen` (DXJ0003, → v0.4.0).

**Offen:** Die Anker-Zeilen-Mitigation ist eine Hypothese, kein bestätigter Fix — in dieser Arbeitsumgebung steht kein DevExpress Report Designer zur Verfügung, um einen echten Round-Trip (Datei mit Anker-Zeile öffnen, speichern, prüfen ob ScriptsSource überlebt) zu testen. Sobald ein so gebauter/gefixter Report das nächste Mal im Designer gespeichert wird, bitte gezielt gegenprüfen und das Ergebnis in `fix-folgeseiten-uebertrag-problem/references/known-issues.md` Eintrag 21 nachtragen.

---

## 2026-09-03 — Root-Attribute (`Version`, `ScriptLanguage`) müssen konsistent zur restlichen Datei sein, nicht nur syntaktisch gültig

**Kontext:** Derselbe `dxArticleList`-Lauf, vor dem oben beschriebenen Designer-Speicher-Befund.

**Befund:** Zwei unabhängige, jeweils für sich genommen syntaktisch valide Root-Attribute verhinderten das Laden im Designer, weil sie inkonsistent zum Rest der Datei waren:
1. `Version="25.2"` auf dem `XtraReportsLayoutSerializer`-Root-Element, obwohl `ControlType` und `SerializerVersion` durchgängig `v25.1`/`25.1.3.0` referenzierten und jede bekannt funktionierende Referenzdatei (`dxClientList.repx`, ein minimaler Testreport) ebenfalls `Version="25.1"` trug.
2. `ScriptLanguage="VisualBasic"`, obwohl der eingebettete `work4all-log`-Kommentar mit `'` (VB-Syntax) statt `//` (C#) geschrieben war und die produktive Referenzdatei (`dxAio_template.repx`, Skill DXJ0001) durchgängig C# verwendet (kein `ScriptLanguage`-Attribut = impliziter CSharp-Default, echte `//`-Kommentare, echte C#-Event-Handler).

Beide Werte fielen bei einer reinen XML-Wohlgeformtheits-/Ref-Auflösungs-Prüfung (wie sie `validation-generic.md`/`validierung-vor-auslieferung.md` vorschreiben) nicht auf — die Datei war strukturell vollständig valide, lud aber trotzdem nicht.

**Konsequenz:** Bei jedem neu gebauten oder reparierten Report zusätzlich zur strukturellen Validierung einen gezielten Attribut-Abgleich gegen eine bekannt funktionierende Referenzdatei desselben Reporttyps durchführen (Root-Attribute komplett gegenüberstellen: Werte, die in der Referenz vorkommen, aber in der neuen Datei fehlen oder abweichen). Dieser Abgleich ist kein Ersatz für den echten Designer-Testdruck, aber ein günstiger Zwischenschritt, der genau diese Art von "syntaktisch gültig, aber inkonsistent" Fehlern zuverlässig aufdeckt, bevor der Nutzer sie im Designer erlebt.

## Sitzung 03./04.09.2026 — vier Fehlerklassen, die alle bestehenden Checks passiert haben

Beim Fix des Reports `dxAio_template` (Übertrag-/Folgeseiten-Logik) sind vier Fehler nacheinander erst dadurch aufgefallen, dass der Nutzer sie im Enduser-Designer bzw. im Testdruck gesehen hat. Alle vier haben die bis dahin bestehende Validierungs-Checkliste vollständig grün passiert. Das ist die eigentliche Lehre: Die Checks prüften **Wohlgeformtheit und Werte**, aber nicht, ob die Werte auch **wirksam** sind.

1. **Lücken in der `ItemN`-Nummerierung.** Nach dem Entfernen von Elementen war die Nummerierung dreier Sammlungen nicht mehr lückenlos. DevExpress ignoriert alles hinter der ersten Lücke stillschweigend — der neu gesetzte Höhen-Eintrag eines Bands kam deshalb nie an, obwohl er wertgleich zur Referenz in der Datei stand.
2. **Phasentrennung übersehen.** Ein in `PrintOnPage` gesetztes Flag wurde in `BeforePrint`-Handlern gelesen. Die PrintOnPage-Phase läuft dokumentweit erst nach allen BeforePrint-Ereignissen — das Flag ist dort immer `false`, die betroffenen Controls blieben auf allen Seiten minimal.
3. **Halb angewendetes Muster.** Von einem zweiteiligen Fix wurde nur der Kompensations-Teil angewendet, weil eine **Zählung** von Attribut-Vorkommen (statt einer element-gescopten Prüfung) fälschlich nahelegte, der erste Teil sei schon vorhanden. Ergebnis: das Symptom wurde verstärkt statt behoben.
4. **Referenzdatei ungeprüft als Vorlage genommen.** Die als Referenz benannte Datei war eine Diagnose-Zwischenfassung („DEBUG", „v31", trotz „FINAL" im Namen) mit Debug-Code und einem echten Logikfehler. Daraus wurde Code 1:1 übernommen — samt Fehler.

**Konsequenzen (umgesetzt in Plugin-Version 1.6.0):**

- Neuer, ausführbarer Check-Index `scripts/validate_repx.py` mit den Checks `C01`–`C18` (inzwischen 18 Checks), verbindlich nach **jeder** Bearbeitungsrunde statt nur am Ende. Er meldet alle vier Fehlerklassen oben automatisch; die Gegenprobe an den Zwischenständen dieser Sitzung hat das bestätigt.
- Das Skript ist zusätzlich verbindlich **auf der Referenzdatei selbst** auszuführen (Selbst-Audit). Für die hier verwendete Referenz meldet es sofort Debug-Reste und den Logikfehler.
- Generische Regeln in `validation-generic.md` (Punkte 13–16) und `repx-format-basics.md` (Abschnitte zu `ItemN` und zur dokumentweiten Phasentrennung) ergänzt, damit sie nicht an einen einzelnen Fach-Skill gebunden sind.
- Arbeitsregel: Fehlalarme eines Checks werden durch **Nachschärfen des Checks** behoben, nicht durch Ignorieren des Befunds — der Check-Index wächst dadurch mit jedem Lauf.
- Arbeitsregel: Prüfungen sind immer auf das konkrete Element zu scopen; Zählungen über die ganze Datei sind kein Nachweis.

### Nachtrag: eine fünfte Fehlerklasse — Doku statt Datei geglaubt

`Padding` wird als `Left,Right,Top,Bottom,Dpi` serialisiert. Ein im Changelog einer Referenzdatei als
„Padding (Top) 0 → 10" beschriebener Fix hatte in Wahrheit den **Right**-Wert gesetzt (Position 2) und war
vertikal wirkungslos; übernommen wurde er trotzdem, weil die Beschreibung plausibel klang. Aufgefallen ist es
erst, als der Nutzer meldete, der Abstand sei weiterhin zu gering.

Die Lehre ist dieselbe wie bei Punkt 3 oben, nur in einer anderen Verkleidung: **eine Aussage über eine Datei
wird an der Datei verifiziert, nicht aus einem Text übernommen** — auch dann nicht, wenn der Text aus dem
eigenen Projekt stammt. In diesem Fall stand der Beweis in der Datei selbst: 19 Zellen mit expliziten
`Padding.LeftF`/`Padding.RightF`-Bindungen belegen die Reihenfolge eindeutig. Check `C17` leitet sie seitdem
bei jedem Lauf automatisch ab.

## Abgleich mit der offiziellen Agent-Skills-Spezifikation (04.09.2026)

Ein Abgleich der eigenen Skills mit der offiziellen Dokumentation hat zwei **harte** Verstöße gefunden, die im Alltag
nicht aufgefallen wären, weil sie erst beim Upload bzw. beim Folgen eines Pfades zuschlagen:

1. **`skill_id` und `version` standen als Top-Level-Frontmatter-Keys.** Erlaubt sind für claude.ai-Uploads, die
   Skills-API und `package_skill.py` nur `name`, `description`, `license`, `compatibility`, `metadata`,
   `allowed-tools`; alles andere wird als „unexpected key" abgelehnt. Eigene Felder gehören unter `metadata:`.
2. **Skillübergreifende Verweise zeigten ins Leere.** Mehrere `SKILL.md` verwiesen auf `references/fix-log-format.md`
   — diese Datei liegt aber im Meta-Skill, nicht im verweisenden Skill. Jetzt mit vollständigem relativem Pfad.

Dazu kamen dokumentierte Best Practices: Inhaltsverzeichnis für Referenzdateien >100 Zeilen, Skript-Aufrufe über
`${CLAUDE_SKILL_DIR}` statt relativer Pfade, SKILL.md schlank halten (sie lädt bei **jedem** Trigger — die
ausgelagerte Versionshistorie spart rund 1.800 Tokens pro Auslösung), und Evaluations-Szenarien als Regressionsschutz.

**Konsequenz:** Die Regeln stehen jetzt als Baustein 12 im Meta-Skill und werden von `scripts/lint_skills.py`
(`S01`–`S10`) maschinell geprüft — dieselbe Mechanik wie `validate_repx.py` für Report-Dateien. Der Linter hat den
zweiten Verstoß oben selbst gefunden, nicht ein Mensch.
