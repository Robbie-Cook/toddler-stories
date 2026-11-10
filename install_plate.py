import sys
from PIL import Image
src, name = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
w, h = im.size
th = round(w * 572 / 1024)
if th < h:
    t = (h - th) // 2
    im = im.crop((0, t, w, t + th))
im = im.resize((1024, 572), Image.Resampling.LANCZOS)
im.save(f"img/{name}.webp", "WEBP", quality=82)
im.save(f"img/{name}.png", optimize=True)
print(name, "installed")
