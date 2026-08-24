#!/usr/bin/env bash
# Converts a HEIC image to JPEG via ffmpeg, two passes (extract frame, then
# re-encode) -- a single-pass "-i in.heic -vf scale ... out.jpg" fails with
# "Filtergraph was specified for a stream fed from a complex filtergraph"
# because HEIC uses an internal tile-grid ffmpeg can't filter directly.
# Facebook/Instagram's upload APIs don't reliably accept raw HEIC bytes, so
# every feed image goes through this before posting.
#
# Some real client photos (confirmed 2026-08-24, GM's IMG_8090.HEIC) use a
# tile-grid variant ffmpeg's HEIF demuxer can't read AT ALL -- not flaky,
# fails identically on every retry. Falls back to Pillow + pillow-heif
# (same library already used for this in Bernardino's pipeline), which
# handles tile-grid HEIC correctly.
# Usage: convert_heic_to_jpg.sh <input.heic> <output.jpg>
set -euo pipefail

IN="$1"
OUT="$2"
FULL="$(mktemp --suffix=.jpg)"

if ffmpeg -y -i "$IN" -frames:v 1 "$FULL" >/dev/null 2>&1 && \
   ffmpeg -y -i "$FULL" -vf "scale=1600:-2" -q:v 3 "$OUT" >/dev/null 2>&1 && \
   [ -s "$OUT" ]; then
  rm -f "$FULL"
  exit 0
fi
rm -f "$FULL"

echo "AVISO: ffmpeg nao conseguiu converter $IN, tentando via Pillow/pillow-heif..." >&2
python3 - "$IN" "$OUT" <<'PYEOF'
import sys
from pillow_heif import register_heif_opener
from PIL import Image

register_heif_opener()
in_path, out_path = sys.argv[1], sys.argv[2]
img = Image.open(in_path)
img.convert("RGB").save(out_path, format="JPEG", quality=92)
PYEOF

if [ ! -s "$OUT" ]; then
  echo "ERRO: conversao HEIC->JPG falhou para $IN (ffmpeg e Pillow/pillow-heif)" >&2
  exit 1
fi
