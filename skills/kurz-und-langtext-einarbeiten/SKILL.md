---
name: kurz-und-langtext-einarbeiten
description: Erweitert einen bestehenden work4all-dxAio_template.repx-Positionsreport um einen per Parameter umschaltbaren Kurztext-/Langtext-Druck (?ArgKurzLangtext) inklusive optionaler interner Bemerkung. Verwenden, wenn ein Nutzer in einem work4all-DevExpress-Positionsreport Kurztext und Langtext (Bezeichnung) wahlweise oder gemeinsam andrucken möchte, nach einem Parameter "ArgKurzLangtext" fragt, die Positionszeile um Artikelnummer/Kurztext/Langtext/Bemerkung erweitern will, oder eine bestehende Iif-Expression zur Kurztext-/Langtext-Auswahl in einer Positionszeile überarbeiten möchte.
metadata:
  skill_id: DXJ0005
  version: 1.0.0
---

# Kurz- und Langtext-Umschaltung in einen work4all-Positionsreport einarbeiten

## Worum es geht

Ein bestehender work4all-`dxAio_template.repx`-Report (und strukturell ähnlich gebaute Ableger) soll um die Möglichkeit erweitert werden, pro Position wahlweise **nur Kurztext**, **nur Langtext** oder **beides zusammen** anzudrucken — gesteuert über einen neuen Boolean-Report-Parameter `?ArgKurzLangtext`. Diese Skill kapselt eine am Report `dxAio_template` (work4all, September 2026) erarbeitete und vom Nutzer bestätigte Lösung, damit sie sich auf weitere Report-Varianten übertragen lässt.

**Erweiterungs-Typ, kein Bugfix.** Diese Skill fügt einem funktionierenden Report ein neues, optionales Verhalten hinzu — sie repariert nichts Kaputtes. Trotzdem gelten dieselben Sorgfaltsregeln wie beim Verbesserungs-Typ (Referenzabgleich, Sicherheitsstufen, Validierung, zeitgestempelte Auslieferung), weil auch hier eine bestehende `.repx` verändert wird.

Lies **`../neuen-devexpress-report-skill-anlegen/references/repx-format-basics.md`** zuerst, bevor du das eingebettete C#-Skript oder rohes XML einer `.repx` direkt liest oder änderst (Pflichtbaustein 10 des Meta-Skills) — Encoding/BOM, Escaping-Pipeline, Bandmodell, `<Localization>`-Block.

## Zielverhalten (verbindliche, vom Nutzer bestätigte Spezifikation)

Die Positionszeile (bestehendes Band `Sub_POS`, Spalten Pos | ggf. ArtNr & Text | Anzahl | Einheit | EPreis | GPreis) und ein neues Band darunter (`Sub_LangtextBemerkung`) verhalten sich je nach Parameter so:

| `?ArgKurzLangtext` | Sub_POS (Textzelle) | Sub_LangtextBemerkung |
|---|---|---|
| **True** | ggf. ArtNr + (Kurztext, falls vorhanden — sonst Fallback auf Bezeichnung/Langtext) | Langtext, **nur wenn** er sich vom Kurztext unterscheidet, **und** ggf. Bemerkung |
| **False** (Default) | ggf. ArtNr + immer Langtext (Bezeichnung), nie Kurztext | nur ggf. Bemerkung (kein Langtext — der steht ja schon oben) |

Kurz gesagt: Bei `True` verhält sich `Sub_POS` wie die ursprüngliche, unveränderte Kurztext-Logik des Reports (Kurztext bevorzugt, Bezeichnung als Fallback), und `Sub_LangtextBemerkung` ergänzt bei Bedarf den abweichenden Langtext + Bemerkung darunter. Bei `False` wird `Sub_POS` zur reinen Langtext-Zeile, und `Sub_LangtextBemerkung` zeigt nur noch die Bemerkung.

Beide Bänder gelten nur für `[POS_ArtikelArt] In (0, -10, -24)` — für alle anderen ArtikelArten bleibt `Sub_POS` unverändert bei `[POS_Bezeichnung]`, und `Sub_LangtextBemerkung` bleibt unsichtbar.

## Voraussetzung im Ziel-Report

- Ein Band `Sub_POS` mit einem Calculated Field, das den Text der Positionszeile liefert (im Referenzfall `_KurztextAndArtNrPOS`) — inklusive vorhandener ArtNr-Präfix-Logik (`?ArgShowArticleNo`) und Kurztext-mit-Bezeichnung-Fallback.
- Die Felder `POS_ArtikelArt`, `POS_ArtNr`, `POS_Kurztext`, `POS_Bezeichnung`, `POS_Bemerkung` sowie die Parameter `?ArgShowArticleNo` und `?ArgShowInternalText` existieren bereits.
- **Prüfen, welche ArtikelArt-Liste der Zielreport aktuell verwendet.** Die hier dokumentierte Lösung nutzt `(0, -10, -24)`. Ältere Report-Varianten verwenden teils die umfassendere Liste `(0, -10, -2, -3, -12, -13)` (reiner Kurztext-Fallback ohne Langtext-Band). Weicht der Zielreport ab: **Rückfrage an den Nutzer**, ob die neue, engere Liste übernommen werden soll oder ob am Zielreport eine andere Liste gilt (Sicherheitsstufe 2, siehe unten).

