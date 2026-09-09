# Validierungs-Checkliste — kurz-und-langtext-einarbeiten

Ergänzt die generische Basis-Checkliste `../../neuen-devexpress-report-skill-anlegen/references/validation-generic.md` (Pflichtbaustein 4 des Meta-Skills) um die fachlichen Prüfpunkte dieser Skill. Beide gelten zusammen, keine ersetzt die andere.

1. **Parameter existiert korrekt.** `ArgKurzLangtext` ist vom Typ Boolean und hat Default Value `No` (false). Ein abweichender Typ oder Default ist ein Fehler, kein Stilpunkt — bei `True` als Default würde jeder bestehende Ausdruck des Reports, der stillschweigend auf das bisherige Kurztext-Verhalten baut, sofort sein Verhalten ändern.

2. **Wahrheitstabelle manuell durchspielen — alle vier Kombinationen, nicht nur den Regelfall.** Für jede Kombination aus `?ArgKurzLangtext` (True/False) und "Kurztext vorhanden, weicht von Bezeichnung ab" (Ja/Nein) das erwartete Ergebnis gegen die Zieltabelle in `../SKILL.md` prüfen:

   | ArgKurzLangtext | Kurztext vorhanden & weicht ab | Sub_POS zeigt | Sub_LangtextBemerkung zeigt |
   |---|---|---|---|
   | True | Ja | Kurztext | Bezeichnung (+ ggf. Bemerkung) |
   | True | Nein (leer oder identisch mit Bezeichnung) | Bezeichnung (Fallback) | nur ggf. Bemerkung (kein Bezeichnung-Zusatz, sonst Dopplung mit dem Fallback in Sub_POS) |
   | False | Ja | Bezeichnung (nie Kurztext) | nur ggf. Bemerkung |
   | False | Nein | Bezeichnung | nur ggf. Bemerkung |

   Der Fall "True + Kurztext vorhanden aber identisch mit Bezeichnung" ist der wichtigste Grenzfall: Formel A zeigt hier Kurztext (weil er vorhanden ist), Formel B/C zeigen wegen der `<>`-Prüfung korrekt **nichts** zusätzlich — würde diese Prüfung fehlen, erschiene derselbe Text zweimal untereinander.

3. **Keine Dopplung zwischen Sub_POS und Sub_LangtextBemerkung in echten Testdaten.** Mindestens eine Position mit Kurztext = Bezeichnung, eine mit Kurztext ≠ Bezeichnung, und eine mit leerem Kurztext probeweise durchrechnen (Formel-Editor-Vorschau oder Testdruck), jeweils für `ArgKurzLangtext = True` und `= False`.

4. **ArtikelArt-Liste ist in allen drei Formeln identisch.** Formel A, B und C müssen exakt dieselbe Liste verwenden (Referenzfall: `(0, -10, -24)`). Eine an nur einer Stelle vergessene Anpassung (z.B. weil aus einer älteren Formel mit der Liste `(0, -10, -2, -3, -12, -13)` kopiert wurde) führt dazu, dass das neue Band für manche ArtikelArten sichtbar wird, obwohl Sub_POS für dieselbe ArtikelArt gar keinen Kurztext-Zweig kennt, oder umgekehrt.

5. **Bandreihenfolge und -sichtbarkeit im Report-Designer visuell prüfen.** `Sub_LangtextBemerkung` muss direkt unterhalb von `Sub_POS` gedruckt werden, darf aber bei unsichtbarem Zustand keine Leerzeile/keinen Abstand hinterlassen (Band-Eigenschaft, die dafür sorgt, dass eine unsichtbare Band-Instanz keine Höhe reserviert — am Zielreport prüfen, wie `Sub_POS` selbst das für seine eigene bedingte Sichtbarkeit handhabt, und dieselbe Technik übernehmen).

6. **Bestehendes Verhalten bei `?ArgKurzLangtext = False` gegen einen Report-Ausdruck VOR dieser Änderung vergleichen**, sofern eine solche Vorversion vorliegt. Da `False` der Default ist, darf sich für Reports, die den neuen Parameter nicht aktiv setzen, das gedruckte Ergebnis gegenüber dem alten Kurztext-Verhalten des Reports **bewusst** ändern (Sub_POS zeigt jetzt immer Langtext statt Kurztext-mit-Fallback) — das ist der Kern dieser Erweiterung, kein Bug. Sicherstellen, dass diese Verhaltensänderung dem Nutzer im Abschlussbericht explizit genannt wird, falls der Zielreport vorher produktiv im alten Verhalten lief.

7. **Manueller DevExpress-Designer-Test bleibt Pflicht**, wie in der generischen Basis-Checkliste Punkt 10 festgehalten — diese Checkliste ersetzt kein Laden im Designer und keinen Testdruck.
