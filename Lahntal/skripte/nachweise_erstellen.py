#!/usr/bin/env python
"""Erstellt Quellen- und Methodennachweis als Markdown und eigenständige PDF."""
from pathlib import Path
import hashlib
import json
import html
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

B=Path(__file__).resolve().parents[1]
stats=json.loads((B/'recherche/Endvalidierung.json').read_text())
photos=sorted(json.loads((B/'recherche/Fotonachweise.json').read_text()),key=lambda r:r['nr'])
rows=[
('Gewässernetz 2017','Wasserwirtschaftsverwaltung Rheinland-Pfalz','https://geodienste-wasser.rlp-umwelt.de/geoserver/gewaesser/wfs','gewaesser:VW_F_GEWAESSER','CC BY 4.0 (bereitgestellte Urhebertabelle)','https://creativecommons.org/licenses/by/4.0/'),
('Wald und ergänzende Straßen','© GeoBasis-DE / BKG (2026), dl-de/by-2-0','https://sgx.geodatenzentrum.de/wfs_dlm250','dlm250:objart_43002_f; dlm250:objart_42003_l','Datenlizenz Deutschland – Namensnennung 2.0','https://www.govdata.de/dl-de/by-2-0'),
('Landwirtschaft und lagegenaue Straßen','©GeoBasis-DE / LVermGeoRP (2026), dl-de/by-2-0, http://www.lvermgeo.rlp.de [Daten bearbeitet]','https://geo5.service24.rlp.de/wfs/basisdlm_shape_rp.fcgi','vermkv:Vegetation_VEG01_F; vermkv:Verkehr_VER01_L','Datenlizenz Deutschland – Namensnennung 2.0','https://www.govdata.de/dl-de/by-2-0'),
('Kreisgrenzen','© BKG (2026) dl-de/by-2-0','https://sgx.geodatenzentrum.de/wfs_vg250','vg250:vg250_krs','Datenlizenz Deutschland – Namensnennung 2.0','https://www.govdata.de/dl-de/by-2-0'),
('Ortslagen','Bereitgestelltes Basis-DLM RLP / VermKV RLP','Prüfungseingabe ortslage.gpkg','ortslage','Im Kontext des Basis-DLM RLP verwendet; Quelldatei ohne getrennte Lizenzbeilage','https://www.govdata.de/dl-de/by-2-0'),
('Lahnwanderweg','Prüfungseingabe Lahnwanderweg.gpx','Bereitgestellte GPX-Datei','tracks','Zur Aufgabenbearbeitung bereitgestellt; keine gesonderte Lizenzangabe in der Aufgabenstellung',''),
('Fotostandorte','Prüfungseingabe Koordinaten_Fotos.txt','Bereitgestellte Textdatei','zehn Standorte','Zur Aufgabenbearbeitung bereitgestellt',''),
]
sections=[
('Umfang und Ausgabe',f'Einseitige Übersichtskarte des unteren Lahntals von Diez bis zur Mündung in den Rhein, DIN A2 quer (594 × 420 mm), Maßstab 1:65 000, EPSG:25832. Die Auszeichnung zur Flusslandschaft 2026 ist ein fiktives Szenario der Aufgabenstellung. Kennziffer: 204. Rechnerkennung: 65d375cd8802. Der Nutzername wird nicht genannt. Bearbeitung und Datenabruf: 27.10.2026.'),
('Gewässerauswahl',f'Das GetCapabilities-Dokument bezeichnet den ausgewählten Datensatz ausdrücklich als „Gewässernetz (2017)“. Die Abfrage umfasst EPSG:25832, BBOX 385000,5540000,455000,5620000. Alle Abschnitte werden nach der zehnstelligen Gewässerkennzahl gruppiert. Lahn: 2580000000; Rhein: 2000000000. Ein Zufluss wird ausgewählt, wenn seine Kennzahl mit 258 beginnt, er nicht selbst die Lahn ist, die Summe der amtlichen Abschnittslängen LAENGE strikt größer als 1000 m ist und mindestens ein stromabwärtiger Abschnittsendpunkt die Lahn mit höchstens 0,1 m Rechentoleranz trifft. Das ergibt {stats["direkte_zufluesse"]} direkte Zuflüsse. Damit werden indirekte Nebenbäche trotz gleichem Präfix ausgeschlossen. Die vollständige Auswahl samt Längen und Anschlussdistanzen liegt als Ausgewaehlte_Zufluesse.csv bei. Längen aus dem RLP-Datenbestand sind keine Behauptung über die vollständige Länge von Gewässern außerhalb des Landes.'),
('Anschluss und Fließrichtung','Die Auswahl nutzt tatsächliche Anschlüsse im amtlichen Fließgewässernetz, keine bloßen Einzugsgebietsbeziehungen oder Grundwasserzuflüsse. Der WFS enthält kein separates Attribut zur Verrohrung. Einzelne kurze Durchlässe können damit nicht eigenständig als unterirdisch ausgeschlossen werden; die Karte stellt den kartierten Fließgewässeranschluss dar. Die Lahngeometrie ist in der Datenquelle von Diez zur Rheinmündung gerichtet; die stromabwärtigen Zuflussenden sind über diesen Anschluss geprüft. Der Rhein verläuft im Ausschnitt stromabwärts nach Norden. Die Fließpfeile werden entlang der unverändert gerichteten Linien aus lokalen Tangenten erzeugt; geometrisches Vereinigen wird für die Darstellung der Fließrichtung vermieden.'),
('Straßen und Topologie','DLM250 AX_Strassenachse wurde früh per BBOX auf den Untersuchungsraum beschränkt. WDM 1301 = Autobahn, 1303 = Bundesstraße, 1305 = Landesstraße. Für die Lage innerhalb RLP werden die gleichartig klassifizierten, genaueren Straßenachsen des amtlichen Basis-DLM eingesetzt; die stark generalisierten DLM250-Achsen könnten sonst gegenüber der lagetreuen Lahn versetzt verlaufen. DLM250 ergänzt die Straßen am hessischen Kartenrand. Es wurden keine Flusslinien zur Straße hin verschoben und keine frei erfundenen Brücken ergänzt. Straßen liegen in der Zeichnungsreihenfolge über den Gewässern. A3 und A48 sind vorhanden und weiß auf blau beschriftet; Bundesstraßen sind mit gelben Nummernschildern gekennzeichnet.'),
('Ortslagen und 500-m-Regel',f'Alle Ortslagen im endgültigen Ausschnitt werden dargestellt. Für jede vollständige ursprüngliche Ortslagenfläche wird der minimale planare Abstand in Metern zu Lahn, Rhein (Abfluss) und den ausgewählten direkten Zuflüssen berechnet. Abstand ≤ 500 m führt zur Hervorhebung und Namensbeschriftung. Die Entfernung bezieht sich auf die Fläche, nicht auf deren Schwerpunkt. {stats["ortslagen"]} beschnittene Ortslagenobjekte, davon {stats["ortslagen_hervorgehoben"]} hervorgehoben. Mehrere Objekte können denselben Ortsnamen tragen.'),
('Wanderweg und Fotokoordinaten',f'Der bereitgestellte GPX-Track wurde von WGS84 nach EPSG:25832 transformiert. Der Abschnitt wird ab dem nächstgelegenen Trackpunkt zum oberstromigen Ende der Lahngeometrie bei Diez bis Lahnstein verwendet; so reicht der Weg nicht weiter als der Aufgabenbereich nach Osten. Im endgültigen Kartenausschnitt werden {stats["wanderweg_laenge_km"]:.3f} km dargestellt. Die zehn Fotopunkte werden über die Nummern mit der Fotoleiste verknüpft. Die Koordinatendatei nennt kein CRS; ihre Werte wurden als EPSG:25832 interpretiert und durch die räumliche Übereinstimmung der benannten Orte mit Ortslagen und GPX plausibilisiert.'),
('Landnutzung und Verwaltung','Wald: DLM250 AX_Wald, Objektart 43002. Landwirtschaft: AX_Landwirtschaft, Objektart 43001, aus dem genaueren Basis-DLM RLP. Der in der Excel-Tabelle als „DLM50“ bezeichnete Dienst liefert laut amtlichem GetCapabilities tatsächlich das Basis-DLM; dieses wurde verwendet und nicht falsch als DLM50 bezeichnet. Die Nutzung von DLM50 ist in der Aufgabe als Möglichkeit formuliert. Kreisgrenzen: VG250, Auswahl Rheinland-Pfalz (SN_L = 07), räumlich beschnitten und mit Kreisnamen bzw. Koblenz als kreisfreier Stadt beschriftet. Die Landesmaske aus VG250 dient zusätzlich der Trennung der beiden Straßenquellen.'),
('Fotos, Quellenkorrekturen und Lizenzen','Es werden die in der Urhebertabelle genannten Originaldateien von Wikimedia Commons verwendet. Die API-Metadaten jedes Bildes wurden gespeichert und die Originaldateien heruntergeladen. Alle zehn Fotos erscheinen in gleich großen Querformatrahmen von 54,7 × 30 mm. Die Layoutansichten vergrößern die Fotos proportional und beschneiden überstehende Bereiche; dadurch entstehen keine Verzerrungen oder weißen Ränder. Die Ausschnitte sind zentriert, beim Malbergturm zugunsten der Turmkrone nach oben verschoben. Die Original-JPEGs bleiben unverändert. Kleine VRT-Dateien mit relativen Verweisen und eine ausgeblendete Foto-Layergruppe steuern ausschließlich die Layoutansichten; deren technische Pixelkoordinaten sind keine geografischen Bildstandorte. Die Änderung ist unter jedem Bild als „Ausschnitt“ gekennzeichnet. Die Lizenzangaben der Tabelle wurden mit Commons verglichen. Ruppertsklamm, Malbergturm, Emser Therme und Kloster Arnstein stehen dort unter CC BY-SA 4.0 statt des in der Tabelle genannten CC BY 4.0. Beim Goethepunkt wird die ebenfalls auf Commons angebotene Lizenz CC BY-SA 3.0 verwendet. Die DE-Versionen bei Stolzenfels und Concordiaturm sind berücksichtigt. Jede Bildlizenz gilt für das jeweilige Foto, nicht automatisch für alle Bestandteile der Zusammenstellung. Vollständige Links folgen unten.'),
('Validierung und Grenzen der Aussage','Das QGIS-Projekt wurde nach dem Speichern erneut geöffnet; alle Datenlayer sind gültig, die Abhängigkeiten sind relativ zum Projektordner gespeichert. Die Klassen Rhein, Lahn, Zufluss sowie Autobahn, Bundes- und Landesstraße sind vorhanden. Alle zehn Fotostandorte und Bilder sind enthalten. Gewässerauswahl, Abstandsklassifikation und Seitengröße wurden rechnerisch geprüft, die exportierte Karte wurde visuell kontrolliert. Dies ersetzt keine amtliche Ortsbesichtigung einzelner Durchlässe oder Brücken. Die komprimierte Druck-PDF behält Vektorgeometrien und DIN A2 bei; die eingebetteten Fotos sind für 300 dpi Druckauflösung optimiert.'),
]

