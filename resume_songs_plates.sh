#!/usr/bin/env bash
# Finish the song plates after the Antigravity image-quota reset
# (quota window resets around 2026-10-02T15:24:16Z).
# Regenerates: song-3 (spider fix) and song-12..20, converts to webp,
# then commits and pushes so the deploy picks them up.
set -u
cd /home/robbie/projects/toddler-stories
LOG=/tmp/songs-resume.log
TARGET_EPOCH=$(date -u -d '2026-10-02T15:27:00Z' +%s)

echo "[resume] waiting for quota reset (15:27Z)..." >> "$LOG"
while [ "$(date -u +%s)" -lt "$TARGET_EPOCH" ]; do sleep 60; done

for attempt in 1 2 3; do
  echo "[resume] attempt $attempt at $(date -u +%FT%TZ)" >> "$LOG"
  SONGS_CONVERT=1 /home/robbie/.venvs/nanobanana/bin/python3 batch_songs_agy.py >> "$LOG" 2>&1
  n=$(ls img/song-*.webp 2>/dev/null | wc -l)
  echo "[resume] attempt $attempt: $n/20 webp present" >> "$LOG"
  [ "$n" -ge 20 ] && break
  sleep 1800
done

git add img/song-*.webp
if git diff --cached --quiet; then
  echo "[resume] nothing to commit" >> "$LOG"
else
  git commit -m "Add remaining nano-banana song plates (resume after Antigravity quota reset)" >> "$LOG" 2>&1
  git pull --rebase origin main >> "$LOG" 2>&1 || true
  git push origin main >> "$LOG" 2>&1 || true
  echo "[resume] pushed" >> "$LOG"
fi
echo "[resume] DONE with $n/20 webp" >> "$LOG"