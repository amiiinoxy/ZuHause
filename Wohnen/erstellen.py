"""Bündelt Karte, Leaflet und recherchierte Daten zu einer lokal nutzbaren HTML-Datei."""
from pathlib import Path
import json
B=Path(__file__).parent
source=(B/'recherche/vorlage.html').read_text()
for key,name in [('__LEAFLET_CSS__','leaflet.css'),('__LEAFLET_JS__','leaflet.js')]:source=source.replace(key,(B/'recherche'/name).read_text())
for key,name in [('__DATA__','orte.json'),('__RIVERS__','fluesse.geojson')]:
 source=source.replace(key,json.dumps(json.loads((B/'recherche'/name).read_text()),ensure_ascii=False).replace('<','\\u003c'))
source=source.replace('__BASEMAP__',json.dumps({k:json.loads((B/'recherche'/('grundkarte_'+k+'.geojson')).read_text()) for k in ['wald','orte','strassen','bahn']},ensure_ascii=False).replace('<','\\u003c'))
license=(B/'recherche/leaflet-LICENSE').read_text()
source=source.replace('<head>','<head><!-- Leaflet 1.9.4 license:\n'+license.replace('--','—')+'\n-->')
(B/'index.html').write_text(source,encoding='utf-8')
(B.parent/'index.html').write_text(source,encoding='utf-8')
print('HTML erstellt',len(source.encode()),'Bytes')
