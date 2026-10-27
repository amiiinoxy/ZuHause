#!/usr/bin/python3
"""Fachliche Aufbereitung und A2-Kartenexport der recherchierten Originaldaten."""
import collections
import csv
import json
import math
import os
from pathlib import Path
import socket
import subprocess
import zipfile

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from qgis.core import *
from qgis.PyQt.QtCore import QVariant, QSizeF, QPointF
from qgis.PyQt.QtGui import QColor, QFont, QPolygonF
from fotoleiste import add_photo_panel

B = Path(__file__).resolve().parents[1]
app = QgsApplication([], False)
app.initQgis()
P = QgsProject.instance()
CRS = QgsCoordinateReferenceSystem('EPSG:25832')
P.setCrs(CRS)
P.setFilePathStorage(Qgis.FilePathType.Relative)
EXT = QgsRectangle(396690, 5569575, 434000, 5585500)
BOX = QgsGeometry.fromRect(EXT)
OUT = B/'daten/Kartendaten.gpkg'
if OUT.exists():
    OUT.unlink()
STATS = {}

def load(name):
    layer = QgsVectorLayer(str(B/'daten'/f'{name}_quelle.geojson'), name, 'ogr')
    assert layer.isValid() and layer.crs() == CRS, (name, layer.crs().authid())
    return layer

def memory(name, typ, fields):
    layer = QgsVectorLayer(typ+'?crs=EPSG:25832', name, 'memory')
    layer.dataProvider().addAttributes([QgsField(n,t) for n,t in fields])
    layer.updateFields()
    return layer

def add(layer, geom, attrs):
    if geom.isEmpty() or geom.isNull():
        return
    feature = QgsFeature(layer.fields())
    feature.setGeometry(geom)
    feature.setAttributes(attrs)
    assert layer.dataProvider().addFeatures([feature])[0]

def cut(geom):
    if not geom.intersects(BOX):
        return QgsGeometry()
    if not geom.isGeosValid():
        geom = geom.makeValid()
    return geom.intersection(BOX)

def save(layer, table):
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = 'GPKG'
    options.layerName = table
    options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer if OUT.exists() else QgsVectorFileWriter.CreateOrOverwriteFile
    result = QgsVectorFileWriter.writeAsVectorFormatV3(layer, str(OUT), P.transformContext(), options)
    assert result[0] == QgsVectorFileWriter.NoError, result
    result = QgsVectorLayer(str(OUT)+'|layername='+table, layer.name(), 'ogr')
    assert result.isValid() and result.featureCount(), table
    P.addMapLayer(result)
    STATS[table] = result.featureCount()
    return result

def lineparts(geom):
    return geom.asMultiPolyline() if geom.isMultipart() else [geom.asPolyline()]

def labels(layer, field, size=8, color='#263c41', expression=False, bold=False, italic=False):
    settings = QgsPalLayerSettings()
    settings.fieldName = field
    settings.isExpression = expression
    fmt = QgsTextFormat()
    font = QFont('DejaVu Sans')
    font.setPointSizeF(size)
    font.setBold(bold)
    font.setItalic(italic)
    fmt.setFont(font)
    fmt.setSize(size)
    fmt.setColor(QColor(color))
    buf = QgsTextBufferSettings()
    buf.setEnabled(True)
    buf.setSize(0.7)
    buf.setColor(QColor('#fffef9'))
    fmt.setBuffer(buf)
    settings.setFormat(fmt)
    if layer.geometryType() == Qgis.GeometryType.Line:
        settings.placement = Qgis.LabelPlacement.Line
    layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    layer.setLabelsEnabled(True)
    return settings

# Gewässer: vollständige GKZ-Gruppen, keine Auswahl allein nach dem Präfix.
water_source = load('wasser')
groups = collections.defaultdict(list)
for f in water_source.getFeatures():
    groups[str(f['GEWAESSER'])].append(f)
