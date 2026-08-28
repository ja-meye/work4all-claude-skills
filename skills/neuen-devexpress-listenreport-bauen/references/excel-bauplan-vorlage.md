# Aufbau der Feldzuordnungs-Excel

Ziel der Excel: der Fachbereich/Nutzer kann pro Ausgabefeld die technische Herkunft (DB-Tabelle, DB-Feld) eintragen, ohne dass Missverständnisse über welches Feld gemeint ist entstehen. Die Excel ist gleichzeitig Arbeitsdokument (vor dem Bau) und Kontrollliste (nach dem Bau, mit den tatsächlich verwendeten Zuordnungen befüllt).

## Spalten (eine Tabelle, ein Blatt "Feldzuordnung")

| Spalte | Inhalt |
|---|---|
| Nr. | Laufende Nummer |
| Ausgabefeld (Report) | Bezeichnung, wie sie im Mockup steht (z.B. "Firma / Name") |
| Beispielwert (aus Entwurf) | Echter Beispielwert aus dem Mockup — macht eindeutig, welches Feld gemeint ist |
| Typ | "Detail" (wiederholt sich pro Zeile) oder "Kopf/Parameter" (einmal pro Report) |
| DB-Tabelle | **leer, gelb markiert** — vom Nutzer auszufüllen, sofern nicht schon aus einer mitgelieferten Query bekannt |
| DB-Feld | **leer, gelb markiert** — dito |
| Anmerkung | Offene Fragen, Formatierungshinweise, Sonderfälle |

## Struktur/Reihenfolge im Blatt

1. Titelzeile (zusammengeführt über alle Spalten) + kurze Legende, was auszufüllen ist.
2. Abschnitt "Detailzeile – wiederholt sich pro Datensatz" mit den Feldern, die pro Zeile im Report vorkommen.
3. Abschnitt "Kopf-/Parameterangaben – einmal pro Report" für Sortierung, Filtertext, Datensatzanzahl, Zeitstempel, Seitenzahl, Logo. Dazu jeweils in der Anmerkung-Spalte kurz einordnen, dass es sich meist um einen Report-Parameter/Ausdruck handelt, nicht um ein einfaches DB-Feld.
4. Falls schon eine Referenzquelle (alte Query, alter Report) vorliegt: ein grün hinterlegter Beispielblock "Beispiel zur Orientierung – so ist das Format gemeint", der 2–3 bereits bekannte Zuordnungen aus einem anderen, bestehenden Report zeigt (mit Hinweis, dass das nur zur Veranschaulichung dient, nicht 1:1 übernommen werden soll, wenn es ein anderer Report/andere Datenbasis ist).

## Formatierung

- Kopfzeile: dunkler Fond, weiße fette Schrift.
- Eingabespalten (DB-Tabelle, DB-Feld): helle Gelbfüllung (`FFF2AE` o.ä.) als klares visuelles Signal "hier ausfüllen".
- Beispielblock: helle Grünfüllung, damit er sich klar von den auszufüllenden Zeilen unterscheidet.
- Abschnittsüberschriften: graue Fülllinie über die volle Breite.
- Professionelle Schriftart (Arial), keine Formeln nötig für dieses Dokument — es ist eine reine Übersichts-/Eingabetabelle, kein Rechenmodell.
- Spaltenbreiten so wählen, dass Beispielwerte und Anmerkungen nicht abgeschnitten wirken (`wrap_text=True` auf den Textspalten).

## Nach dem Bau der .repx

Die Excel erneut öffnen und die inzwischen bekannten Zuordnungen in die vorher leeren DB-Tabelle/DB-Feld-Spalten eintragen — sie wird dadurch zur Kontrollliste, die zusammen mit der `.repx` ausgeliefert wird. Für Felder, die mangels Information im Report nur als Platzhalter (`TODO: DB-Feld?`) gebaut werden konnten, in der Anmerkung-Spalte explizit "OFFEN: ..." mit der konkreten Rückfrage vermerken — nicht einfach leer lassen, sonst geht die Information unter, warum das Feld noch fehlt.
