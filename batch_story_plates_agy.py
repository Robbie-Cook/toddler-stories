#!/usr/bin/env python3
"""Generate story plates via agy/nano banana. Usage: python3 batch_story_plates_agy.py [name ...]
Run with /home/robbie/.venvs/nanobanana/bin/python3 (PIL). Existing PNGs >100KB are skipped."""
import json, os, subprocess, sys
HOME = "/home/robbie/.hermes/profiles/hermes2/home"
AGY = HOME + "/.local/bin/agy"
MODEL = "gemini-3.8-flash-high"
WORKDIR = "/tmp/story-plates"
IMG_DIR = "/home/robbie/projects/toddler-stories/img"
STYLE = ("Soft watercolor children's book illustration, warm golden light, "
         "gentle storybook ink outlines, wide 16:9 landscape format.")
NOTEXT = " No text, letters or writing anywhere in the image."
PLATES = {
 "story-11": "A tall tower of twenty plump mattresses and feather eiderdowns piled high in a castle bedchamber, a tiny green pea resting on the very bottom beneath them, a little wooden ladder leaning against the pile",
 "story-11-2": "A young princess in a nightgown tossing and turning on an enormous tall bed of piled mattresses, unable to sleep, rain and lightning at the castle window on a stormy night, candlelight glowing",
 "story-11-3": "A happy prince and princess in royal wedding clothes celebrating outside a castle with cheering villagers, flower petals in the air, sunny day",
 "story-12": "A vain emperor in a grand procession walking down a main street under a golden canopy, townspeople watching from both sides, a medieval town with bunting, sunny day",
 "story-12-2": "Two sly weavers working at empty wooden looms in a workshop while an old minister in robes peers in with spectacles, looking puzzled, warm light through the window",
 "story-12-3": "A small child in the crowd pointing up at the emperor in a grand parade, crowd laughing and gasping, the emperor wearing a long white undershirt and looking embarrassed, gentle and funny, not indecent",
 "story-13": "A giant green beanstalk reaching up through the clouds to a huge castle in the sky at the top, a small cottage and garden at its foot, blue sky",
 "story-13-2": "A young boy Jack climbing a thick leafy beanstalk high above the countryside, fields and cottages tiny below, clouds around him, warm golden light",
 "story-13-3": "Jack at the base of the beanstalk chopping it with an axe while a big friendly-looking cartoon giant tumbles down through the clouds, his mother watching from the cottage doorway",
 "story-14": "Two tiny elves with pointed hats working at a shoemaker's wooden bench by candlelight, stitching little leather shoes, a cozy cobbler's workshop at night",
 "story-14-2": "An old shoemaker and his wife peeping out from behind a rack of hanging clothes in a cozy workshop at midnight, watching two tiny elves at the bench by candlelight",
 "story-14-3": "Two little elves dancing joyfully out of a cobbler's shop door wearing tiny new coats and boots, the shoemaker and his wife waving happily, morning light, snowy cobbled street",
 "story-15": "A golden ball tumbling into a deep forest spring with a green frog watching from a lily pad, a young princess in a gown at the edge of the water, dappled forest light",
 "story-15-2": "A friendly green frog sitting at a royal dining table beside a princess's golden dinner plate, a king and the princess looking on, warm candlelit castle dining hall",
 "story-15-3": "A handsome young prince with kind eyes in royal clothes standing beside a princess in a castle garden, a few sparkles in the air, a golden carriage waiting, warm light",
 "story-4-2": "The tall-eared brown hare sprinting far ahead along a winding country racecourse through green meadows, dust kicking up behind him, a small slow tortoise visible tiny and far behind in the distance, sunny sky with plain clouds",
 "story-5-3": "A sly orange fox swimming across a wide river with a little gingerbread man cookie riding on his nose, the gingerbread man with icing buttons and a worried smile, riverbanks with reeds, warm light",
 "story-6-2": "A big grey wolf wearing a frilly white nightcap and little spectacles lying in grandmother's cozy bed with the quilt pulled up to his chin, sharp teeth showing in a sly grin, a small cottage bedroom with a window, a little girl in a red hooded cape standing at the bedside",
 "story-6-3": "A kind huntsman with an axe and green coat standing in a cottage bedroom beside a big grey wolf lying fast asleep on the floor, freeing a little girl in a red hooded cape and her old grandmother in a shawl who are climbing out, the huntsman helping them, warm lamplight",
 "story-7-2": "A small young billy goat, the smallest of the three, trip-trapping carefully across a wooden plank bridge over a rushing stream, green meadow beyond, a hint of a grumpy troll's eyes peeking from beneath the bridge, sunny day",
 "story-7-3": "A huge big billy goat with great curved horns standing bravely on a wooden bridge facing a hulking grumpy green troll with a lumpy nose who rises from beneath, the goat lowering his horns to charge, rocky stream below",
 "story-8-3": "A sly red fox with a bushy tail leading a line of a little hen, a duck, a goose and a turkey along a forest path toward the dark mouth of his den in a hillside, the fox looking back with a sly smile, the animals trusting and following, dusk light",
 "story-9-2": "A group of villagers, men and women with sticks and pitchforks, running up a green hillside toward a flock of sheep, a young shepherd boy on the hilltop waving his arms and shouting, village in the valley below, afternoon light",
 "story-9-3": "A big grey wolf leaping in among a flock of frightened sheep scattering in every direction across a hillside at dusk, a young shepherd boy on the hill looking terrified, alone with nobody else near, dramatic but storybook-gentle",
 "story-10-2": "A small grey ugly duckling alone and shivering on a frozen pond in winter, ice and snow all around, bare trees, snowflakes falling, cold blue light, the duckling looking sad and tiny",
 "story-10-3": "A lovely young white swan, the former ugly duckling, gazing at its own beautiful reflection in a clear pond at sunrise, surrounded by graceful swans gliding past, golden pink dawn light, reeds and water lilies",
}
SIZES = {}  # name -> (w,h)
def size_for(n): return (1024, 572)