md=['# Quellen und Methodik – Unteres Lahntal','']
for title,body in sections:
    md.extend(['## '+title,'',body,''])
md.extend(['## Datenquellen',''])
for title,credit,url,layer,license,licenseurl in rows:
    md.extend(['### '+title,'',credit,'',f'Quelle: {url}',f'Layer: {layer}',f'Lizenz: {license}',licenseurl,''])
md.extend(['Die VG250-Datenquellen sind gemäß Dienstangabe dokumentiert unter:','https://sg.geodatenzentrum.de/web_public/gdz/datenquellen/datenquellen_vg_nuts.pdf','','## Bildnachweise',''])
for r in photos:
    md.extend([f'### {r["nr"]:02d} · {r["titel"].removeprefix("File:")}', '',f'Urheber: {r["urheber"]}',f'Lizenz: {r["lizenz"]}',r['quelle'],r['lizenz_url'],'Darstellung: proportional skalierter Bildausschnitt in einem einheitlichen Querformatrahmen (54,7 × 30 mm); Originaldatei unverändert.',''])
md.extend(['## Ausgewählte direkte Zuflüsse','', '| GKZ | Gewässer | Länge im RLP-Datenbestand (m) |','| --- | --- | ---: |'])
for code,data in sorted(stats['zufluesse'].items()):
    md.append(f'| {code} | {data["name"]} | {data["laenge_m"]:.2f} |')
