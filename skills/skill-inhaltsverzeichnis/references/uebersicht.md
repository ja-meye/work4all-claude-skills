# Inhaltsverzeichnis aller Fix-/Unterpunkt-IDs

Lebendes Dokument (analog zu `known-issues.md` der Fach-Skills) — bei jeder inhaltlichen Überarbeitung eines Verbesserungs-Skills wird diese Tabelle im selben Zug mitgepflegt (siehe `SKILL.md`, Schritt 2). Quelle der Wahrheit für den Inhalt jeder ID bleibt aber immer der jeweilige Fach-Skill (`fix-catalog.md` bzw. `SKILL.md`, Abschnitt „Unterpunkt-IDs") — diese Tabelle ist eine Kopie zur schnellen Übersicht, kein Ersatz.

## DXJ0001 — `fix-folgeseiten-uebertrag-problem` (Verbesserungs-Typ, aktuell v1.2.0)

| ID | Kurzbeschreibung | Sicherheitsstufe |
|----|----|----|
| `DXJ0001.A` | Edge-Case Übertrag-Problem: fehlende Summe/Übertrag auf Seiten abgefangen, auf denen der Detailbereich noch nicht begonnen hat (langer Kopftext/Titelübersicht) | Vorschlag mit Rückfrage |
| `DXJ0001.B` | Folgeseitenproblem: fehlende Titelzeile auf Folgeseite behoben (sabotierende `BeforePrint`-Logik entfernt) | Automatisch sicher* |
| `DXJ0001.C` | Skript aufgeräumt (leere Handler, toter Code, work4all-interne Parameter, wirkungslose Bänder, Debug-Ausgaben, gekürzte Kommentare) | Automatisch sicher, PFLICHT* |
| `DXJ0001.D` | Log-Eintrag im Script wird ergänzt (`work4all-log`-Mechanismus selbst, kein Fix-Muster) | — (Infrastruktur) |
| `DXJ0001.E` | Abstand-vor-Rabatt-Problem behoben (`AllowMarkupText`-Leerzeile + Folge-Padding) | Vorschlag mit Rückfrage |
| `DXJ0001.F` | Übertrag-Problem: Sektionen werden auf Seite 1 nicht mehr fälschlich mit reserviertem Platz angezeigt | Vorschlag mit Rückfrage* |
| `DXJ0001.G` | Mindesthöhen statt `KeepTogether` gegen Weißraum/abgeschnittene Übertrag-Anzeige (ersetzt `DXJ0001`-Alt-Muster b) | Automatisch sicher* |
| `DXJ0001.H` | Batch-Sicherheits-Reset bei Sammeldruck mehrerer Belege in einem Lauf | Vorschlag mit Rückfrage* |

`*` = abhängig von Bedingungen (z. B. bestätigte Referenzdatei) automatisch sicher, siehe Detaileinstufung im jeweiligen `fix-catalog.md`-Eintrag.

## DXJ0002 — `neuen-devexpress-listenreport-bauen` (Neuerstellungs-Typ)

Noch keine Unterpunkt-IDs — Baustein 11 gilt aktuell nur für Verbesserungs-Typ-Skills. Bei Bedarf (z. B. wiederkehrende, einzeln abwählbare Bauschritte) kann das Schema sinngemäß übertragen werden.

## DXJ0003 — `neuen-devexpress-report-skill-anlegen` (Meta-Skill)

Kein Fach-Skill mit Fix-Mustern — keine Unterpunkt-IDs vorgesehen.

## Pflege-Hinweis

Wird ein neues Muster/eine neue Unterpunkt-ID in einem Fach-Skill vergeben (oder eine bestehende geändert/als überholt markiert), wird diese Tabelle im selben Arbeitsschritt aktualisiert — nicht nachträglich gesammelt. Reihenfolge/Buchstaben folgen den Stabilitätsregeln aus `unterpunkt-ids.md` (append-only, keine Neuvergabe bestehender Buchstaben).
