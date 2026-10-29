#!/usr/bin/env python3
"""Build a faithful Lake Geneva SVG map from OSM polygon, inject into index.html."""
import json, math

osm = json.load(open('/home/hermes/github/lemanloop/assets/lake_osm.json'))
ring = osm[0]['geojson']['coordinates'][0]  # outer polygon of (lon,lat)

# Simplify (Douglas-Peucker, epsilon tuned)
def dp(points, eps):
    if len(points) < 3: return points
    (x0,y0),(x1,y1) = points[0], points[-1]
    dmax, idx = 0, 0
    def perp(p):
        (x,y) = p
        dx,dy = x1-x0, y1-y0
        L = math.hypot(dx,dy) or 1
        return abs(dx*(y0-y)-dy*(x0-x))/L
    dmax, idx = max((perp(p),i) for i,p in enumerate(points[1:-1],1))
    if dmax > eps:
        a = dp(points[:idx+1], eps); b = dp(points[idx:], eps)
        return a[:-1]+b
    return [points[0], points[-1]]

def simplify(pts, n_target=180):
    """Keep every k-th point of the ring for a smooth-but-compact shape."""
    if len(pts) <= n_target:
        return pts
    step = len(pts) / n_target
    return [pts[int(i*step)] for i in range(n_target)]

pts_ll = simplify([(lon,lat) for lon,lat in ring])
print("simplified:", len(pts_ll))
# Calibrated projection into 1000x620 viewBox
lons = [p[0] for p in pts_ll]; lats = [p[1] for p in pts_ll]
lon0, lon1 = min(lons), max(lons); lat0, lat1 = min(lats), max(lats)
# Aspect correction: at lat ~46.4, 1 deg lon = cos(46.4)*111km = 76.7km; 1 deg lat=111km
aspect = math.cos(math.radians(46.4))
w_deg = lon1-lon0; h_deg = lat1-lat0
W = w_deg*aspect*11100  # "natural units"
H = h_deg*11100
scale = min(840/W, 440/H)
def xy(lon,lat):
    x = (lon-lon0)*aspect*11100*scale
    y = (lat1-lat)*11100*scale
    return (x, y)  # will be shifted after

pts = [xy(lon,lat) for lon,lat in pts_ll]
# shift into view
minx = min(p[0] for p in pts); miny=min(p[1] for p in pts)
tx = (1000-(max(p[0] for p in pts)-minx))/2 - minx
ty = (620-(max(p[1] for p in pts)-miny))/2 - miny
pts = [(x+tx, y+ty) for x,y in pts]

cx = sum(x for x,_ in pts)/len(pts); cy = sum(y for _,y in pts)/len(pts)

def smooth_closed(p):
    n=len(p)
    d=f'M {(p[0][0]+p[n-1][0])/2:.1f},{(p[0][1]+p[n-1][1])/2:.1f}'
    for i in range(n):
        a,b = p[i], p[(i+1)%n]
        d+=f' Q {a[0]:.1f},{a[1]:.1f} {(a[0]+b[0])/2:.1f},{(a[1]+b[1])/2:.1f}'
    return d+' Z'

shore_d = smooth_closed(pts)
def ring(k):
    r = [(cx+(x-cx)*k, cy+(y-cy)*k) for x,y in pts]
    return smooth_closed(r)
trace_d = ring(1.075)

GEO = {
    'Genève':(6.150,46.207),'Nyon':(6.235,46.400),'Lausanne':(6.460,46.510),
    'Vevey':(6.525,46.515),'Montreux':(6.555,46.455),'Évian':(6.365,46.400),
    'Thonon':(6.215,46.385),
}
labels=[]
for name,(lon,lat) in GEO.items():
    x,y = xy(lon,lat); x,y = x+tx, y+ty
    dx,dy = x-cx, y-cy
    n = math.hypot(dx,dy) or 1
    ax,ay = cx+dx*1.07, cy+dy*1.07
    lx,ly = cx+dx*1.24, cy+dy*1.24
    fr = name in ('Évian','Thonon')
    color = '#d9b49a' if fr else '#c8d6d9'
    anchor='middle'
    # placement overrides (nudges in px)
    if name=='Genève': anchor='start'; lx=x+16; ly=y-6
    if name=='Nyon':   anchor='start'; lx+=10; ly+=0
    if name=='Lausanne': anchor='start'; lx+=12; ly+=2
    if name=='Vevey':  anchor='start'; lx+=12; ly=-4+ly-ly  # y at shore
    if name=='Vevey':  ly=y+6; lx=x+26
    if name=='Montreux': anchor='end'; lx=x-14; ly=y+8
    if name=='Évian':  anchor='start'; lx=x+16; ly=y+6
    if name=='Thonon': anchor='end';  lx=x-12; ly=y+6
    labels.append(f'<g><circle cx="{ax:.0f}" cy="{ay:.0f}" r="7" fill="#5fb760"/>'
      f'<circle cx="{ax:.0f}" cy="{ay:.0f}" r="12" fill="none" stroke="#5fb760" stroke-opacity=".35"/>'
      f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="{anchor}" font-size="17" font-weight="600" fill="{color}" font-family="Space Grotesk,Inter,sans-serif">{name}</text></g>')

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
    <circle cx="795" cy="140" r="3"/><circle cx="850" cy="205" r="2.5"/><circle cx="150" cy="500" r="3"/>
    <circle cx="105" cy="430" r="2.5"/><circle cx="890" cy="115" r="2"/><circle cx="760" cy="490" r="2.5"/>
  </g>
  <path d="{shore_d}" fill="url(#lakeG)" stroke="#8fd3c8" stroke-opacity=".45" stroke-width="2"/>
  <path d="{trace_d}" fill="none" stroke="#8fd3c8" stroke-opacity=".9" stroke-width="3" stroke-dasharray="10 7" stroke-linecap="round"/>
  {''.join(labels)}
</svg>'''

path='/home/hermes/github/lemanloop/index.html'
html=open(path).read()
new='<div class="map-visual">'+svg+'</div>'
m_start=html.index('<div class="map-visual">')
m_end=html.index('<div class="map-legend">')
html=html[:m_start]+new+'\n    '+html[m_end:]
open(path,'w').write(html)
print("Injected faithfully. size:",len(html))
