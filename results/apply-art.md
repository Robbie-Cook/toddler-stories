# apply-art
- Art commits 8fe5203 + 689077f were already on origin/main; img/story-36..45 (+-2,-3, webp+png) all serve 200 image/webp live.
- Bug found+fixed (5de50bd): card/resume thumbnails used story-(index+1).webp, so stories 16-25 (Cinderella..Beauty & Beast) pointed at nonexistent story-16..25. Added cardSrc() -> MULTI_IMAGES[idx][0].
- Live check: story-36/37/41/45(+-2/-3) 200 image/webp; live HTML contains cardSrc; screenshot shows Hansel and Gretel card art.
- Video: results/baby-stories-art-live.mp4 (390px, recorded 23:12 after final commit 23:09). Cowork push UNVERIFIED: cowork-card.py could not resolve a target session (no --session given).
- Cowork todo t_815686b3ea: no notes found in briefs; not duplicated.