(B/'QUELLEN_UND_METHODIK.md').write_text('\n'.join(md),encoding='utf-8')

pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DV-Bold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyDV',fontName='DV',fontSize=9,leading=13,spaceAfter=7,wordWrap='CJK'))
styles.add(ParagraphStyle(name='HeadingDV',fontName='DV-Bold',fontSize=12,leading=16,spaceBefore=13,spaceAfter=7))
styles.add(ParagraphStyle(name='TitleDV',fontName='DV-Bold',fontSize=19,leading=24,spaceAfter=15))
story=[Paragraph('Unteres Lahntal<br/>Quellen und Methodik',styles['TitleDV'])]
def para(value):return Paragraph(html.escape(value),styles['BodyDV'])
for title,body in sections:
    story.extend([Paragraph(html.escape(title),styles['HeadingDV']),para(body)])
story.append(PageBreak())
story.append(Paragraph('Datenquellen',styles['TitleDV']))
for title,credit,url,layer,license,licenseurl in rows:
    story.extend([Paragraph(html.escape(title),styles['HeadingDV']),para(credit),para('Quelle: '+url),para('Layer: '+layer),para('Lizenz: '+license),para(licenseurl)])
story.append(para('VG250-Datenquellen: https://sg.geodatenzentrum.de/web_public/gdz/datenquellen/datenquellen_vg_nuts.pdf'))
story.append(PageBreak())
story.append(Paragraph('Bildnachweise',styles['TitleDV']))
for r in photos:
    story.extend([Paragraph(f'{r["nr"]:02d} · '+html.escape(r['titel'].removeprefix('File:')),styles['HeadingDV']),para('Urheber: '+r['urheber']),para('Lizenz: '+r['lizenz']),para(r['quelle']),para(r['lizenz_url']),para('Darstellung: proportional skalierter Bildausschnitt im einheitlichen Querformat; Originaldatei unverändert.')])
