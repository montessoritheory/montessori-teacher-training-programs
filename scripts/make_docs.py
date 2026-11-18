"""Write data_dictionary.csv, the Kaggle metadata and the Hugging Face card from one column list and the README.
Run after build_programs.py. Outputs go to ../data_dictionary.csv, ../../kaggle and ../../huggingface."""
import csv, json, re
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PKG = REPO.parent
GH = "https://raw.githubusercontent.com/montessoritheory/montessori-teacher-training-programs/main/"
HF = "https://huggingface.co/datasets/montessoritheory/montessori-teacher-training-programs/resolve/main/"
MSF_US = "https://www.montessorischoolfinder.com/montessori-certifications/training-centers/united-states/"

# (file, column, type, description, example)
COLS = [
 ("programs.csv", "program_id", "string", "Stable id built from country slug, city and program name", ""),
 ("programs.csv", "name", "string", "Program name as listed by MACTE or AMI", ""),
 ("programs.csv", "city", "string", "City, empty for 4 programs", ""),
 ("programs.csv", "state_province", "string", "State or province when known, empty otherwise", ""),
 ("programs.csv", "country", "string", "Country name", ""),
 ("programs.csv", "country_slug", "string", "Country slug used in the Montessori School Finder URL", ""),
 ("programs.csv", "listed_by", "string", "MACTE, AMI or MACTE and AMI", ""),
 ("programs.csv", "macte_listed", "boolean", "The program appears in the MACTE accredited program search", ""),
 ("programs.csv", "ami_listed", "boolean", "The program appears in the AMI list of training centres", ""),
 ("programs.csv", "macte_status", "string", "MACTE accreditation status of its sites, Full Accreditation, Other MACTE status (probation or withdrawn) or Not listed by MACTE", ""),
 ("programs.csv", "macte_sites", "integer", "Number of MACTE site and level entries behind the program, empty if not MACTE listed", ""),
 ("programs.csv", "affiliation", "string", "Association given by MACTE, values joined by semicolons", ""),
 ("programs.csv", "delivery_format", "string", "MACTE delivery format, share of hours online", ""),
 ("programs.csv", "levels", "string", "Levels offered, names joined by semicolons (MACTE names, AMI age bands mapped to them)", ""),
 ("programs.csv", "levels_published", "boolean", "At least one level is published for the program", ""),
 ("programs.csv", "level_infant_toddler", "boolean", "Offers Infant and Toddler (0 to 3)", ""),
 ("programs.csv", "level_early_childhood", "boolean", "Offers Early Childhood (3 to 6)", ""),
 ("programs.csv", "level_elementary", "boolean", "Offers any Elementary level (6 to 12)", ""),
 ("programs.csv", "level_secondary", "boolean", "Offers any Secondary level (12 to 18)", ""),
 ("programs.csv", "website", "string", "The own website of the program", ""),
 ("programs.csv", "macte_url", "string", "MACTE page of the program, empty if not MACTE listed", ""),
 ("programs.csv", "latitude", "number", "City centre latitude (WGS84), not a street address, empty for 9 programs", ""),
 ("programs.csv", "longitude", "number", "City centre longitude (WGS84), not a street address, empty for 9 programs", ""),
 ("programs.csv", "msf_url", "string", "Montessori School Finder page, the country page or the all-countries hub", ""),
 ("programs.csv", "msf_url_type", "string", "country page, or all-countries hub when the country has fewer than 3 programs", ""),
 ("programs.csv", "last_checked", "string", "Date of the last collection, YYYY-MM-DD", ""),
 ("by_country.csv", "rank", "integer", "Rank by number of programs, ties in alphabetical order", "1"),
 ("by_country.csv", "country", "string", "Country name", "United States"),
 ("by_country.csv", "country_slug", "string", "Country slug used in the Montessori School Finder URL", "united-states"),
 ("by_country.csv", "programs", "integer", "Programs in the country", "173"),
 ("by_country.csv", "macte_listed", "integer", "Programs listed by MACTE", "165"),
 ("by_country.csv", "ami_listed", "integer", "Programs listed by AMI", "16"),
 ("by_country.csv", "both", "integer", "Programs on both lists", "8"),
 ("by_country.csv", "cities", "integer", "Distinct cities", "154"),
 ("by_country.csv", "programs_with_levels", "integer", "Programs that publish at least one level", "167"),
 ("by_country.csv", "msf_url", "string", "Montessori School Finder page of the country", MSF_US),
 ("by_country.csv", "share_of_programs_pct", "number", "Share of all programs, percent", "48.6"),
 ("by_level.csv", "level", "string", "Level name, or (levels not published)", "Early Childhood"),
 ("by_level.csv", "programs", "integer", "Programs offering the level. A program with several levels counts once per level", "205"),
 ("by_level.csv", "macte_listed", "integer", "Of those, listed by MACTE", "203"),
 ("by_level.csv", "ami_listed", "integer", "Of those, listed by AMI", "10"),
 ("by_level.csv", "countries", "integer", "Countries with such a program", "21"),
 ("by_level.csv", "share_of_programs_with_levels_pct", "number", "Share of the 255 programs that publish levels, empty on the last row", "80.4"),
 ("by_accreditation.csv", "listed_by", "string", "MACTE, AMI or MACTE and AMI", "MACTE"),
 ("by_accreditation.csv", "macte_status", "string", "MACTE status group", "Full Accreditation"),
 ("by_accreditation.csv", "programs", "integer", "Programs in the group, the 5 rows add up to 356", "241"),
 ("by_accreditation.csv", "countries", "integer", "Countries with such a program", "21"),
 ("by_accreditation.csv", "share_of_programs_pct", "number", "Share of all programs, percent", "67.7"),
]
FILE_DESC = {
 "programs.csv": "356 rows, one per Montessori teacher training program from the MACTE accredited program search and the AMI list of training centres, with place, levels, accreditation and Montessori School Finder link.",
 "by_country.csv": "56 rows, programs per country with MACTE and AMI counts, ranked.",
 "by_level.csv": "10 rows, programs per level, plus the programs that publish no level.",
 "by_accreditation.csv": "5 rows, programs by list (MACTE, AMI, both) and MACTE status, adding up to 356.",
}

