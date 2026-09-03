# Lessons Learned — work4all DevExpress-Report-Skills

Fachlich unkritische, projektübergreifende Erkenntnisse aus der Report-/Skill-Entwicklung. Kundenbezogene oder sonst intern sensible Details (konkrete Report-Inhalte, DB-Felder mit Kundenbezug) gehören NICHT hierher, sondern bleiben lokal unter `Referenz\`.

Format pro Eintrag: **Datum — Kontext → Befund → Konsequenz.**

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
