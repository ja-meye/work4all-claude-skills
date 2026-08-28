# Validierung vor Auslieferung

Diese Checks laufen **immer**, bevor eine neu gebaute `.repx` ausgeliefert wird. Sie ersetzen nicht den echten Test im DevExpress Report Designer (siehe unten), fangen aber die häufigsten strukturellen Fehler beim programmatischen Bauen ab.

## 1. Gesamtdatei ist wohlgeformtes XML

```python
import xml.etree.ElementTree as ET
ET.parse("neuer_report.repx")  # wirft bei Fehlern eine Exception
```

## 2. Ref-IDs sind eindeutig, alle #Ref-Verweise lösen auf

```python
import re, collections

content = open("neuer_report.repx", encoding="utf-8").read()

refs = re.findall(r'Ref="(-?\d+)"', content)
dup = [r for r, c in collections.Counter(refs).items() if c > 1]
assert not dup, f"Doppelte Ref-IDs: {dup}"

refset = set(refs)
used = re.findall(r'#Ref-(-?\d+)', content)
missing = [u for u in used if u not in refset]
assert not missing, f"#Ref-Verweise ohne Ziel: {missing}"
```

## 3. Base64-Blob separat dekodieren und als eigenes XML validieren

```python
import base64, xml.etree.ElementTree as ET

m = re.search(r'Base64="([^"]+)"', content)
decoded = base64.b64decode(m.group(1)).decode("utf-8")
ET.fromstring(decoded)  # eigenständig wohlgeformt?
```

Beim Ausgeben/Prüfen des SQL-Texts daran denken, dass `&lt;`/`&gt;` darin absichtlich stehen bleiben, wenn die Query selbst mit XML arbeitet (siehe `repx-technische-notizen.md`) — das ist kein Fehler.

## 4. Jede Feld-Expression zeigt auf ein tatsächlich vorhandenes ResultSchema-Feld

```python
exprs = set(re.findall(r'Expression="\[([^\].]+)\]"', content))
field_names = set(re.findall(r'<Field Name="([^"]+)"', decoded))
unbekannt = exprs - field_names
assert not unbekannt, f"Expressions ohne passendes Feld im ResultSchema: {unbekannt}"
```

Ein Treffer hier bedeutet: irgendwo wurde ein Feldname gebunden, der in der Query gar nicht selektiert wird — die Query würde beim Ausführen fehlschlagen. Vor Auslieferung immer beheben, nie ausliefern und hoffen.

## 5. Keine erfundenen DB-Felder als echte Bindung

Für jedes Feld, das im Bauplan als "offen"/unbekannt markiert wurde (siehe `excel-bauplan-vorlage.md`), prüfen: Steht im Layout wirklich ein reiner Text-Platzhalter ohne `ExpressionBindings` (z.B. `TODO: DB-Feld?`), und keine geratene `[Feldname]`-Bindung? Das lässt sich mit demselben Muster wie Check 4 grob gegenprüfen, sollte aber auch beim manuellen Review des generierten XML nochmal bewusst angeschaut werden.

## 6. Quick-Look über die Excel-Kontrollliste

`markitdown datei.xlsx` (falls installiert) oder `pandas.read_excel` reicht, um zu prüfen, dass alle Felder aus dem Mockup tatsächlich als Zeile vorhanden sind und die neu bekannten Zuordnungen richtig eingetragen wurden.

## 7. Was hier NICHT geprüft werden kann — immer im Bericht an den Nutzer nennen

- Ob die Datei im DevExpress Report Designer tatsächlich lädt.
- Ob das Rendering visuell dem Mockup entspricht (Farben, exakte Abstände, echtes Logo statt Platzhaltertext).
- Ob die SQL-Query gegen die echte Datenbank tatsächlich läuft und die angenommenen Datentypen/Tabellennamen stimmen.
- Ob 1:n-Join-Situationen (mehrere verknüpfte Zeilen pro Hauptdatensatz) in der Praxis tatsächlich auftreten.

Diese vier Punkte klar als nächste, noch ausstehende Schritte benennen — nie stillschweigend als "fertig" ausliefern, nur weil die strukturelle Validierung oben grün ist.
