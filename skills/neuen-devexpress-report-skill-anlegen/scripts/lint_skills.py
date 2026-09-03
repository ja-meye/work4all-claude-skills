#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lint_skills.py - prueft alle Skills dieses Plugins gegen die offizielle Agent-Skills-Spezifikation.

Aufruf:   python3 lint_skills.py [<plugin-wurzel>]     (Standard: zwei Ebenen ueber diesem Skript)
Ergebnis: Tabelle mit OK/FAIL/WARN je Regel, Exit-Code 1 sobald ein FAIL auftritt.

Quellen der Regeln (Stand 09/2026):
  https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
  https://code.claude.com/docs/en/skills  (Frontmatter-Referenz)

S01-S04 sind harte Spec-Grenzen (Upload/Packaging schlaegt sonst fehl bzw. der Skill wird
nicht gefunden), S05-S09 sind dokumentierte Best Practices mit spuerbarer Wirkung.
"""
import sys, os, re, glob, io

# claude.ai-Upload, Skills-API und package_skill.py akzeptieren NUR diese Frontmatter-Keys.
ALLOWED_KEYS = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}
NAME_RE = re.compile(r'^[a-z0-9-]{1,64}$')
RESERVED = ('anthropic', 'claude')
DESC_MAX = 1024          # Zeichen, harte Grenze
SKILL_MAX_LINES = 500    # Best Practice
TOKEN_RUNAWAY = 15000    # nur Ausreisser melden: die offizielle Grenze ist "<=500 Zeilen".
                         # Qualitaet geht vor Token-Zahl - eine SKILL.md darf so lang sein,
                         # wie der Ablauf es braucht. Gemeldet wird erst unkontrolliertes Wachstum.

rows = []
def add(sid, skill, rule, ok, detail='', warn=False):
    rows.append((sid, skill, rule, 'WARN' if (warn and not ok) else ('PASS' if ok else 'FAIL'), detail))

def frontmatter(text):
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    if not m:
        return None, {}
    body = m.group(1)
    keys, cur = {}, None
    for line in body.splitlines():
        if re.match(r'^[A-Za-z_-]+:', line):
            cur = line.split(':', 1)[0]
            keys[cur] = line.split(':', 1)[1].strip()
        elif cur and line.startswith(' '):
            keys[cur] = (keys[cur] + ' ' + line.strip()).strip()
    return body, keys

def lint(root):
    for path in sorted(glob.glob(os.path.join(root, 'skills', '*', 'SKILL.md'))):
        skill = os.path.basename(os.path.dirname(path))
        text = io.open(path, encoding='utf-8').read()
        body, keys = frontmatter(text)

        # S01 Frontmatter-Keys
        if body is None:
            add('S01', skill, 'YAML-Frontmatter vorhanden', False, 'kein --- Block')
            continue
        unexpected = sorted(set(keys) - ALLOWED_KEYS)
        add('S01', skill, 'Nur erlaubte Frontmatter-Keys', not unexpected,
            'unerlaubt: %s (eigene Felder gehoeren unter metadata:)' % unexpected)

        # S02 name
        name = keys.get('name', os.path.basename(os.path.dirname(path)))
        ok = bool(NAME_RE.match(name)) and not any(r in name.lower() for r in RESERVED)
        add('S02', skill, 'name: klein/Ziffern/Bindestrich, <=64, ohne Reservwort', ok, name)

        # S03 description
        desc = keys.get('description', '')
        add('S03', skill, 'description vorhanden und <=1024 Zeichen', bool(desc) and len(desc) <= DESC_MAX,
            '%d Zeichen' % len(desc))
        # S04 description nennt WAS und WANN
        has_when = bool(re.search(r'\b(verwenden|nutzen|wenn|use when|triggers?)\b', desc, re.I))
        add('S04', skill, 'description nennt WAS und WANN (Trigger)', has_when, '' if has_when else 'kein Wann-Teil erkennbar')

        # S05 Laenge / Token-Last
        lines = text.count('\n') + 1
        tokens = len(text) // 4
        add('S05', skill, 'SKILL.md <=500 Zeilen', lines <= SKILL_MAX_LINES, '%d Zeilen' % lines)
        add('S06', skill, 'SKILL.md-Umfang (Information, kein Zielwert)', tokens <= TOKEN_RUNAWAY,
            '~%d Tokens%s' % (tokens, '' if tokens <= TOKEN_RUNAWAY else ' - unkontrolliertes Wachstum pruefen'), warn=True)

        # S07 Referenzen nur eine Ebene tief + existieren
        refs = re.findall(r'`(references/[\w\-./]+\.md)`', text) + re.findall(r'\]\((references/[\w\-./]+\.md)\)', text)
        missing = [r for r in set(refs) if not os.path.exists(os.path.join(os.path.dirname(path), r))]
        add('S07', skill, 'In SKILL.md genannte references/ existieren', not missing, 'fehlt: %s' % missing[:3])

        # S08 keine Windows-Pfadtrenner in Skill-internen Pfaden
        bad = re.findall(r'`(?:references|scripts|assets)\\[^`]*`', text)
        add('S08', skill, 'Nur Forward-Slashes in Skill-internen Pfaden', not bad, str(bad[:3]))

        # S09 Referenzdateien >100 Zeilen brauchen ein Inhaltsverzeichnis
        noToc = []
        for ref in glob.glob(os.path.join(os.path.dirname(path), 'references', '*.md')):
            t = io.open(ref, encoding='utf-8').read()
            if t.count('\n') > 100 and not re.search(r'^## (Inhalt|Contents)\b', t, re.M):
                noToc.append(os.path.basename(ref))
        add('S09', skill, 'Referenzdateien >100 Zeilen mit Inhaltsverzeichnis', not noToc, str(noToc), warn=True)

        # S10 Evaluations vorhanden (Best Practice: >=3 Szenarien)
        ev = glob.glob(os.path.join(os.path.dirname(path), 'evals', '*.json'))
        add('S10', skill, 'Mindestens 3 Evaluations-Szenarien', len(ev) >= 3, '%d gefunden' % len(ev), warn=True)

def cross_checks(root):
    """S11/S12: dieselbe Information darf nicht an zwei Stellen auseinanderlaufen."""
    import json
    fix = os.path.join(root, 'skills', 'fix-folgeseiten-uebertrag-problem')
    meta = os.path.join(root, 'skills', 'neuen-devexpress-report-skill-anlegen')
    toc = os.path.join(root, 'skills', 'skill-inhaltsverzeichnis')

    def txt(*parts):
        p = os.path.join(*parts)
        return io.open(p, encoding='utf-8').read() if os.path.exists(p) else ''

    # --- S11 Unterpunkt-IDs ---
    sk_t, cat_t, toc_t = txt(fix, 'SKILL.md'), txt(fix, 'references', 'fix-catalog.md'), txt(toc, 'references', 'uebersicht.md')
    ids_sk = set(re.findall(r'`(DXJ\d{4}\.[A-Z])`', sk_t))
    ids_cat = set(re.findall(r'Unterpunkt-ID `(DXJ\d{4}\.[A-Z])`', cat_t))
    ids_toc = set(re.findall(r'`(DXJ\d{4}\.[A-Z])`', toc_t))
    # IDs ohne Katalogeintrag sind erlaubt, wenn die SKILL.md sie ausdruecklich als Nicht-Muster ausweist
    documented = set(re.findall(r'`(DXJ\d{4}\.[A-Z])` ist bewusst kein Fix-Muster', sk_t))
    missing_cat = sorted((ids_sk - ids_cat) - documented)
    toc_diff = sorted(ids_sk ^ ids_toc)
    add('S11', 'plugin-weit', 'Unterpunkt-IDs stimmen ueber SKILL.md/Katalog/Inhaltsverzeichnis',
        not missing_cat and not toc_diff,
        ('ohne Katalogeintrag: %s ' % missing_cat if missing_cat else '') +
        ('Abweichung zum Inhaltsverzeichnis: %s' % toc_diff if toc_diff else ''))

    # --- S12 Versionsangaben ---
    reg_t = txt(meta, 'references', 'skill-id-registry.md')
    problems = []
    for path in sorted(glob.glob(os.path.join(root, 'skills', '*', 'SKILL.md'))):
        t = io.open(path, encoding='utf-8').read()
        m_id = re.search(r'skill_id:\s*(\S+)', t)
        m_v = re.search(r'version:\s*(\S+)', t)
        if not (m_id and m_v):
            continue
        sid, ver = m_id.group(1), m_v.group(1)
        row = re.search(r'\|\s*' + sid + r'\s*\|[^\n]*\|\s*([\d.]+)\s*\|', reg_t)
        if row and row.group(1) != ver:
            problems.append('%s: Frontmatter %s vs. Registry %s' % (sid, ver, row.group(1)))
    m_toc = re.search(r'aktuell v([\d.]+)', toc_t)
    m_fix = re.search(r'version:\s*(\S+)', sk_t)
    if m_toc and m_fix and m_toc.group(1) != m_fix.group(1):
        problems.append('DXJ0001: Frontmatter %s vs. Inhaltsverzeichnis %s' % (m_fix.group(1), m_toc.group(1)))
    add('S12', 'plugin-weit', 'Versionsangaben stimmen ueber alle Dateien ueberein', not problems, ' | '.join(problems))

def report():
    w1 = max(len(r[1]) for r in rows); w2 = max(len(r[2]) for r in rows)
    fails = 0
    print('=' * (w1 + w2 + 40))
    for sid, skill, rule, status, detail in rows:
        mark = {'PASS': 'OK  ', 'FAIL': 'FAIL', 'WARN': 'WARN'}[status]
        print('%s %-4s %-*s %-*s %s' % (mark, sid, w1, skill, w2, rule, detail if status != 'PASS' else ''))
        fails += status == 'FAIL'
    print('=' * (w1 + w2 + 40))
    print('%d Pruefungen, %d FAIL' % (len(rows), fails))
    return 1 if fails else 0

if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')
    root = os.path.normpath(root)
    lint(root)
    cross_checks(root)
    sys.exit(report())
