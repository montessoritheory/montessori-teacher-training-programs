"""Cover and charts from the tables in ../data. Run build_programs.py first.
World outlines come from Natural Earth (public domain), downloaded once into ../../_raw."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import msf_style as S

HERE = Path(__file__).resolve().parent
DATA, IMG = HERE.parent / "data", HERE.parent / "images"
RAW = HERE.parent.parent / "_raw"
IMG.mkdir(exist_ok=True)

df = pd.read_csv(DATA / "programs.csv").fillna("")
bc = pd.read_csv(DATA / "by_country.csv")
n = len(df)
n_countries = df.country.nunique()
macte, ami = int(df.macte_listed.sum()), int(df.ami_listed.sum())
both = int((df.listed_by == "MACTE and AMI").sum())
with_levels = int(df.levels_published.sum())
us = int(bc.programs.iloc[0])
SRC = "Sources: MACTE accredited program search, AMI list of training centres, Montessori School Finder. Checked 2026-11-14."

# ---- cover
S.cover(IMG / "cover.png", HERE / "cover_photo.jpg", "Montessori Teacher\nTraining Programs Worldwide",
        "Open dataset  ·  AMI and MACTE", f"{n}", f"training programs\nin {n_countries} countries",
        [f"{macte} MACTE listed", f"{ami} AMI centres", f"{both} on both lists"],
        "Photo: Anil Sharma, Pexels", accent=S.VIOLET, flip=True, focus=(0.5, 0.55))

# ---- key numbers
S.key_numbers(IMG / "key_numbers.png", "Montessori Teacher Training in Six Numbers",
              "What the list holds, from the two public sources behind a Montessori certification.", SRC, [
                  (f"{n}", "training programs in the file", S.VIOLET),
                  (f"{n_countries}", "countries with at least one program", S.BLUE),
                  (f"{macte}", "listed in the MACTE accredited program search", S.TEAL),
                  (f"{ami}", "listed as AMI training centres", S.GREEN),
                  (f"{both}", "on both lists", S.AMBER),
                  (f"{us / n:.1%}".replace("%", " %"), f"of all programs are in the United States ({us})", S.CORAL),
              ], accent=S.VIOLET)

# ---- world bubble map
world = S.World(S.natural_earth(RAW))
alias = {"United States": "United States of America", "Ivory Coast": "Côte d'Ivoire", "The Netherlands": "Netherlands"}
extra = {"Bahrain": (50.55, 26.07)}  # too small for the 110m outlines, drawn from its coordinates
p = S.Page("Where Montessori Teacher Training Is Offered",
           f"Programs per country. Bubble area follows the count. The United States holds {us} of {n}.",
           SRC, accent=S.VIOLET, size=(1400, 880))
ax = p.axes(50, p.top - 10, 1300, p.bottom - p.top - 10)
world.draw(ax, lambda c, nm: "#e7ecf3")
k = 4.1 / 235 * 1.0
lab = {"United States": (0, -0.02), "China": (0, 0), "Canada": (0, 0), "Mexico": (0, 0), "Spain": (0, 0), "Vietnam": (0, 0)}
for _, r in bc.sort_values("programs", ascending=False).iterrows():
    nm = alias.get(r.country, r.country)
    if nm in extra:
        x, y = world.point(*extra[nm])
    else:
        c = world.centroid(None, nm)
        if c is None:
            print("no outline for", r.country); continue
        x, y = c
    rad = k * np.sqrt(r.programs) * 1.25
    ax.add_patch(Circle((x, y), rad, fc=S.VIOLET, ec="white", lw=1.4, alpha=0.62, zorder=3))
    if r.programs >= 8:
        ax.text(x, y, f"{r.programs}", ha="center", va="center", fontsize=12 if r.programs < 100 else 22, fontweight="bold", color="white", zorder=4)
# legend
lx, ly = 90, p.bottom - 20
for i, v in enumerate([1, 10, 50]):
    r_px = 4.1 * np.sqrt(v) * 1.25
    p.ax.add_patch(Circle((lx + 30 + i * 110, ly - 30), r_px, fc=S.VIOLET, ec="white", alpha=0.62, zorder=5))
    p.ax.text(lx + 30 + i * 110 + r_px + 8, ly - 30, f"{v}", fontsize=12.5, color=S.MUTED, va="center", zorder=5)
p.ax.text(lx, ly - 80, "Programs in the country", fontsize=12.5, color=S.MUTED, zorder=5)
p.save(IMG / "world_map.png")

# ---- dumbbell, MACTE against AMI in the 12 largest countries
top = bc.head(12)
p = S.Page("MACTE or AMI, Country by Country",
           f"The 12 countries with the most programs, with the count on each list. Total programs on the right.",
           SRC, accent=S.BLUE, size=(1400, 880))
ax = p.axes(250, p.top - 4, 880, p.bottom - p.top - 6)
ys = np.arange(len(top))[::-1]
for y, (_, r) in zip(ys, top.iterrows()):
    for off, v, col in ((0.18, r.macte_listed, S.BLUE), (-0.18, r.ami_listed, S.GREEN)):
        ax.plot([0, v], [y + off, y + off], color=S.mix(col, "#ffffff", 0.5), lw=3, solid_capstyle="round", zorder=2)
        ax.scatter([v], [y + off], s=150, color=col, edgecolor="white", linewidth=1.6, zorder=3)
        ax.text(v + 3, y + off, f"{v}", fontsize=11, color=col, va="center", fontweight="bold")
ax.set_yticks(ys); ax.set_yticklabels(top.country, fontsize=13.5)
ax.set_xlim(-2, 190); ax.set_ylim(-0.7, len(top) - 0.3)
ax.xaxis.grid(True, color=S.GRID, lw=1.2); ax.tick_params(axis="y", length=0, pad=10); ax.tick_params(axis="x", length=0, labelsize=11)
ax.spines["bottom"].set_visible(False)
ax2 = ax.twinx(); ax2.set_ylim(ax.get_ylim()); ax2.set_yticks(ys)
ax2.set_yticklabels([f"{v} programs" for v in top.programs], fontsize=13, fontweight="bold")
ax2.tick_params(length=0, pad=16)
for s in ax2.spines.values(): s.set_visible(False)
ax2.patch.set_alpha(0)
p.ax.scatter([480], [p.top - 8], s=140, color=S.BLUE, zorder=5); p.ax.text(498, p.top - 8, "Listed by MACTE", fontsize=13, va="center", zorder=5)
p.ax.scatter([700], [p.top - 8], s=140, color=S.GREEN, zorder=5); p.ax.text(718, p.top - 8, "Listed as AMI centre", fontsize=13, va="center", zorder=5)
p.save(IMG / "countries_by_list.png")

# ---- donut of the lists + levels lollipop
p = S.Page("Which List, and Which Levels",
           f"Left, the {n} programs by list. Right, programs per level among the {with_levels} that publish levels.",
           SRC, accent=S.TEAL, size=(1400, 880))
a1 = p.axes(90, p.top + 10, 440, 440)
only_m, only_a = macte - both, ami - both
S.donut(a1, [only_m, both, only_a], [S.BLUE, S.AMBER, S.GREEN], f"{n}", "programs")
for i, (lab_, v, c) in enumerate([("MACTE only", only_m, S.BLUE), ("Both lists", both, S.AMBER), ("AMI only", only_a, S.GREEN)]):
    y = p.top + 530 + i * 0
    x = 90 + i * 165
    p.ax.scatter([x + 8], [p.top + 500], s=120, color=c, zorder=5)
    p.ax.text(x + 24, p.top + 500, f"{lab_}", fontsize=12.5, va="center", zorder=5)
    p.ax.text(x + 24, p.top + 526, f"{v}  ({v / n:.0%})", fontsize=12.5, va="center", fontweight="bold", color=c if c != S.AMBER else "#b45309", zorder=5)
a2 = p.axes(780, p.top + 20, 490, 420)
lv = [("Early Childhood\n3 to 6", df.level_early_childhood.sum(), S.TEAL), ("Infant and Toddler\n0 to 3", df.level_infant_toddler.sum(), S.BLUE),
      ("Elementary\n6 to 12", df.level_elementary.sum(), S.VIOLET), ("Secondary\n12 to 18", df.level_secondary.sum(), S.CORAL)]
S.lollipop(a2, [a for a, _, _ in lv], [int(b) for _, b, _ in lv], [c for _, _, c in lv], xmax=260,
           note=lambda v: f"{v}  ({v / with_levels:.0%})")
a2.set_xticks([])
p.save(IMG / "levels_and_lists.png")
print("ok")
