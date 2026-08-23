# Toddler Storybook — Fix Brief

## Stack
- Single-file HTML at `/home/robbie/projects/toddler-stories/index.html`
- All CSS, HTML, JS inline in one file (~114KB)
- Hosted: https://toddler-stories.robbie.digital
- Repo: https://github.com/Robbie-Cook/toddler-stories (master branch, push direct)
- Deploy: Push to master → deploy dashboard auto-builds
- Images: `/home/robbie/projects/toddler-stories/img/` (story-1.webp through story-10.webp)

## HARD CONSTRAINTS — DO NOT BREAK
1. **Single self-contained HTML file** — output to `/home/robbie/projects/toddler-stories/index.html`
2. **Keep hash-routing** (`#story/<id>` navigation)
3. **Keep ALL 10 stories** — do not add or remove stories
4. **Keep responsive grid** (1/2/3 columns on mobile/tablet/desktop)
5. **Keep photographic images** — `img/story-*.webp` must remain the primary visual (SVG fallback)
6. **Do NOT remove existing images** — cards MUST show the `.webp` images

## What to Change

### 1. Remove the Table of Contents
The HTML has a `<nav class="toc">` with `<ol id="tocList">` that lists story names/numbers. DELETE this entire block. The Home Screen should show ONLY picture cards (`.grid` with `.card` elements). No numbered list, no "Contents" heading.

### 2. Rewrite ONLY the Scary Bits
Do NOT replace entire stories with full unabridged versions. Instead, find the parts of each story that were sanitized/softened for toddlers and rewrite THOSE specific paragraphs to restore the original dark edges. The key stories needing changes:

| Story | What's currently sanitized | Restore this |
|-------|---------------------------|--------------|
| Three Little Pigs | The first two pigs "ran away to their brothers" | The wolf HUFFS AND PUFFS AND BLOWS THE HOUSE IN and EATS the first two pigs. Only the brick pig survives. |
| Red Riding Hood | Wolf may just talk to grandma | The wolf EATS the grandmother, gets in bed, then EATS Little Red Riding Hood too. Huntsman cuts him open to save them. |
| Chicken Little | Acorn ending with owl — fox doesn't eat them | The fox lures them into his den and EATS every one of them. |
| Boy Who Cried Wolf | Sheep may escape | The wolf EATS the sheep. Nobody comes. Real consequences. |

Keep the rest of each story as-is. Don't expand paragraphs to full original length — just punch up the sanitized bits. The tone should stay storybook-appropriate but dark where the originals were dark.

### 3. Build a Fresh Ink Effect (DON'T use old broken versions)
The current "golden curtain sweep left-to-right" is broken. The old backup at `.build/index.old.html` was ALSO broken. **Build a proper ink effect from scratch** modeled after the blog (blog.robbie.digital)'s aesthetic — tasteful, subtle, dark ink blooming from center.

What the ink effect should do:
- **Color**: dark India ink — `rgba(38, 24, 16, ...)` / `rgba(26, 16, 11, ...)` — NOT golden/yellow
- **Direction**: CENTER OUT (blooming radial), not curtain/sweep
- **Shape**: organic radial blobs that grow and merge, like ink bleeding into paper
- **Feel**: real India ink on paper — soft blurred edges, dense core, organic unevenness
- **Trigger**: scroll into view (IntersectionObserver on the plate images)
- **Duration**: ~1.2-1.8s to full bloom, subtle easing

Design the canvas/JS from scratch. Don't copy the old implementation.

| Aspect | OLD (restore this) | CURRENT (remove this) |
|--------|-------------------|----------------------|
| Color | Dark ink brown `rgba(38,24,16)` | Golden `rgba(217,164,65)` |
| Direction | Bloom center-out | Sweep left-to-right |
| Shape | Radial blobs growing | Curtain line |
| Feel | Paper drinking ink | Golden curtain |

### 4. Apple Touch Icon
Add to `<head>`:
```html
<link rel="apple-touch-icon" sizes="180x180" href="img/apple-touch-icon.png">
```
Generate a simple 180×180 PNG icon at `img/apple-touch-icon.png` — a simple book/star motif in warm tones.

### 5. SEO Meta Tags
Add to `<head>`:
- `<meta name="description" content="...">` — descriptive, keyword-rich
- Open Graph tags: `og:title`, `og:description`, `og:image` (point to story-1.webp), `og:url`, `og:type` (website)
- Twitter Card tags: `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`
- `<meta name="viewport" content="width=device-width, initial-scale=1">`
- Canonical URL tag

### 6. Update Footer Text
Change "These retellings are shortened and softened" to reflect these are now complete with the original story elements.

## Process
1. Survey the codebase fully
2. Make ALL changes above
3. Verify the page loads and looks right in VNC :10
4. Write reasoning for Apple Touch + SEO decisions in a comment block
5. Commit with descriptive message
6. Push to master (triggers auto-deploy)

## Verification
- Open `file:///home/robbie/projects/toddler-stories/index.html` in browser
- Check: no TOC visible, only cards with images
- Check: scary bits restored (wolf eats pigs, fox eats Chicken Little, etc.)
- Check: ink effect blooms dark ink from center on each illustration plate
- Check: page source shows proper SEO meta tags + apple-touch-icon link