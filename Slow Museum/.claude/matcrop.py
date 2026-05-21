#!/usr/bin/env python3
"""Mat (border) auto-crop + JPEG optimize for Slow Museum paintings.

Detects a uniform mat/border by sampling the 4 corners, trims it (keeping the
artwork's true aspect ratio), and writes an optimized JPEG WORK copy. The
original is never modified.

Usage:
  python3 matcrop.py <input> <output.work.jpg> [--tol N] [--quality Q] [--no-crop]

--tol      per-channel tolerance for "same as border" (default 18)
--quality  JPEG quality (default 85)
--no-crop  skip mat detection, only re-encode (for full-bleed images)
"""
import sys
from PIL import Image, ImageChops


def corner_bg(img, s=12):
    w, h = img.size
    s = max(1, min(s, w // 4, h // 4))
    boxes = [(0, 0, s, s), (w - s, 0, w, s), (0, h - s, s, h), (w - s, h - s, w, h)]
    px = []
    for b in boxes:
        c = img.crop(b)
        px.append(tuple(round(v) for v in c.resize((1, 1)).getpixel((0, 0))))
    # median per channel across the 4 corners (robust to one busy corner)
    return tuple(sorted(ch)[1] for ch in zip(*px))


def matcrop(src, dst, tol=18, quality=85, do_crop=True):
    im = Image.open(src)
    im = im.convert("RGB")
    box = None
    if do_crop:
        bg = corner_bg(im)
        bgimg = Image.new("RGB", im.size, bg)
        diff = ImageChops.difference(im, bgimg).convert("L")
        # threshold: anything beyond tolerance counts as "artwork"
        mask = diff.point(lambda p: 255 if p > tol else 0)
        box = mask.getbbox()
        w, h = im.size
        if box:
            bw, bh = box[2] - box[0], box[3] - box[1]
            # ignore if "crop" is basically the whole image (no real mat)
            if bw >= w * 0.985 and bh >= h * 0.985:
                box = None
    if box:
        im = im.crop(box)
    im.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)
    # No crop + already-small JPEG that didn't shrink → keep original bytes
    # (avoid re-encode bloat / quality loss). Cropped or non-JPEG keeps encoded.
    import os
    src_jpeg = src.lower().endswith((".jpg", ".jpeg"))
    if box is None and src_jpeg and os.path.getsize(dst) >= os.path.getsize(src):
        import shutil
        shutil.copyfile(src, dst)
        return (src, im.size, box, "copied-original")
    return (src, im.size, box, "encoded")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        sys.exit(1)
    src, dst = a[0], a[1]
    tol = int(a[a.index("--tol") + 1]) if "--tol" in a else 18
    q = int(a[a.index("--quality") + 1]) if "--quality" in a else 85
    crop = "--no-crop" not in a
    r = matcrop(src, dst, tol, q, crop)
    print(f"{r[0]} -> {dst}  size={r[1]}  cropbox={r[2]}")
