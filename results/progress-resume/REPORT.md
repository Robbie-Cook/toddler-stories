# Progress bar + resume + newest-first order

## 1. Story order
Judged "old/bad": the 10 original first-draft tales (git: all added 2026-08-22 in the initial commit, SVG-fallback-era art, reader plates only 1-3 each, texts repeatedly rewritten): Three Little Pigs, Goldilocks, Little Red Hen, Tortoise and Hare, Gingerbread Man, Red Riding Hood, Billy Goats Gruff, Chicken Little, Boy Who Cried Wolf, Ugly Duckling.
Newer: 5 tales added 2026-08-27 with fresh agy/nano-banana plates (2026-10-14): Frog Prince, Elves and Shoemaker, Jack and Beanstalk, Emperor's New Clothes, Princess and Pea.
(Judgement is from git dates + plate generation, not a quality review of the text; within each group the original relative order is kept.)

Before: Pigs, Goldilocks, Hen, Tortoise, Gingerbread, Red Riding Hood, Billy Goats, Chicken Little, Boy Wolf, Ugly Duckling, Princess & Pea, Emperor, Jack, Elves, Frog Prince.
After:  Frog Prince, Elves, Jack, Emperor, Princess & Pea, then the original ten as above.
Implemented as a `SHELF_IDS` display order; the `STORIES` array is untouched so `img/story-N.webp` mapping and `#story/<id>` routing are unchanged. Roman numerals and prev/next follow shelf order. Stories added later and not listed go to the top.

## 2. Progress bar
Fixed 5px gold-to-red bar at the top (role=progressbar) plus a % pill, only while reading a story. Progress = scrollY over the distance to the closing "The End" block. The site has no dark theme, so light only.

## 3. Resume
localStorage `fbs-progress-v1` {id:{p,t,done}}. Home: "Continue reading" card (thumb, title, meter, Resume · N%), per-card % badge + strip, "Read ✓" + "x of 15 read". Reopening restores position (re-aims while lazy images settle) with a "Start over" toast. >=97% = done: no resume, shown as read. Garbage / unknown ids / out-of-range values are sanitised. Found and fixed one bug: the #contents anchor jump on Back overwrote the saved position with 0.

## Evidence (real Chrome via Playwright)
Asserted at 390 and 1440, local and live: bar width 0 -> ~47%/59% of viewport after scroll; localStorage holds p; resume after full reload restores scrollY 2500 (diff 0); hard reload on a story hash restores; finishing hides resume and counts "1 of 15 read"; garbage storage = no errors. See *-assert-log.txt.
Videos: local-flow.mp4, live-flow.mp4 (home -> story -> scroll -> back -> Resume card -> reload -> click -> same position, 2660px).
Screenshot critique: fixed (a) resume card lost side margin (margin override), (b) % pill collided with the red header button on 390 (moved under the header). Remaining nit: the status pill makes the kicker row ~2px taller on the card that has it.