## Referenzdatei (liegt bei, Anfordern beim Nutzer bleibt trotzdem optional)

Diese Skill bringt bereits eine bestätigte Referenzdatei mit: `reference-files/dxAio_template_new.repx` — die Referenzimplementierung dieser Logik, **Autor: Ploner**. Sie kann bei Anwendung des Skills direkt herangezogen werden, ohne sie erst beim Nutzer anzufordern. Vorgehen:

1. Vor dem Umsetzen der Formeln `reference-files/dxAio_template_new.repx` strukturell gegen den Zielreport abgleichen: Bandnamen, Calculated-Field-Namen, Tabellen-/Zellnamen und die Feldnamen (`POS_...`) können am Zielreport abweichen — die Referenz zeigt das bestätigt funktionierende Muster, nicht zwingend identische Objektnamen.
2. Weicht der Zielreport strukturell stark von dieser Referenz ab, oder wirkt die mitgelieferte Referenz veraltet (z.B. weil sich die Formeln seither weiterentwickelt haben): den Nutzer optional nach einer aktuelleren Referenz-`.repx` fragen — anders als beim Verbesserungs-Skill `fix-folgeseiten-uebertrag-problem` ist das **kein Pflichtschritt**, die Anwendung des Skills darf auch ohne eine (weitere) vom Nutzer bereitgestellte Referenz weiterlaufen.
3. Liegt weder die mitgelieferte noch eine zusätzliche Referenz strukturell nah genug am Zielreport: anhand der unten dokumentierten Formeln und Bandstruktur arbeiten und im Abschlussbericht an den Nutzer kurz vermerken, dass ohne engen Referenzabgleich gearbeitet wurde.

## Arbeitsablauf

1. **Report entgegennehmen, Ist-Zustand prüfen.** Existiert `Sub_POS` mit einem Kurztext-Calculated-Field wie oben beschrieben? Welche ArtikelArt-Liste ist dort aktuell hinterlegt? Gibt es bereits ein Band unterhalb von `Sub_POS`, das mit einem neuen `Sub_LangtextBemerkung` kollidieren würde?
2. **Referenzdatei optional anfordern** (siehe oben) und ggf. strukturell abgleichen.
3. **Parameter `ArgKurzLangtext` anlegen:** Typ Boolean, Default Value **No** (false). Sicherheitsstufe 1 (automatisch sicher), sofern noch kein gleichnamiger Parameter existiert — existiert bereits einer mit anderem Typ/Default: Rückfrage.
4. **Kurztext-Formel im bestehenden Sub_POS-Calculated-Field erweitern** (Feld heißt im Referenzfall `_KurztextAndArtNrPOS`) — siehe Formel A unten. Sicherheitsstufe 1, wenn die bestehende Formel strukturell der Ausgangsformel unten entspricht; sonst Sicherheitsstufe 2 (dem Nutzer die geplante Änderung vor dem Einfügen zeigen).
5. **Neues Band `Sub_LangtextBemerkung` unterhalb von `Sub_POS` anlegen**, darin eine dreispaltige Tabelle (Leer | Inhalt | Leer, wie bei `Sub_POS`) mit einer Inhaltszelle. Konkrete Namen im Referenzfall: Tabelle `xrTable30`, Zelle `xrTableZell148` — im Zielreport gelten die dort als Nächstes freien DevExpress-Objektnamen; die Referenznamen nicht blind übernehmen, wenn sie im Zielreport bereits vergeben sind.
6. **Neues Calculated Field für die Inhaltszelle anlegen** (Referenzname `_BezeichnungAndBemerkung`) mit Formel B unten, und die **Visible-Expression des neuen Bands** mit Formel C.
7. **Skript-Hygiene** — nur als separater, ausdrücklich angeforderter Schritt (siehe Zwei-Wege-Kommentarregel im Meta-Skill), nie beiläufig in diesem Lauf.
8. **Validierung**: generische Basis-Checkliste `../neuen-devexpress-report-skill-anlegen/references/validation-generic.md` plus die fachspezifischen Punkte in `references/validierung-kurz-langtext.md` (insbesondere: Wahrheitstabelle der vier Kombinationen manuell durchspielen).
9. **Auslieferung** als neue, zeitgestempelte `.repx` (`<Reportname>_<JJJJ-MM-TT>_<hh-mm>.repx`, Europe/Berlin) — nie In-Place-Überschreiben, außer der Nutzer verlangt es ausdrücklich (dann vorher Backup, siehe Meta-Skill Baustein 9). `work4all-log`-Eintrag mit Skill-ID `DXJ0005` schreiben (Format siehe `../neuen-devexpress-report-skill-anlegen/references/fix-log-format.md`), Anker-Zeile nachrüsten falls fehlend.
10. **`references/known-issues.md` pflegen** — neue Erkenntnisse aus der Anwendung auf einen weiteren Zielreport ergänzen.

## Die drei Formeln (verbindlich, nur hier dokumentiert)

