#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_repx.py - Check-Index fuer work4all-DevExpress-.repx-Dateien (Skill DXJ0001)

Aufruf:   python3 validate_repx.py <bearbeitet.repx> [--baseline <original.repx>]
Ergebnis: Tabelle mit PASS/FAIL/WARN je Check, Exit-Code 1 sobald ein FAIL auftritt.

Jeder Check hier hat in der Praxis mindestens einmal einen echten Fehler gefangen
(Quelle: known-issues.md). C01-C09 sind die klassischen Checks aus
validation-checklist.md, C10-C16 sind aus der Sitzung vom 03./04.09.2026
dazugekommen - genau die Fehler, die dort erst der Kunde im Designer bzw. im
Testdruck gefunden hat.
"""
import sys, re, html
from collections import Counter
import xml.dom.minidom as minidom

TAG_RE = re.compile(r'<(/?)([A-Za-z_][\w.\-]*)((?:"[^"]*"|\'[^\']*\'|[^>"\'])*)>')
results = []

def add(cid, name, ok, detail='', warn=False):
    results.append((cid, name, 'WARN' if (warn and not ok) else ('PASS' if ok else 'FAIL'), detail))

def load(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        return f.read()

def main_script(c):
    s = c.find('ScriptsSource="')
    if s == -1:
        return None, None
    s += len('ScriptsSource="')
    e = c.find('SnapGridSize="10"')
    if e == -1:
        return None, None
    raw = c[s:e].rstrip()[:-1]
    return raw, html.unescape(raw)

def strip_comments(code):
    """Entfernt // ... und /* ... */ - sonst schlagen Checks auf Kommentartext an."""
    code = re.sub(r'/\*.*?\*/', ' ', code, flags=re.S)
    return re.sub(r'//[^\r\n]*', ' ', code)

def handler_bodies(script):
    """{Methodenname: Rumpf} fuer alle 'private void X(...) { ... }'."""
    out = {}
    for m in re.finditer(r'private void (\w+)\([^)]*\)\s*\{', script):
        depth, i = 1, m.end()
        while depth > 0 and i < len(script):
            if script[i] == '{': depth += 1
            elif script[i] == '}': depth -= 1
            i += 1
        out[m.group(1)] = script[m.end():i-1]
    return out

