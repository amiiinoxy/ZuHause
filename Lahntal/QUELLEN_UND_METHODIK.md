# Quellen und Methodik – Unteres Lahntal

## Umfang und Ausgabe

Einseitige Übersichtskarte des unteren Lahntals von Diez bis zur Mündung in den Rhein, DIN A2 quer (594 × 420 mm), Maßstab 1:65 000, EPSG:25832. Die Auszeichnung zur Flusslandschaft 2026 ist ein fiktives Szenario der Aufgabenstellung. Kennziffer: 204. Rechnerkennung: 65d375cd8802. Der Nutzername wird nicht genannt. Bearbeitung und Datenabruf: 27.10.2026.

## Gewässerauswahl

Das GetCapabilities-Dokument bezeichnet den ausgewählten Datensatz ausdrücklich als „Gewässernetz (2017)“. Die Abfrage umfasst EPSG:25832, BBOX 385000,5540000,455000,5620000. Alle Abschnitte werden nach der zehnstelligen Gewässerkennzahl gruppiert. Lahn: 2580000000; Rhein: 2000000000. Ein Zufluss wird ausgewählt, wenn seine Kennzahl mit 258 beginnt, er nicht selbst die Lahn ist, die Summe der amtlichen Abschnittslängen LAENGE strikt größer als 1000 m ist und mindestens ein stromabwärtiger Abschnittsendpunkt die Lahn mit höchstens 0,1 m Rechentoleranz trifft. Das ergibt 40 direkte Zuflüsse. Damit werden indirekte Nebenbäche trotz gleichem Präfix ausgeschlossen. Die vollständige Auswahl samt Längen und Anschlussdistanzen liegt als Ausgewaehlte_Zufluesse.csv bei. Längen aus dem RLP-Datenbestand sind keine Behauptung über die vollständige Länge von Gewässern außerhalb des Landes.

## Anschluss und Fließrichtung

Die Auswahl nutzt tatsächliche Anschlüsse im amtlichen Fließgewässernetz, keine bloßen Einzugsgebietsbeziehungen oder Grundwasserzuflüsse. Der WFS enthält kein separates Attribut zur Verrohrung. Einzelne kurze Durchlässe können damit nicht eigenständig als unterirdisch ausgeschlossen werden; die Karte stellt den kartierten Fließgewässeranschluss dar. Die Lahngeometrie ist in der Datenquelle von Diez zur Rheinmündung gerichtet; die stromabwärtigen Zuflussenden sind über diesen Anschluss geprüft. Der Rhein verläuft im Ausschnitt stromabwärts nach Norden. Die Fließpfeile werden entlang der unverändert gerichteten Linien aus lokalen Tangenten erzeugt; geometrisches Vereinigen wird für die Darstellung der Fließrichtung vermieden.

## Straßen und Topologie

DLM250 AX_Strassenachse wurde früh per BBOX auf den Untersuchungsraum beschränkt. WDM 1301 = Autobahn, 1303 = Bundesstraße, 1305 = Landesstraße. Für die Lage innerhalb RLP werden die gleichartig klassifizierten, genaueren Straßenachsen des amtlichen Basis-DLM eingesetzt; die stark generalisierten DLM250-Achsen könnten sonst gegenüber der lagetreuen Lahn versetzt verlaufen. DLM250 ergänzt die Straßen am hessischen Kartenrand. Es wurden keine Flusslinien zur Straße hin verschoben und keine frei erfundenen Brücken ergänzt. Straßen liegen in der Zeichnungsreihenfolge über den Gewässern. A3 und A48 sind vorhanden und weiß auf blau beschriftet; Bundesstraßen sind mit gelben Nummernschildern gekennzeichnet.

## Ortslagen und 500-m-Regel

Alle Ortslagen im endgültigen Ausschnitt werden dargestellt. Für jede vollständige ursprüngliche Ortslagenfläche wird der minimale planare Abstand in Metern zu Lahn, Rhein (Abfluss) und den ausgewählten direkten Zuflüssen berechnet. Abstand ≤ 500 m führt zur Hervorhebung und Namensbeschriftung. Die Entfernung bezieht sich auf die Fläche, nicht auf deren Schwerpunkt. 150 beschnittene Ortslagenobjekte, davon 96 hervorgehoben. Mehrere Objekte können denselben Ortsnamen tragen.

