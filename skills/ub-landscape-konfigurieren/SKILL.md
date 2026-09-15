---
name: ub-landscape-konfigurieren
description: Stellt einen bestehenden Unterbericht (XRSubreport) in einem work4all-dxAio_template.repx-Report (und strukturell ähnlichen Ablegern) auf eigenständige Querformat-Seiten um, inklusive der bekannten Fallen (doppelter Seitenumbruch/Leerseite, mögliche Störung der Übertrag-/Folgeseiten-Logik des Hauptberichts). Verwenden, wenn ein Nutzer einen Unterbericht "im Querformat" / "Landscape" drucken möchte, nach GenerateOwnPages fragt, eine Leerseite vor oder nach einem Unterbericht beobachtet, oder einen bestehenden Portrait-Unterbericht auf eigene Querformat-Seiten umstellen will.
metadata:
  skill_id: DXJ0006
  version: 1.0.0
---

# Unterbericht auf Querformat (Landscape) umstellen

## Worum es geht

Ein bestehender Unterbericht (`XRSubreport`) in einem work4all-`dxAio_template.repx`-Report (Hauptbericht bleibt im Hochformat) soll auf eigenständige Querformat-Seiten umgestellt werden — typischerweise, weil eine breite Tabelle (z.B. ein Stunden-/Leistungsnachweis) im Hochformat nicht mehr lesbar passt. Diese Skill kapselt eine am Report `dxAio_template` (work4all, September 2026) erarbeitete und vom Nutzer bestätigte Umstellung (`SubReport_Leistungsnachweis`), damit sie sich auf weitere Unterberichte/Reports übertragen lässt.

**Erweiterungs-Typ, kein Bugfix am Unterbericht selbst.** Diese Skill ändert die Seiten-Orientierung eines funktionierenden Unterberichts — sie repariert dessen fachlichen Inhalt nicht. Trotzdem gelten dieselben Sorgfaltsregeln wie beim Verbesserungs-Typ (Referenzabgleich, Sicherheitsstufen, Validierung, zeitgestempelte Auslieferung), weil eine bestehende `.repx` verändert wird — und weil die Umstellung, siehe unten, den *Hauptbericht* an einer ganz anderen Stelle beeinflussen kann.

Lies **`../neuen-devexpress-report-skill-anlegen/references/repx-format-basics.md`** zuerst, bevor du das eingebettete C#-Skript oder rohes XML einer `.repx` direkt liest oder änderst (Pflichtbaustein 10 des Meta-Skills) — Encoding/BOM, Escaping-Pipeline, Bandmodell, `<Localization>`-Block.

## Das Kern-Rezept (verbindlich, an `dxAio_template` bestätigt)

Drei Attribut-Änderungen, immer als Einheit:

1. **Auf dem `XRSubreport`-Host-Control** (im Hauptbericht, die Stelle, die den Unterbericht einbindet): `GenerateOwnPages="true"` setzen. Das sorgt dafür, dass der Unterbericht auf einer eigenen, neuen Seite beginnt — unabhängig vom Seitenfluss des Hauptberichts.
2. **Im eingebetteten `ReportSource`** des Unterberichts (dessen eigenes Report-Wurzelelement, mit eigenem `ScriptsSource`, `ReportUnit`, `PageWidthF` usw.): `Landscape="true"` setzen.
3. **`PageWidthF`/`PageHeightF` im selben `ReportSource`-Element vertauschen.** Bei Hochformat A4 (`ReportUnit="TenthsOfAMillimeter"`) ist das `PageWidthF="2100" PageHeightF="2970"` → Querformat wird `PageWidthF="2970" PageHeightF="2100"`. Bei einem anderen Papierformat/anderer Maßeinheit: die vorhandenen Hochformat-Werte des Unterberichts selbst als Ausgangspunkt nehmen und tauschen, nicht die Werte des Hauptberichts kopieren.