def gen(name):
    out = f"{WORKDIR}/{name}.png"
    if os.path.exists(out) and os.path.getsize(out) > 100_000: return True
    prompt = (f"Generate an image: {PLATES[name]}. {STYLE}{NOTEXT} "
              f"Save the generated image to {out} using your image generation tool.")
    env = dict(os.environ, HOME=HOME)
    try:
        r = subprocess.run([AGY, "-p", prompt, "--model", MODEL, "--print-timeout", "6m",
            "--dangerously-skip-permissions", "--output-format", "json"],
            capture_output=True, text=True, timeout=420, env=env)
    except subprocess.TimeoutExpired:
        print(name, "TIMEOUT"); return False
    size = os.path.getsize(out) if os.path.exists(out) else 0
    print(name, "size", size, (r.stdout or "")[-200:].replace("\n", " "), flush=True)
    return size > 100_000

def convert(name):
    from PIL import Image
    W, H = size_for(name)
    im = Image.open(f"{WORKDIR}/{name}.png").convert("RGB")
    w, h = im.size; t = W / H
    if w / h > t:
        nw = int(h * t); l = (w - nw) // 2; im = im.crop((l, 0, l + nw, h))
    elif w / h < t:
        nh = int(w / t); tp = (h - nh) // 2; im = im.crop((0, tp, w, tp + nh))
    im = im.resize((W, H), Image.LANCZOS)
    im.save(f"{IMG_DIR}/{name}.webp", "WEBP", quality=85, method=6)

if __name__ == "__main__":
    os.makedirs(WORKDIR, exist_ok=True)
    names = sys.argv[1:] or list(PLATES)
    failed = []
    for n in names:
        ok = False
        for attempt in range(3):
            if gen(n): ok = True; break
        if ok: convert(n)
        else: failed.append(n)
    print("FAILED:", failed)
