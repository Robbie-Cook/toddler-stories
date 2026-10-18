# Toddler Storybook — Free Baby Stories

Fifteen classic fairy tales and fables — Grimm, Joseph Jacobs, Aesop and Andersen —
set in big, warm type for reading aloud at bedtime, on
[toddler-stories.robbie.digital](https://toddler-stories.robbie.digital).

The site is a single self-contained `index.html`; `img/` holds the story plates.
Deploys from `main`.

## iOS app

`ios-shell/` packages this site as the **Free Baby Stories** iPhone app
(`digital.robbie.babystories`) — a Capacitor shell around the live origin, with a
native bridge for the things a web view cannot do for itself: holding the splash
until the page paints, pushing the real safe-area insets into the site's own
sticky masthead, keeping the screen awake while a story is open, and reading a
story aloud through `AVSpeechSynthesizer` on a long press.

It is a subdirectory on purpose: a `package.json` at this repo's root would make
Cloudflare Pages try to build the static site with Node and break the deploy.

```bash
cd ios-shell
npm install
npm run build:sim          # Debug build for the simulator
npm run open               # open the Xcode project
python3 scripts/generate-assets.py   # regenerate the icon and launch image
```

See `ios-shell/README.md` for the full detail, and `ios-shell/evidence/` for the
simulator recording and screenshots.
