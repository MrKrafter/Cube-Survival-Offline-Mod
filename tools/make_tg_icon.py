"""Draw cubefix/telegram.png, the Settings button icon that replaces the Facebook one.
White disc with a blue paper plane: a blue disc gets lost on the blue button.
usage: python make_tg_icon.py   (needs Pillow)"""
import os
from PIL import Image, ImageDraw

SIZE = 128
SS = 4  # supersampling
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cubefix', 'telegram.png')
# paper plane on a 240-unit grid
PLANE = [(50, 117), (178, 66), (157, 175), (119, 147), (99, 167), (96, 139), (152, 89), (88, 131)]
FOLD = [(96, 139), (152, 89), (104, 141)]


def main():
    n = SIZE * SS
    k = n / 240
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, n - 1, n - 1], fill=(255, 255, 255, 255))
    plane = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plane)
    for y in range(n):  # top-to-bottom gradient like the app icon
        t = y / n
        pd.line([(0, y), (n, y)], fill=(int(42 + (34 - 42) * t), int(171 + (158 - 171) * t), int(238 + (217 - 238) * t), 255))
    mask = Image.new('L', (n, n), 0)
    ImageDraw.Draw(mask).polygon([(x * k, y * k) for x, y in PLANE], fill=255)
    img.paste(plane, (0, 0), mask)
    d.polygon([(x * k, y * k) for x, y in FOLD], fill=(20, 120, 180, 255))
    img.resize((SIZE, SIZE), Image.LANCZOS).save(OUT, optimize=True)
    print(OUT, os.path.getsize(OUT))


if __name__ == '__main__':
    main()