YAML = """---
license: cc-by-4.0
pretty_name: Montessori Teacher Training Programs Worldwide
language:
- en
tags:
- montessori
- education
- teacher-training
- teacher-certification
- ami
- macte
- early-childhood
- geospatial
- tabular
size_categories:
- n<1K
source_datasets:
- original
configs:
- config_name: programs
  data_files: data/programs.csv
  default: true
- config_name: by_country
  data_files: data/by_country.csv
- config_name: by_level
  data_files: data/by_level.csv
- config_name: by_accreditation
  data_files: data/by_accreditation.csv
---

"""


def main():
    p = pd.read_csv(REPO / "data/programs.csv", dtype=str).fillna("")
    first = p[p.name.str.startswith("Adrian Dominican")].iloc[0]
    rows = []
    for f, c, t, d, e in COLS:
        if f == "programs.csv":
            e = str(first[c])
        rows.append((f, c, t, d, e))
    with open(REPO / "data_dictionary.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "column", "type", "description", "example"])
        w.writerows(rows)

    for f in FILE_DESC:  # every column of every file must be documented
        cols = list(pd.read_csv(REPO / "data" / f, nrows=1).columns)
        doc = [c for ff, c, *_ in COLS if ff == f]
        assert cols == doc, (f, cols, doc)

    readme = (REPO / "README.md").read_text(encoding="utf-8")
    english = readme.split("\n---\n\n## Version")[0]

    def absolute(text, base):
        return re.sub(r"\]\((images/[^)]+)\)", lambda m: "](" + base + m.group(1) + ")", text)

    tmap = {"boolean": "boolean", "integer": "integer", "number": "number"}
    fields = lambda f: [{"name": c, "description": d, "type": tmap.get(t, "string")} for ff, c, t, d, e in rows if ff == f]
    meta = {
        "title": "Montessori Teacher Training Programs Worldwide",
        "subtitle": "356 AMI training centres and MACTE accredited programs in 56 countries, with levels and accreditation",
        "id": "mariamontessori/montessori-teacher-training-programs",
        "licenses": [{"name": "CC-BY-4.0"}],
        "keywords": ["education", "teaching", "universities and colleges", "geospatial analysis", "tabular", "early childhood"],
        "description": absolute(english, GH),
        "resources": [{"path": f, "description": FILE_DESC[f], "schema": {"fields": fields(f)}} for f in FILE_DESC]
        + [{"path": "data_dictionary.csv", "description": "Every column of every file, with type, description and an example."}],
        "expectedUpdateFrequency": "quarterly",
        "userSpecifiedSources": "MACTE accredited program search, https://www.macte.org/accredited-programs/ and AMI list of training centres, https://montessori-ami.org/training-programmes/training-centres (public listings read in November 2026). Companion directory, https://www.montessorischoolfinder.com/montessori-certifications/training-centers/",
    }
    (PKG / "kaggle").mkdir(exist_ok=True)
    (PKG / "kaggle/dataset-metadata.json").write_text(json.dumps(meta, indent=1, ensure_ascii=True), encoding="utf-8")
    (PKG / "huggingface").mkdir(exist_ok=True)
    (PKG / "huggingface/README.md").write_text(YAML + absolute(readme, HF), encoding="utf-8")
    print("docs ok", len(rows), "dictionary rows")


if __name__ == "__main__":
    main()
