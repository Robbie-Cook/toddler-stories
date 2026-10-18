#!/usr/bin/env python3
"""
Generate the Free Baby Stories iOS app icon and launch image.

Redrawn — not upscaled — from the storybook's existing apple-touch-icon, in
the site's own tokens: cream paper, ink outline, a rust-red left page and a
forest-green right page, with a gold crescent moon and two gold stars.

The mark is a proper open-book silhouette (pages pinched at the fold on both
the head and the tail) rather than a rounded rectangle, so it still reads as
a book at 60px on a home screen.

No text on the icon by design.

Run:  python3 scripts/generate-assets.py
"""
import math
from pathlib import Path

from playwright.sync_api import sync_playwright

PAPER = "#FBF4E6"        # --paper
PAPER_CARD = "#FFFBF1"   # --paper-card
PAPER_DEEP = "#EAD9BC"   # --paper-deep
INK = "#2C1810"          # --ink
RED = "#B23A2E"          # --red
FOREST = "#2F5D4E"       # --forest
GOLD = "#D9A441"         # --gold

# Open book, in a 1024 coordinate space. Head and tail both pinch inward at
# x=512 so the silhouette reads as two pages rather than one block.
FOLD_X = 512
BOOK = (
    "M 168 476 Q 168 452 192 450 "
    "C 310 438 430 470 512 522 "
    "C 594 470 714 438 832 450 "
    "Q 856 452 856 476 "
    "L 856 748 Q 856 772 832 774 "
    "C 714 762 594 794 512 846 "
    "C 430 794 310 762 192 774 "
    "Q 168 772 168 748 Z"
)
BOOK_STROKE = 46

# Centroid of the artwork, used so the motif is optically centred on both the
# icon and (at a smaller scale) the launch screen.
CONTENT_CX, CONTENT_CY = 512, 508


def star(cx: float, cy: float, outer: float, inner_ratio: float = 0.46) -> str:
    """A chunky five-point star: kid-friendly, still legible at 40px."""
    inner = outer * inner_ratio
    pts = []
    for i in range(10):
        r = outer if i % 2 == 0 else inner
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{GOLD}"/>'


def artwork() -> str:
    """The motif, drawn once in the 1024 coordinate space."""
    moon_cx, moon_cy, moon_r = 752, 250, 108
    return f"""
<defs>
  <clipPath id="rightHalf">
    <rect x="{FOLD_X}" y="0" width="{1024 - FOLD_X}" height="1024"/>
  </clipPath>
  <mask id="crescent">
    <rect x="0" y="0" width="1024" height="1024" fill="#000"/>
    <circle cx="{moon_cx}" cy="{moon_cy}" r="{moon_r}" fill="#fff"/>
    <circle cx="{moon_cx + moon_r * 0.40:.0f}" cy="{moon_cy - moon_r * 0.34:.0f}"
            r="{moon_r * 0.95:.0f}" fill="#000"/>
  </mask>
</defs>

<!-- the book: red left page, green right page, ink outline via paint-order -->
<path d="{BOOK}" fill="{RED}" stroke="{INK}" stroke-width="{BOOK_STROKE}"
      stroke-linejoin="round" paint-order="stroke"/>
<g clip-path="url(#rightHalf)">
  <path d="{BOOK}" fill="{FOREST}" stroke="{INK}" stroke-width="{BOOK_STROKE}"
        stroke-linejoin="round" paint-order="stroke"/>
</g>
<path d="M {FOLD_X} 524 L {FOLD_X} 846" stroke="{INK}"
      stroke-width="{BOOK_STROKE * 0.86:.0f}" stroke-linecap="round"/>

<!-- night sky -->
<rect x="0" y="0" width="1024" height="1024" fill="{GOLD}" mask="url(#crescent)"/>
{star(268, 268, 78)}
{star(408, 382, 42)}
"""


def page(size: int, inner: str) -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  html,body{{margin:0;padding:0;width:{size}px;height:{size}px;overflow:hidden}}
  .bg{{position:absolute;inset:0;background:radial-gradient(circle at 50% 34%,
        {PAPER_CARD} 0%, {PAPER} 50%, {PAPER_DEEP} 100%)}}
  svg{{position:absolute;inset:0;width:{size}px;height:{size}px}}
</style></head>
<body><div class="bg"></div>
  <svg viewBox="0 0 1024 1024">{inner}</svg></body></html>"""


def scaled(scale: float) -> str:
    """Artwork scaled about its own centroid."""
    return (f'<g transform="translate({CONTENT_CX} {CONTENT_CY}) scale({scale}) '
            f'translate({-CONTENT_CX} {-CONTENT_CY})">{artwork()}</g>')


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    appicon = root / "ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png"
    splash_dir = root / "ios/App/App/Assets.xcassets/Splash.imageset"
    appicon.parent.mkdir(parents=True, exist_ok=True)
    splash_dir.mkdir(parents=True, exist_ok=True)

    jobs = [
        # Home-screen icon: motif fills the square, snug inside Apple's inset.
        (appicon, 1024, page(1024, scaled(1.0))),
        # Launch image: same motif, quieter, breathing on the paper.
        (splash_dir / "splash-2732x2732.png", 2732, page(2732, scaled(0.52))),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(device_scale_factor=1)
        pg = ctx.new_page()
        for path, size, html in jobs:
            pg.set_viewport_size({"width": size, "height": size})
            pg.set_content(html, wait_until="load")
            pg.screenshot(path=str(path), omit_background=False)
            print(f"wrote {path} ({path.stat().st_size:,} bytes)")
        ctx.close()
        browser.close()

    src = splash_dir / "splash-2732x2732.png"
    for name in ("splash-2732x2732-1.png", "splash-2732x2732-2.png"):
        dst = splash_dir / name
        dst.write_bytes(src.read_bytes())
        print(f"wrote {dst} ({dst.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
