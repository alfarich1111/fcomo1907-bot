"""Replace text inside a picture with Karakalpak text, keeping the background.

registan_patch.py IN OUT --patch "x0,y0,x1,y1|font size|weight|text" [--patch ...]

The box must hold only the old text on a plain or gradient background, with the
same background just outside its sides. A weight ending in c ("400c") centres the text;
\\n in the text starts a new line.
"""
import argparse
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = "assets/fonts/Inter.ttf"


def font(size, weight):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_axes([min(32, max(14, size)), weight])
    return f


def wrap(draw, text, f, width):
    lines = []
    for part in text.split("\n"):
        line = ""
        for word in part.split():
            test = f"{line} {word}".strip()
            if line and draw.textlength(test, font=f) > width:
                lines.append(line)
                line = word
            else:
                line = test
        lines.append(line)
    return lines


def erase(img, box):
    x0, y0, x1, y1 = box
    m = 6
    px = img.filter(ImageFilter.GaussianBlur(3)).load()
    out = img.load()
    c = [px[x0 - m, y0 - m], px[x1 + m, y0 - m], px[x0 - m, y1 + m], px[x1 + m, y1 + m]]
    for y in range(y0, y1):
        s = (y - y0) / (y1 - y0)
        left, right = px[x0 - m, y], px[x1 + m, y]
        for x in range(x0, x1):
            t = (x - x0) / (x1 - x0)
            top, bottom = px[x, y0 - m], px[x, y1 + m]
            out[x, y] = tuple(round(
                (1 - t) * left[i] + t * right[i] + (1 - s) * top[i] + s * bottom[i]
                - (1 - s) * ((1 - t) * c[0][i] + t * c[1][i]) - s * ((1 - t) * c[2][i] + t * c[3][i])
            ) for i in range(3))
    img.paste(img.crop(box).filter(ImageFilter.GaussianBlur(14)), box[:2])


def write(img, box, size, weight, text, center=False):
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(img)
    while True:
        f = font(size, weight)
        lines = wrap(draw, text, f, x1 - x0)
        step = round(size * 1.24)
        if step * len(lines) <= y1 - y0 or size <= 14:
            break
        size -= 1
    y = y0 + (y1 - y0 - step * len(lines)) // 2
    for line in lines:
        x = (x0 + x1 - draw.textlength(line, font=f)) / 2 if center else x0
        draw.text((x, y), line, font=f, fill="white")
        y += step
    print(f"box {box}: size {size}, {len(lines)} lines")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("src")
    p.add_argument("out")
    p.add_argument("--patch", action="append", required=True)
    a = p.parse_args()
    img = Image.open(a.src).convert("RGB")
    for spec in a.patch:
        box, size, weight, text = spec.split("|", 3)
        box = tuple(int(v) for v in box.split(","))
        erase(img, box)
        write(img, box, int(size), int(weight.rstrip("c")), text.replace("\\n", "\n"), weight.endswith("c"))
    img.save(a.out, quality=93)


if __name__ == "__main__":
    main()
