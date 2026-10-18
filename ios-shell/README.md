# Free Baby Stories — iOS

The iPhone app for
[toddler-stories.robbie.digital](https://toddler-stories.robbie.digital):
fifteen classic fairy tales and fables — Grimm, Jacobs, Aesop, Andersen — set in
big warm type for reading aloud at bedtime.

The app is the live storybook inside a Capacitor shell, in the same shape as the
Sprout and Free Books shells: the site stays the single source of truth, and the
native target adds only what a web view cannot do for itself.

## What is native here

| | Why it cannot be done in the web view |
|---|---|
| **Read aloud, out loud** | Long-press a story and iOS reads the visible text with `AVSpeechSynthesizer`, using a spoken-audio session that ducks other audio instead of stopping it. Safari on iOS exposes no speech synthesis to a page, so this is genuinely unreachable from the web view — and it is the thing that lets a parent put the phone face-down and still hear the tale. |
| **The screen stays awake while a story is open** | A parent reading aloud is not touching the screen, which is exactly what the idle timer punishes: five minutes into a tale the display dims and the child loses the picture. Held open on `#story/<id>` and `#song/<id>`, released on the shelf. |
| **Status bar follows the paper** | UIKit never hears about the page's own background, so on a dark system appearance the status bar can end up invisible against the cream. |
| **Touch behaviour** | No grey flash on the illustrations, no double-tap zoom delay, no rubber-band overscroll pulling the page off its masthead, light haptic on the controls the reader presses. |
| **Offline start** | A cold start with no connection loads the shell's own `public/index.html` instead of a blank screen. |

## Layout

```
capacitor.config.ts                     live origin, paper background, contentInset
public/index.html                       offline fallback (the shell's own page)
scripts/generate-assets.py              regenerates the icon + launch image
ios/App/App/StorybookBridgeViewController.swift   the native layer described above
ios/App/App/Assets.xcassets             icon and Splash, generated not placeholder
```

## The icon

Redrawn — not upscaled — from the storybook's existing `apple-touch-icon`, in
the site's own tokens (`--paper`, `--ink`, `--red`, `--forest`, `--gold`). The
mark is a real open-book silhouette with the fold pinching both the head and the
tail, so it still reads as a book at 60px on a home screen. No text on the icon.

## Working on it

```bash
npm install
npm run sync                 # copy public/ and write capacitor.config.json
npm run open                 # open the Xcode project
npm run build:sim            # build for the simulator into ./build
```

To regenerate the icon and launch image after changing the mark:

```bash
python3 scripts/generate-assets.py   # needs playwright's chromium
```

## Run it in the simulator

```bash
npm run build:sim
xcrun simctl boot "iPhone 18 Pro"
xcrun simctl install booted build/Build/Products/Debug-iphonesimulator/App.app
xcrun simctl launch booted digital.robbie.babystories
```

## Notes

- `ios.contentInset: 'never'` pairs with the site's `viewport-fit=cover`: the web
  view spans the display and the storybook's own bars own the safe-area insets.
- `ITSAppUsesNonExemptEncryption` is set to `false`, so uploads skip the export
  compliance questionnaire.
- Only `toddler-stories.robbie.digital` is in `allowNavigation`.
