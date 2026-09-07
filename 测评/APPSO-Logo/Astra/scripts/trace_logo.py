"""Extract the supplied logo contours. Original PNG is never modified."""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'appso-logo.png'
data = source.read_bytes()
im = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
mask = cv2.inRange(im, np.array([210, 210, 210]), np.array([255, 255, 255]))
contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
shapes = []
for i, contour in enumerate(contours):
    if hierarchy[0][i][3] != -1 or cv2.contourArea(contour) < 500:
        continue
    def points(c):
        return cv2.approxPolyDP(c, 0.65, True).reshape(-1, 2).tolist()
    holes = []
    child = hierarchy[0][i][2]
    while child != -1:
        holes.append(points(contours[child]))
        child = hierarchy[0][child][0]
    x, y, w, h = cv2.boundingRect(contour)
    shapes.append(dict(outline=points(contour), holes=holes, bounds=[x,y,w,h]))
shapes.sort(key=lambda s: s['bounds'][0])
for s, name in zip(shapes, ['dot', 'A', 'P1', 'P2', 'S', 'O']):
    s['name'] = name
result = dict(width=im.shape[1], height=im.shape[0], source='appso-logo.png',
              sha256=hashlib.sha256(data).hexdigest(), shapes=shapes)
(ROOT / 'src' / 'logo-contours.json').write_text(json.dumps(result, separators=(',', ':')), encoding='utf-8')
print('Extracted:', [(s['name'], len(s['outline']), len(s['holes'])) for s in shapes])
