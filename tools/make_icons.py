#!/usr/bin/env python3

import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

PATH_D = "M9 2.5v15M5.5 6h7M9 13.2c2.2-3.4 8.6-3.2 8.2 1.6-.3 3.2-4 4.2-3.4 8.2.2 1.2 1 2 2 2.2"
LINES = [((9.0, 2.5), (9.0, 17.5)), ((5.5, 6.0), (12.5, 6.0))]
CUBICS = [
    ((9.0, 13.2), (11.2, 9.8), (17.6, 10.0), (17.2, 14.8)),
    ((17.2, 14.8), (16.9, 18.0), (13.2, 19.0), (13.8, 23.0)),
    ((13.8, 23.0), (14.0, 24.2), (14.8, 25.0), (15.8, 25.2)),
]

VARIANTS = {
    "site": dict(
        bg="#100e0b",
        stops=[(0.0, "#8f6f2e"), (0.375, "#e8cc8c"), (1.0, "#8f6f2e")],
        radius=4.3,
    ),
    "github": dict(
        bg="#111111",
        stops=[(0.0, "#20880c"), (0.375, "#6fcf6f"), (1.0, "#20880c")],
        radius=0.0,
    ),
}


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def segments():
    segs = list(LINES)
    for p0, p1, p2, p3 in CUBICS:
        prev = p0
        for i in range(1, 49):
            t = i / 48
            u = 1 - t
            x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
            y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
            segs.append((prev, (x, y)))
            prev = (x, y)
    return segs


SEGS = segments()
XS = [p[0] for s in SEGS for p in s]
YS = [p[1] for s in SEGS for p in s]
CENTRE = ((min(XS) + max(XS)) / 2, (min(YS) + max(YS)) / 2)
SIGN_H = max(YS) - min(YS)


def placement(height_frac, stroke_frac):
    total = height_frac * 24
    stroke = stroke_frac * total
    scale = (total - stroke) / SIGN_H
    tx, ty = 12 - CENTRE[0] * scale, 12 - CENTRE[1] * scale
    return scale, stroke, tx, ty


def grad_line(scale, stroke, tx, ty):
    x0 = min(XS) * scale + tx - stroke / 2
    x1 = max(XS) * scale + tx + stroke / 2
    y0 = min(YS) * scale + ty - stroke / 2
    y1 = max(YS) * scale + ty + stroke / 2
    w, h = x1 - x0, y1 - y0
    a = math.radians(120)
    dx, dy = math.sin(a), -math.cos(a)
    length = abs(w * math.sin(a)) + abs(h * math.cos(a))
    cx, cy = x0 + w / 2, y0 + h / 2
    return cx - dx * length / 2, cy - dy * length / 2, cx + dx * length / 2, cy + dy * length / 2


