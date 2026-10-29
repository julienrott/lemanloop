# Reference labels from user's reference map (Lac Léman, Alamy stock):
# Key positions on the user's reference:
#   Genève: bottom-left tip, label to LEFT of point
#   Nyon: west shore (middle of Petit Lac, west side), label to LEFT
#   Lausanne: upper-middle (north-east of centre), label RIGHT
#   Vevey: upper-right area of the croissant, label RIGHT
#   Montreux: right, just BELOW Vevey, label RIGHT
#   Évian: bottom-middle-right (south shore), label BELOW
#   Thonon: bottom-middle-left (south shore), label BELOW
# All markers sit ON the shoreline, labels OUTSIDE the lake.

GEO = {
    'Genève':  dict(marker_px=(140, 560), label_txt='Genève',  anchor='end',   lx_off=( -18,   8)),
    'Nyon':    dict(marker_px=(296, 455), label_txt='Nyon',    anchor='end',   lx_off=( -18,   6)),
    'Lausanne':dict(marker_px=(778, 215), label_txt='Lausanne',anchor='start', lx_off=( +18,   6)),
    'Vevey':   dict(marker_px=(895, 205), label_txt='Vevey',   anchor='start', lx_off=( +18,   2)),
    'Montreux':dict(marker_px=(935, 260), label_txt='Montreux',anchor='start', lx_off=( +18,  10)),
    'Évian':   dict(marker_px=(700, 420), label_txt='Évian',   anchor='middle',lx_off=(  0,  +30)),
    'Thonon':  dict(marker_px=(508, 470), label_txt='Thonon',  anchor='middle',lx_off=( -6,  +32)),
}