lahn_full = QgsGeometry.unaryUnion([f.geometry() for f in groups['2580000000']])
direct = {}
for code, fs in groups.items():
    if not code.startswith('258') or code == '2580000000':
        continue
    total = sum(float(f['LAENGE']) for f in fs)
    if total <= 1000:
        continue
    mouths = []
    for f in fs:
        for line in lineparts(f.geometry()):
            endpoint = QgsGeometry.fromPointXY(line[-1])
            if endpoint.distance(lahn_full) <= 0.1:
                mouths.append(line[-1])
    if mouths:
        direct[code] = {'name': str(fs[0]['GEWAESSERNAME']), 'laenge_m': total, 'muen_distanzen_m': [QgsGeometry.fromPointXY(p).distance(lahn_full) for p in mouths]}

water_mem = memory('Rhein, Lahn und direkte Zuflüsse', 'MultiLineString', [('GKZ',QVariant.String),('Name',QVariant.String),('Klasse',QVariant.String),('Laenge_gesamt_m',QVariant.Double)])
selected_full = []
for code in ['2000000000','2580000000',*direct]:
    fs = groups[code]
    kind = 'Rhein' if code == '2000000000' else 'Lahn' if code == '2580000000' else 'Zufluss > 1 km'
    for f in fs:
        selected_full.append(f.geometry())
        g = cut(f.geometry())
        if not g.isEmpty():
            g.convertToMultiType()
            add(water_mem,g,[code,f['GEWAESSERNAME'],kind,sum(float(x['LAENGE']) for x in fs)])
water = save(water_mem,'gewaesser')
categories = []
for name,color,width in [('Rhein','#3d7e9a',2.0),('Lahn','#237d9c',0.95),('Zufluss > 1 km','#5599b2',0.32)]:
    sym = QgsLineSymbol.createSimple({'line_color':color,'line_width':str(width),'capstyle':'round','joinstyle':'round'})
    categories.append(QgsRendererCategory(name,sym,name))
water.setRenderer(QgsCategorizedSymbolRenderer('Klasse',categories))
labels(water, 'CASE WHEN "Klasse" IN (\'Rhein\',\'Lahn\') THEN upper("Name") END', 12, '#145c79', True, True, True)

# Pfeile werden aus der unverändert gerichteten Ausgangsgeometrie abgeleitet.
arrow_mem = memory('Fließrichtung', 'Point', [('Klasse',QVariant.String),('Winkel',QVariant.Double)])
for f in water.getFeatures():
    for line in lineparts(f.geometry()):
        g = QgsGeometry.fromPolylineXY(line)
        length = g.length()
        if length < 170:
            continue
        interval = 2200 if f['Klasse'] != 'Zufluss > 1 km' else 1800
        distances = [length/2] if length < interval*1.4 else [interval/2+i*interval for i in range(int(length/interval))]
        for distance in distances:
            point = g.interpolate(distance)
            p1 = g.interpolate(max(0,distance-12)).asPoint()
            p2 = g.interpolate(min(length,distance+12)).asPoint()
            angle = math.degrees(math.atan2(p2.x()-p1.x(),p2.y()-p1.y()))%360
            add(arrow_mem,point,[f['Klasse'],angle])
arrows = save(arrow_mem,'fliessrichtung')
cats = []
for name,color,size in [('Rhein','#155a79',1.8),('Lahn','#115673',1.6),('Zufluss > 1 km','#25708f',1.15)]:
    symbol = QgsMarkerSymbol.createSimple({'name':'triangle','color':color,'outline_style':'no','size':str(size)})
    symbol.setDataDefinedAngle(QgsProperty.fromField('Winkel'))
    cats.append(QgsRendererCategory(name,symbol,name))
arrows.setRenderer(QgsCategorizedSymbolRenderer('Klasse',cats))

# Ortslagen: minimaler Abstand jeder Ortslagenfläche zu den ausgewählten Gewässern.
all_water = QgsGeometry.unaryUnion(selected_full)
water_index_geom = QgsGeometry.createGeometryEngine(all_water.constGet())
water_index_geom.prepareGeometry()
town_source = QgsVectorLayer(str(B/'daten/ortslage_original.gpkg')+'|layername=ortslage','Ortslagen','ogr')
town_mem = memory('Ortslagen · Gewässernähe', 'MultiPolygon', [('Name',QVariant.String),('Abstand_m',QVariant.Double),('Nah',QVariant.Int)])
for f in town_source.getFeatures(QgsFeatureRequest().setFilterRect(EXT)):
    full = f.geometry()
    distance = full.distance(all_water)
    g = cut(full)
    if not g.isEmpty():
        g.convertToMultiType()
        add(town_mem,g,[f['NAM'],distance,int(distance<=500)])
