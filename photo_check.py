"""Check that a post photo is big enough: python photo_check.py <file> ...

Prints OK or LOW for each file and exits with 1 if any is too small or unreadable.
"""
import sys

from PIL import Image

MIN_LONG, MIN_SHORT = 1000, 600


def main():
    bad = 0
    for path in sys.argv[1:]:
        try:
            w, h = Image.open(path).size
        except Exception as e:
            print(f"LOW {path}: not an image ({e})")
            bad = 1
            continue
        ok = max(w, h) >= MIN_LONG and min(w, h) >= MIN_SHORT
        print(f"{'OK' if ok else 'LOW'} {path}: {w}x{h} (need at least {MIN_LONG}x{MIN_SHORT})")
        bad = bad or not ok
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