Referenz-Fundstelle (`reference-files/dxAio_template_final_landscape.repx`): das `Item3`-Element mit `ControlType="XRSubreport" Name="SubReport_Leistungsnachweis" ... GenerateOwnPages="true"`, darin `<ReportSource ... ReportUnit="TenthsOfAMillimeter" Landscape="true" PageWidthF="2970" PageHeightF="2100" ...>`. Der Vorher-Zustand ganz ohne diese drei Attribute liegt in `reference-files/dxAio_template_BeforeLandscape.repx` an derselben Stelle (`Name="SubReport_Leistungsnachweis"`, ohne `GenerateOwnPages`, ohne `Landscape`, Hochformat-Maße).

**Was NICHT Teil dieses Rezepts ist:** Der Diff zwischen den beiden mitgelieferten Referenzdateien enthält daneben noch umfangreiche fachliche Weiterentwicklung des Unterberichts selbst (Ticket-Sammel-Logik in der Fußzeile, neue `Kostenerfassung`-Felder, RTF-Bereinigung, kultursichere Dezimal-Konvertierung). Das ist Business-Inhalt dieses einen Unterberichts, kein Bestandteil der Landscape-Umstellung — beim Übertragen auf einen anderen Ziel-Unterbericht wird nur das Kern-Rezept oben angewendet, nicht der komplette Referenz-Diff.

## Bekannte Falle 1: Leerseite durch doppelten Seitenumbruch

**Symptom:** Vor der ersten Seite des (jetzt querformatigen) Unterberichts erscheint eine leere Seite.

**Ursache:** Die Band (meist eine `SubBand`), die den `XRSubreport` direkt enthält, hat zusätzlich selbst `PageBreak="BeforeBand"` gesetzt — oft ein Überbleibsel aus der Zeit, als der Unterbericht noch im Hochformat lief und ein manueller Seitenumbruch vor ihm gewünscht war. Mit `GenerateOwnPages="true"` (Schritt 1 des Rezepts) erzwingt DevExpress selbst bereits einen neuen Seitenanfang für den Unterbericht — der zusätzliche `PageBreak="BeforeBand"` erzeugt dann einen zweiten, überflüssigen Umbruch davor. Die dazwischenliegende Seite bleibt leer, weil die Host-Band meist nur ein unsichtbares Marker-Label o.ä. enthält, nicht den eigentlichen Inhalt.

**Fix (automatisch sicher, wenn das Muster zutrifft):** `PageBreak="BeforeBand"` von der Host-`SubBand` entfernen. Der Unterbericht beginnt weiterhin zuverlässig auf einer eigenen Seite — jetzt aber ohne vorgeschaltete Leerseite. Vor dem Entfernen kurz prüfen, ob die Band außer dem `XRSubreport` noch sichtbaren Inhalt enthält, der absichtlich einen eigenen Seitenumbruch braucht (dann Sicherheitsstufe 2: Rückfrage statt automatischem Entfernen).

## Bekannte Falle 2 (nur Risiko, an `dxAio_template` NICHT eingetreten): Übertrag-/Folgeseiten-Logik im Hauptbericht

`GenerateOwnPages="true"` auf einem Unterbericht kann laut DevExpress-Support-Dokumentation `RepeatEveryPage`-Bänder **dokumentweit** stören — nicht nur innerhalb des Unterberichts, sondern auch im Hauptbericht, an Stellen, die mit dem umgestellten Unterbericht auf den ersten Blick nichts zu tun haben (typisch betroffen: eine wiederholte Tabellenkopfzeile oder ein Übertrag/Carry-Forward-Betrag auf Folgeseiten der Positionstabelle).

An `dxAio_template` wurde dieses Risiko in einer ausführlichen Diagnose-Sitzung (04.–15.09.2026) untersucht — mit dem Ergebnis, dass es **in diesem konkreten Fall nicht eingetreten ist**: Die Übertrag-/Folgeseiten-Logik funktionierte nach der Landscape-Umstellung unverändert korrekt (bestätigt mit echten, mehrseitigen Testdaten). Das ursprünglich beobachtete Symptom (fehlende Titelzeile/Übertrag) hatte zwei andere Ursachen: fehlende Preise in den Testdaten und eine Druckvorschau, die den Hauptbericht im Querformat rechts abschneidet und die Preisspalte dadurch unsichtbar machte. Details: `references/known-issues.md`, Eintrag 1.