**Formel A — Sub_POS, Text-Expression (z.B. `_KurztextAndArtNrPOS`):**

```
Iif(
    [POS_ArtikelArt] In (0, -10, -24)
    And ?ArgShowArticleNo
    And Not IsNull([POS_ArtNr])
    And [POS_ArtNr] != '',
    [_ArtikelNrPOS] + [POS_ArtNr] + NewLine(),
    ''
)
+
Iif(
    [POS_ArtikelArt] In (0, -10, -24)
    And ?ArgKurzLangtext
    And Not IsNull([POS_Kurztext])
    And Trim([POS_Kurztext]) != '',
    [POS_Kurztext],
    [POS_Bezeichnung]
)
```

**Formel B — Sub_LangtextBemerkung, Text-Expression (z.B. `_BezeichnungAndBemerkung`):**

```
/* Langtext, nur wenn ArgKurzLangtext=True, Kurztext vorhanden ist und er sich vom Kurztext unterscheidet */
Iif(
    ?ArgKurzLangtext
    And Not IsNullOrEmpty([POS_Kurztext])
    And Not IsNullOrEmpty([POS_Bezeichnung])
    And Trim([POS_Bezeichnung]) <> Trim([POS_Kurztext]),
    [POS_Bezeichnung],
    ''
)
+
/* Interner Text */
Iif(
    ?ArgShowInternalText
    And Not IsNullOrEmpty([POS_Bemerkung]),
    NewLine() + NewLine() + [POS_Bemerkung],
    ''
)
```

**Formel C — Sub_LangtextBemerkung, Visible-Expression:**

```
[POS_ArtikelArt] In (0, -10, -24)
And (
    (
        ?ArgKurzLangtext
        And Not IsNullOrEmpty([POS_Kurztext])
        And Not IsNullOrEmpty([POS_Bezeichnung])
        And Trim([POS_Bezeichnung]) <> Trim([POS_Kurztext])
    )
    Or (
        ?ArgShowInternalText
        And Not IsNullOrEmpty([POS_Bemerkung])
    )
)
```

**Warum genau diese drei Formeln zusammenpassen:** Formel A und C teilen dieselbe `?ArgKurzLangtext`-Bedingung an derselben logischen Stelle (im Kurztext-Zweig). Dadurch zeigt Sub_POS bei `True` Kurztext (mit alter Fallback-Logik) und bei `False` immer Langtext — und Sub_LangtextBemerkung zeigt den Langtext-Zusatz ausschließlich dann, wenn Sub_POS ihn NICHT bereits selbst gezeigt hat (`True` + Kurztext vorhanden + abweichend). Wird eine der drei Formeln isoliert geändert, ohne die anderen zwei entsprechend anzupassen, entsteht entweder eine Dopplung (Langtext erscheint zweimal) oder ein Totalausfall (Langtext erscheint nirgends). Deshalb werden diese drei Formeln immer als Einheit behandelt, nie einzeln.

## Sicherheitsstufen — Entscheidungspunkte bei der Anwendung auf einen neuen Zielreport

1. **Automatisch sicher:** Parameter `ArgKurzLangtext` neu anlegen (Boolean, Default No), sofern keine Namenskollision. Übernahme der drei Formeln 1:1, wenn Feldnamen (`POS_ArtikelArt`, `POS_ArtNr`, `POS_Kurztext`, `POS_Bezeichnung`, `POS_Bemerkung`), Parameter (`?ArgShowArticleNo`, `?ArgShowInternalText`) und die ArtikelArt-Liste `(0, -10, -24)` am Zielreport identisch vorliegen.
2. **Vorschlag mit Rückfrage:** Abweichende ArtikelArt-Liste am Zielreport (z.B. `(0, -10, -2, -3, -12, -13)`); abweichende Feld-/Parameternamen; bereits belegte Objektnamen `Sub_LangtextBemerkung`/`xrTable30`/`xrTableZell148` (dann nächste freie Namen verwenden und dem Nutzer mitteilen); ein bereits vorhandenes Band direkt unterhalb von `Sub_POS`, mit dem das neue Band kollidieren könnte.
3. **Nur Verdacht / Platzhalter:** Kein Feld für Kurztext, Bezeichnung oder Bemerkung im Zielreport auffindbar, oder die Positionszeile ist grundlegend anders aufgebaut als bei `dxAio_template` — dann keine der drei Formeln blind übertragen, sondern Struktur explizit mit dem Nutzer klären.

## Skill-ID & Version

Diese Skill trägt die ID **DXJ0005** (aktuell Version **1.0.0**). Format des `work4all-log`-Blocks, Idempotenz-Check und Registry: siehe `../neuen-devexpress-report-skill-anlegen/references/fix-log-format.md` und `../neuen-devexpress-report-skill-anlegen/references/skill-id-registry.md`.

## Versionshistorie

- v1.0.0 — Erstfassung. Lösung erarbeitet und vom Nutzer am Report `dxAio_template` bestätigt (September 2026), Referenz-Implementierung `dxAio_template_new.repx` von Ploner. Kein Verbesserungs-, sondern Erweiterungs-Typ — erste Skill dieses Typs im Plugin.
