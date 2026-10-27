#!/usr/bin/python3
"""Read-only-Prüfung der für die Aufgaben benötigten öffentlichen Dienste."""
import concurrent.futures
import datetime
import json
from pathlib import Path
import urllib.request

BASE = Path(__file__).resolve().parents[1]
URLS = {
    'dlm250': 'https://sgx.geodatenzentrum.de/wfs_dlm250?SERVICE=WFS&REQUEST=GetCapabilities&VERSION=2.0.0',
    'dlm50': 'https://www.geoportal.rlp.de/registry/wfs/606?SERVICE=WFS&REQUEST=GetCapabilities&VERSION=2.0.0',
    'gewaesser': 'https://geodienste-wasser.rlp-umwelt.de/geoserver/gewaesser/wfs?SERVICE=WFS&REQUEST=GetCapabilities&VERSION=2.0.0',
    'verwaltungsgrenzen_kandidat': 'https://sgx.geodatenzentrum.de/wfs_vg250?SERVICE=WFS&REQUEST=GetCapabilities&VERSION=2.0.0',
    'fotoinformation': 'https://commons.wikimedia.org/w/api.php?action=query&format=json&titles=File:Malbergturm.JPG&prop=imageinfo&iiprop=url%7Cextmetadata',
}

def check(item):
    name, url = item
    record = {'quelle': name, 'url': url, 'zeitpunkt_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Lahntal-QGIS-Study/1.0'})
        with urllib.request.urlopen(req, timeout=35) as response:
            data = response.read(8 * 1024 * 1024)
            record.update(status=response.status, bytes=len(data), content_type=response.headers.get('Content-Type'))
        suffix = '.json' if name == 'fotoinformation' else '.xml'
        (BASE/'recherche'/('dienst_'+name+suffix)).write_bytes(data)
    except Exception as exc:
        record['fehler'] = str(exc)
    return record

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    results = list(pool.map(check, URLS.items()))
(BASE/'recherche/Internetpruefung.json').write_text(json.dumps(results, indent=2, ensure_ascii=False))
print(json.dumps(results, indent=2, ensure_ascii=False))
raise SystemExit(1 if any('fehler' in r for r in results) else 0)
