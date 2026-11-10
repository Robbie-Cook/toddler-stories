#!/usr/bin/env python3
"""Generate art for stories 16-25 (cinderella..beauty-and-the-beast) via agy, house style from a reference plate.
Run with /home/robbie/.venvs/nanobanana/bin/python3 batch_story_plates_16_25.py [name ...]  (parallel: 3)"""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import batch_story_plates_agy as B
REF = "/home/robbie/projects/toddler-stories/img/story-3.webp"
P = {
 "story-16": "A pretty girl in a patched dress sitting by a hearth of warm embers with a gentle grey cat, a pumpkin carriage with white mice just visible through the window behind her, a sparkling fairy godmother with a wand",
 "story-16-2": "Cinderella in a shimmering pale-gold ball gown dancing with a kind prince in a grand candlelit ballroom, a large clock on the wall nearly at midnight, other guests twirling softly",
 "story-16-3": "The prince kneeling to fit a small glass slipper on Cinderella's foot in a humble cottage kitchen, two surprised stepsisters watching, warm morning light",
 "story-17": "A sleeping princess lying peacefully on a canopied bed in a tower room, a spinning wheel beside her, a thick hedge of thorns and pink roses climbing the castle outside the window, soft magical dusk light",
 "story-17-2": "A tiny castle with sleepy sleeping people: a cook dozing at the hearth, a king nodding on his throne, dogs and doves asleep, drifting golden dust in the air",
 "story-17-3": "A brave young prince on a white horse riding through parting thorn bushes covered in white roses toward a castle on a hill, morning sunlight",
 "story-18": "A boy and a girl, brother and sister, walking hand in hand along a moonlit forest path scattering shining white pebbles behind them, tall dark friendly trees, a big round moon",
 "story-18-2": "Two children standing in front of a cottage made of gingerbread, frosting and candy with gumdrop windows in the middle of the forest, an old woman with a cane smiling in the doorway",
 "story-18-3": "A brother and sister hugging their father at the door of a humble cottage in a sunny forest clearing, a white duck and a small bag of jewels beside them, joyful reunion",
 "story-19": "A girl with very long golden hair leaning from the window of a tall stone tower in a forest, hair streaming down to the ground, a bright sky, a bird flying by",
 "story-19-2": "A young prince in a green cloak standing at the foot of a tall stone tower in a forest at sunset, looking up as long golden hair hangs down the wall like a rope, an old enchantress approaching on the path",
 "story-19-3": "A prince and a young woman with long golden hair reunited in a quiet green meadow, a pair of small twins playing nearby, tears of joy, soft golden light, gentle healing",
 "story-20": "A miller's daughter sitting at a spinning wheel in a bare straw-filled room, golden thread glowing on the spindle, a tiny wrinkled man in a pointed hat at her side, candlelight",
 "story-20-2": "A tiny wrinkled man in a pointed hat dancing around a small crackling fire deep in the forest at night, singing, a hidden messenger peeking from behind a tree",
 "story-20-3": "A queen with a baby in a castle hall pointing at a tiny angry man in a pointed hat who stamps his foot through the floor boards, warm lamps, storybook-gentle",
 "story-21": "A piper in a long coat of red and yellow patches playing a pipe in a medieval town square, a stream of rats following him, townsfolk with a mayor watching from windows, afternoon light",
 "story-21-2": "A piper walking over a hill playing a pipe with a line of happy children dancing and following him, a mountain opening in the distance with golden light, townsfolk waving sadly behind",
 "story-21-3": "A single little lame boy sitting alone on the edge of a green hillside looking at a mountain, wildflowers in the grass, the town at his back, wistful and golden-hour",
 "story-22": "A young mermaid with long red hair and a green tail resting her arms on a rock in the sea at sunset, looking at a distant ship with lanterns, silver fish around her",
 "story-22-2": "A mermaid and a sea-witch in a coral cave with glowing jars of potion, shells and seaweed, the mermaid holding a glittering bottle, underwater blue-green light, storybook-gentle",
 "story-22-3": "A shining spirit of the air, with soft rainbow-coloured wings, rising up from sea foam into pink and gold clouds at sunrise over a calm sea, a ship in the distance",
 "story-23": "A small brave tailor sitting cross-legged by a window with a needle and bright cloth, swatting seven flies on a slice of bread with jam, a belt sewn with the words seven at one blow stitched as pictures only, no letters",
 "story-23-2": "A small tailor sitting calmly beside a big gentle-looking giant, the tailor squeezing a soft white cheese in his hand while the giant squeezes a stone, forest clearing, warm daylight",
 "story-23-3": "A small tailor wearing a golden crown and a royal cloak standing next to a smiling princess and a king in a castle courtyard, cheering villagers, sunny day",
 "story-24": "A tiny girl no bigger than a thumb asleep in a walnut-shell cradle with a violet-petal blanket, on a polished table beside a flower pot, a window with morning light",
 "story-24-2": "A tiny girl tucking a warm blanket of woven hay around a sleeping swallow lying in a snowy burrow under the ground, a gentle winter glow, small underground tunnel",
 "story-24-3": "A tiny girl sitting on the back of a swallow flying high over green hills, rivers and blue mountains toward a warm south, golden light, flowers below",
 "story-25": "A single glowing red rose in a candlelit garden of an enchanted castle at dusk, a kind young woman in a simple dress reaching for it, a gentle shadowy figure watching from the archway",
 "story-25-2": "A kind young woman in a gown and a gentle furry beast in a fine coat sitting together at a candlelit table in a great hall, shared supper, soft golden light, warm and friendly",
 "story-25-3": "A handsome prince in royal clothes and a young woman in a gown holding hands in a castle garden full of roses, magical sparkles in the air, morning light",
}
B.PLATES.update(P)
STYLE = ("Soft watercolor children's book illustration with gentle ink outlines and a warm muted golden-hour palette, "
         "wide 16:9 landscape, storybook composition. Match the style of the reference illustration at " + REF +
         " (view it first and match its brushwork, outlines and palette exactly).")
B.STYLE = STYLE
def one(n):
    ok = any(B.gen(n) for _ in range(3))
    if ok: B.convert(n)
    return n, ok
if __name__ == "__main__":
    os.makedirs(B.WORKDIR, exist_ok=True)
    names = sys.argv[1:] or list(P)
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(one, names))
    print("FAILED:", [n for n, ok in res if not ok]); print("DONE", len(res))