def run(path, baseline_path=None):
    raw_bytes = open(path, 'rb').read()
    c = load(path)
    base = load(baseline_path) if baseline_path else None
    raw_val, script = main_script(c)

    # --- C01 BOM ---------------------------------------------------------
    add('C01', 'UTF-8-BOM am Dateianfang', raw_bytes[:3] == b'\xef\xbb\xbf')

    # --- C02 XML wohlgeformt --------------------------------------------
    try:
        minidom.parseString(c.encode('utf-8'))
        add('C02', 'XML wohlgeformt', True)
    except Exception as ex:
        add('C02', 'XML wohlgeformt', False, str(ex))

    # --- C03 Tag-Paarigkeit (findet auch, was minidom nur vage meldet) ---
    stack, mismatch = [], ''
    for m in TAG_RE.finditer(c):
        closing, name, attrs = m.group(1), m.group(2), m.group(3)
        if attrs.endswith('/'):
            continue
        line = c.count('\n', 0, m.start()) + 1
        if closing:
            if not stack:
                mismatch = '</%s> Zeile %d ohne offenes Tag' % (name, line); break
            top, topline = stack.pop()
            if top != name:
                mismatch = 'Zeile %d: </%s> schliesst <%s> von Zeile %d' % (line, name, top, topline); break
        else:
            stack.append((name, line))
    add('C03', 'Tag-Paarigkeit (Open/Close identisch)', not mismatch and not stack,
        mismatch or ('unclosed: %s' % stack[-3:] if stack else ''))

    # --- C04 ItemN lueckenlos (Sitzung 03.09.: Luecke => Eintraege werden ignoriert) ---
    stack, gaps = [], []
    for m in TAG_RE.finditer(c):
        closing, name, attrs = m.group(1), m.group(2), m.group(3)
        if closing:
            if stack:
                nm, kids, line = stack.pop()
                if kids and kids != list(range(1, len(kids) + 1)):
                    gaps.append('<%s> Zeile %d: %s...' % (nm, line, kids[:6]))
        else:
            if re.fullmatch(r'Item\d+', name) and stack:
                stack[-1][1].append(int(name[4:]))
            if not attrs.endswith('/'):
                stack.append([name, [], c.count('\n', 0, m.start()) + 1])
    add('C04', 'ItemN-Sammlungen lueckenlos ab Item1', not gaps, ' | '.join(gaps[:3]))

    # --- C05 Ref-Eindeutigkeit ------------------------------------------
    refs = re.findall(r'Ref="(\d+)"', c)
    dupes = [r for r, n in Counter(refs).items() if n > 1]
    add('C05', 'Keine doppelten Ref-IDs', not dupes, 'Duplikate: %s' % dupes[:5])

    # --- C06 Localization zeigt nur auf existierende Refs ----------------
    refset = set(refs)
    orphan = sorted({r for r in re.findall(r'Component="#Ref-(\d+)"', c) if r not in refset})
    add('C06', 'Keine verwaisten Localization-Verweise', not orphan, 'ohne Ziel: %s' % orphan[:5])

    if script is None:
        add('C07', 'ScriptsSource gefunden', False, 'kein Haupt-ScriptsSource lesbar')
        return

    # --- C07 Scripts-Verdrahtung <-> Methoden ----------------------------
    wired = set()
    for m in re.finditer(r'<Scripts\b[^/]*/>', c):
        wired |= set(re.findall(r'On\w+="(\w+)"', m.group(0)))
    defined = set(re.findall(r'private void (\w+)\(', script))
    missing = wired - defined
    if base is not None:
        b_raw, b_script = main_script(base)
        b_wired = set()
        for m in re.finditer(r'<Scripts\b[^/]*/>', base):
            b_wired |= set(re.findall(r'On\w+="(\w+)"', m.group(0)))
        missing -= (b_wired - set(re.findall(r'private void (\w+)\(', b_script)))
    add('C07', 'Jede <Scripts>-Verdrahtung hat eine Methode', not missing, 'fehlend: %s' % sorted(missing)[:5])

    # --- C08 Klammern-Balance -------------------------------------------
    add('C08', 'Klammern-Balance im Skript', script.count('{') == script.count('}'),
        '{ %d vs } %d' % (script.count('{'), script.count('}')))

    # --- C09 Summary-Anzahl unveraendert (sumCarryoverSum-Falle) ---------
    if base is not None:
        a, b = base.count('<Summary '), c.count('<Summary ')
        add('C09', '<Summary>-Anzahl unveraendert', a == b, 'vorher %d / nachher %d' % (a, b))
    else:
        add('C09', '<Summary>-Anzahl unveraendert', True, 'uebersprungen (keine Baseline)', warn=True)

    # --- C10 kein rohes \r/\n im re-escapten ScriptsSource ---------------
    add('C10', 'ScriptsSource ohne rohe \\r/\\n', raw_val.count('\r') == 0 and raw_val.count('\n') == 0,
        'CR=%d LF=%d' % (raw_val.count('\r'), raw_val.count('\n')))

    # --- C11 PrintOnPage-Flags nicht in BeforePrint lesen ----------------
    # _detailPrintedSoFar (und Verwandte) werden erst in der PrintOnPage-Phase gesetzt,
    # die fuer das GESAMTE Dokument nach allen BeforePrint-Ereignissen laeuft.
    bodies = {n: strip_comments(b) for n, b in handler_bodies(script).items()}
    po_flags = set()
    for name, body in bodies.items():
        if name.endswith('PrintOnPage'):
            po_flags |= set(re.findall(r'(\b_\w+)\s*=\s*(?:true|false)', body))
    bad = []
    for name, body in bodies.items():
        if not name.endswith('BeforePrint'):
            continue
        for f in po_flags:
            # Schreibzugriffe (Reset, z.B. Batch-Sicherheits-Reset in Muster d) sind erlaubt;
            # nur LESE-Zugriffe sind das Problem, weil das Flag hier immer false ist.
            for m in re.finditer(re.escape(f) + r'\b\s*(=(?!=))?', body):
                if not m.group(1):
                    bad.append('%s liest %s' % (name, f))
                    break
    add('C11', 'Kein PrintOnPage-Flag in einem BeforePrint-Handler', not bad, ' | '.join(bad[:4]))

    # --- C12 Hoehe nur in PrintOnPage gesetzt = wirkungslos --------------
    late = [n for n, b in bodies.items() if n.endswith('PrintOnPage') and re.search(r'\.HeightF\s*=', b)]
    add('C12', 'Keine HeightF-Zuweisung in PrintOnPage (Layout ist dort durch)', not late,
        'betroffen: %s' % late[:4])

    # --- C13 geschrumpfte Design-Hoehen brauchen Laufzeit-Wiederherstellung ---
    tiny = re.findall(r'Component="#Ref-(\d+)" Culture="[^"]*" Path="(?:HeightF|SizeF)" Data="(?:[\d.]+,)?([0-5](?:\.\d+)?)"', c)
    restores = len(re.findall(r'\.HeightF\s*=', script))
    add('C13', 'Mindesthoehen im Design haben Laufzeit-Wiederherstellung',
        (not tiny) or restores > 0, '%d Controls/Baender <=5, %d HeightF-Zuweisungen im Skript' % (len(tiny), restores),
        warn=True)

    # --- C14 kein Diagnose-/Debug-Code ausgeliefert ----------------------
    debug_hits = []
    for pat in [r'_dbgHelper', r'lblDebug\w*\s*\.', r'Diagnose-Test', r'DEBUG ']:
        for name, body in bodies.items():
            if re.search(pat, body):
                debug_hits.append('%s (%s)' % (name, pat))
    add('C14', 'Kein Debug-/Diagnose-Code im Skript', not debug_hits, ' | '.join(debug_hits[:4]))

    # --- C17 Padding-Positionen aus der Datei selbst ableiten ------------
    # Padding wird als "Left,Right,Top,Bottom,Dpi" serialisiert. Diese Reihenfolge NIE aus
    # einer Doku uebernehmen, sondern hier gegen die im Report vorhandenen expliziten
    # Padding.LeftF-/Padding.RightF-Bindungen pruefen (Top ist damit Position 3, nicht 2).
    conflicts, checked = [], 0
    for m in re.finditer(r'<Item\d+ Ref="\d+" ControlType="XRTableCell" Name="([^"]+)"[^>]*Padding="([^"]*)"[^>]*>', c):
        name, pad = m.group(1), m.group(2).split(',')
        seg = c[m.end():m.end() + 1200]
        nxt = seg.find('ControlType="XRTableCell"')
        seg = seg[:nxt] if nxt != -1 else seg
        for b in re.finditer(r'PropertyName="Padding\.(Left|Right|Top|Bottom)F" Expression="([\d.]+)"', seg):
            idx = {'Left': 0, 'Right': 1, 'Top': 2, 'Bottom': 3}[b.group(1)]
            checked += 1
            if idx < len(pad) and pad[idx].strip() != b.group(2).strip():
                conflicts.append('%s: Padding.%sF=%s, aber Position %d ist %s'
                                 % (name, b.group(1), b.group(2), idx + 1, pad[idx]))
    add('C17', 'Padding-Reihenfolge Left,Right,Top,Bottom bestaetigt', not conflicts,
        (' | '.join(conflicts[:3]) if conflicts else '%d Bindungen geprueft' % checked))

    # --- C18 Padding-Aenderungen gegen die Baseline benennen ---------------
    # Meldet JEDE geaenderte Padding-Position im Klartext ("Right 0 -> 10"). Damit faellt
    # sofort auf, wenn eine Aenderung auf einer anderen Position gelandet ist als beabsichtigt
    # (siehe known-issues.md Eintrag 28: ein als "Top" gemeinter Fix sass auf "Right").
    if base is not None:
        names = ['Left', 'Right', 'Top', 'Bottom']
        def pads(x):
            out = {}
            for m in re.finditer(r'<Item\d+ Ref="(\d+)" ControlType="\w+" Name="([^"]+)"[^>]*Padding="([^"]*)"', x):
                out[m.group(1)] = (m.group(2), m.group(3).split(','))
            return out
        a, b = pads(base), pads(c)
        changes = []
        for ref, (nm, newv) in b.items():
            if ref in a and a[ref][1] != newv:
                for i in range(min(4, len(newv), len(a[ref][1]))):
                    if a[ref][1][i] != newv[i]:
                        changes.append('%s: %s %s->%s' % (nm, names[i], a[ref][1][i], newv[i]))
        add('C18', 'Padding-Aenderungen gegenueber Baseline (Sichtpruefung)', not changes,
            ' | '.join(changes[:6]) + ('' if len(changes) <= 6 else ' | +%d weitere' % (len(changes) - 6)),
            warn=True)

    # --- C19 work4all-log append-only ------------------------------------
    # fix-log-format.md Regel 1: bestehende Log-Zeilen werden nie veraendert oder entfernt,
    # nur angehaengt. Sichert insbesondere eine Kommentar-Kuerzung in der Live-Datei ab.
    if base is not None:
        b_raw, b_script = main_script(base)
        def logrows(x):
            m = re.search(r'// === work4all-log.*?// === end work4all-log ===', x or '', re.S)
            return [l.strip() for l in m.group(0).splitlines() if ' | ' in l] if m else []
        old_rows, new_rows = logrows(b_script), logrows(script)
        lost = [r for r in old_rows if r not in new_rows]
        add('C19', 'work4all-log append-only (keine Zeile verloren/veraendert)', not lost,
            ('verloren: %s' % lost[:2]) if lost else '%d -> %d Zeilen' % (len(old_rows), len(new_rows)))

    # --- C15 work4all-log + Anker-Zeile ---------------------------------
    has_log = '=== work4all-log' in script
    has_anchor = '_work4allLogAnchor' in script
    add('C15', 'work4all-log-Block vorhanden', has_log)
    add('C16', 'Anker-Zeile _work4allLogAnchor vorhanden', has_anchor and has_log)

def report():
    w = max(len(n) for _, n, _, _ in results)
    fails = 0
    print('\n' + '=' * (w + 24))
    for cid, name, status, detail in results:
        mark = {'PASS': 'OK  ', 'FAIL': 'FAIL', 'WARN': 'WARN'}[status]
        print('%s %-4s %-*s %s' % (mark, cid, w, name, detail if status != 'PASS' else ''))
        if status == 'FAIL':
            fails += 1
    print('=' * (w + 24))
    print('%d Checks, %d FAIL' % (len(results), fails))
    return 1 if fails else 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    baseline = None
    if '--baseline' in sys.argv:
        baseline = sys.argv[sys.argv.index('--baseline') + 1]
    run(sys.argv[1], baseline)
    sys.exit(report())
