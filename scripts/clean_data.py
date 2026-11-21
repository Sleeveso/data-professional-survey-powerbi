#!/usr/bin/env python3
"""
clean_data.py - reproducible ETL for the Data Professional Survey.

Reads  : data/raw/Data_Professional_Survey.xlsx  (+ data/reference/*.csv)
Writes : data/processed/*.csv   (star schema: 2 facts + 9 dimensions)
         docs/data_quality_report.md

This script is the *reference implementation* of the cleaning rules. The Power
Query (M) scripts in /powerquery implement exactly the same rules so the report
can be refreshed straight from the raw workbook inside Power BI.

Usage:  python scripts/clean_data.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "Data_Professional_Survey.xlsx"
REF = ROOT / "data" / "reference"
OUT = ROOT / "data" / "processed"
DOCS = ROOT / "docs"

HAPPINESS_FACTORS = [
    "Salary",
    "Work/Life Balance",
    "Coworkers",
    "Management",
    "Upward Mobility",
    "Learning New Things",
]

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def split_other(value: str) -> tuple[bool, str]:
    """'Other (Please Specify):Retail' -> (True, 'Retail'); 'Tech' -> (False, '')."""
    v = str(value).strip()
    if not v.startswith("Other"):
        return False, ""
    detail = v.split(":", 1)[1].strip() if ":" in v else ""
    return True, detail


def has_any(text: str, keywords: list[str]) -> bool:
    return any(k in text for k in keywords)


# --------------------------------------------------------------------------- #
# Column-level cleaning rules (mirrored 1:1 in powerquery/*.pq)
# --------------------------------------------------------------------------- #
LISTED_JOBS = {
    "Data Analyst", "Data Engineer", "Data Scientist",
    "Database Developer", "Data Architect", "Student/Looking/None",
}


def clean_job(v: str) -> str:
    v = str(v).strip()
    if v in LISTED_JOBS:
        return v
    _, d = split_other(v)
    d = d.lower()
    if d == "":
        return "Other"
    if "student" in d:
        return "Student/Looking/None"
    if has_any(d, ["business analy", "business intelligence", "bi developer", "bi analyst", "insights"]):
        return "Business / BI Analyst"
    if has_any(d, ["manager", "director"]):
        return "Manager / Director"
    if "analytics engineer" in d:
        return "Data Engineer"
    if has_any(d, ["software", "developer"]):
        return "Software Developer"
    if has_any(d, ["analyst", "analytic"]):
        return "Other Analyst"
    return "Other"


LISTED_INDUSTRIES = {
    "Tech", "Finance", "Healthcare", "Education", "Telecommunication",
    "Construction", "Real Estate", "Agriculture",
}


def clean_industry(v: str) -> str:
    v = str(v).strip()
    if v in LISTED_INDUSTRIES:
        return v
    _, d = split_other(v)
    d = d.lower()
    if d == "":
        return "Other"
    if has_any(d, ["not working", "studying", "none"]):
        return "Not Working / Student"
    if d.startswith("cons"):
        return "Consulting"
    if has_any(d, ["insurance"]):
        return "Finance"
    if has_any(d, ["biotech"]):
        return "Healthcare"
    if has_any(d, ["retail", "wholesale", "consumer", "ecom", "e-com"]):
        return "Retail & E-commerce"
    if has_any(d, ["manuf", "automotive", "aerospace", "semiconductor", "food"]):
        return "Manufacturing"
    if has_any(d, ["logistic", "supply chain", "distribution", "aviation"]):
        return "Logistics & Supply Chain"
    if has_any(d, ["energy", "oil and gas", "utili"]):
        return "Energy & Utilities"
    if has_any(d, ["market", "advertis"]):
        return "Marketing & Advertising"
    if has_any(d, ["government", "nonprofit"]):
        return "Government & Nonprofit"
    return "Other"


LISTED_COUNTRIES = {"United States", "India", "United Kingdom", "Canada"}
COUNTRY_FIXES = {
    "uae": "United Arab Emirates",
    "perú": "Peru",
    "republic democratic of congo": "Democratic Republic of the Congo",
    # typos / truncated entries (inferred; documented in docs/data_quality_report.md)
    "africa (nigeria)": "Nigeria",
    "aisa": "Unknown",          # a continent, not a country
    "argentine": "Argentina",
    "austr": "Australia",
    "brazik": "Brazil",
    "fin": "Finland",
    "ire": "Ireland",
    "irel": "Ireland",
    "kenua": "Kenya",
    "leba": "Lebanon",
    "portugsl": "Portugal",
    "sg": "Singapore",
    "uzb": "Uzbekistan",
    "antigua": "Antigua and Barbuda",
    "macedonia": "North Macedonia",
}


def clean_country(v: str) -> str:
    v = str(v).strip()
    if v in LISTED_COUNTRIES:
        return v
    _, d = split_other(v)
    d = d.strip()
    if d == "":
        return "Unknown"
    if d.lower() in COUNTRY_FIXES:
        return COUNTRY_FIXES[d.lower()]
    return d.title()


def clean_language(v: str) -> str:
    v = str(v).strip()
    if v in {"Python", "R", "C/C++", "JavaScript", "Java"}:
        return v
    _, d = split_other(v)
    d = d.lower()
    if d == "":
        return "Other"
    if "sql" in d:
        return "SQL"
    if has_any(d, ["excel", "vba"]):
        return "Excel / VBA"
    if has_any(d, ["dax", "power bi"]):
        return "DAX / Power BI"
    if d == "na" or has_any(
        d, ["none", "dont", "don't", "don\u2019t", "do not", "unknown", "not use", "started", "require", "presentations"]
    ):
        return "None / Not Applicable"
    return "Other"


LISTED_PRIORITIES = {"Better Salary", "Remote Work", "Good Work/Life Balance", "Good Culture"}


def clean_priority(v: str) -> str:
    v = str(v).strip()
    if v in LISTED_PRIORITIES:
        return v
    _, d = split_other(v)
    d = d.lower()
    if d == "":
        return "Other"
    if has_any(d, ["all of", "combination", "mix", "both"]):
        return "Multiple / All of the Above"
    if has_any(d, ["learn", "growth", "advanc", "develop", "opportunit", "mentor", "skills", "challeng", "exposure"]):
        return "Growth & Learning"
    return "Other"


LISTED_ETHNICITY = {
    "White or Caucasian", "Asian or Asian American", "Black or African American",
    "Hispanic or Latino", "American Indian or Alaska Native",
    "Native Hawaiian or other Pacific Islander",
}


def clean_ethnicity(v: str) -> str:
    v = str(v).strip()
    if v in LISTED_ETHNICITY:
        return v
    _, d = split_other(v)
    d = d.lower()
    if d == "":
        return "Other / Not Specified"
    if has_any(d, ["half", "mixed", "bi-racial"]):
        return "Mixed / Multiracial"
    if has_any(d, ["indian", "asian", "pakistani", "bangladeshi", "dravidian", "malay", "melayu"]):
        return "Asian or Asian American"
    if has_any(d, ["african", "black"]) or d in {"bla", "nigeria"}:
        return "Black or African American"
    return "Other / Not Specified"


def age_group(age: float) -> str:
    if pd.isna(age):
        return "Unknown"
    for label, lo, hi in [("18-24", 18, 24), ("25-29", 25, 29), ("30-34", 30, 34),
                          ("35-39", 35, 39), ("40-44", 40, 44)]:
        if lo <= age <= hi:
            return label
    return "45+"


def duration_to_seconds(s: str) -> int:
    h, m, sec = (int(x) for x in str(s).split(":"))
    return h * 3600 + m * 60 + sec


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build() -> dict[str, pd.DataFrame]:
    raw = pd.read_excel(RAW, sheet_name="Data Professional Survey")
    n_raw = len(raw)

    # Short, stable column names
    q6 = {f"Q6 - How Happy are you in your Current Position with the following? ({f})": f"Happiness - {f}"
          for f in HAPPINESS_FACTORS}
    raw = raw.rename(columns={
        "Unique ID": "Respondent ID",
        "Date Taken (America/New_York)": "Date Taken",
        "Time Taken (America/New_York)": "Time Taken",
        "Q1 - Which Title Best Fits your Current Role?": "Job Title Raw",
        "Q2 - Did you switch careers into Data?": "Switched Careers",
        "Q3 - Current Yearly Salary (in USD)": "Salary Band",
        "Q4 - What Industry do you work in?": "Industry Raw",
        "Q5 - Favorite Programming Language": "Language Raw",
        "Q7 - How difficult was it for you to break into Data?": "Break-in Difficulty",
        "Q8 - If you were to look for a new job today, what would be the most important thing to you?": "Priority Raw",
        "Q9 - Male/Female?": "Gender",
        "Q10 - Current Age": "Age Raw",
        "Q11 - Which Country do you live in?": "Country Raw",
        "Q12 - Highest Level of Education": "Education Level",
        "Q13 - Ethnicity": "Ethnicity Raw",
        **q6,
    })

    sal = pd.read_csv(REF / "salary_bands.csv")
    edu = pd.read_csv(REF / "education_levels.csv")
    diff = pd.read_csv(REF / "difficulty_levels.csv")
    fac = pd.read_csv(REF / "happiness_factors.csv")

    f = pd.DataFrame()
    f["Respondent Key"] = np.arange(1, n_raw + 1)
    f["Respondent ID"] = raw["Respondent ID"].astype(str).str.strip()

    # Date / time (source is US m/d/yyyy text, America/New_York)
    f["Survey Date"] = pd.to_datetime(raw["Date Taken"], format="%m/%d/%Y").dt.date
    f["Survey Hour"] = raw["Time Taken"].str.split(":").str[0].astype(int)
    secs = raw["Time Spent"].map(duration_to_seconds)
    f["Time Spent (Sec)"] = secs
    f["Response Quality"] = np.select(
        [secs < 30, secs > 1800], ["Speeder (<30s)", "Idle Session (>30 min)"], default="Normal"
    )

    # Categorical cleaning
    f["Job Title"] = raw["Job Title Raw"].map(clean_job)
    f["Industry"] = raw["Industry Raw"].map(clean_industry)
    f["Country"] = raw["Country Raw"].map(clean_country)
    f["Education Level"] = raw["Education Level"].fillna("Not Provided").str.strip()
    f["Salary Band"] = raw["Salary Band"].str.strip()
    f["Gender"] = raw["Gender"].str.strip()
    f["Ethnicity"] = raw["Ethnicity Raw"].map(clean_ethnicity)
    f["Favorite Language"] = raw["Language Raw"].map(clean_language)
    f["Top Job Priority"] = raw["Priority Raw"].map(clean_priority)
    f["Switched Careers"] = raw["Switched Careers"].str.strip()
    f["Break-in Difficulty"] = raw["Break-in Difficulty"].str.strip()

    # Numeric enrichment from reference tables
    f = f.merge(sal[["Salary Band", "Salary Midpoint"]], on="Salary Band", how="left")
    f = f.merge(diff[["Break-in Difficulty", "Difficulty Score"]], on="Break-in Difficulty", how="left")

    # Age: keep plausible values only (92 is treated as a data-entry error)
    age = raw["Age Raw"].astype(float)
    f["Age"] = age.where(age.between(18, 80)).astype("Int64")
    f["Age Group"] = f["Age"].map(age_group)

    # Happiness (0-10) - blanks stay blank, never zero
    hcols = [f"Happiness - {x}" for x in HAPPINESS_FACTORS]
    for c in hcols:
        f[c] = raw[c].astype("Int64")
    f["Overall Happiness"] = raw[hcols].mean(axis=1).round(3)
    f["Straight-lined Happiness"] = (raw[hcols].nunique(axis=1) == 1)

    col_order = [
        "Respondent Key", "Respondent ID", "Survey Date", "Survey Hour", "Time Spent (Sec)",
        "Response Quality", "Job Title", "Industry", "Country", "Education Level",
        "Salary Band", "Salary Midpoint", "Age", "Age Group", "Gender", "Ethnicity",
        "Favorite Language", "Switched Careers", "Break-in Difficulty", "Difficulty Score",
        "Top Job Priority", *hcols, "Overall Happiness", "Straight-lined Happiness",
    ]
    fact_survey = f[col_order].copy()

    # ---- fact_happiness: respondent x factor (long format) ---- #
    fh = fact_survey[["Respondent Key", *hcols]].melt(
        id_vars="Respondent Key", var_name="Happiness Factor", value_name="Happiness Score"
    )
    fh["Happiness Factor"] = fh["Happiness Factor"].str.replace("Happiness - ", "", regex=False)
    fh = fh.dropna(subset=["Happiness Score"]).copy()
    fh["Happiness Score"] = fh["Happiness Score"].astype(int)
    fh["Happiness Category"] = pd.cut(
        fh["Happiness Score"], bins=[-1, 3, 6, 10], labels=["Unhappy (0-3)", "Neutral (4-6)", "Happy (7-10)"]
    ).astype(str)
    fact_happiness = fh.sort_values(["Respondent Key", "Happiness Factor"]).reset_index(drop=True)

    # ---- dimensions ---- #
    dim_job = pd.DataFrame({"Job Title": sorted(f["Job Title"].unique())})
    dim_industry = pd.DataFrame({"Industry": sorted(f["Industry"].unique())})

    country_region = pd.read_csv(REF / "country_region.csv")
    dim_country = (pd.DataFrame({"Country": sorted(f["Country"].unique())})
                   .merge(country_region, on="Country", how="left"))
    missing = dim_country[dim_country["Region"].isna()]["Country"].tolist()
    if missing:
        raise SystemExit(f"country_region.csv is missing: {missing}")

    dim_education = edu[edu["Education Level"].isin(f["Education Level"].unique())].copy()
    dim_salary = sal.copy()
    dim_age_group = pd.read_csv(REF / "age_groups.csv")
    dim_difficulty = diff.copy()
    dim_happiness_factor = fac.copy()

    dates = pd.date_range(pd.to_datetime(f["Survey Date"]).min(), pd.to_datetime(f["Survey Date"]).max())
    dim_date = pd.DataFrame({"Date": dates})
    dim_date["Year"] = dim_date["Date"].dt.year
    dim_date["Month Number"] = dim_date["Date"].dt.month
    dim_date["Month Name"] = dim_date["Date"].dt.strftime("%B")
    dim_date["Day of Month"] = dim_date["Date"].dt.day
    dim_date["Day of Week Number"] = dim_date["Date"].dt.dayofweek + 1  # Mon=1
    dim_date["Day of Week"] = dim_date["Date"].dt.strftime("%A")
    dim_date["Is Weekend"] = dim_date["Date"].dt.dayofweek >= 5
    dim_date["Survey Day Number"] = np.arange(1, len(dim_date) + 1)
    dim_date["Date"] = dim_date["Date"].dt.date

    return {
        "fact_survey": fact_survey,
        "fact_happiness": fact_happiness,
        "dim_job": dim_job,
        "dim_industry": dim_industry,
        "dim_country": dim_country,
        "dim_education": dim_education,
        "dim_salary": dim_salary,
        "dim_age_group": dim_age_group,
        "dim_difficulty": dim_difficulty,
        "dim_happiness_factor": dim_happiness_factor,
        "dim_date": dim_date,
    }, raw


def data_quality_report(raw: pd.DataFrame, t: dict[str, pd.DataFrame]) -> str:
    f = t["fact_survey"]
    hcols = [c for c in f.columns if c.startswith("Happiness - ")]
    empty_cols = [c for c in raw.columns if raw[c].isna().all()]
    n = len(f)

    def changed(raw_col: str, clean_col: str) -> int:
        return int((raw[raw_col].astype(str).str.strip() != f[clean_col].astype(str)).sum())

    lines = [
        "# Data Quality Report",
        "",
        "_Generated by `scripts/clean_data.py` - do not edit by hand._",
        "",
        "## Source profile",
        "",
        f"- Rows (respondents): **{n}**; duplicate Unique IDs: **{int(raw['Respondent ID'].duplicated().sum())}**",
        f"- Survey window: **{f['Survey Date'].min()} -> {f['Survey Date'].max()}**",
        f"- Columns that are 100% empty and dropped: `{', '.join(empty_cols)}`",
        "- `Email` is the constant value `anonymous` and is dropped (no PII is retained).",
        "",
        "## Issues found and how they are handled",
        "",
        "| # | Issue | Records affected | Treatment |",
        "|---|-------|-----------------:|-----------|",
        f"| 1 | Free-text 'Other (Please Specify)' job titles | {changed('Job Title Raw', 'Job Title')} | Keyword rules map to a standard `Job Title` (11 categories) |",
        f"| 2 | Free-text industries with typos / truncation (`Consulti`, `Manuf`, `Utili`, `Ecom` ...) | {changed('Industry Raw', 'Industry')} | Keyword rules map to 17 standard industries |",
        f"| 3 | Free-text countries (casing, trailing spaces, `UAE`, `Per\u00fa`) | {changed('Country Raw', 'Country')} | Prefix stripped, trimmed, title-cased, corrected; joined to World Bank region |",
        f"| 4 | Programming-language free text (`Sql`, `sql`, `SQL Postgres` ...) | {changed('Language Raw', 'Favorite Language')} | Collapsed into SQL / Excel-VBA / DAX / None / Other |",
        f"| 5 | Missing education | {int(raw['Education Level'].isna().sum())} | Labelled `Not Provided` (kept in the analysis, never dropped) |",
        f"| 6 | Implausible age (92) | {int((~raw['Age Raw'].between(18, 80)).sum())} | Age set to blank; respondent kept; `Age Group` = Unknown |",
        "| 7 | Missing happiness ratings (per factor) | "
        + ", ".join(f"{c.replace('Happiness - ', '')}: {int(f[c].isna().sum())}" for c in hcols)
        + " | Left blank (never 0) so averages are not biased; `fact_happiness` omits blanks |",
        f"| 8 | Straight-lined happiness (all six answers identical) | {int(f['Straight-lined Happiness'].sum())} | Flagged `Straight-lined Happiness`; kept, filterable |",
        f"| 9 | Speeders (<30 s) / idle sessions (>30 min) | {int((f['Response Quality'] == 'Speeder (<30s)').sum())} / {int((f['Response Quality'] == 'Idle Session (>30 min)').sum())} | Flagged in `Response Quality`; kept; average completion time excludes idle sessions |",
        "| 10 | Salary stored as text bands | all | Mapped to ordered `dim_salary` with min / max / **midpoint** (assumption: midpoints; `225k+` is set to 250k) |",
        "| 11 | Date and time stored as text (US m/d/yyyy) | all | Parsed to real `Date`; hour extracted |",
        "",
        "## Known limitations",
        "",
        "- **Self-selected sample** (a data-analytics community audience) - not representative of all data professionals.",
        "- Salary is a **band**, so every salary figure in the report is a midpoint *estimate*.",
        "- Several segments have small samples (e.g. PhD n=5, `225k+` n=2). Measures use a configurable minimum sample size and return BLANK below it.",
        "- Salary is in USD but respondents are worldwide; cross-country salary comparisons ignore purchasing power.",
        "- `Niger` (2 respondents) may be a typo for `Nigeria`; it has been left as entered.",
        "",
        "## Output tables",
        "",
        "| Table | Rows | Columns |",
        "|-------|-----:|--------:|",
    ]
    for name, df in t.items():
        lines.append(f"| `{name}` | {len(df)} | {df.shape[1]} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tables, raw = build()
    for name, df in tables.items():
        df.to_csv(OUT / f"{name}.csv", index=False)
        print(f"  wrote data/processed/{name}.csv  ({len(df)} rows x {df.shape[1]} cols)")
    (DOCS / "data_quality_report.md").write_text(data_quality_report(raw, tables), encoding="utf-8")
    print("  wrote docs/data_quality_report.md")


if __name__ == "__main__":
    main()
