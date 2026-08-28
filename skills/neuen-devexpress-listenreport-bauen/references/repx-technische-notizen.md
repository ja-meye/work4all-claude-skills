# .repx-Technik: Base64-SqlDataSource, Ref-IDs, Parametermuster

## Dateiformat

Eine `.repx` von DevExpress XtraReports ist eine wohlgeformte XML-Datei (`XtraReportsLayoutSerializer` als Wurzelelement) — kein Binärformat wie Crystal Reports' `.rpt`. Das macht sie direkt mit einem Text-/XML-Editor bzw. programmatisch bearbeitbar, solange man sich an die Serialisierungskonventionen hält, die DevExpress selbst produziert. Es gibt keine öffentlich dokumentierte XSD-Spezifikation für das Format — Struktur immer aus einer echten, funktionierenden Referenzdatei ableiten, nicht aus der DevExpress-Dokumentation raten.

## Die SqlDataSource steckt Base64-kodiert im ComponentStorage

Die eigentliche Datenquelle (Connection, SQL-Query, Parameter, ResultSchema) ist **nicht** direkt sichtbares XML, sondern als Base64-String im `Base64`-Attribut eines `<Item>` innerhalb von `<ComponentStorage>` eingebettet. Dekodiert ergibt das selbst wieder XML:

```xml
<SqlDataSource Name="sqlDataSource1">
  <Connection Name="localhost_WorkM004_Connection" FromAppConfig="true" />
  <Query Type="CustomSqlQuery" Name="Kunden">
    <Parameter Name="keys" Type="DevExpress.DataAccess.Expression">(System.String)(JOIN(?keys))</Parameter>
    <Parameter Name="listFilter" Type="DevExpress.DataAccess.Expression">(System.String)(?listFilter)</Parameter>
    <Sql>select ...</Sql>
  </Query>
  <ResultSchema>
    <DataSet Name="sqlDataSource1">
      <View Name="Kunden">
        <Field Name="Code" Type="Int32" />
        ...
      </View>
    </DataSet>
  </ResultSchema>
  <ConnectionOptions CloseConnection="true" />
</SqlDataSource>
```

Vorgehen zum Bearbeiten (Python, `base64` + `xml.etree.ElementTree`):

1. Base64-Attribut aus der Referenzdatei extrahieren (Regex auf `Base64="([^"]+)"` reicht meistens, da es i.d.R. nur eine SqlDataSource pro einfachem Listenreport gibt).
2. `base64.b64decode(...).decode("utf-8")` → dekodiertes XML als Textbasis.
3. Neuen `<Sql>`-Text, neue `<Parameter>`- und `<Field>`-Einträge einsetzen (String-Ersetzung oder Neuaufbau als f-String — beides ist in Ordnung, solange am Ende `xml.etree.ElementTree.fromstring(...)` das Ergebnis ohne Fehler parst).
4. `base64.b64encode(...).decode("ascii")` und zurück ins `Base64`-Attribut der neuen Report-Datei schreiben.

**Der SQL-Text selbst enthält oft zusätzliches XML-Escaping**, wenn die Query intern mit XML arbeitet (typisches Muster für Multi-Value-Parameter, siehe unten): `<` und `>` erscheinen dann als `&lt;`/`&gt;` *innerhalb* des schon-als-Text-serialisierten `<Sql>`-Elements. Das ist korrekt und nötig — nicht "reparieren", indem die Entities entfernt werden, sonst ist das äußere XML nicht mehr wohlgeformt.

## Parameter-/Filtermuster für ID-Listen

Reports, die über eine Liste von IDs gedruckt werden (typischer Fall: "diese markierten Datensätze drucken"), verwenden meist folgendes Muster, das 1:1 übernommen werden sollte:

- Ein `MultiValue="true"`-Parameter (z.B. `keys`) auf Report-Ebene (`<Parameters>`).
- In der Query ein `Parameter`-Element vom `Type="DevExpress.DataAccess.Expression"` mit Ausdruck `(System.String)(JOIN(?keys))` — DevExpress verbindet die Werteliste serverseitig zu einem kommagetrennten String.
- Im SQL-Text ein CAST-über-XML-Trick, um den kommagetrennten String in eine echte `IN (...)`-Liste umzuwandeln:

```sql
where "Tabelle"."IdSpalte" in (
  select cast(m.n.value('.', 'int') as int)
  from (select cast('<x>' + replace(@keys, ',', '</x><x>') + '</x>' as xml) as x) as t
  cross apply t.x.nodes('/x') as m(n)
)
```

Nur die Tabellen-/Spaltennamen ändern (z.B. `Kunden.Code` statt `ERP_Code`), die Mechanik unverändert lassen — sie ist SQL-Server-spezifisch und wurde bereits produktiv verifiziert.

Ein zweiter, rein informativer Parameter (z.B. `listFilter`) wird oft nur zur Anzeige eines Filtertexts im Report-Kopf verwendet (`Iif(IsNullOrEmpty([Parameters.listFilter]), '(keiner)', [Parameters.listFilter])`), nicht in der SQL-`WHERE`-Klausel.

## Ref-IDs müssen im ganzen Dokument eindeutig sein

Jedes Element trägt ein `Ref="n"`-Attribut (ganzzahlig), und Attribute wie `DataSource="#Ref-0"` oder `Parameter="#Ref-3"` verweisen darauf. Beim Neubau:

- `Ref="0"` ist üblicherweise für die Haupt-Datenquelle im `ComponentStorage` reserviert (referenziert von `DataSource="#Ref-0"` am Wurzelelement), `Ref="1"` für das Wurzelelement selbst.
- Alle übrigen Ref-Werte müssen im gesamten Dokument einmalig sein — am einfachsten mit einem einzigen hochzählenden Python-Zähler für das ganze Skript erzeugen, nicht pro Band/Sektion neu bei 1 anfangen.
- Nach dem Bauen prüfen: jedes `Ref="n"` kommt nur einmal vor, und jedes `#Ref-n` verweist auf ein tatsächlich vorhandenes `Ref="n"` (siehe `validierung-vor-auslieferung.md`).

## Farbangaben

Farben werden im gesehenen Referenzmaterial als benannte .NET-Farben serialisiert (`ForeColor="Gray"`). Es gibt kein bestätigtes Beispiel für das exakte Format numerischer ARGB-Werte in diesem Kontext — deshalb beim Neubau nur benannte .NET-Farben verwenden (`MidnightBlue`, `Gainsboro`, `White`, `Gray`, `Navy`, …), keine geratenen `"R, G, B"`- oder Hex-Strings. Passt die benannte Farbe nicht exakt zur Kundenfarbe (z.B. Mandanten-Blau), das im Bericht an den Nutzer als offenen Punkt für die Feinjustierung im DevExpress Designer benennen.

## Was hier nicht geprüft werden kann

Diese Umgebung hat keine DevExpress-Rendering-Engine. Alles, was hier passiert, ist strukturelle/syntaktische Validierung (wohlgeformtes XML, aufgelöste Referenzen, plausible Feldnamen). Ob der Report in DevExpress tatsächlich lädt und wie erwartet aussieht, kann nur der Nutzer im echten Report Designer prüfen — das im Bericht an den Nutzer immer explizit als nächsten, noch ausstehenden Schritt benennen.