## Wanderweg und Fotokoordinaten

Der bereitgestellte GPX-Track wurde von WGS84 nach EPSG:25832 transformiert. Der Abschnitt wird ab dem nächstgelegenen Trackpunkt zum oberstromigen Ende der Lahngeometrie bei Diez bis Lahnstein verwendet; so reicht der Weg nicht weiter als der Aufgabenbereich nach Osten. Im endgültigen Kartenausschnitt werden 63.236 km dargestellt. Die zehn Fotopunkte werden über die Nummern mit der Fotoleiste verknüpft. Die Koordinatendatei nennt kein CRS; ihre Werte wurden als EPSG:25832 interpretiert und durch die räumliche Übereinstimmung der benannten Orte mit Ortslagen und GPX plausibilisiert.

## Landnutzung und Verwaltung

Wald: DLM250 AX_Wald, Objektart 43002. Landwirtschaft: AX_Landwirtschaft, Objektart 43001, aus dem genaueren Basis-DLM RLP. Der in der Excel-Tabelle als „DLM50“ bezeichnete Dienst liefert laut amtlichem GetCapabilities tatsächlich das Basis-DLM; dieses wurde verwendet und nicht falsch als DLM50 bezeichnet. Die Nutzung von DLM50 ist in der Aufgabe als Möglichkeit formuliert. Kreisgrenzen: VG250, Auswahl Rheinland-Pfalz (SN_L = 07), räumlich beschnitten und mit Kreisnamen bzw. Koblenz als kreisfreier Stadt beschriftet. Die Landesmaske aus VG250 dient zusätzlich der Trennung der beiden Straßenquellen.

## Fotos, Quellenkorrekturen und Lizenzen

Es werden die in der Urhebertabelle genannten Originaldateien von Wikimedia Commons verwendet. Die API-Metadaten jedes Bildes wurden gespeichert und die Originaldateien heruntergeladen. Die Bilder werden vollständig, ohne Beschnitt und ohne inhaltliche Bearbeitung in Bildrahmen eingepasst; ihre Größen ändern sich nur für den Kartendruck. Die Lizenzangaben der Tabelle wurden mit Commons verglichen. Ruppertsklamm, Malbergturm, Emser Therme und Kloster Arnstein stehen dort unter CC BY-SA 4.0 statt des in der Tabelle genannten CC BY 4.0. Beim Goethepunkt wird die ebenfalls auf Commons angebotene Lizenz CC BY-SA 3.0 verwendet. Die DE-Versionen bei Stolzenfels und Concordiaturm sind berücksichtigt. Jede Bildlizenz gilt für das jeweilige Foto, nicht automatisch für alle Bestandteile der Zusammenstellung. Vollständige Links folgen unten.

## Validierung und Grenzen der Aussage

Das QGIS-Projekt wurde nach dem Speichern erneut geöffnet; alle Datenlayer sind gültig, die Abhängigkeiten sind relativ zum Projektordner gespeichert. Die Klassen Rhein, Lahn, Zufluss sowie Autobahn, Bundes- und Landesstraße sind vorhanden. Alle zehn Fotostandorte und Bilder sind enthalten. Gewässerauswahl, Abstandsklassifikation und Seitengröße wurden rechnerisch geprüft, die exportierte Karte wurde visuell kontrolliert. Dies ersetzt keine amtliche Ortsbesichtigung einzelner Durchlässe oder Brücken. Die komprimierte Druck-PDF behält Vektorgeometrien und DIN A2 bei; die eingebetteten Fotos sind für 300 dpi Druckauflösung optimiert.

## Datenquellen

### Gewässernetz 2017

Wasserwirtschaftsverwaltung Rheinland-Pfalz

Quelle: https://geodienste-wasser.rlp-umwelt.de/geoserver/gewaesser/wfs
Layer: gewaesser:VW_F_GEWAESSER
Lizenz: CC BY 4.0 (bereitgestellte Urhebertabelle)
https://creativecommons.org/licenses/by/4.0/

### Wald und ergänzende Straßen

© GeoBasis-DE / BKG (2026), dl-de/by-2-0

Quelle: https://sgx.geodatenzentrum.de/wfs_dlm250
Layer: dlm250:objart_43002_f; dlm250:objart_42003_l
Lizenz: Datenlizenz Deutschland – Namensnennung 2.0
https://www.govdata.de/dl-de/by-2-0

