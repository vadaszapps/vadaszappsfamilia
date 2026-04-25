#!/usr/bin/env python3
"""
Camper Vadász PWA icon generator - Windows compatible (Pillow)
Run: pip install pillow && python3 gen_icons.py
"""
import os
from PIL import Image, ImageDraw

os.makedirs('icons', exist_ok=True)

def generate_icon(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size

    # Background
    d.rounded_rectangle([0, 0, s-1, s-1], radius=int(s*0.22), fill=(26, 58, 21, 255))

    # Camper body
    d.rounded_rectangle([int(s*0.15), int(s*0.35), int(s*0.88), int(s*0.65)],
                        radius=int(s*0.06), fill=(200, 169, 110, 255))

    # Cab front
    d.rounded_rectangle([int(s*0.62), int(s*0.38), int(s*0.88), int(s*0.65)],
                        radius=int(s*0.05), fill=(180, 140, 80, 255))

    # Windows
    d.rounded_rectangle([int(s*0.20), int(s*0.40), int(s*0.42), int(s*0.55)],
                        radius=int(s*0.03), fill=(168, 207, 224, 255))
    d.rounded_rectangle([int(s*0.46), int(s*0.40), int(s*0.58), int(s*0.55)],
                        radius=int(s*0.03), fill=(168, 207, 224, 255))
    d.rounded_rectangle([int(s*0.65), int(s*0.41), int(s*0.85), int(s*0.55)],
                        radius=int(s*0.03), fill=(168, 207, 224, 200))

    # Wheels
    for wx in [int(s*0.28), int(s*0.72)]:
        wy = int(s*0.64)
        wr = int(s*0.10)
        d.ellipse([wx-wr, wy-wr, wx+wr, wy+wr], fill=(26, 58, 21, 255))
        d.ellipse([wx-int(wr*0.5), wy-int(wr*0.5), wx+int(wr*0.5), wy+int(wr*0.5)], fill=(107, 76, 42, 255))

    # Tree left
    d.polygon([(int(s*0.06), int(s*0.55)), (int(s*0.13), int(s*0.32)), (int(s*0.20), int(s*0.55))],
              fill=(74, 138, 66, 255))
    d.rectangle([int(s*0.12), int(s*0.55), int(s*0.14), int(s*0.60)], fill=(107, 76, 42, 255))

    # Ground strip
    d.rounded_rectangle([int(s*0.12), int(s*0.62), int(s*0.88), int(s*0.68)],
                        radius=int(s*0.02), fill=(45, 90, 39, 255))

    return img

for size in [192, 512]:
    img = generate_icon(size)
    img.save(f'icons/icon-{size}.png')
    print(f'✅ icons/icon-{size}.png generálva')

print('🎉 Kész!')
