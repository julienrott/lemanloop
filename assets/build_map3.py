#!/usr/bin/env python3
"""Build the faithful Lake Geneva map with SNAPPED station anchors + animated pod along trace."""
import json, math

osm = json.load(open('/home/hermes/github/lemanloop/assets/lake_osm.json'))
ring = osm[0]['geojson']['coordinates'][0]

def simplify(pts, n=180):
    step = len(pts) / n
    return [pts[int(i*step)] for i in range(n)]

pts_ll = simplify([(lon,lat) for lon,lat in ring])
lons=[p[0] for p in pts_ll]; lats=[p[1] for p in pts_ll]
lon0,lon1=min(lons),max(lons); lat0,lat1=min(lats),max(lats)
aspect=math.cos(math.radians(46.4))
W=(lon1-lon0)*aspect*11100; H=(lat1-lat0)*11100
scale=min(840/W,440/H)
def xy(lon,lat): return ((lon-lon0)*aspect*11100*scale,(lat1-lat)*11100*scale)
pts=[xy(*p) for p in pts_ll]
minx=min(p[0] for p in pts); miny=min(p[1] for p in pts)
tx=(1000-(max(p[0] for p in pts)-minx))/2-minx
ty=(620-(max(p[1] for p in pts)-miny))/2-miny
pts=[(x+tx,y+ty) for x,y in pts]
cx=sum(x for x,_ in pts)/len(pts); cy=sum(y for _,y in pts)/len(pts)
print("lake bbox:", min(x for x,_ in pts), min(y for _,y in pts), max(x for x,_ in pts), max(y for _,y in pts))

# Lakeside polyline (closed). Distances along it for pod animation.
def path_len(p):
    L=0
    for i in range(len(p)):
        a,b=p[i],p[(i+1)%len(p)]
        L+=math.hypot(b[0]-a[0], b[1]-a[1])
    return L
total_len = path_len(pts)

GEO = {
    # (lon,lat) + shoreline anchors measured on the reference map (marker sits ON the shore)
    'Genève':  dict(city=(6.150,46.207), shore=(6.150,46.205)),# SW tip on Rhône exit
    'Nyon':    dict(city=(6.238,46.383), shore=(6.236,46.395)),
    'Lausanne':dict(city=(6.462,46.507), shore=(6.459,46.509)),
    'Vevey':   dict(city=(6.526,46.512), shore=(6.525,46.513)),
    'Montreux':dict(city=(6.551,46.442), shore=(6.540,46.455)),# bord Montreux-Clarens rive sud
    'Évian':   dict(city=(6.363,46.400), shore=(6.362,46.402)),
    'Thonon':  dict(city=(6.215,46.379), shore=(6.215,46.385)),
}
def snap_to_shore(px,py):
    best=None
    for i in range(len(pts)):
        a,b=pts[i],pts[(i+1)%len(pts)]
        dx,dy=b[0]-a[0], b[1]-a[1]
        L2=dx*dx+dy*dy
        t=max(0,min(1,((px-a[0])*dx+(py-a[1])*dy)/L2 if L2 else 0))
        cxp,cyp=a[0]+t*dx,a[1]+t*dy
        d=math.hypot(px-cxp,py-cyp)
        if best is None or d<best[0]: best=(d,cxp,cyp)
    return best