Weil das Risiko dokumentiert, aber nicht report-übergreifend widerlegt ist, empfiehlt diese Skill einen **optionalen** Check mit dem Skill `fix-folgeseiten-uebertrag-problem` (DXJ0001) — sowohl vorher als Baseline als auch nachher zum Abgleich:

- **Vor der Landscape-Umstellung (optional, Schritt 0):** Dem Nutzer anbieten, `fix-folgeseiten-uebertrag-problem` diagnostisch auf dem Zielreport laufen zu lassen, um zu bestätigen, dass Übertrag/Folgeseiten-Kopfzeile im Hauptbericht vor der Umstellung sauber funktionieren. Das ist eine Baseline, kein Pflichtschritt — bei Ablehnung durch den Nutzer normal fortfahren.
- **Nach der Umstellung (Empfehlung, kein Blocker):** Dem Nutzer empfehlen, einen mehrseitigen Testdruck mit **echten, von Null verschiedenen Preisen auf den Positionen** zu machen (siehe `references/known-issues.md` Eintrag 1 — mit leeren Testdaten ist ein Übertrag=0 nicht von einem echten Bug zu unterscheiden) und dabei gezielt auf die Positionstabelle jenseits der Seite mit dem Unterbericht zu achten. Zeigt sich dort ein Symptom aus der Trigger-Liste von `fix-folgeseiten-uebertrag-problem`, diese Skill zur Diagnose hinzuziehen — nicht blind einen Workaround bauen, sondern erst den `fix-folgeseiten-uebertrag-problem`-Skill diagnostizieren lassen, ob es sich überhaupt um einen echten, reproduzierbaren Bug handelt (siehe Warnung unten).

**Warnung aus der Diagnose-Sitzung, festgehalten in `references/known-issues.md` Eintrag 2:** Ein com­plexer PageHeader-Kopie-Workaround (manuelle Nachbildung von Tabellenkopf und Übertrag in einer eigenen `PageHeaderBand`) wurde an `dxAio_template` vollständig durchgebaut, mehrfach iteriert und am Ende wieder verworfen, weil sich herausstellte, dass er gar nicht nötig war. Bevor an einem neuen Zielreport ein ähnlicher Workaround begonnen wird: zuerst mit echten, mehrseitigen Testdaten (nicht mit leeren Preisen) und ohne UI-Beschneidung durch die Druckvorschau (PDF-Export statt Vorschau) bestätigen, dass tatsächlich ein Bug vorliegt.

## Arbeitsablauf

1. **Zielreport und Ziel-Unterbericht entgegennehmen.** Welcher `XRSubreport` soll auf Querformat umgestellt werden? Ist er aktuell im Hochformat eingebettet (wie im Referenzfall) oder wird er neu angelegt?
2. **Schritt 0 (optional):** `fix-folgeseiten-uebertrag-problem` als Baseline-Check anbieten (siehe Falle 2 oben).
3. **Referenzdateien optional abgleichen** (siehe unten) — kein Pflichtschritt, die Skill funktioniert auch ohne strukturell nahe Referenz anhand des Kern-Rezepts.
4. **Kern-Rezept anwenden** (die drei Attribute, siehe oben). Sicherheitsstufe 1, wenn der Zielreport dieselbe `ReportUnit="TenthsOfAMillimeter"`-Konvention und ein reguläres Hochformat-Papierformat verwendet; sonst Sicherheitsstufe 2 (Ziel-Maße vor dem Vertauschen mit dem Nutzer bestätigen).
5. **Host-Band auf `PageBreak="BeforeBand"` prüfen** (Falle 1) und ggf. entfernen.
6. **Skript-Hygiene** — nur als separater, ausdrücklich angeforderter Schritt (Zwei-Wege-Kommentarregel im Meta-Skill), nie beiläufig in diesem Lauf.
7. **Validierung**: generische Basis-Checkliste `../neuen-devexpress-report-skill-anlegen/references/validation-generic.md` plus die fachspezifischen Punkte in `references/validierung-ub-landscape.md`.
8. **Empfehlung nach der Umstellung** aussprechen (siehe Falle 2 — mehrseitiger Testdruck mit echten Preisen, PDF statt Vorschau).
9. **Auslieferung** als neue, zeitgestempelte `.repx` (`<Reportname>_<JJJJ-MM-TT>_<hh-mm>.repx`, Europe/Berlin) — nie In-Place-Überschreiben, außer der Nutzer verlangt es ausdrücklich (dann vorher Backup, siehe Meta-Skill Baustein 9). `work4all-log`-Eintrag mit Skill-ID `DXJ0006` schreiben (Format siehe `../neuen-devexpress-report-skill-anlegen/references/fix-log-format.md`), Anker-Zeile nachrüsten falls fehlend.
10. **`references/known-issues.md` pflegen** — neue Erkenntnisse aus der Anwendung auf einen weiteren Zielreport/Unterbericht ergänzen.

