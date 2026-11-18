"""Cover and charts from the tables in ../data. Run build_programs.py first."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import msf_style as S

HERE = Path(__file__).resolve().parent
DATA, IMG = HERE.parent / "data", HERE.parent / "images"
IMG.mkdir(exist_ok=True)
S.setup()
df = pd.read_csv(DATA / "programs.csv").fillna("")
bc = pd.read_csv(DATA / "by_country.csv")
bl = pd.read_csv(DATA / "by_level.csv")

n = len(df)
macte, ami = int(df.macte_listed.sum()), int(df.ami_listed.sum())
both = int((df.listed_by == "MACTE and AMI").sum())
S.cover(IMG / "cover.png", "Montessori Teacher\nTraining Programs Worldwide", "Open dataset · AMI and MACTE",
        f"{n}", f"programs in {df.country.nunique()} countries",
        [f"{macte} MACTE listed", f"{ami} AMI centres", f"{both} on both lists"])

# Chart 1, top countries, stacked by list
top = bc.head(12).iloc[::-1]
fig = S.chart_frame("Where Montessori Teacher Training Is Offered",
                    f"Programs per country, the 12 largest of {df.country.nunique()}. The United States holds {int(bc.programs.iloc[0])} of {n}.")
ax = fig.add_axes([0.2, 0.12, 0.74, 0.7])
only_m = top.macte_listed - top.both; only_a = top.ami_listed - top.both
ax.barh(top.country, only_m, color=S.BLUE, label="MACTE", height=0.62)
ax.barh(top.country, top.both, left=only_m, color=S.INK, label="Both lists", height=0.62)
ax.barh(top.country, only_a, left=only_m + top.both, color=S.GREEN, label="AMI", height=0.62)
for y, t in enumerate(top.programs): ax.text(t + 1.5, y, str(t), va="center", fontsize=12, fontweight="bold")
ax.xaxis.grid(True, color=S.LINE); ax.set_axisbelow(True); ax.tick_params(length=0)
ax.legend(frameon=False, loc="lower right", fontsize=12)
fig.savefig(IMG / "top_countries.png", facecolor=S.SOFT); plt.close(fig)

# Chart 2, levels (left) and listing (right)
fig = S.chart_frame("Levels And Lists", f"Left, programs per level among the {int(df.levels_published.sum())} that publish levels. Right, which list each of the {n} programs is on.", figsize=(11, 6.2))
a1 = fig.add_axes([0.2, 0.12, 0.33, 0.7])
lv = bl[~bl.level.str.startswith("(")].sort_values("programs").tail(8)
a1.barh(lv.level, lv.programs, color=S.BLUE, height=0.62)
for y, t in enumerate(lv.programs): a1.text(t + 2, y, str(t), va="center", fontsize=11, fontweight="bold")
a1.set_xlim(0, 240); a1.xaxis.grid(True, color=S.LINE); a1.set_axisbelow(True); a1.tick_params(length=0)
a2 = fig.add_axes([0.6, 0.12, 0.36, 0.7])
lb = df.listed_by.value_counts().reindex(["MACTE", "MACTE and AMI", "AMI"])
a2.bar(["MACTE\nonly", "Both\nlists", "AMI\nonly"], lb.values, color=[S.BLUE, S.INK, S.GREEN], width=0.6)
for x, v in enumerate(lb.values): a2.text(x, v + 4, str(v), ha="center", fontsize=12, fontweight="bold")
a2.yaxis.grid(True, color=S.LINE); a2.set_axisbelow(True); a2.tick_params(length=0)
fig.savefig(IMG / "levels_and_lists.png", facecolor=S.SOFT); plt.close(fig)
print("ok")
