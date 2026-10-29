#!/usr/bin/env python3
"""Build the true-shape Léman SVG map and inject it into index.html."""
import math

# Map viewBox: 0 0 1000 620. Calibrated on real lake geo.
def xy(lon, lat):
    return (round((lon-6.14)*1200+70), round((46.52-lat)*1451.5+70))

# Shoreline: real-shape sampled points, clockwise from Geneve W tip
shore_geo = [
    (6.148,46.207),(6.155,46.230),(6.235,46.400),(6.335,46.475),
    (6.460,46.510),(6.525,46.505),(6.560,46.460),(6.635,46.420),
    (6.700,46.375),(6.690,46.335),(6.510,46.360),(6.360,46.400),
    (6.215,46.385),(6.290,46.375),(6.170,46.300),
]
shore = [xy(*p) for p in shore_geo]
cx = sum(x for x,_ in shore)/len(shore); cy = sum(y for _,y in shore)/len(shore)

# Smooth closed path (Catmull-Rom through midpoints)
def smooth_closed(pts):
    n = len(pts)
    d = f'M {(pts[0][0]+pts[n-1][0])/2:.0f},{(pts[0][1]+pts[n-1][1])/2:.0f}'
    for i in range(n):
        p0, p1 = pts[i], pts[(i+1) % n]
        d += f' Q {p0[0]},{p0[1]} {(p0[0]+p1[0])/2:.0f},{(p0[1]+p1[1])/2:.0f}'
    return d + ' Z'

shore_d = smooth_closed(shore)

# Offset loop: scaled from centroid
def ring(pts, k):
    return [(cx+(x-cx)*k, cy+(y-cy)*k) for x,y in pts]
trace_ring = ring(shore, 1.10)
trace_d = smooth_closed(trace_ring)

GEO = {
    'Geneve':   (6.150,46.207),'Nyon':(6.235,46.400),'Lausanne':(6.460,46.510),
    'Vevey':(6.525,46.515),'Montreux':(6.555,46.455),'Evian':(6.365,46.400),
    'Thonon':(6.215,46.385),
}
disp = {'Evian':'Évian'}
labels = []
for name,(lon,lat) in GEO.items():
    x,y = xy(lon,lat)
    dx,dy = x-cx, y-cy
    n = math.hypot(dx,dy) or 1
    ax,ay = cx+dx*(1.10)*1, cy+dy*1.10   # on the trace ring
    lx,ly = cx+dx*1.22, cy+dy*1.22       # label further out
    fr = name in ('Evian','Thonon')
    color = '#d9b49a' if fr else '#c8d6d9'
    # label placement tweaks
    anchor = 'middle'
    if name=='Lausanne': anchor='start'; lx=x+40; ly=y+4
    if name=='Vevey':    anchor='start'; lx=x+44; ly=y-2
    if name=='Montreux': anchor='end';   lx=x-10; ly=y+22; ay=y-20
    if name=='Nyon':     anchor='start'; lx=x+46; ly=y+16
    if name=='Geneve':   anchor='start'; lx=x;    ly=y-18
    if name=='Evian':    anchor='middle';lx=x;    ly=y+42
    if name=='Thonon':   anchor='middle';lx=x-10; ly=y+40
    labels.append(
        f'<g><circle cx="{ax:.0f}" cy="{ay:.0f}" r="7" fill="#5fb760"/>'
        f'<circle cx="{ax:.0f}" cy="{ay:.0f}" r="12" fill="none" stroke="#5fb760" stroke-opacity=".35"/>'
        f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="{anchor}" font-size="17" font-weight="600" '
        f'fill="{color}" font-family="Space Grotesk,Inter,sans-serif">{disp.get(name,name)}</text></g>')

svg = f'''<svg viewBox="0 0 1000 620" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Carte du tracé LémanLoop autour du lac Léman">
  <defs>
    <radialGradient id="lakeG" cx="45%" cy="40%" r="75%">
      <stop offset="0%" stop-color="#1d7ea0"/><stop offset="70%" stop-color="#0d4a63"/><stop offset="100%" stop-color="#0a3a50"/>
    </radialGradient>
    <radialGradient id="bgG" cx="50%" cy="45%" r="80%">
      <stop offset="0%" stop-color="#0d5a70"/><stop offset="60%" stop-color="#073542"/><stop offset="100%" stop-color="#03242e"/>
    </radialGradient>
  </defs>
  <rect width="1000" height="620" fill="url(#bgG)"/>
  <g fill="#8fb6be" opacity=".18">
    <circle cx="790" cy="150" r="3"/><circle cx="840" cy="200" r="2.5"/><circle cx="160" cy="480" r="3"/>
    <circle cx="120" cy="420" r="2.5"/><circle cx="880" cy="120" r="2"/><circle cx="750" cy="470" r="2.5"/><circle cx="220" cy="150" r="2"/>
  </g>
  <path d="M 640 90 Q 700 60 780 100 Q 870 140 960 180 Q 890 170 800 155 Q 700 130 640 90 Z" fill="#ffffff" opacity=".05"/>
  <path d="M 100 560 Q 160 530 240 555 Q 200 570 100 560 Z" fill="#ffffff" opacity=".04"/>
  <path d="{shore_d}" fill="url(#lakeG)" stroke="#8fd3c8" stroke-opacity=".4" stroke-width="2"/>
  <path d="{trace_d}" fill="none" stroke="#8fd3c8" stroke-opacity=".9" stroke-width="3" stroke-dasharray="10 7" stroke-linecap="round"/>
  {''.join(labels)}
</svg>'''

path = '/home/hermes/github/lemanloop/index.html'
html = open(path).read()

new_block = '<div class="map-visual">' + svg + '</div>'
m_start = html.index('<div class="map-visual">')
m_end = html.index('<div class="map-legend">')
html = html[:m_start] + new_block + '\n    ' + html[m_end:]

# Trim leftover old div closers between new_block and map-legend if duplicated
open(path,'w').write(html)
print("Injected. size:", len(html))
