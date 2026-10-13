# Round 2 report — NOT COMPLETED: Google rejects the Firefox profile's session (human sign-in needed)

## Phase 1 diagnosis
- MCP launch (`gemini-image-mcp-server.py:236-241`): `p.firefox.launch_persistent_context(PROFILE, headless=False, ignore_default_args=["--enable-automation"], firefox_user_prefs={"dom.webdriver.enabled": False}, executable_path=<ms-playwright firefox>)`. No `-profile`/`-no-remote` flags; stale `.parentlock`/`lock` are deleted first. Prompt box found via `[contenteditable="true"]` selectors and `.click()`ed.
- `PROFILE = /home/robbie/.mozilla/firefox/lj7opnlf.default-release-2` — **the correct profile**. It is not a temporary/wrong profile, so there is no launch bug to fix; the MCP file was not changed.
- The profile's `cookies.sqlite` does hold SID/SAPISID/`__Secure-1PSID`/`__Secure-1PSIDTS`/LSID for google.com, unexpired (expiry 2027). But the headed Firefox on :10 with that profile shows **signed out**: gemini.google.com shows "Sign in" buttons and "Sign in to save activity" (`diag/gemini-home.png`), and `myaccount.google.com` redirects to the public "Create an account / Go to Google Account" page (`diag/myaccount.png`).
- Root cause: the cookies exist but Google no longer accepts the session server-side (revoked/expired/device-bound session). It is not a launch, profile-path, overlay or page-load problem. The earlier "element is not enabled" clicks were on greyed-out signed-out controls. Only a human Google sign-in in this profile on VNC :10 fixes it.
- Per the brief's hard rule, I stopped here: no generation attempted, no sign-in attempted, no files fabricated.

## Per-plate table
| plate | status | note |
|---|---|---|
| story-15 (Frog Prince cover) | still-failing | not generated; Gemini signed out |
| story-15-3 | still-failing | not generated; Gemini signed out |
| story-4-2, 5-3, 6-2, 6-3, 7-2, 7-3, 8-3, 9-2, 9-3, 10-2, 10-3 | kept (still wrong-subject) | not regenerated; files untouched |
| all other story plates and 20 song plates | kept | byte-identical |

## Live check (2026-10-14)
| URL | result |
|---|---|
| https://freebabystories.com/img/story-15.webp | 200 text/html (file missing; SPA fallback) |
| https://freebabystories.com/img/story-15-3.webp | 200 text/html (file missing; SPA fallback) |

## Screenshots / video
`frog-card-390.png`, `frog-card-1440.png`, `flow-390.mp4` (37s: scroll home to Frog Prince, open story, scroll text). These record the **current live state**: the Frog Prince card shows the SVG placeholder, not a painted plate, because the webp doesn't exist.

## Outstanding
1. A human signs in to Google in Firefox profile `lj7opnlf.default-release-2` at VNC :10 (use the same Playwright Firefox, or sign in so cookies persist), then rerun Task A and Task B. `/tmp/gen/gen.py` is ready.
2. Alternative: wait for the agy image quota to reset.
