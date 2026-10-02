#!/usr/bin/env python3
"""
Batch generator for the 20 song plates (img/song-1..20.webp) via the
Antigravity CLI (`agy`), whose agent can drive Google's Nano Banana
image generation. This path is used because the Playwright-Firefox
gemini.google.com profile (batch_songs.py) is currently signed out of
Google and needs a manual VNC re-login before it works again.

Each song = one `agy -p` run (~45-90s). Re-runnable: existing PNGs over
100KB are skipped, so failures can be retried cheaply.

Run with the nanobanana venv python (has PIL for the convert step):
  SONGS_CONVERT=1 /home/robbie/.venvs/nanobanana/bin/python3 batch_songs_agy.py
"""
import json
import os
import subprocess
import sys

HOME = "/home/robbie/.hermes/profiles/hermes2/home"
AGY = HOME + "/.local/bin/agy"
MODEL = "gemini-3.8-flash-medium"
WORKDIR = "/tmp/song-plates"
IMG_DIR = "/home/robbie/projects/toddler-stories/img"

STYLE = ("Soft watercolor children's book illustration, warm golden light, "
         "gentle storybook ink outlines, wide 16:9 landscape format.")

# (file base name, scene) — song-N order must match the SONGS array in index.html
SONGS = [
    ("song-1",  "A sleepy baby in a wooden cot by an open cottage window at night, looking up at a large friendly crescent moon and twinkling golden stars over quiet rooftops, deep blue night sky with warm golden starlight"),
    ("song-2",  "A friendly black sheep standing on a country lane with three bulging white wool sacks beside it, rolling green hills and a little village in the distance, warm afternoon light"),
    ("song-3",  "A cheerful little round spider with a friendly smiling face and eight legs climbing up a rain spout beside a cottage window, gentle raindrops falling and a bright rainbow arcing over a garden of flowers below, the spider must clearly be a spider, not a bee or any other insect"),
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


def generate_all():
    os.makedirs(WORKDIR, exist_ok=True)
    env = dict(os.environ, HOME=HOME)
    ok, failed = 0, []
    for i, (name, scene) in enumerate(SONGS):
        out = os.path.join(WORKDIR, f"{name}.png")
        print(f"\n{'=' * 60}", flush=True)
        if os.path.exists(out) and os.path.getsize(out) > 100_000:
            print(f"[{i + 1}/{len(SONGS)}] {name}: PNG already exists, skipping")
            ok += 1
            continue
        prompt = (f"Generate an image: {scene}. {STYLE} "
                  f"Save the generated image to {out} using your image generation tool.")
        print(f"[{i + 1}/{len(SONGS)}] {name}: agy run starting...")
        try:
            r = subprocess.run(
                [AGY, "-p", prompt, "--model", MODEL, "--print-timeout", "6m",
                 "--dangerously-skip-permissions", "--output-format", "json"],
                capture_output=True, text=True, timeout=420, env=env,
            )
            status = "?"
            try:
                payload = json.loads(r.stdout.strip().splitlines()[-1])
                status = payload.get("status", "?")
            except Exception:
                pass
            size = os.path.getsize(out) if os.path.exists(out) else 0
            good = status == "SUCCESS" and size > 100_000
            print(f"  status={status} file={'yes ' + str(size) + 'B' if size else 'MISSING'}")
            if good:
                ok += 1
            else:
                failed.append(name)
                print("  STDOUT tail:", (r.stdout or "")[-300:])
                print("  STDERR tail:", (r.stderr or "")[-300:])
        except subprocess.TimeoutExpired:
            failed.append(name)
            print(f"  TIMEOUT after 420s")
    print(f"\nGenerated {ok}/{len(SONGS)}")
    if failed:
        print("FAILED:", ", ".join(failed))
    return failed


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
    failed = generate_all()
    if os.environ.get("SONGS_CONVERT", "") == "1":
        print("\n[CONVERT]")
        convert()
    print("PENDING_CONVERSION" if failed else "ALL_DONE")
