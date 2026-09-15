#!/bin/bash
# Usage: photos_add_to_album.sh <uuid_file> <album_name>
# Adds assets (by Photos UUID) to an album, creating it if needed. Batches of 250.
set -u
UUID_FILE="$1"; ALBUM="$2"
osascript -e "tell application \"Photos\" to if not (exists album \"$ALBUM\") then make new album named \"$ALBUM\"" >/dev/null
total=$(wc -l < "$UUID_FILE" | tr -d ' ')
done=0
split -l 250 "$UUID_FILE" /tmp/uuid_batch_
for f in /tmp/uuid_batch_*; do
  ids=$(awk '{printf "media item id \"%s/L0/001\", ", $0}' "$f" | sed 's/, $//')
  osascript -e "tell application \"Photos\" to add {$ids} to album \"$ALBUM\"" >/dev/null 2>/tmp/album_err.txt
  if [ -s /tmp/album_err.txt ]; then echo "batch $f error: $(cat /tmp/album_err.txt)"; fi
  done=$((done+$(wc -l < "$f")))
  echo "$ALBUM: $done/$total"
  rm "$f"
done
echo "DONE $ALBUM"
