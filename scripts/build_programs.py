"""Build the training programs tables from the Montessori School Finder inputs.

Inputs (read only), defaults point at the MSF repository layout:
  site/src/data/training-centers.json   merged and geocoded list shown on the site
  data/raw/training/macte.json          MACTE accredited program search, as collected
  data/raw/training/ami.json            AMI list of training centres, as collected

Usage: python build_programs.py [--root PATH_TO_MSF_REPO] [--out ../data]
Writes programs.csv, by_country.csv, by_level.csv, by_accreditation.csv.
"""
import argparse, json, re, unicodedata
from pathlib import Path
import pandas as pd

BASE = "https://www.montessorischoolfinder.com/montessori-certifications/training-centers/"
MIN_COUNTRY_PAGE = 3  # the site builds a country page from 3 programs

def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower().replace("&", " and "))
    s = re.sub(r"[̀-ͯ]", "", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()

def domain(u):
    if not u: return ""
    m = re.sub(r"^https?://", "", u.strip().lower()).split("/")[0]
    return re.sub(r"^www\.", "", m)

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", norm(s)).strip("-")

def clean_levels(levels):
    """AMI publishes age bands as free text, split on commas upstream. Map them to the MACTE level names.
    Assumption: AMI 0-3 = Infant and Toddler, 3-6 = Early Childhood, 6-12 = Elementary I-II, 12-18 = Secondary I-II."""
    joined = ", ".join(levels)
    if not re.search(r"\d+-\d+", joined):
        return levels
    out = []
    for key, name in (("Infancy|0-3", "Infant and Toddler"), ("Primary|3-6", "Early Childhood"),
                      ("Elementary|6-12", "Elementary I-II"), ("Adolescent|12-18", "Secondary I-II")):
        if re.search(key, joined): out.append(name)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[4]))
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "data"))
    a = ap.parse_args()
    root, out = Path(a.root), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    site = json.loads((root / "site/src/data/training-centers.json").read_text(encoding="utf8"))
    macte = json.loads((root / "data/raw/training/macte.json").read_text(encoding="utf8"))

    by_name_city, by_dom_city, by_name = {}, {}, {}
    for r in macte:
        by_name_city.setdefault((norm(r["name"]), norm(r["city"])), []).append(r)
        by_dom_city.setdefault((domain(r.get("website")), norm(r["city"])), []).append(r)
        by_name.setdefault(norm(r["name"]), []).append(r)

    def raw_rows(p):
        k = (norm(p["name"]), norm(p["city"]))
        if k in by_name_city: return by_name_city[k]
        d = (domain(p.get("website")), norm(p["city"]))
        if d[0] and d in by_dom_city: return by_dom_city[d]
        if len(by_name.get(norm(p["name"]), [])) >= 1: return by_name[norm(p["name"])]
        return []

    rows, unmatched = [], []
    counts = {}
    for p in site:
        counts[p["countrySlug"]] = counts.get(p["countrySlug"], 0) + 1
    for p in site:
        raw = raw_rows(p) if p["macte"] else []
        if p["macte"] and not raw: unmatched.append(p["name"])
        statuses, sites, macte_url = set(), 0, ""
        for r in raw:
            macte_url = macte_url or r.get("macte_url") or ""
            for s in r.get("sites", []):
                statuses.add(s["accreditation"]); sites += 1
        if not p["macte"]: status = "Not listed by MACTE"
        elif statuses == {"Full Accreditation"}: status = "Full Accreditation"
        elif not statuses: status = "Listed by MACTE, status not published"
        else: status = "Other MACTE status (probation or withdrawn)"
        listed = "MACTE and AMI" if p["macte"] and p["ami"] else "MACTE" if p["macte"] else "AMI"
        levels = clean_levels(p["levels"])
        has = lambda *keys: any(any(k in l for k in keys) for l in levels)
        page = counts[p["countrySlug"]] >= MIN_COUNTRY_PAGE
        rows.append({
            "program_id": f'{p["countrySlug"]}-{slug(p["city"])}-{slug(p["name"])}'[:120],
            "name": p["name"], "city": p["city"], "state_province": p["state"] or "",
            "country": p["country"], "country_slug": p["countrySlug"],
            "listed_by": listed, "macte_listed": p["macte"], "ami_listed": p["ami"],
            "macte_status": status, "macte_sites": sites if p["macte"] else "",
            "affiliation": "; ".join(p["affiliations"]), "delivery_format": p["delivery"] or "",
            "levels": "; ".join(levels), "levels_published": bool(levels),
            "level_infant_toddler": has("Infant"), "level_early_childhood": has("Early Childhood"),
            "level_elementary": has("Elementary"), "level_secondary": has("Secondary"),
            "website": p["website"] or "", "macte_url": macte_url,
            "latitude": p.get("lat", ""), "longitude": p.get("lng", ""),
            "msf_url": BASE + (p["countrySlug"] + "/" if page else ""),
            "msf_url_type": "country page" if page else "all-countries hub",
            "last_checked": p["updated"],
        })
    df = pd.DataFrame(rows)
    assert df.program_id.is_unique, df[df.program_id.duplicated(keep=False)]
    df.to_csv(out / "programs.csv", index=False, encoding="utf-8")

    g = df.groupby(["country", "country_slug"], sort=False)
    bc = g.agg(programs=("name", "size"), macte_listed=("macte_listed", "sum"), ami_listed=("ami_listed", "sum"),
               both=("listed_by", lambda s: (s == "MACTE and AMI").sum()),
               cities=("city", lambda s: s.replace("", pd.NA).nunique()),
               programs_with_levels=("levels_published", "sum"), msf_url=("msf_url", "first")).reset_index()
    bc["share_of_programs_pct"] = (bc.programs / len(df) * 100).round(1)
    bc = bc.sort_values(["programs", "country"], ascending=[False, True])
    bc.insert(0, "rank", range(1, len(bc) + 1))
    bc.to_csv(out / "by_country.csv", index=False)

    lv = []
    for lab, grp in df[df.levels_published].assign(l=lambda d: d.levels.str.split("; ")).explode("l").groupby("l"):
        lv.append({"level": lab, "programs": len(grp), "macte_listed": int(grp.macte_listed.sum()),
                   "ami_listed": int(grp.ami_listed.sum()), "countries": grp.country.nunique()})
    bl = pd.DataFrame(lv).sort_values(["programs", "level"], ascending=[False, True])
    n_pub = int(df.levels_published.sum())
    bl["share_of_programs_with_levels_pct"] = (bl.programs / n_pub * 100).round(1)
    bl.loc[len(bl)] = {"level": "(levels not published)", "programs": int((~df.levels_published).sum()),
                       "macte_listed": int(df[~df.levels_published].macte_listed.sum()),
                       "ami_listed": int(df[~df.levels_published].ami_listed.sum()),
                       "countries": df[~df.levels_published].country.nunique(), "share_of_programs_with_levels_pct": ""}
    bl.to_csv(out / "by_level.csv", index=False)

    ba = (df.groupby(["listed_by", "macte_status"]).agg(programs=("name", "size"), countries=("country", "nunique")).reset_index())
    ba["share_of_programs_pct"] = (ba.programs / len(df) * 100).round(1)
    ba = ba.sort_values("programs", ascending=False)
    ba.to_csv(out / "by_accreditation.csv", index=False)

    print(len(df), "programs,", df.country.nunique(), "countries, unmatched MACTE:", unmatched)

if __name__ == "__main__":
    main()
