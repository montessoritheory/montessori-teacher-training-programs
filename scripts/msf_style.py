"""Shared look for the Montessori School Finder open datasets: ink, blue, green, soft backgrounds, rounded cards."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK, BLUE, GREEN = "#0f172a", "#2563eb", "#059669"
SOFT, MINT, LINE, MUTED = "#f8fafc", "#ecfdf5", "#e2e8f0", "#64748b"
FOOTER = "Montessori School Finder × Montessori Theory"

def setup():
    plt.rcParams.update({
        "font.family": ["Segoe UI", "Arial", "DejaVu Sans"], "figure.facecolor": SOFT, "axes.facecolor": "white",
        "axes.edgecolor": LINE, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "text.color": INK, "font.size": 13,
    })

def card(ax, x, y, w, h, fc="white", ec=LINE, r=0.02, lw=1.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw,
                                transform=ax.transAxes, mutation_aspect=0.5))

def chart_frame(title, subtitle, figsize=(11, 6.2)):
    fig = plt.figure(figsize=figsize, dpi=150)
    fig.text(0.04, 0.945, title, fontsize=20, fontweight="bold", va="top")
    fig.text(0.04, 0.885, subtitle, fontsize=12.5, color=MUTED, va="top")
    fig.text(0.04, 0.025, FOOTER + "  ·  montessorischoolfinder.com  ·  CC BY 4.0", fontsize=9.5, color=MUTED)
    return fig

def cover(path, title, kicker, big, big_label, chips):
    """1600x800 cover: kicker, title, one key number, three small stat chips, footer line."""
    setup()
    fig = plt.figure(figsize=(16, 8), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, fc=SOFT, ec="none"))
    ax.add_patch(plt.Rectangle((0.64, 0), 0.36, 1, fc=MINT, ec="none"))
    card(ax, 0.045, 0.12, 0.91, 0.76, fc="white", r=0.025)
    ax.add_patch(FancyBboxPatch((0.085, 0.76), 0.012, 0.075, boxstyle="round,pad=0,rounding_size=0.004", fc=BLUE, ec="none"))
    ax.text(0.108, 0.797, kicker.upper(), fontsize=15, color=BLUE, fontweight="bold", va="center")
    ax.text(0.085, 0.62, title, fontsize=40, fontweight="bold", color=INK, va="center", linespacing=1.15)
    ax.text(0.085, 0.37, big, fontsize=84, fontweight="bold", color=BLUE, va="center")
    ax.text(0.085 + 0.0415 * len(big) + 0.012, 0.355, big_label, fontsize=22, color=INK, va="center")
    x = 0.085
    for label in chips:
        w = 0.0105 * len(label) + 0.035
        card(ax, x, 0.17, w, 0.075, fc=MINT, ec="#a7f3d0", r=0.03)
        ax.text(x + w / 2, 0.2075, label, fontsize=15, color="#065f46", ha="center", va="center", fontweight="bold")
        x += w + 0.015
    ax.text(0.085, 0.06, FOOTER, fontsize=15, color=MUTED, ha="left", va="center")
    fig.savefig(path, dpi=100, facecolor=SOFT); plt.close(fig)