lab_cfg = {
    'Genève':  dict(anchor='end',   lx_n=(-26,  -6)),   # label LEFT of marker (SW tip)
    'Nyon':    dict(anchor='end',   lx_n=(-26,  -4)),   # label LEFT (north-west shore)
    'Lausanne':dict(anchor='start', lx_n=(+30,  -8)),   # label RIGHT, slightly ABOVE (north shore)
    'Vevey':   dict(anchor='start', lx_n=(+20, -16)),   # label UP-RIGHT (Haut Lac, north)
    'Montreux':dict(anchor='end',   lx_n=(-26, +40)),   # label BELOW, far enough from Lausanne's (y 102) — Riviera bay
    'Évian':   dict(anchor='start', lx_n=(+22, +26)),   # label BELOW-RIGHT (south shore)
    'Thonon':  dict(anchor='end',   lx_n=(-26,  -8)),   # label LEFT of marker at (200,600), keep above bottom edge
}
labels=[]
PULSE_KEYS=[]
for name,geo in GEO.items():
    shore_lon, shore_lat = geo['shore']
    x,y = xy(shore_lon, shore_lat); x,y = x+tx, y+ty   # anchor point directly on the shoreline
    d,sx,sy = snap_to_shore(x,y)
    # Hardcoded pixel overrides calibrated on the user's reference map — snap fails
    # where the OSM polygon is straight-line across bays (Montreux).
    FIXED = {'Montreux': (558, 88), 'Vevey': (500, 82), 'Lausanne': (427, 110), 'Thonon': (450, 300)}
    if name in FIXED:
        ax, ay = FIXED[name]
        # verify: keep marker on land by nudge outward if inside simplified ring
        cfg = lab_cfg[name]
        lx,ly = ax + cfg['lx_n'][0], ay + cfg['lx_n'][1]
        lx = max(58, min(930, lx)); ly = max(66, min(600, ly))
        fr = name in ('Évian','Thonon')
        color = '#d9b49a' if fr else '#c8d6d9'
        labels.append(f'''<g><circle cx="{ax:.0f}" cy="{ay:.0f}" r="7" fill="#5fb760"/>'''
          f'''<circle class="stn-pulse" cx="{ax:.0f}" cy="{ay:.0f}" r="12" fill="none" stroke="#5fb760" stroke-opacity=".35"/>'''
          f'''<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="{cfg['anchor']}" font-size="17" font-weight="600" fill="{color}" font-family="Space Grotesk,Inter,sans-serif">{name}</text></g>''')
        print(f'{name}: marker=({ax:.0f},{ay:.0f}) label=({lx:.0f},{ly:.0f}) [HARDCODED]')
        continue
    # outward normal (away from lake centroid) so marker sits on seafront land
    dxn,dyn = sx-cx, sy-cy
    n = math.hypot(dxn,dyn) or 1
    ax,ay = sx + dxn/n*10, sy + dyn/n*10          # marker just outside shore
    cfg = lab_cfg[name]
    # fixed label displacement (reference-map style), clamped to viewBox
    lx,ly = ax + cfg['lx_n'][0], ay + cfg['lx_n'][1]
    lx = max(58, min(930, lx)); ly = max(66, min(600, ly))
    fr = name in ('Évian','Thonon')
    color = '#d9b49a' if fr else '#c8d6d9'
    labels.append(f'''<g><circle cx="{ax:.0f}" cy="{ay:.0f}" r="7" fill="#5fb760"/>'''
      f'''<circle class="stn-pulse" cx="{ax:.0f}" cy="{ay:.0f}" r="12" fill="none" stroke="#5fb760" stroke-opacity=".35"/>'''
      f'''<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="{cfg['anchor']}" font-size="17" font-weight="600" fill="{color}" font-family="Space Grotesk,Inter,sans-serif">{name}</text></g>''')
    print(f'{name}: marker=({ax:.0f},{ay:.0f}) label=({lx:.0f},{ly:.0f}) distance_to_shore_snapped={d:.0f}')

shore_d_path = None
# Closed path with midpoint quadratic smoothing
def smooth_closed(p):
    n=len(p)
    d=f'M {(p[0][0]+p[-1][0])/2:.1f},{(p[0][1]+p[-1][1])/2:.1f}'
    for i in range(n):
        a,b = p[i], p[(i+1)%n]
        d+=f' Q {a[0]:.1f},{a[1]:.1f} {(a[0]+b[0])/2:.1f},{(a[1]+b[1])/2:.1f}'
    return d+' Z'

shore_d = smooth_closed(pts)
# Trace OUTSIDE the lake: dense resample -> outward normal offset -> verify strict
# point-in-polygon outside status; smooth curve via polyline of offset points.
def point_in_poly(px, py, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside

# Dense shoreline (use ALL OSM ring points, not the 180 sample, for accurate normals)
ring_xy_all = []
for lon,lat in ring:
    x,y = xy(lon,lat)
    x,y = x+tx, y+ty
    ring_xy_all.append((x,y))

# true high-res lake polygon (for containment checks)
lake = ring_xy_all[::2]

# reduce very dense ring for speed but keep good fidelity: take every 3rd point
dense = ring_xy_all[::3]
nd = len(dense)
trace_pts = []
for i,(x,y) in enumerate(dense):
    a, b = dense[(i-1) % nd], dense[(i+1) % nd]
    tx2, ty2 = b[0]-a[0], b[1]-a[1]
    n2 = math.hypot(tx2,ty2) or 1
    nx, ny = -ty2/n2, tx2/n2
    # outward = away from lake centroid
    dxn = x - sum(p[0] for p in dense)/nd
    dyn = y - sum(p[1] for p in dense)/nd
    if nx*dxn + ny*dyn < 0:
        nx, ny = -nx, -ny
    placed = None
    for k in (30, 24, 18, 12, 8, 5):
        ox, oy = x - nx*k, y - ny*k   # NEGATIVE = offset INWARD (lake interior), 2 versions back
        if point_in_poly(ox, oy, pts):
            placed = (ox, oy)
            break
    if placed: trace_pts.append(placed)

# SINGLE polyline through the offset points (no Q smoothing — smoothing made the
# curve dip outside-page errors at concavities). Dense points keep it visually smooth.
trace_d = 'M ' + ' L '.join(f'{x:.1f},{y:.1f}' for x,y in trace_pts) + ' Z'
trace_pts_ = [tuple(map(float, p)) for p in trace_pts]

svg = f'''<svg viewBox="0 0 1000 620" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Carte animée du tracé LémanLoop autour du lac Léman">
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
  <path id="lakeShape" d="{shore_d}" fill="url(#lakeG)" stroke="#8fd3c8" stroke-opacity=".45" stroke-width="2"/>
  {''.join(labels)}
</svg>'''

path='/home/hermes/github/lemanloop/index.html'
html=open(path).read()
new='<div class="map-visual">'+svg+'</div>'
m_start=html.index('<div class="map-visual">')
m_end=html.index('<div class="map-legend">')
html=html[:m_start]+new+'\n    '+html[m_end:]
open(path,'w').write(html)
print("Injected. size:",len(html))