towns = save(town_mem,'ortslagen')
towns.setRenderer(QgsCategorizedSymbolRenderer('Nah',[
    QgsRendererCategory(0,QgsFillSymbol.createSimple({'color':'#e0ddd5','outline_color':'#ccc6ba','outline_width':'0.12'}),'Weitere Ortslagen'),
    QgsRendererCategory(1,QgsFillSymbol.createSimple({'color':'#d6b28f','outline_color':'#ab8665','outline_width':'0.17'}),'Ortslagen bis 500 m vom Gewässer')]))
labels(towns,'CASE WHEN "Nah"=1 THEN "Name" END',8.2,'#423a34',True,True)
STATS['ortslagen_hervorgehoben'] = sum(int(f['Nah']) for f in towns.getFeatures())

def polygon_layer(source_name,title,table,color):
    src = load(source_name)
    mem = memory(title,'MultiPolygon',[('Herkunft',QVariant.String)])
    for f in src.getFeatures():
        g = cut(f.geometry())
        if not g.isEmpty():
            g.convertToMultiType()
            add(mem,g,[source_name])
    out = save(mem,table)
    out.renderer().setSymbol(QgsFillSymbol.createSimple({'color':color,'outline_style':'no'}))
    return out

forest = polygon_layer('wald','Wald','wald','#c6d8b5')
agriculture = polygon_layer('landwirtschaft','Landwirtschaft','landwirtschaft','#f0e6bb')

# Kreisgrenzen für RLP. Die genaue Landesmaske trennt die Straßenquellen.
county_source = load('kreise')
county_mem = memory('Kreise und kreisfreie Stadt','MultiPolygon',[('Name',QVariant.String),('Art',QVariant.String)])
rlp_full = []
for f in county_source.getFeatures():
    if str(f['sn_l']) != '07':
        continue
    rlp_full.append(f.geometry())
    g = cut(f.geometry())
    if not g.isEmpty():
        g.convertToMultiType()
        add(county_mem,g,[f['gen'],f['bez']])
counties = save(county_mem,'kreise')
counties.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'255,255,255,0','outline_color':'#947d93','outline_width':'0.4','outline_style':'dash_dot'}))
labels(counties,'upper("Name")',11,'#7d687e',True,False,True)
rlp = QgsGeometry.unaryUnion(rlp_full)

# Basis-DLM innerhalb RLP verhindert Scheinkreuzungen des generalisierten
# DLM250 mit der lagetreuen Lahn. DLM250 ergänzt den hessischen Kartenrand.
road_mem = memory('Straßennetz','MultiLineString',[('Klasse',QVariant.String),('Nummer',QVariant.String),('Quelle',QVariant.String)])
wdm = {'1301':'Autobahn','1303':'Bundesstraße','1305':'Landesstraße'}
for source_name in ['strassen_basisdlm','strassen']:
    src = load(source_name)
    for f in src.getFeatures(QgsFeatureRequest().setFilterRect(EXT)):
        klass = wdm.get(str(f['wdm']))
        if not klass:
            continue
        g = f.geometry()
        if source_name=='strassen':
            g = g.difference(rlp)
        g = cut(g)
        if g.isEmpty():
            continue
        g.convertToMultiType()
        raw = str(f['bez']) if not QgsVariantUtils.isNull(f['bez']) else ''
        nums = [v for v in raw.split('#') if v.startswith('A' if klass=='Autobahn' else 'B' if klass=='Bundesstraße' else 'L')]
        add(road_mem,g,[klass,nums[0].replace('A','A ').replace('B','B ').replace('L','L ') if nums else '',source_name])
roads = save(road_mem,'strassen')
cats=[]
for name,color,width in [('Autobahn','#4383b2',0.85),('Bundesstraße','#e3b85f',0.6),('Landesstraße','#aaa69b',0.28)]:
    sym=QgsLineSymbol.createSimple({'line_color':'#fffef9','line_width':str(width+0.5),'capstyle':'round','joinstyle':'round'})
    sym.appendSymbolLayer(QgsSimpleLineSymbolLayer.create({'line_color':color,'line_width':str(width),'capstyle':'round','joinstyle':'round'}))
    cats.append(QgsRendererCategory(name,sym,name))
