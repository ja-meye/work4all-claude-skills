# Skill-ID-Registry

Zentrale, fortlaufend gepflegte Liste aller vergebenen Skill-IDs für die work4all-DevExpress-Report-Skills. Bei jedem neuen Skill wird hier eine Zeile ergänzt — nie überschreiben, nur anhängen.

## Format der Skill-ID

`DX` + Autoren-Kürzel (1 Buchstabe, Großbuchstabe) + 4-stellige, fortlaufende Nummer (mit führenden Nullen):

```
DX J 0001
│  │ └── fortlaufende Nummer, 4-stellig, pro Autor eigener Zähler
│  └──── Autoren-Kürzel (1 Buchstabe)
└─────── festes Präfix "DX" (DevExpress)
```

Beispiele: `DXJ0001` (Jens, 1. Skill), `DXM0001` (Musti, 1. Skill), `DXO0001` (Oliver, 1. Skill).

Jeder Autor führt seinen eigenen Nummernkreis (Autoren-Kürzel + Nummer ist eindeutig), damit unabhängig voneinander gearbeitet werden kann, ohne Kollisionen bei der Nummernvergabe abstimmen zu müssen. Kürzel-Vergabe bei neuen Kollegen: erster Buchstabe des Vornamens, bei Kollision mit einem bereits vergebenen Kürzel wird ein zweiter, gut unterscheidbarer Buchstabe gewählt (z.B. zwei Kollegen mit "M": `DXM...` und `DXMU...` oder ein anderer Buchstabe nach Absprache).

## Registrierte Skill-IDs

| Skill-ID  | Skill-Name                               | Typ            | Autor | Erstellt am | Version |
|-----------|-------------------------------------------|----------------|-------|-------------|---------|
| DXJ0001   | fix-folgeseiten-uebertrag-problem          | Verbesserung   | Jens  | 2026-08-28  | 1.1.0   |
| DXJ0002   | neuen-devexpress-listenreport-bauen        | Neuerstellung  | Jens  | 2026-08-28  | 1.1.0   |
| DXJ0003   | neuen-devexpress-report-skill-anlegen      | Meta-Skill     | Jens  | 2026-08-30  | 0.2.0   |

Nächste freie Nummer für Jens: **DXJ0004**.

## Ablauf bei einem neuen Skill

1. Nächste freie Nummer für den jeweiligen Autor in dieser Tabelle nachschlagen.
2. Neue Zeile am Ende der Tabelle ergänzen (Skill-ID, Name, Typ, Autor, Datum, Startversion — üblicherweise `1.0.0` für Verbesserungs-/Neuerstellungs-Skills, `0.1.0` für Meta-/Hilfs-Skills in einer noch nicht finalen Erstfassung).
3. Die vergebene Skill-ID in das Frontmatter (`skill_id:`) des neuen `SKILL.md` eintragen.
4. Diese Datei zusammen mit dem neuen Skill an beide Ablageorte ausliefern (siehe `ablage-und-versionierung.md`).
