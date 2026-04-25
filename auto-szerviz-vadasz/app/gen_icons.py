#!/usr/bin/env python3
"""Autószerviz Vadász icon generator - pip install pillow && python3 gen_icons.py"""
import os
from PIL import Image, ImageDraw

os.makedirs('icons', exist_ok=True)

def generate_icon(size):
    img = Image.new('RGBA', (size, size), (0,0,0,0))
    d = ImageDraw.Draw(img)
    s = size
    # Background
    d.rounded_rectangle([0,0,s-1,s-1], radius=int(s*0.22), fill=(13,13,13,255))
    # Orange accent bar top
    d.rounded_rectangle([int(s*0.1),int(s*0.08),int(s*0.9),int(s*0.18)], radius=4, fill=(255,107,0,255))
    # Wrench body
    cx, cy = s//2, s//2+int(s*0.05)
    wr = int(s*0.28)
    d.ellipse([cx-wr,cy-wr,cx+wr,cy+wr], fill=(46,46,46,255))
    d.ellipse([cx-int(wr*0.55),cy-int(wr*0.55),cx+int(wr*0.55),cy+int(wr*0.55)], fill=(13,13,13,255))
    # Orange gear dots
    for i in range(8):
        import math
        angle = i * math.pi / 4
        dx = int(wr*0.85 * math.cos(angle))
        dy = int(wr*0.85 * math.sin(angle))
        gr = int(s*0.05)
        d.ellipse([cx+dx-gr,cy+dy-gr,cx+dx+gr,cy+dy+gr], fill=(255,107,0,255))
    # Center dot
    cr = int(s*0.08)
    d.ellipse([cx-cr,cy-cr,cx+cr,cy+cr], fill=(255,107,0,255))
    return img

for size in [192, 512]:
    generate_icon(size).save(f'icons/icon-{size}.png')
    print(f'✅ icons/icon-{size}.png')
print('🎉 Kész!')