roads.setRenderer(QgsCategorizedSymbolRenderer('Klasse',cats))
# Nummernschilder werden nur für längere zusammengesetzte Strecken erzeugt.
shield_mem = memory('Straßennummern','MultiLineString',[('Klasse',QVariant.String),('Nummer',QVariant.String)])
road_groups = collections.defaultdict(list)
for f in roads.getFeatures():
    if f['Klasse'] in ['Autobahn','Bundesstraße'] and f['Nummer']:
        road_groups[(f['Klasse'],f['Nummer'])].append(f.geometry())
for (kind,num),geoms in road_groups.items():
    g = QgsGeometry.unaryUnion(geoms).mergeLines()
    parts=sorted(lineparts(g),key=lambda line:QgsGeometry.fromPolylineXY(line).length(),reverse=True)[:2]
    for line in parts:
        geom=QgsGeometry.fromPolylineXY(line)
        if geom.length()>500:
            geom.convertToMultiType()
            add(shield_mem,geom,[kind,num])
shields=save(shield_mem,'strassennummern')
shields.renderer().setSymbol(QgsLineSymbol.createSimple({'line_style':'no'}))
rules=QgsRuleBasedLabeling.Rule(QgsPalLayerSettings())
for kind,bg,fg in [('Autobahn','#276393','#ffffff'),('Bundesstraße','#f6d577','#473c25')]:
    settings=QgsPalLayerSettings()
    settings.fieldName='Nummer'
    settings.placement=Qgis.LabelPlacement.Line
    settings.repeatDistance=70
    fmt=QgsTextFormat()
    fmt.setFont(QFont('DejaVu Sans',8,QFont.Bold))
    fmt.setSize(8)
    fmt.setColor(QColor(fg))
    background=QgsTextBackgroundSettings()
    background.setEnabled(True)
    background.setType(QgsTextBackgroundSettings.ShapeRectangle)
    background.setFillColor(QColor(bg))
    background.setStrokeColor(QColor('#fffef9'))
    background.setStrokeWidth(0.25)
    background.setSize(QSizeF(0.9,0.6))
    fmt.setBackground(background)
    settings.setFormat(fmt)
    rule=QgsRuleBasedLabeling.Rule(settings)
    rule.setFilterExpression('"Klasse"=\''+kind+'\'')
    rules.appendChild(rule)
shields.setLabeling(QgsRuleBasedLabeling(rules))
shields.setLabelsEnabled(True)

# GPX: auf den Abschnitt ab Diez begrenzen, statt den Wanderweg östlich
# des Aufgabenbereichs lediglich am Kartenrahmen abzuschneiden.
gpx=QgsVectorLayer(str(B/'daten/Lahnwanderweg.gpx')+'|layername=tracks','GPX','ogr')
track_mem=memory('Lahnwanderweg','MultiLineString',[('Name',QVariant.String),('Laenge_km',QVariant.Double)])
upstream=QgsGeometry.fromPointXY(lineparts(groups['2580000000'][0].geometry())[0][0])
tx=QgsCoordinateTransform(gpx.crs(),CRS,P)
for f in gpx.getFeatures():
    g=f.geometry()
    g.transform(tx)
    for line in lineparts(g):
        line_geom=QgsGeometry.fromPolylineXY(line)
        d=line_geom.lineLocatePoint(upstream)
        end=QgsGeometry.fromPointXY(line[-1]).distance(lahn_full)
        start=QgsGeometry.fromPointXY(line[0]).distance(lahn_full)
        curve=line_geom.constGet().curveSubstring(d,line_geom.length()) if end<start else line_geom.constGet().curveSubstring(0,d)
        selected=cut(QgsGeometry(curve))
        selected.convertToMultiType()
        add(track_mem,selected,['Lahnwanderweg',selected.length()/1000])
track=save(track_mem,'lahnwanderweg')
track.renderer().setSymbol(QgsLineSymbol.createSimple({'line_color':'#a4562f','line_width':'0.55','line_style':'dash','capstyle':'round'}))

