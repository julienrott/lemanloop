#!/usr/bin/env python3
"""Filter the Rhône canal tail from the OSM lake polygon -> lake_ring_clean.json"""
import json

osm = json.load(open('/home/hermes/github/lemanloop/assets/lake_osm.json'))
ring = osm[0]['geojson']['coordinates'][0]

# The OSM polygon includes the upper Rhône below the lake (thin strip at lat
# ~46.385-46.397 extending east of lon 6.48). Cut it: drop points in that zone,
# except we must bridge the polygon across the gap (Montreux→Villeneuve coast).
out = []
for lo, la in ring:
    if lo > 6.48 and la < 46.40:
        continue  # Rhône canal tail east of the lake's true south-east coast
    out.append([lo, la])

print('filtered ring:', len(out), 'of', len(ring))
print('lon range:', round(min(p[0] for p in out), 3), round(max(p[0] for p in out), 3))
print('lat range:', round(min(p[1] for p in out), 3), round(max(p[1] for p in out), 3))

json.dump(out, open('/home/hermes/github/lemanloop/assets/lake_ring_clean.json', 'w'))
print('saved lake_ring_clean.json')

# Check Montreux coastal points now present
mon = [(round(p[0],3), round(p[1],3)) for p in out if 6.49 <= p[0] <= 6.56 and 46.430 <= p[1] <= 46.460]
print('montreux coastal pts:', len(mon), mon[:8])
