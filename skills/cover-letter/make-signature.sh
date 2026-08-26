#!/usr/bin/env bash
# Turn a signature scanned on white paper into signature.png with a transparent
# background, ready for \includegraphics in the cover letter.
#
# Usage: make-signature.sh <scan.pdf|scan.png|scan.jpg> [output.png]
#        (output defaults to $JOB_HUNT_HOME/signature.png, i.e. the workspace —
#         never inside the plugin, which a update would replace)
#
# The input is a photo or scan of a signature on a BLANK WHITE SHEET, flat and
# in good light. A photo of a signature on lined or coloured paper will key
# badly: the paper colour is what gets removed.
#
# Needs: pdftoppm + magick (poppler + imagemagick) and Pillow.
#   brew install poppler imagemagick && pip3 install --user Pillow
set -euo pipefail

PATH="$PATH:/opt/homebrew/bin:/usr/local/bin"
export PATH

JOB_HUNT_HOME="${JOB_HUNT_HOME:-$HOME/Documents/job_applications}"
SRC="${1:?usage: make-signature.sh <scan.pdf|scan.png|scan.jpg> [output.png]}"
OUT="${2:-$JOB_HUNT_HOME/signature.png}"
mkdir -p "$(dirname "$OUT")"

# Windows has no `python3` on the PATH by default — the interpreter is `python`,
# or the `py` launcher. Resolve one rather than assuming the Unix name, and
# verify Pillow is importable while we are at it: "python exists" and "Pillow is
# installed" are different facts, and failing on the second one at the last line
# of the script would waste the whole run.
PYBIN=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import PIL" >/dev/null 2>&1; then
    PYBIN="$c"; break
  fi
done
if [ -z "$PYBIN" ]; then
  echo "ERROR: no Python with Pillow found (tried python3, python, py)." >&2
  echo "  macOS:   brew install imagemagick && python3 -m pip install --user Pillow" >&2
  echo "  Debian:  sudo apt install -y imagemagick python3-pil" >&2
  echo "  Windows: winget install --id Python.Python.3.12 -e && py -m pip install --user Pillow" >&2
  exit 3
fi

if ! command -v magick >/dev/null 2>&1; then
  echo "ERROR: magick not found (ImageMagick)." >&2
  echo "  macOS:   brew install imagemagick" >&2
  echo "  Debian:  sudo apt install -y imagemagick" >&2
  echo "  Windows: winget install --id ImageMagick.ImageMagick -e" >&2
  exit 3
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# A PDF scan must be rasterised first; 600 dpi keeps the stroke edges smooth.
case "$SRC" in
  *.pdf|*.PDF)
    if ! command -v pdftoppm >/dev/null 2>&1; then
      echo "ERROR: pdftoppm not found (it comes with Poppler)." >&2
      echo "  macOS:   brew install poppler" >&2
      echo "  Debian:  sudo apt install -y poppler-utils" >&2
      echo "  Windows: winget install --id oschwartz10612.Poppler -e" >&2
      echo "  Or convert the scan to PNG yourself and pass that instead." >&2
      exit 3
    fi
    pdftoppm -r 600 -png -singlefile "$SRC" "$TMP/raw"
    RAW="$TMP/raw.png"
    ;;
  *) RAW="$SRC" ;;
esac

"$PYBIN" - "$RAW" "$TMP/keyed.png" <<'PY'
"""Key the paper out of a signature scan. Pillow-only (no numpy needed).

Alpha comes from a level-stretched luminance, so the paper goes fully
transparent while anti-aliased stroke edges keep their soft falloff. The RGB is
then flattened to the sampled ink colour, which makes a white halo impossible.
"""
import sys
from PIL import Image, ImageFilter, ImageStat

SRC, DST = sys.argv[1], sys.argv[2]

# Endpoints on the 0-255 luminance scale.
# PAPER: this light or lighter -> fully transparent (also kills scan dust).
# INK:   this dark or darker    -> fully opaque.
PAPER, INK = 205, 90
PAD = 24  # px of transparent margin kept around the ink

img = Image.open(SRC).convert("RGB")
gray = img.convert("L")

span = PAPER - INK
alpha = gray.point(lambda v: 0 if v >= PAPER else 255 if v <= INK
                   else int(round((PAPER - v) * 255 / span)))

# Opening (erode then dilate) drops isolated speckles; at 600 dpi the strokes
# are far thicker than the 3x3 kernel, so they survive untouched.
alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))

# Sample the ink colour from the darkest pixels only, so the flattened RGB keeps
# the pen's real hue instead of a paper-diluted wash.
core = gray.point(lambda v: 255 if v <= INK else 0)
ink = tuple(int(round(c)) for c in ImageStat.Stat(img, core.convert("1")).mean)
print(f"  ink colour: #{ink[0]:02X}{ink[1]:02X}{ink[2]:02X}")

out = Image.new("RGBA", img.size, ink + (0,))
out.putalpha(alpha)

box = alpha.getbbox()
if box:
    l, t, r, b = box
    out = out.crop((max(0, l - PAD), max(0, t - PAD),
                    min(img.width, r + PAD), min(img.height, b + PAD)))

out.save(DST)
print(f"  cropped to {out.width}x{out.height}, aspect w/h {out.width / out.height:.3f}")
PY

# 1600 px stays crisp well beyond any print size the letter will use.
magick "$TMP/keyed.png" -background none -resize 1600x -strip "$OUT"
echo "Wrote $OUT ($(magick identify -format '%wx%h' "$OUT"))"
echo "Size it by HEIGHT in the letter — see the Signature section of your candidate.md."
echo "Open it and check the paper is gone and the strokes are intact before using it."
