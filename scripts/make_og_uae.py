# regula-ignore
"""Generate og-uae.png (1200x630) — UAE-specific OG/Twitter share image.

Matches Regula brand: dark background (#070711), blue accent (#3b82f6),
minimal DIFC-style skyline silhouette, no third-party assets.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "og-uae.png"

W, H = 1200, 630
BG = (7, 7, 17)
TEXT = (255, 255, 255)
MUTED = (170, 170, 192)
ACCENT = (59, 130, 246)
ACCENT_SOFT = (125, 211, 252)

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img, "RGBA")

# Soft radial glow (blue, top-left)
for r in range(600, 0, -40):
    alpha = max(0, int(18 * (r / 600)))
    draw.ellipse((-200 - r, -200 - r, -200 + r, -200 + r),
                 fill=(59, 130, 246, alpha))

# Accent bar
draw.rectangle((64, 72, 120, 80), fill=ACCENT)

F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

f_brand = ImageFont.truetype(F_BOLD, 34)
f_pill = ImageFont.truetype(F_MONO, 18)
f_h1 = ImageFont.truetype(F_BOLD, 64)
f_sub = ImageFont.truetype(F_REG, 26)
f_foot = ImageFont.truetype(F_MONO, 22)

# Brand + pill
draw.text((64, 100), "Regula", font=f_brand, fill=TEXT)
pill_text = "  v1.6 · UAE  "
bbox = draw.textbbox((0, 0), pill_text, font=f_pill)
pw, ph = bbox[2] - bbox[0], bbox[3] - bbox[1]
px, py = 240, 112
draw.rounded_rectangle((px, py, px + pw + 16, py + ph + 14),
                       radius=14, fill=(59, 130, 246, 40))
draw.text((px + 8, py + 4), pill_text, font=f_pill, fill=ACCENT_SOFT)

# Headline (two lines)
draw.text((64, 200), "EU AI Act compliance", font=f_h1, fill=TEXT)
draw.text((64, 278), "for UAE & GCC teams", font=f_h1, fill=TEXT)

# Accent underline
draw.rectangle((64, 364, 360, 368), fill=ACCENT)

# Subtitle
draw.text((64, 392),
          "Free open-source CLI. Audits your codebase against",
          font=f_sub, fill=MUTED)
draw.text((64, 426),
          "EU AI Act risk patterns — in one command.",
          font=f_sub, fill=MUTED)

# Minimalist DIFC/Burj skyline silhouette (bottom-right, geometric)
def tower(x, base_w, height, taper=0.35):
    """Draw a tapered tower polygon."""
    top_w = base_w * taper
    cx = x + base_w / 2
    pts = [
        (x, H - 80),
        (x + base_w, H - 80),
        (cx + top_w / 2, H - 80 - height),
        (cx, H - 80 - height - base_w * 0.25),  # spire
        (cx - top_w / 2, H - 80 - height),
    ]
    draw.polygon(pts, fill=(30, 41, 80))

# Low-rise base
draw.rectangle((760, H - 80, W - 40, H - 60), fill=(30, 41, 80))
# Supporting towers
tower(780, 44, 120)
tower(830, 54, 160)
tower(895, 46, 100)
# Hero "Burj" tower — slender + tall
burj_x, burj_base, burj_h = 970, 62, 300
tower(burj_x, burj_base, burj_h, taper=0.18)
# Additional small towers right of Burj
tower(1055, 38, 90)
tower(1100, 50, 140)

# Footer strip
draw.rectangle((0, H - 48, W, H), fill=(12, 12, 24))
draw.text((64, H - 38), "getregula.com", font=f_foot, fill=ACCENT_SOFT)
right = "DIFC · ADGM · GCC"
rbbox = draw.textbbox((0, 0), right, font=f_foot)
draw.text((W - 64 - (rbbox[2] - rbbox[0]), H - 38),
          right, font=f_foot, fill=MUTED)

img.save(OUT, "PNG", optimize=True)
print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