# Zehn nummerierte Fotostandorte mit zugehörigen Originalbildern.
poi_mem=memory('Sehenswürdigkeiten','Point',[('Nr',QVariant.Int),('Name',QVariant.String),('Foto',QVariant.String)])
with (B/'daten/Koordinaten_Fotos.txt').open(encoding='utf-8-sig') as handle:
    for i,row in enumerate(csv.DictReader(handle,delimiter='|'),1):
        assert (B/'fotos'/f'{i:02d}.jpg').exists()
        add(poi_mem,QgsGeometry.fromPointXY(QgsPointXY(float(row['X']),float(row['Y']))),[i,row['Name'],f'fotos/{i:02d}.jpg'])
poi=save(poi_mem,'fotostandorte')
(B/'symbole').mkdir(exist_ok=True)
cats=[]
for i in range(1,11):
    svg=B/'symbole'/f'foto_{i:02d}.svg'
    svg.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><circle cx="20" cy="20" r="18" fill="#873e55" stroke="white" stroke-width="2.2"/><text x="20" y="26" font-family="DejaVu Sans" font-weight="bold" font-size="18" text-anchor="middle" fill="white">{i}</text></svg>')
    sym=QgsMarkerSymbol()
    sym.changeSymbolLayer(0,QgsSvgMarkerSymbolLayer(str(svg),5.8))
    cats.append(QgsRendererCategory(i,sym,str(i)))
poi.setRenderer(QgsCategorizedSymbolRenderer('Nr',cats))

ORDER=[poi,shields,arrows,track,roads,water,towns,counties,forest,agriculture]
P.layerTreeRoot().setHasCustomLayerOrder(True)
P.layerTreeRoot().setCustomLayerOrder(ORDER)
P.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(EXT,CRS))
P.setTitle('Das untere Lahntal – Flusslandschaft 2026 (fiktives Szenario)')
P.writeEntry('Pruefung','Kennziffer','204')
P.writeEntry('Pruefung','Rechnerkennung',socket.gethostname())

# A2-Drucklayout mit durchgehendem visuellen Schlüssel zu den Fotostandorten.
from qgis.PyQt.QtCore import QSizeF
layout=QgsPrintLayout(P)
layout.initializeDefaults()
layout.setName('Unteres Lahntal – DIN A2')
layout.pageCollection().page(0).setPageSize('A2',QgsLayoutItemPage.Landscape)

def text(x,y,w,h,value,size=9,color='#233e44',bold=False,italic=False):
    item=QgsLayoutItemLabel(layout)
    item.setText(value)
    font=QFont('DejaVu Sans',int(size),QFont.Bold if bold else QFont.Normal)
    font.setPointSizeF(size)
    font.setItalic(italic)
    item.setFont(font)
    item.setFontColor(QColor(color))
    layout.addLayoutItem(item)
    item.attemptMove(QgsLayoutPoint(x,y))
    item.attemptResize(QgsLayoutSize(w,h))
    return item

def shape_line(x,y,length,color,width=0.5,dash='solid'):
    item=QgsLayoutItemPolyline(QPolygonF([QPointF(x,y),QPointF(x+length,y)]),layout)
    item.setSymbol(QgsLineSymbol.createSimple({'line_color':color,'line_width':str(width),'line_style':dash}))
    layout.addLayoutItem(item)
    return item

text(11,6,430,15,'DAS UNTERE LAHNTAL',27,bold=True)
text(12,23,420,8,'Von Diez an den Rhein · Gewässer, Wanderweg und Kulturlandschaft',12)
text(459,9,125,8,'FLUSSLANDSCHAFT 2026',12,bold=True)
text(459,19,125,7,'Fiktives Szenario der Probeklausur',8,color='#69797a')

legend1=[('Rhein','#3d7e9a',1.6),('Lahn','#237d9c',0.95),('Direkter Zufluss > 1 km','#5599b2',0.35),('Autobahn','#4383b2',0.85),('Bundesstraße','#e3b85f',0.65),('Landesstraße','#aaa69b',0.3)]
positions=[12,76,138,251,339,439]
for (title,color,width),x in zip(legend1,positions):
    shape_line(x,39,11,color,width)
    text(x+14,34,112,9,title,8.5)
