#!/usr/bin/env python3
"""Inject the user-provided reference SVG map (map.svg) into index.html."""
SVG_PATH = '/home/hermes/github/lemanloop/assets/map.svg'
HTML_PATH = '/home/hermes/github/lemanloop/index.html'

svg = open(SVG_PATH).read().strip()
new_block = '<div class="map-visual">' + svg + '</div>'

html = open(HTML_PATH).read()
m_start = html.index('<div class="map-visual">')
m_end = html.index('<div class="map-legend">')
html = html[:m_start] + new_block + '\n    ' + html[m_end:]
open(HTML_PATH, 'w').write(html)
print('Injected user map. size:', len(html))