## Referenzdateien (liegen bei, Anfordern beim Nutzer bleibt optional)

- `reference-files/dxAio_template_BeforeLandscape.repx` — Vorher-Zustand: `SubReport_Leistungsnachweis` existiert bereits, aber im Hochformat, ohne `GenerateOwnPages`.
- `reference-files/dxAio_template_final_landscape.repx` — Nachher-Zustand: Kern-Rezept angewendet, Falle 1 bereits behoben (kein `PageBreak="BeforeBand"` mehr auf der Host-Band).

Vorgehen: vor dem Umsetzen strukturell gegen den Zielreport abgleichen (Bandnamen, Control-Namen können abweichen — die Referenz zeigt das bestätigte Muster, nicht zwingend identische Objektnamen). Weicht der Zielreport strukturell stark ab: anhand des Kern-Rezepts arbeiten und im Abschlussbericht kurz vermerken, dass ohne engen Referenzabgleich gearbeitet wurde.

## Sicherheitsstufen — Entscheidungspunkte bei der Anwendung auf einen neuen Zielreport

1. **Automatisch sicher:** Die drei Attribute des Kern-Rezepts setzen, wenn der Zielreport `ReportUnit="TenthsOfAMillimeter"` verwendet und die aktuellen Hochformat-Maße des Ziel-Unterberichts eindeutig ablesbar sind (einfaches Vertauschen von `PageWidthF`/`PageHeightF`). `PageBreak="BeforeBand"` von der Host-Band entfernen, wenn diese außer dem `XRSubreport` erkennbar nur unsichtbaren/Marker-Inhalt enthält.
2. **Vorschlag mit Rückfrage:** Abweichende Maßeinheit/Papierformat am Zielreport; die Host-Band enthält neben dem `XRSubreport` noch sichtbaren eigenen Inhalt, der möglicherweise absichtlich einen eigenen Seitenumbruch braucht; der Ziel-Unterbericht ist bereits auf `GenerateOwnPages="true"` gesetzt (dann erst klären, ob nur die Orientierung fehlt oder ob schon einmal an dieser Stelle gearbeitet wurde).
3. **Nur Verdacht / Platzhalter:** Der Zielreport verwendet eine andere `ReportUnit` als `TenthsOfAMillimeter`, oder der Ziel-`XRSubreport` hat kein eigenes `ReportSource`-Element mit eigenen Seitenmaßen (untypischer Aufbau) — dann nicht blind das Kern-Rezept übertragen, sondern Struktur explizit mit dem Nutzer klären.

## Skill-ID & Version

Diese Skill trägt die ID **DXJ0006** (aktuell Version **1.0.0**). Format des `work4all-log`-Blocks, Idempotenz-Check und Registry: siehe `../neuen-devexpress-report-skill-anlegen/references/fix-log-format.md` und `../neuen-devexpress-report-skill-anlegen/references/skill-id-registry.md`.

## Versionshistorie

- v1.0.0 — Erstfassung. Kern-Rezept und beide Fallen erarbeitet und am Report `dxAio_template` bestätigt (September 2026), Referenzpaar `dxAio_template_BeforeLandscape.repx` / `dxAio_template_final_landscape.repx`. Erweiterungs-Typ, analog zu `kurz-und-langtext-einarbeiten` (DXJ0005).
