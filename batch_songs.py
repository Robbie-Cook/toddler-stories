#!/usr/bin/env python3
"""
Batch generator for the 20 song plates (img/song-1..20.webp).

Same Playwright-Firefox + gemini.google.com flow as batch_generate.py, but:
  - uses the hermes profile-home ms-playwright cache (where firefox-1538 lives)
  - saves PNGs to /tmp song workdir, converts/crops to 1024x576 WEBP with PIL
  - prompts ask for a wide landscape composition so the 16:9 crop is kind

Run with the nanobanana venv python (has playwright):
  /home/robbie/.venvs/nanobanana/bin/python3 batch_songs.py
"""
import asyncio
import glob
import os
import subprocess
import sys

import batch_generate as bg  # reuses JS snippets, selectors, generate_one()

# The browsers cache lives under the hermes profile home (HOME is remapped there).
BROWSERS = "/home/robbie/.hermes/profiles/hermes2/home/.cache/ms-playwright"
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = BROWSERS
os.environ["DISPLAY"] = ":10"

WORKDIR = "/tmp/song-plates"
IMG_DIR = bg.IMG_DIR

STYLE = "soft watercolor children's book illustration, warm golden light, gentle storybook ink outlines, wide landscape composition"

# (file base name, scene)  ->  song-N order must match the SONGS array in index.html
SONGS = [
    ("song-1",  "A sleepy baby in a wooden cot by an open cottage window at night, looking up at a large friendly crescent moon and twinkling golden stars over quiet rooftops, deep blue night sky with warm golden starlight"),
    ("song-2",  "A friendly black sheep standing on a country lane with three bulging white wool sacks beside it, rolling green hills and a little village in the distance, warm afternoon light"),
    ("song-3",  "A cheerful little spider climbing up a rain spout beside a cottage window, gentle raindrops falling and a bright rainbow arcing over a garden of flowers below"),
    ("song-4",  "Two small children in a little wooden rowing boat drifting down a calm gentle stream under a weeping willow tree on a sunny summer day, ducks paddling alongside"),
    ("song-5",  "A jolly farmer in overalls and a straw hat standing by a red barn with a cow, a pig, a duck and a dog gathered around him in a green farmyard on a sunny day"),
    ("song-6",  "A smiling egg character in a little jacket sitting on a tall brick garden wall, with the king's horses and soldiers resting in a sunny flower meadow behind him"),
    ("song-7",  "A cheerful round-nosed city bus driving down a friendly town street, children waving from the windows, a small dog sitting beside the driver, trees and shops along the road"),
    ("song-8",  "A small grey mouse scampering down the face of a tall wooden grandfather clock in a cozy cottage hallway, warm lamplight, a chequered floor"),
    ("song-9",  "A little girl in a sunbonnet walking to a small red schoolhouse with a fluffy white lamb trotting faithfully behind her, spring flowers lining the path"),
    ("song-10", "A grand old stone bridge with towers crossing a wide river, little sailing boats passing beneath, children holding hands and dancing in a flowery meadow in the foreground, golden afternoon light"),
    ("song-11", "A boy and a girl in old-fashioned clothes climbing a grassy hill toward an old wooden well, carrying one big pail of water between them, blue sky with puffy clouds"),
    ("song-12", "A mother duck with five little ducklings waddling across rolling green hills toward a pond, one little duckling looking back over its shoulder, warm sunny day"),
    ("song-13", "A happy toddler standing on a rug in a sunny playroom giggling and touching the top of their head with both hands, toys and a big bright window around them"),
    ("song-14", "A woven wicker cradle hanging gently from the bough of a tall oak tree, soft wind stirring the leaves, first stars appearing in a dusky evening sky"),
    ("song-15", "Five cheerful little pigs in a row on a country road, one carrying a market basket and one waving goodbye, rolling green fields and a market town in the distance"),
    ("song-16", "A golden pie on a royal banquet table with blackbirds flying out of the crust, a surprised king in a crown and a queen at the table, grand candlelit castle hall"),
    ("song-17", "A little shepherdess in a pink bonnet holding a crook, looking over a flowery meadow while her fluffy white sheep come bounding home over the hill toward her"),
    ("song-18", "Ten teddy bears snuggled together in one big bed under a patchwork quilt, one bear tumbling over the edge of the mattress, moonlit bedroom with toys on the floor"),
    ("song-19", "A farmer and his wife leading a happy procession across a green valley, a child, a nurse, a cow, a dog, a cat and a mouse all walking in a friendly line with a wheel of cheese at the end"),
    ("song-20", "A little robin sheltering in a cozy barn doorway from falling snow, tucking its head under its wing, snowy fields and a frosted tree outside, warm golden lamplight glowing from the barn"),
]


