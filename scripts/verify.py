"""Checks. Totals must add up to programs.csv, and 10 rows are compared with the raw MACTE and AMI files.
Usage: python verify.py [--root PATH_TO_MSF_REPO]"""
import argparse, json
from pathlib import Path
import pandas as pd
from build_programs import norm, domain

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=str(Path(__file__).resolve().parents[4]))
root = Path(ap.parse_args().root)
D = Path(__file__).resolve().parents[1] / "data"
p = pd.read_csv(D / "programs.csv").fillna("")
n = len(p)

c = pd.read_csv(D / "by_country.csv")
a = pd.read_csv(D / "by_accreditation.csv")
lv = pd.read_csv(D / "by_level.csv")
assert c.programs.sum() == n and len(c) == p.country.nunique()
assert a.programs.sum() == n
assert lv[lv.level.str.startswith("(")].programs.iloc[0] + p.levels_published.sum() == n
assert (c.macte_listed.sum(), c.ami_listed.sum(), c.both.sum()) == (p.macte_listed.sum(), p.ami_listed.sum(), (p.listed_by == "MACTE and AMI").sum())
assert p.macte_listed.sum() + p.ami_listed.sum() - c.both.sum() == n
assert p.msf_url.str.startswith("https://www.montessorischoolfinder.com/montessori-certifications/training-centers/").all()
print("totals add up", n)

macte = json.loads((root / "data/raw/training/macte.json").read_text(encoding="utf8"))
ami = json.loads((root / "data/raw/training/ami.json").read_text(encoding="utf8"))
sample = p.sample(10, random_state=7)
ok = 0
for _, r in sample.iterrows():
    hits = []
    if r.macte_listed:
        hits += [x for x in macte if norm(x["name"]) == norm(r["name"]) and norm(x["city"]) == norm(r.city)]
    if r.ami_listed:
        hits += [x for x in ami if norm(x["name"]) == norm(r["name"]) and norm(x["city"] or "") == norm(r.city)]
    good = bool(hits) and (not r.website or any(domain(h.get("website")) == domain(r.website) for h in hits))
    ok += good
    print("OK " if good else "?? ", r["name"], "|", r.city, "|", r.country, "|", r.listed_by, "|", len(hits), "raw rows")
print(ok, "of 10 match the raw files")