### Landwirtschaft und lagegenaue Straßen

©GeoBasis-DE / LVermGeoRP (2026), dl-de/by-2-0, http://www.lvermgeo.rlp.de [Daten bearbeitet]

Quelle: https://geo5.service24.rlp.de/wfs/basisdlm_shape_rp.fcgi
Layer: vermkv:Vegetation_VEG01_F; vermkv:Verkehr_VER01_L
Lizenz: Datenlizenz Deutschland – Namensnennung 2.0
https://www.govdata.de/dl-de/by-2-0

### Kreisgrenzen

© BKG (2026) dl-de/by-2-0

Quelle: https://sgx.geodatenzentrum.de/wfs_vg250
Layer: vg250:vg250_krs
Lizenz: Datenlizenz Deutschland – Namensnennung 2.0
https://www.govdata.de/dl-de/by-2-0

### Ortslagen

Bereitgestelltes Basis-DLM RLP / VermKV RLP

Quelle: Prüfungseingabe ortslage.gpkg
Layer: ortslage
Lizenz: Im Kontext des Basis-DLM RLP verwendet; Quelldatei ohne getrennte Lizenzbeilage
https://www.govdata.de/dl-de/by-2-0

### Lahnwanderweg

Prüfungseingabe Lahnwanderweg.gpx

Quelle: Bereitgestellte GPX-Datei
Layer: tracks
Lizenz: Zur Aufgabenbearbeitung bereitgestellt; keine gesonderte Lizenzangabe in der Aufgabenstellung


### Fotostandorte

Prüfungseingabe Koordinaten_Fotos.txt

Quelle: Bereitgestellte Textdatei
Layer: zehn Standorte
Lizenz: Zur Aufgabenbearbeitung bereitgestellt


Die VG250-Datenquellen sind gemäß Dienstangabe dokumentiert unter:
https://sg.geodatenzentrum.de/web_public/gdz/datenquellen/datenquellen_vg_nuts.pdf

## Bildnachweise

### 01 · Naturschutzgebiet Ruppertsklamm (2).jpg

Urheber: Qwertzu111111
Lizenz: CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:Naturschutzgebiet_Ruppertsklamm_(2).jpg
https://creativecommons.org/licenses/by-sa/4.0
Darstellung: verkleinert, vollständiges Bild, keine inhaltliche Änderung.

### 02 · Schloss Stolzenfels 01 Koblenz 2015.jpg

Urheber: Holger Weinandt
Lizenz: CC BY-SA 3.0 de
https://commons.wikimedia.org/wiki/File:Schloss_Stolzenfels_01_Koblenz_2015.jpg
https://creativecommons.org/licenses/by-sa/3.0/de/deed.en
Darstellung: verkleinert, vollständiges Bild, keine inhaltliche Änderung.

### 03 · BadEmsEmserTherme2.jpg

Urheber: LigaDue
Lizenz: CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:BadEmsEmserTherme2.jpg
https://creativecommons.org/licenses/by-sa/4.0
Darstellung: verkleinert, vollständiges Bild, keine inhaltliche Änderung.

### 04 · Burcht Laurenburg te Laurenburg - Flickr - Frans Berkelaar.jpg

Urheber: Frans Berkelaar
Lizenz: CC BY 4.0
https://commons.wikimedia.org/wiki/File:Burcht_Laurenburg_te_Laurenburg_-_Flickr_-_Frans_Berkelaar.jpg
https://creativecommons.org/licenses/by/4.0
Darstellung: verkleinert, vollständiges Bild, keine inhaltliche Änderung.

### 05 · Nassau Luftbild 071.jpg

Urheber: Fritz Geller-Grimm
Lizenz: CC BY-SA 3.0
https://commons.wikimedia.org/wiki/File:Nassau_Luftbild_071.jpg
https://creativecommons.org/licenses/by-sa/3.0
Darstellung: verkleinert, vollständiges Bild, keine inhaltliche Änderung.

### 06 · Malbergturm.JPG

Urheber: Muck
Lizenz: CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:Malbergturm.JPG
https://creativecommons.org/licenses/by-sa/4.0
Darstellung: verkleinert, vollständiges Bild, keine inhaltliche Änderung.

### 07 · Concordia-Turm-Bad-Ems-JR-E-181-2010-05-23.jpg

