# Plates audit — 2026-10-14

## Task 1: new plates (agy / nano banana, `batch_story_plates_agy.py`, 1024x572 webp)
Generated (13): story-11, 11-2, 11-3, 12, 12-2, 12-3, 13, 13-2, 13-3, 14, 14-2, 14-3, 15-2.
**NOT generated (2): `story-15.webp` (Frog Prince cover) and `story-15-3.webp`.** agy returned
"quota/capacity" on 9 attempts (3 per file, plus a re-run). These files do not exist; the live site
returns the SPA HTML fallback for them and the Frog Prince card still shows the generic SVG plate.
Re-run: `/home/robbie/.venvs/nanobanana/bin/python3 batch_story_plates_agy.py story-15 story-15-3`
once quota resets (the script converts straight into `img/`).
One transient failure (12-2, bad model response) succeeded on retry.

## Task 2: audit of existing 30 story + 20 song plates (viewed individually at full size)
**Songs 1-20: all KEEP.** Minor nit only (song-18 shelf book labels are gibberish; song-2/4/5/7 have
legible baked-in signs) — not worth regenerating.

**Stories KEEP (19):** 1, 1-2, 1-3, 2, 2-2, 2-3, 3, 3-2, 3-3, 4, 4-3, 5, 5-2, 6, 7, 8, 8-2, 9, 10.

**Stories flagged REGENERATE (11) — NOT regenerated.** Over the ~8-plate budget guard, so per the
brief I'm stopping and reporting instead of redoing the book:
| plate | named defect |
|---|---|
| story-4-2 | baked-in title banner "The Tortoise and the Hare", "FINISH LINE" ribbon on the shell, clock in sky; does not show the hare racing ahead |
| story-5-3 | children on stepping stones; no fox/gingerbread man (alt: fox carries him across river) |
| story-6-2 | child asleep in bed; should be wolf in grandmother's nightcap |
| story-6-3 | empty kitchen; should be huntsman freeing Red Riding Hood and grandmother |
| story-7-2 | empty bridge; should be smallest goat trip-trapping |
| story-7-3 | empty forest bridge; should be big goat facing troll |
| story-8-3 | empty forest path; should be Foxy Loxy leading them to his den |
| story-9-2 | empty sheep hillside; should be villagers running up |
| story-9-3 | sleeping sheep under tree; should be wolf scattering flock |
| story-10-2 | frozen pond with no duckling |
| story-10-3 | swans at sunrise, no duckling reflection |
These are all "subject does not match the story" (scenery with the actors missing), not blur. Style/quality
is otherwise consistent. No before/after pairs since none were regenerated.
Decision needed from the user: approve regenerating these 11 (~20 min of agy).

## Live verification (https://freebabystories.com/img/…)
HTTP 200 + `image/webp`: story-11, 11-2, 11-3, 12, 12-2, 12-3, 13, 13-2, 13-3, 14, 14-2, 14-3, 15-2.
HTTP 200 but `text/html` (missing): story-15, story-15-3.

## Screenshot self-critique
- First full-page captures showed blank pastel cards for stories 7-14: lazy-loading artifact (images load
  on scroll). Re-shot after scrolling through; all cards 1-14 show plates. Real users are unaffected.
- Frog Prince card still shows the SVG fallback (missing plates above) — style clash with the rest of the grid.
- Plate ratio 1024x572 matches stories 1-4; cards crop cleanly. Palette consistent with stories 1-10.
- Video was recorded with fast scrolling; lazy images may appear late in it.

## MEDIA (results/plates-audit/media/)
m390-home-top.png, m390-home-full.png, m390-princess-and-pea-full.png, m390-jack-and-beanstalk-full.png, m390-song.png,
d1440-home-top.png, d1440-home-full.png, d1440-princess-and-pea-full.png, d1440-jack-and-beanstalk-full.png, d1440-song.png,
flow-390.mp4