story.append(PageBreak())
story.append(Paragraph('40 ausgewählte direkte Zuflüsse',styles['TitleDV']))
data=[['GKZ','Gewässer','Länge RLP (m)']]
for code,row in sorted(stats['zufluesse'].items()):data.append([code,row['name'],f'{row["laenge_m"]:.2f}'])
table=Table(data,colWidths=[95,285,100],repeatRows=1)
table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'DV'),('FONTSIZE',(0,0),(-1,-1),8),('FONTNAME',(0,0),(-1,0),'DV-Bold'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5eee9')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f7f4')]),('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5)]))
story.append(table)
def footer(canvas,doc):
    canvas.setFont('DV',7)
    canvas.drawString(42,25,'Unteres Lahntal · Kennziffer 204 · 27.10.2026')
    canvas.drawRightString(A4[0]-42,25,str(doc.page))
SimpleDocTemplate(str(B/'Quellen_und_Methodik.pdf'),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=42,bottomMargin=43).build(story,onFirstPage=footer,onLaterPages=footer)

hashes={str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest() for directory in ['daten','fotos'] for p in (B/directory).glob('*') if p.is_file() and p.name!='Lahntal.gpkg'}
(B/'recherche/SHA256_Daten_und_Fotos.json').write_text(json.dumps(hashes,indent=2))
print('Quellen_und_Methodik.pdf und QUELLEN_UND_METHODIK.md erstellt.')