def render(size, variant, height_frac, stroke_frac):
    v = VARIANTS[variant]
    scale, stroke, tx, ty = placement(height_frac, stroke_frac)
    gx1, gy1, gx2, gy2 = grad_line(scale, stroke, tx, ty)
    gvx, gvy = gx2 - gx1, gy2 - gy1
    glen2 = gvx * gvx + gvy * gvy
    stops = [(o, np.array(rgb(c), dtype=np.float32)) for o, c in v["stops"]]
    bg = np.array(rgb(v["bg"]), dtype=np.float32)
    px_unit = 24 / size
    radius = v["radius"]
    segs = [((ax * scale + tx, ay * scale + ty), (bx * scale + tx, by * scale + ty))
            for (ax, ay), (bx, by) in SEGS]

    out = np.zeros((size, size, 4), dtype=np.uint8)
    xs = ((np.arange(size, dtype=np.float32) + 0.5) * px_unit)
    chunk = max(1, 2_000_000 // size)
    for r0 in range(0, size, chunk):
        r1 = min(size, r0 + chunk)
        ys = ((np.arange(r0, r1, dtype=np.float32) + 0.5) * px_unit)
        px, py = np.meshgrid(xs, ys)

        if radius > 0:
            qx = np.clip(np.abs(px - 12) - (12 - radius), 0, None)
            qy = np.clip(np.abs(py - 12) - (12 - radius), 0, None)
            d_bg = np.hypot(qx, qy) - radius
            bg_cov = np.clip(0.5 - d_bg / px_unit, 0, 1)
        else:
            bg_cov = np.ones_like(px)

        dist = np.full(px.shape, np.inf, dtype=np.float32)
        for (ax, ay), (bx, by) in segs:
            vx, vy = bx - ax, by - ay
            ll = vx * vx + vy * vy
            h = np.clip(((px - ax) * vx + (py - ay) * vy) / ll, 0, 1) if ll else 0
            np.minimum(dist, np.hypot(px - ax - h * vx, py - ay - h * vy), out=dist)
        ink_cov = np.clip(0.5 - (dist - stroke / 2) / px_unit, 0, 1)

        t = np.clip(((px - gx1) * gvx + (py - gy1) * gvy) / glen2, 0, 1)
        ink = np.zeros(px.shape + (3,), dtype=np.float32)
        for (o0, c0), (o1, c1) in zip(stops, stops[1:]):
            m = (t >= o0) & (t <= o1)
            f = ((t - o0) / (o1 - o0))[..., None]
            ink[m] = (c0 * (1 - f) + c1 * f)[m]

        col = bg * (1 - ink_cov[..., None]) + ink * ink_cov[..., None]
        out[r0:r1, :, :3] = col.clip(0, 255).round().astype(np.uint8)
        out[r0:r1, :, 3] = (bg_cov * 255).round().astype(np.uint8)
    return Image.fromarray(out, "RGBA" if radius > 0 else "RGBA").convert("RGBA" if radius > 0 else "RGB")


def svg(variant, height_frac, stroke_frac, size):
    v = VARIANTS[variant]
    scale, stroke, tx, ty = placement(height_frac, stroke_frac)
    x1, y1, x2, y2 = grad_line(scale, stroke, tx, ty)
    stops = "\n".join(f'      <stop offset="{o}" stop-color="{c}"/>' for o, c in v["stops"])
    rx = f' rx="{v["radius"]}"' if v["radius"] else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">
  <defs>
    <linearGradient id="g" gradientUnits="userSpaceOnUse" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}">
{stops}
    </linearGradient>
  </defs>
  <rect width="24" height="24"{rx} fill="{v['bg']}"/>
  <path transform="translate({tx:.3f} {ty:.3f}) scale({scale:.4f})" d="{PATH_D}" fill="none" stroke="url(#g)" stroke-width="{stroke / scale:.3f}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


def clean(d):
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*"):
        f.unlink()
    return d


def main():
    site = clean(ROOT / "static" / "icons")
    big = dict(height_frac=0.74, stroke_frac=0.105)
    tab = dict(height_frac=0.84, stroke_frac=0.15)
    render(180, "site", **big).save(site / "apple-touch-icon.png")
    render(512, "site", **big).save(site / "icon-512.png")
    (site / "favicon.svg").write_text(svg("site", size=64, **tab))
    favs = [render(s, "site", **tab) for s in (16, 32, 48)]
    for im, s in zip(favs, (16, 32, 48)):
        im.save(site / f"favicon-{s}.png")
    favs[-1].save(site / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    gh = clean(ROOT / "art" / "github-avatar")
    avatar = dict(height_frac=0.46, stroke_frac=0.105)
    (gh / "saturn-green.svg").write_text(svg("github", size=1024, **avatar))
    master = render(4096, "github", **avatar)
    master.save(gh / "saturn-green-4096.png", optimize=True)
    for s in (2048, 1024, 460):
        master.resize((s, s), Image.LANCZOS).save(gh / f"saturn-green-{s}.png", optimize=True)

    for d in (site, gh):
        for f in sorted(d.iterdir()):
            print(f"  {f.relative_to(ROOT)}  {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
