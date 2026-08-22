# Toddler Storybook Website

## Stack
- Single self-contained HTML file (no build step, no framework)
- Vanilla CSS with CSS custom properties
- Vanilla JS for the ink-reveal effect
- No external dependencies — everything bundled in one file
- Output: `/home/robbie/projects/toddler-stories/index.html`

## The Ink Reveal Effect (from robbie.digital blog)
The blog uses a canvas-based ink wash reveal effect. Images get class `ink-processed` (opacity: 0, hidden). A `<canvas class="ink-canvas">` layer draws an ink-spread animation (like ink bleeding on paper). When the animation completes, the image gets `ink-revealed` (opacity: 1). The ink effect covers the image area, then dissolves outward revealing the image underneath.

CSS rules:
```css
.ink-processed { opacity: 0 !important; }
.ink-processed.ink-revealed { opacity: 1 !important; }
```

## Important
- Output file path MUST be: `/home/robbie/projects/toddler-stories/index.html`