legend2=[('Wald','#c6d8b5'),('Landwirtschaft','#f0e6bb'),('Ortslage','#e0ddd5'),('Ortslage ≤ 500 m am Gewässer','#d6b28f')]
for (title,color),x in zip(legend2,[12,76,160,230]):
    box=QgsLayoutItemShape(layout)
    box.setShapeType(QgsLayoutItemShape.Rectangle)
    box.setSymbol(QgsFillSymbol.createSimple({'color':color,'outline_style':'no'}))
    layout.addLayoutItem(box)
    box.attemptMove(QgsLayoutPoint(x,46))
    box.attemptResize(QgsLayoutSize(9,4))
    text(x+12,42,122,10,title,8.5)
shape_line(380,48,11,'#a4562f',0.55,'dash')
text(394,42,91,10,'Lahnwanderweg',8.5)
shape_line(482,48,11,'#947d93',0.4,'dash_dot')
text(496,42,88,10,'Kreisgrenze',8.5)

map_item=QgsLayoutItemMap(layout)
layout.addLayoutItem(map_item)
map_item.attemptMove(QgsLayoutPoint(10,56))
map_item.attemptResize(QgsLayoutSize(574,245))
map_item.setCrs(CRS)
map_item.setLayers(ORDER)
map_item.setKeepLayerSet(True)
map_item.setBackgroundColor(QColor('#faf9f3'))
map_item.zoomToExtent(EXT)
map_item.setScale(65000)
map_item.setFrameEnabled(True)
map_item.setFrameStrokeColor(QColor('#b5c1bd'))
grid=map_item.grid()
grid.setEnabled(True)
grid.setIntervalX(5000)
grid.setIntervalY(5000)
grid.setStyle(QgsLayoutItemMapGrid.FrameAnnotationsOnly)
grid.setAnnotationEnabled(True)
grid.setAnnotationFormat(QgsLayoutItemMapGrid.Decimal)
grid.setAnnotationPrecision(0)
grid.setAnnotationFont(QFont('DejaVu Sans',6))
for side in [QgsLayoutItemMapGrid.Left,QgsLayoutItemMapGrid.Right,QgsLayoutItemMapGrid.Top,QgsLayoutItemMapGrid.Bottom]:
    grid.setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll,side)
text(568,59,13,14,'N ↑',12,bold=True)
scale=QgsLayoutItemScaleBar(layout)
scale.setStyle('Single Box')
scale.setLinkedMap(map_item)
scale.applyDefaultSize()
scale.setUnits(Qgis.DistanceUnit.Kilometers)
scale.setUnitsPerSegment(1)
scale.setNumberOfSegments(5)
scale.setNumberOfSegmentsLeft(0)
scale.setUnitLabel('km')
scale.setFont(QFont('DejaVu Sans',8))
scale.setBackgroundEnabled(True)
scale.setBackgroundColor(QColor('#fffef5'))
layout.addLayoutItem(scale)
scale.attemptMove(QgsLayoutPoint(15,285))
text(120,287,210,10,'1 : 65 000 · Fließpfeile zeigen stromabwärts',8.5)

credits={r['nr']:r for r in json.loads((B/'recherche/Fotonachweise.json').read_text())}
names={f['Nr']:f['Name'] for f in poi.getFeatures()}
short_authors={9:'Heribert Pohl',6:'Muck (Muck50)'}
photo_group=P.layerTreeRoot().addGroup('Bildleiste – nur Layout, keine Georeferenzierung')
photo_group.setItemVisibilityChecked(False)
for pos,n in enumerate([2,1,6,3,7,5,10,8,4,9]):
    x=10+pos*57.7
    add_photo_panel(layout,P,B,photo_group,n,x,307)
    text(x,338,55,10,f'{n:02d} · {names[n]}',8.6,bold=True)
    author=short_authors.get(n,credits[n]['urheber'])
    text(x,349,55,12,author+'\n'+credits[n]['lizenz']+' · Ausschnitt',7.2,color='#5e6968')

