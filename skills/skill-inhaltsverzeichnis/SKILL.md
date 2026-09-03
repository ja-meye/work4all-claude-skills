---
name: skill-inhaltsverzeichnis
description: Zeigt eine kompakte Gesamtübersicht aller Fix-/Unterpunkt-IDs über alle work4all-DevExpress-Report-Skills hinweg, mit Kurzbeschreibung und Sicherheitsstufe je ID. Verwenden, wenn der Nutzer wissen will, welche Fixes/Probleme ein Skill (insbesondere `fix-folgeseiten-uebertrag-problem`) überhaupt abdeckt, nach einer bestimmten Fix-ID (z.B. "DXJ0001.F") fragt, ein "Inhaltsverzeichnis" oder eine "Übersicht der Skills/IDs" möchte, oder bevor ein Verbesserungs-Skill läuft kurz zusammengefasst sehen will, was dieser Skill an Einzelfixes kennt.
skill_id: DXJ0004
version: 1.0.0
---

# Skill-Inhaltsverzeichnis

Dokumentations-Typ-Skill (siehe `neuen-devexpress-report-skill-anlegen`, SKILL.md, Abschnitt „Dritter Skill-Typ"). Liest und verändert selbst keine `.repx`-Dateien — reine Übersichts-/Nachschlage-Funktion über das in den anderen Skills bereits vorhandene Unterpunkt-ID-Wissen (siehe `neuen-devexpress-report-skill-anlegen/references/unterpunkt-ids.md`).

## Wann verwenden

- Der Nutzer fragt allgemein, was ein Fach-Skill (insbesondere `fix-folgeseiten-uebertrag-problem`) an Einzelproblemen abdeckt.
- Der Nutzer nennt eine konkrete ID (`DXJ0001.F`, „die F-ID" o. ä.) und will wissen, wofür sie steht.
- Vor dem Start eines Verbesserungs-Skill-Laufs, wenn der Nutzer zusätzlich zur Schritt-3-Vorschau des jeweiligen Fach-Skills einen Gesamtüberblick möchte.
- Der Nutzer bittet direkt um ein "Inhaltsverzeichnis" oder eine "Übersicht der Skills/IDs".

## Schritte

1. **Quelle lesen:** `references/uebersicht.md` — die gepflegte Tabelle aller ID-Zuordnungen, gruppiert nach Skill-ID.
2. **Antwort zusammenstellen:** Je nach Frage entweder die volle Tabelle eines Skills zeigen, oder gezielt die eine angefragte ID mit ihrer Kurzbeschreibung, Sicherheitsstufe und einem Verweis auf den vollständigen Katalog-Eintrag (`<Skill-Name>/references/fix-catalog.md`) für Details.
3. **Nicht die Diagnose-/Fix-Logik selbst ausführen** — dieser Skill beschreibt nur, was existiert, er wendet nichts an. Will der Nutzer einen Fix tatsächlich anwenden, an den zuständigen Fach-Skill verweisen (z. B. `fix-folgeseiten-uebertrag-problem`).

## Pflege

Diese Skill ist nur so aktuell wie `references/uebersicht.md`. Bei jeder inhaltlichen Überarbeitung eines Verbesserungs-Skills (neue/geänderte Unterpunkt-ID) wird `uebersicht.md` im selben Arbeitsschritt mitgepflegt — siehe Hinweis am Ende dieser Datei. Diese Skill selbst bekommt bei einer solchen Aktualisierung KEINEN eigenen Versionsbump, es sei denn, die Struktur/Logik dieses Skills selbst ändert sich (z. B. ein neues Anzeigeformat) — reine Dateninhalts-Updates in `uebersicht.md` sind keine inhaltliche Skill-Überarbeitung im Sinne von Meta-Skill-Baustein 6.

## Versionierung dieses Skills

- v1.0.0 — Erstfassung (2026-09-03): Übersichtstabelle für `DXJ0001` (`fix-folgeseiten-uebertrag-problem`, Unterpunkt-IDs A–H) als Startbestand, Gerüst für künftige Skills mit Unterpunkt-IDs.
