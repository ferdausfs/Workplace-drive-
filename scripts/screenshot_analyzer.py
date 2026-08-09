#!/usr/bin/env python3
"""
screenshot_analyzer.py — programmatic screenshot & image analysis tool.

The agent has no built-in vision in this environment, so this tool gives real,
reproducible image analysis:
  1. Metadata      — dimensions, aspect, mode, file size
  2. Palette       — top dominant colors (quantized), light/dark verdict
  3. Exposure      — mean luminance, contrast, brightness histogram summary
  4. OCR           — extract visible text (RapidOCR, English/Latin + some scripts)
  5. Layout zones  — simple top/middle/bottom brightness so UI structure is inferable

Usage:  python3 screenshot_analyzer.py <image> [--ocr-only]
"""
import sys, os
from collections import Counter
from PIL import Image, ImageStat

def analyze(path: str, do_ocr: bool = True):
    img = Image.open(path).convert('RGB')
    w, h = img.size
    print(f"── IMAGE ───────────────────────────────────────────────")
    print(f"  file     : {os.path.basename(path)} ({os.path.getsize(path)/1024:.0f} KB)")
    print(f"  size     : {w}×{h} px  |  aspect {w/h:.3f}  ({'portrait' if h>w else 'landscape'})")
    print(f"  mode     : {Image.open(path).mode}")

    # palette
    small = img.resize((64, 64))
    q = small.quantize(colors=8, method=Image.MEDIANCUT)
    counts = Counter(q.getdata())
    print(f"── PALETTE (top 6) ─────────────────────────────────────")
    for idx, cnt in counts.most_common(6):
        rgb = q.getpalette()[idx*3:idx*3+3]
        print(f"  #{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}  {cnt/4096*100:4.1f}%  rgb{rgb}")

    # exposure
    stat = ImageStat.Stat(img)
    mr, mg, mb = stat.mean[:3]
    mean_l = 0.299*mr + 0.587*mg + 0.114*mb
    # use grayscale contrast
    gray = img.convert('L')
    gstat = ImageStat.Stat(gray)
    print(f"── EXPOSURE ────────────────────────────────────────────")
    print(f"  mean luminance : {mean_l:.0f}/255  →  {'light theme' if mean_l > 128 else 'dark theme'}")
    print(f"  stddev (contrast): {gstat.stddev[0]:.0f}")

    # zones (3 rows brightness) — helps infer UI layout
    rows = []
    for i in range(3):
        box = (0, int(h*i/3), w, int(h*(i+1)/3))
        z = ImageStat.Stat(gray.crop(box)).mean[0]
        rows.append(f"{z:.0f}")
    print(f"── ZONES (brightness top→bottom) ───────────────────────")
    print(f"  [{', '.join(rows)}]  ({'0=black 255=white'})")

    if do_ocr:
        print(f"── OCR TEXT ───────────────────────────────────────────")
        try:
            from rapidocr_onnxruntime import RapidOCR
            engine = RapidOCR()
            result, _ = engine(str(path))
            if not result:
                print("  (কোনো text পাওয়া যায়নি)")
            else:
                lines = []
                for item in result:
                    box = item[0]
                    text = item[1]
                    try:
                        conf = float(item[2])
                    except (TypeError, ValueError):
                        conf = 0.0
                    y = int(min(p[1] for p in box))
                    lines.append((y, text, conf))
                lines.sort()
                for y, text, conf in lines:
                    print(f"  y={y:4d}  {text}   (conf {conf:.2f})")
        except Exception as e:
            print(f"  OCR error: {e}")

if __name__ == '__main__':
    p = sys.argv[1]
    analyze(p, '--ocr-only' not in sys.argv)