Urheber: Johannes Robalotoff
Lizenz: CC BY-SA 3.0 de
https://commons.wikimedia.org/wiki/File:Concordia-Turm-Bad-Ems-JR-E-181-2010-05-23.jpg
https://creativecommons.org/licenses/by-sa/3.0/de/deed.en
Darstellung: verkleinert, vollständiges Bild, keine inhaltliche Änderung.

### 08 · Obernhof Goethepunkt Aussichtspanorama ks01.jpg

Urheber: Kreuzschnabel
Lizenz: CC BY-SA 3.0
https://commons.wikimedia.org/wiki/File:Obernhof_Goethepunkt_Aussichtspanorama_ks01.jpg
https://creativecommons.org/licenses/by-sa/3.0
Darstellung: verkleinert, vollständiges Bild, keine inhaltliche Änderung.

### 09 · Schloss Schaumburg in der Nähe von Limburg an der Lahn (8621867592).jpg

Urheber: Heribert Pohl --- Thanks for half  a million clicks! from Germering bei München, Bayern
Lizenz: CC BY-SA 2.0
https://commons.wikimedia.org/wiki/File:Schloss_Schaumburg_in_der_N%C3%A4he_von_Limburg_an_der_Lahn_(8621867592).jpg
https://creativecommons.org/licenses/by-sa/2.0
Darstellung: verkleinert, vollständiges Bild, keine inhaltliche Änderung.

### 10 · ObernhofKlosterArnstein1.jpg

Urheber: LigaDue
Lizenz: CC BY-SA 4.0
https://commons.wikimedia.org/wiki/File:ObernhofKlosterArnstein1.jpg
https://creativecommons.org/licenses/by-sa/4.0
Darstellung: verkleinert, vollständiges Bild, keine inhaltliche Änderung.

## Ausgewählte direkte Zuflüsse

| GKZ | Gewässer | Länge im RLP-Datenbestand (m) |
| --- | --- | ---: |
| 2587940000 | Hambach | 6403.41 |
| 2587960000 | Heistenbach | 4750.35 |
| 2588000000 | Aar | 22630.53 |
| 2589111200 | Langenbach | 3059.32 |
| 2589112000 | Reiserbach | 2022.75 |
| 2589114000 | Daubach | 4808.12 |
| 2589120000 | Schaumburgerbach | 3259.34 |
| 2589132000 | Schroarbach | 2662.36 |
| 2589134000 | Kiesbach | 3051.58 |
| 2589139120 | Säuferbach | 1033.96 |
| 2589139600 | Hellbach | 1856.39 |
| 2589140000 | Rupbach | 6884.67 |
| 2589152000 | Bach von Gutenacker | 1150.39 |
| 2589160000 | Waselbach | 4143.48 |
| 2589174000 | Hurbach | 1443.14 |
| 2589176000 | Häuserhofbach | 1228.42 |
| 2589178000 | Bach am Vierseenblick | 1268.82 |
| 2589194000 | Schleusenbach | 1185.03 |
| 2589200000 | Dörsbach | 25686.04 |
| 2589400000 | Gelbach | 39780.14 |
| 2589532000 | Salscheider Bach | 1419.36 |
| 2589540000 | Kallbach | 5374.35 |
| 2589600000 | Mühlbach | 33454.62 |
| 2589712000 | Neuzenbach | 1823.27 |
| 2589719940 | Misselberger Bach | 1042.43 |
| 2589720000 | Unterbach | 5352.06 |
| 2589732000 | Odenbach | 1162.28 |
| 2589739200 | Mohrendell | 1138.56 |
| 2589740000 | Rullsbach | 1448.94 |
| 2589760000 | Wiesbach | 2005.45 |
| 2589780000 | Braunebach | 3543.04 |
| 2589792000 | Westersbach | 1586.47 |
| 2589800000 | Emsbach | 11420.79 |
| 2589914000 | Fröschbach | 1472.09 |
| 2589920000 | Fachbach | 4158.43 |
| 2589936000 | Eschgraben | 1208.07 |
| 2589940000 | Schweizertalbach | 3064.59 |
| 2589960000 | Erzbach | 3426.09 |
| 2589971200 | Bach in den Süßgrund | 1419.38 |
| 2589972000 | Ruppertsklamm | 2032.95 |