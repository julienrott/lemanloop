#!/usr/bin/env python3
"""Extract Lake Geneva silhouette from OSM Nominatim and save ring."""
import json, urllib.request, urllib.parse

# Forward geocode lake Léman
url = "https://nominatim.openstreetmap.org/search?q=Lac+L%C3%A9man&format=json&polygon_geojson=1&limit=3"
req = urllib.request.Request(url, headers={'User-Agent':'lemanloop/0.1 (contact: dev)'})
d = json.loads(urllib.request.urlopen(req, timeout=60).read())
json.dump(d, open('/home/hermes/github/lemanloop/assets/lake_osm.json','w'))
for r in d:
    g = r.get('geojson',{})
    print(r['osm_type'], r['osm_id'], g.get('type'), len(g.get('coordinates',[])) if g else 0)
