"""Stamp a photo with the channel name (@CFC_UZ): python stamp.py <photo> <out>"""
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageFilter

MARK = Path(__file__).resolve().parent / "assets" / "cfc_uz_at.png"


def stamp(src, out=None):
    """Put the white @CFC_UZ mark with a soft shadow in the bottom-left corner; returns the new JPEG's path."""
    img = Image.open(src).convert("RGB")
    w, h = img.size
    mark = Image.open(MARK).convert("RGBA")
    mw = int(w * (0.24 if w >= h else 0.34))
    mark = mark.resize((mw, mark.height * mw // mark.width), Image.LANCZOS)
    x, y = int(w * 0.035), h - mark.height - int(min(w, h) * 0.045)
    shadow = Image.new("L", img.size, 0)
    shadow.paste(mark.getchannel("A"), (x, y))
    shadow = shadow.filter(ImageFilter.GaussianBlur(max(3, mark.height // 6))).point(lambda v: min(255, v * 2))
    img.paste((0, 0, 0), (0, 0), shadow.point(lambda v: v * 3 // 4))
    img.paste(mark, (x, y), mark)
    if out is None:
        out = tempfile.mkstemp(suffix=".jpg")[1]
    img.save(out, "JPEG", quality=93)
    return out


if __name__ == "__main__":
    print(stamp(sys.argv[1], sys.argv[2]))
