"""Build and execute notebooks/starter.ipynb (needs nbformat, nbclient, ipykernel)."""
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient

REPO = Path(__file__).resolve().parents[1]
GH = "https://raw.githubusercontent.com/montessoritheory/montessori-teacher-training-programs/main"
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

cells = [
    md(f"""# Montessori Teacher Training Programs Worldwide, Starter Notebook

![cover]({GH}/images/cover.png)

This notebook loads the dataset and answers four quick questions about Montessori teacher training. Programs come from the MACTE accredited program search and the AMI list of training centres. Companion directory with a page per country, [Montessori School Finder](https://www.montessorischoolfinder.com/montessori-certifications/training-centers/). Dataset by [Montessori Theory](https://www.montessori-theory.com/) and Montessori School Finder, CC BY 4.0."""),
    code(f"""import os, pandas as pd, matplotlib.pyplot as plt

# works on Kaggle, locally, and straight from GitHub
KAGGLE = "/kaggle/input/montessori-teacher-training-programs"
LOCAL = next((p for p in ["data", "../data"] if os.path.exists(p)), "data")
GITHUB = "{GH}/data"
base = KAGGLE if os.path.exists(KAGGLE) else LOCAL if os.path.exists(LOCAL) else GITHUB
sep = "/" if base != LOCAL else os.sep
read = lambda name: pd.read_csv(base + sep + name)

programs = read("programs.csv").fillna("")
by_country = read("by_country.csv")
programs.shape"""),
    code("""plt.rcParams.update({"figure.facecolor": "#f8fafc", "axes.facecolor": "white", "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": "#e2e8f0", "font.size": 12})
INK, BLUE, GREEN = "#0f172a", "#2563eb", "#059669\""""),
    md("## 1. How many programs, and where?\n\n`listed_by` says which list a program is on. A program can be on both."),
    code("""print(len(programs), "programs in", programs.country.nunique(), "countries")
programs.listed_by.value_counts()"""),
    code("""top = by_country.head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(top.country, top.programs, color=BLUE)
for y, v in enumerate(top.programs): ax.text(v + 1, y, v, va="center")
ax.set_title("Programs per country, top 10", loc="left", fontweight="bold")
plt.show()
by_country[["rank", "country", "programs", "macte_listed", "ami_listed", "both"]].head(10)"""),
    md("## 2. Which levels can you train for?\n\nMACTE gives levels. The AMI list mostly does not, so 101 AMI-only centres have `levels_published` set to False."),
    code("""has = programs[programs.levels_published]
flags = ["level_infant_toddler", "level_early_childhood", "level_elementary", "level_secondary"]
levels = has[flags].sum().rename(lambda s: s.replace("level_", "").replace("_", " ").title())
print(len(has), "programs publish levels")
levels"""),
    md("## 3. MACTE accredited programs by delivery format\n\n`delivery_format` is MACTE's share of hours online."),
    code("""macte = programs[programs.macte_listed]
macte.delivery_format.replace("", "Not published").value_counts()"""),
    md("## 4. Find a program\n\nEarly Childhood programs outside the United States, with the Montessori School Finder page to read more."),
    code("""found = programs[programs.level_early_childhood & (programs.country != "United States")]
found[["name", "city", "country", "listed_by", "msf_url"]].sort_values(["country", "city"]).head(15)"""),
    md("""## Read With Care

- This is a snapshot of two public listings read in November 2026. Check dates, fees and entry rules with each program.
- `macte_status` copies what MACTE shows. A program that is not MACTE listed may still be recognized elsewhere.
- Coordinates are city centres, not street addresses.

Credit **Montessori Theory** and **Montessori School Finder** (CC BY 4.0), and the MACTE and AMI listings as sources."""),
]
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
out = REPO / "notebooks" / "starter.ipynb"
NotebookClient(nb, timeout=120, resources={"metadata": {"path": str(REPO / "notebooks")}}).execute()
nbf.write(nb, out)
print("notebook executed", out)