async def run():
    from playwright.async_api import async_playwright

    for lf in [os.path.join(bg.PROFILE, ".parentlock"), os.path.join(bg.PROFILE, "lock"), bg.MUTEX_FILE]:
        if os.path.exists(lf):
            try:
                os.remove(lf)
            except OSError:
                pass

    firefox_paths = sorted(glob.glob(BROWSERS + "/firefox-*/firefox/firefox"))
    if not firefox_paths:
        print("[FATAL] No Playwright Firefox binary under " + BROWSERS)
        sys.exit(1)
    FIREFOX_PATH = firefox_paths[-1]
    print(f"Firefox: {FIREFOX_PATH}")
    os.makedirs(WORKDIR, exist_ok=True)

    async with async_playwright() as p:
        ctx = await p.firefox.launch_persistent_context(
            bg.PROFILE, headless=False,
            ignore_default_args=["--enable-automation"],
            firefox_user_prefs={"dom.webdriver.enabled": False},
            executable_path=FIREFOX_PATH,
        )
        await ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        print("\n[NAVIGATE] Loading Gemini...")
        await page.goto(bg.GEMINI_URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        await page.evaluate('''() => {
            document.querySelectorAll('.cdk-overlay-backdrop, .cdk-overlay-container, [role="dialog"]').forEach(el => {
                el.style.display = 'none';
            });
            document.querySelectorAll('button[aria-label*="Close"], button[aria-label*="close"]').forEach(btn => btn.click());
        }''')
        await page.wait_for_timeout(2000)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(1000)
        await page.evaluate('window.scrollTo(0, 100)')
        await page.wait_for_timeout(2000)

        pre_count = await page.evaluate(bg.JS_COUNT_GENERATED)
        print(f"  [COUNT] {pre_count} AI-generated images on page before any prompt\n")

        success = 0
        failed = []
        for i, (name, scene) in enumerate(SONGS):
            png_path = os.path.join(WORKDIR, f"{name}.png")
            prompt = f"{scene}, {STYLE}"
            print(f"\n{'=' * 60}")
            print(f"[{i + 1}/{len(SONGS)}] Generating: {name}")
            print(f"  Prompt: {prompt[:70]}...")

            ok = await bg.generate_one(page, pre_count, prompt, png_path)
            if ok:
                success += 1
                pre_count += 1
                print(f"  OK {name}.png saved")
            else:
                failed.append(name)
                print(f"  FAILED {name}")
                await page.screenshot(path=os.path.join(WORKDIR, f"{name}-fallback.png"))

            await page.wait_for_timeout(2000)

        await page.close()
        await ctx.close()

    print(f"\nGenerated {success}/{len(SONGS)}")
    if failed:
        print("FAILED:", ", ".join(failed))
    print("PENDING_CONVERSION")


def convert():
    """PNG -> 1024x576 center-cropped WEBP straight into the repo img/ dir."""
    from PIL import Image
    TARGET_W, TARGET_H = 1024, 576
    for name, _ in SONGS:
        png_path = os.path.join(WORKDIR, f"{name}.png")
        webp_path = os.path.join(IMG_DIR, f"{name}.webp")
        if not os.path.exists(png_path):
            print(f"  MISSING png: {name}")
            continue
        im = Image.open(png_path).convert("RGB")
        w, h = im.size
        target_ar = TARGET_W / TARGET_H
        ar = w / h
        if ar > target_ar:
            nw = int(h * target_ar)
            left = (w - nw) // 2
            im = im.crop((left, 0, left + nw, h))
        elif ar < target_ar:
            nh = int(w / target_ar)
            top = (h - nh) // 2
            im = im.crop((0, top, w, top + nh))
        if im.size != (TARGET_W, TARGET_H):
            im = im.resize((TARGET_W, TARGET_H), Image.LANCZOS)
        im.save(webp_path, "WEBP", quality=85, method=6)
        print(f"  [WEBP] {webp_path} {im.size} {os.path.getsize(webp_path)} bytes")


if __name__ == "__main__":
    asyncio.run(run())
    if "--convert" in sys.argv or os.environ.get("SONGS_CONVERT", "") == "1":
        convert()