shape_line(10,360,574,'#b5c1bd',0.25)
text(10,364,570,10,'KARTENGRUNDLAGEN UND NACHWEISE',9,bold=True)
text(10,376,285,26,'Gewässer: Wasserwirtschaftsverwaltung Rheinland-Pfalz, Gewässernetz 2017, CC BY 4.0.\nWald / ergänzende Straßen: © GeoBasis-DE / BKG (2026), DLM250, dl-de/by-2-0.\nKreisgrenzen: © BKG (2026), VG250, dl-de/by-2-0; Datenquellen siehe Begleitnachweis.\nOrtslagen, Landwirtschaft / Straßen: ©GeoBasis-DE / LVermGeoRP (2026), dl-de/by-2-0,\nwww.lvermgeo.rlp.de [Daten bearbeitet]; Wanderweg aus den Prüfungseingaben.',7.8)
text(307,376,278,26,'Fotos: Wikimedia Commons; Nummern verknüpfen Fotostandorte und Bildleiste.\nBildausschnitte im einheitlichen Querformat; Urheber und Lizenz unter jedem Foto.\nLizenztexte: creativecommons.org/licenses/ (BY 4.0; BY-SA 2.0, 3.0, 3.0 DE, 4.0).\nVollständige Bild-URLs, Lizenzlinks, Datenquellen und Auswahlmethodik:\nbeiliegende Datei Quellen_und_Methodik.pdf / QUELLEN_UND_METHODIK.md.',7.8)
text(10,407,570,9,f'Erstellt / Datenabruf: 27.10.2026  ·  Prüfungskennziffer: 204  ·  Rechner: {socket.gethostname()}  ·  ETRS89 / UTM Zone 32N (EPSG:25832)  ·  DIN A2 quer',8)
P.layoutManager().addLayout(layout)
P.setFileName(str(B/'Lahntal.qgz'))
assert P.write()
# QGIS 3.40 speichert im LayerSet des Layouts zusätzlich absolute
# Wiederherstellungspfade. Auch diese Fallbacks portabel ablegen.
project_path=B/'Lahntal.qgz'
portable_path=B/'Lahntal_portabel.tmp'
with zipfile.ZipFile(project_path) as src, zipfile.ZipFile(portable_path,'w',zipfile.ZIP_DEFLATED) as dst:
    for item in src.infolist():
        content=src.read(item.filename)
        if item.filename.endswith('.qgs'):
            content=content.replace((str(B)+'/').encode(),b'./')
        dst.writestr(item,content)
portable_path.replace(project_path)
export=QgsLayoutExporter(layout)
settings=QgsLayoutExporter.PdfExportSettings()
settings.dpi=300
raw_pdf=B/'recherche/Lahntal_A2_Direktexport.pdf'
assert export.exportToPdf(str(raw_pdf),settings)==QgsLayoutExporter.Success
subprocess.run(['gs','-sDEVICE=pdfwrite','-dCompatibilityLevel=1.6','-dNOPAUSE','-dBATCH','-dSAFER','-dDownsampleColorImages=true','-dColorImageResolution=300','-dColorImageDownsampleThreshold=1.2','-dAutoFilterColorImages=false','-dColorImageFilter=/DCTEncode','-dJPEGQ=92','-dDownsampleGrayImages=true','-dGrayImageResolution=300','-sOutputFile='+str(B/'Lahntal_A2.pdf'),str(raw_pdf)],check=True)
STATS['direkte_zufluesse']=len(direct)
STATS['zufluesse']=direct
STATS['massstab']=map_item.scale()
STATS['wanderweg_laenge_km']=sum(float(f['Laenge_km']) for f in track.getFeatures())
STATS['strassen_quellen']=dict(collections.Counter(f['Quelle'] for f in roads.getFeatures()))
(B/'recherche/Endvalidierung.json').write_text(json.dumps(STATS,ensure_ascii=False,indent=2))
with (B/'recherche/Ausgewaehlte_Zufluesse.csv').open('w') as handle:
    writer=csv.writer(handle)
    writer.writerow(['GKZ','Name','Laenge_m','Mindestabstand_Muendung_Lahn_m'])
    for code,data in sorted(direct.items()):
        writer.writerow([code,data['name'],data['laenge_m'],min(data['muen_distanzen_m'])])
print(json.dumps({k:v for k,v in STATS.items() if k!='zufluesse'},ensure_ascii=False,indent=2))
