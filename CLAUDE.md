# Toddler Storybook — Magic Redesign

## Mission
Redesign the single-file storybook at `/home/robbie/projects/toddler-stories/index.html` to be MAGICAL. The site is hosted at https://toddler-stories.robbie.digital and the GitHub repo is https://github.com/Robbie-Cook/toddler-stories.

## Key Constraints
- Output MUST be `/home/robbie/projects/toddler-stories/index.html` (single self-contained HTML file)
- Keep ALL 10 existing stories with their full text
- Keep ink-reveal effect (canvas-based organic ink bloom on scroll)
- Keep hash-routing (`#story/<id>`) for story navigation
- Keep responsive grid (1/2/3 columns)

## What to Change

### 1. Serif Font
Pick a beautiful serif font that has the clean, modern feel of **Lexend Deca** but as a serif. Candidates: Source Serif 4, Literata, IBM Plex Serif, or similar. Use it for headings AND body text (the whole site should feel like a classic storybook). Pair with a warm sans-serif for UI elements if needed.

### 2. Magical Entrance & Transitions
- Page/site-first-load: a beautiful entrance animation (pages turning, a storybook opening, ink blooming across the whole page, etc.)
- Story cards: staggered entrance with a gentle bounce/fade as they come into view
- Reading view: smooth page-turn-style transitions when navigating between stories
- Overall feeling: warmth, wonder, happiness — like unwrapping a gift

### 3. Images
The HTML should reference real images at `img/story-1.webp` through `img/story-10.webp`. Use `<img>` tags with proper `alt` text. The images will be generated separately, so just use placeholder paths. Keep the SVG illustrations as a FALLBACK (using `<picture>` or `onerror` handlers or inline SVG behind the img).

Story-to-number mapping:
1. The Three Little Pigs
2. Goldilocks and the Three Bears
3. The Little Red Hen
4. The Tortoise and the Hare
5. The Gingerbread Man
6. Little Red Riding Hood
7. The Three Billy Goats Gruff
8. Chicken Little
9. The Boy Who Cried Wolf
10. The Ugly Duckling

### 4. Colour Palette
Keep the warm cream/parchment base but make it richer and more magical. Think: warm golden hour light, deep book-ink browns, rich jewel accents. The palette should feel like a beloved old picture book.

### 5. Ink Effect
Keep the canvas-based ink wash reveal. Make it slightly richer — maybe with golden ink particles or warm sepia tones instead of just black ink.

## Style References
- The user loves the Athletica Fitness font (Lexend Deca) — clean, modern, warm
- The blog at robbie.digital has the ink effect they love
- Overall: warm, nostalgic, handcrafted, magical — like a children's book from the golden age of illustration

## Ship
Write the redesigned HTML to `/home/robbie/projects/toddler-stories/index.html`.
