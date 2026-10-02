# SONGS-REPORT — Songs get their own identity + plates + 5 longer rhymes

Date: 2026-10-02 · Branch: `main` · Feature commit: `6e7cc2b` · Live: freebabystories.com

## What changed

### 1. Songs now have their own identity (additive CSS only)
- **Song cards** (`.card--song`): forest-green top strip on the plate frame,
  green border tint, green kicker/CTA accents — stories keep their gold/red look.
- **Music-note badge** on every song plate (cards and reader), in the `--forest`
  green. Stories have no badge.
- **Songs panel** gets a soft meadow/sky wash (`.songs-panel`); the **Songs tab
  pill** is forest green when active (stories stays neutral).
- **Song reader treatment** (`.reader--song`): lyric verses are **centred**, no
  drop cap, green title/subtitle/kicker accents, badge on the plate. Story
  readers are untouched (drop caps, gold/red).
- All changes are new CSS classes + small `classList` toggles in `buildReader`
  and `renderSongs`; no existing story/story-reader rule was edited.
- Section head copy: "Twenty old songs, ready to sing"; hero meta now
  "15 stories / 20 songs". `#song/<slug>` and `#songs` hashes are linkable;
  the ink-bloom effect, responsive grid, and single-file `index.html` are intact.

### 2. Nano-banana plates for the songs
- Each of the 20 songs gets `img/song-<n>.webp` (1024×576, matches the
  story-plate ratio), generated with **Nano Banana** (`gemini-3-pro-image`
  via the Antigravity CLI, `batch_songs_agy.py`) in the same watercolor /
  golden-hour storybook style as `img/story-*.webp`. Prompts are per-song
  subjects (e.g. crib + moon for Twinkle; black sheep + wool sacks).
- The generic `SONG_ART` moon-and-notes SVG remains as the automatic fallback
  whenever a webp is missing or fails to load (`has-photo` gating in
  `makePlate`) — graceful by design.
- **Status: 11/20 plates shipped** in `6e7cc2b` (song-1, 2, 4–11).
  The Antigravity image quota capped mid-run. `resume_songs_plates.sh` is
  armed (background job) to regenerate the remaining 9 (song-3 re-do after a
  spider-fix prompt change, plus song-12–20) when the quota window resets
  (~2026-10-02T15:27Z), convert, commit and push them automatically; log at
  `/tmp/songs-resume.log`. Re-run manually any time with:
  `SONGS_CONVERT=1 /home/robbie/.venvs/nanobanana/bin/python3 batch_songs_agy.py`
  (it resumes — existing PNGs are skipped).

### 3. Five longer public-domain songs added (20 total)
| # | Song | Verses |
|---|------|--------|
| SONG XVI | Sing a Song of Sixpence | 3 |
| SONG XVII | Little Bo Peep | 5 |
| SONG XVIII | Ten in the Bed | 10 |
| SONG XIX | The Farmer in the Dell | 10 |
| SONG XX | The North Wind Doth Blow | 4 |

All five are traditional nursery rhymes in the public domain (verified text
against standard collections). Roman numerals extended to XX. **No modern or
commercial lyrics were added** — nothing uncertain was included.

## Deploy verification
- Push `6e7cc2b` → dashboard build `9013a668` **ready** (14 files uploaded).
- Live checks on freebabystories.com (and toddler-stories.robbie.digital):
  heading "Twenty old songs, ready to sing" ✓, `card--song` markup ✓,
  `img/song-*.webp` served as `image/webp` 200 ✓ (song-3 → SPA HTML fallback
  with 200, so its card shows the SVG plate until the regen pushes).
- Visual QA: 1440px + 390px screenshots of both tabs and both readers; light
  theme only (the site has no dark mode). Song vs story collections pass the
  one-glance test; story tab unchanged (regression clean).

## Notes / honest caveats
- The Firefox gemini.google.com MCP path is dead (profile signed out of
  Google) — `batch_songs.py` is parked until a manual re-login; the Antigravity
  CLI path is what actually produced the plates.
- The background resume job commits + pushes the remaining plates
  autonomously when it completes; its output is logged and easy to review
  (`git log`, `/tmp/songs-resume.log`).
- Scripts added to the repo: `batch_songs.py` (Firefox variant, parked),
  `batch_songs_agy.py` (active), `resume_songs_plates.sh` (quota-reset finisher).

## Plates complete — 2026-10-03

All 20/20 song plates now live. The missing 9 (song-3, song-12–20) were
converted from regenerated Nano Banana PNGs to webp, visually verified
(child-appropriate, correct subjects: song-3 is a spider, not a bee), and
deployed. Live site serves all 20 with HTTP 200.

## MEDIA
- /tmp/songs-shots/live-songs-1440.png (LIVE production site, songs tab)
- /tmp/songs-shots/songs-vs-stories-1440.png (songs vs stories, one-glance test)
- /tmp/songs-shots/songs-390.png (mobile songs grid)
- /tmp/songs-shots/song-reader-1440.png (song reader, painted plate + badge)
- /tmp/songs-shots/song-reader-390.png (mobile song reader, centred lyrics)
- /tmp/songs-shots/stories-1440.png (stories regression check)
- /tmp/song-plates/contact-sheet-1.png (plate QA contact sheet)
- img/contact-sheet-new-9.png (9 new plates: song-3, song-12–20)