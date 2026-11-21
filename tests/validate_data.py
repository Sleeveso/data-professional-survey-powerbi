#!/usr/bin/env python3
"""
validate_data.py - independent checks on data/processed/*.csv

The expected values are recomputed straight from the RAW workbook with simple logic
(not from the cleaning functions) so a bug in clean_data.py cannot hide itself.

Usage:  python tests/validate_data.py        (exit code 0 = all checks passed)
"""
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
raw = pd.read_excel(ROOT / "data" / "raw" / "Data_Professional_Survey.xlsx")

fs = pd.read_csv(P / "fact_survey.csv")
fh = pd.read_csv(P / "fact_happiness.csv")
dims = {n: pd.read_csv(P / f"{n}.csv") for n in
        ["dim_job", "dim_industry", "dim_country", "dim_education", "dim_salary",
         "dim_age_group", "dim_difficulty", "dim_happiness_factor", "dim_date"]}

failures = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail and not ok else ""))
    if not ok:
        failures.append(name)


# ---- row counts & keys ----
check("fact_survey row count equals raw", len(fs) == len(raw), f"{len(fs)} vs {len(raw)}")
check("Respondent Key unique", fs["Respondent Key"].is_unique)
check("Respondent ID unique", fs["Respondent ID"].is_unique)
check("No PII columns present", not {"Email", "Browser", "OS", "City", "Referrer"} & set(fs.columns))

# ---- independent recounts from raw ----
check("Female count", (fs.Gender == "Female").sum() == (raw["Q9 - Male/Female?"] == "Female").sum())
check("Career switchers count", (fs["Switched Careers"] == "Yes").sum() == (raw["Q2 - Did you switch careers into Data?"] == "Yes").sum())
check("Salary band counts match raw",
      fs["Salary Band"].value_counts().to_dict() == raw["Q3 - Current Yearly Salary (in USD)"].value_counts().to_dict())
check("Education nulls re-labelled", (fs["Education Level"] == "Not Provided").sum() == raw["Q12 - Highest Level of Education"].isna().sum())
check("Exactly one invalid age blanked", fs["Age"].isna().sum() == 1)
check("Age range plausible", fs["Age"].dropna().between(18, 80).all())

hap_raw = [c for c in raw.columns if c.startswith("Q6")]
check("fact_happiness rows == non-null raw ratings", len(fh) == int(raw[hap_raw].notna().sum().sum()), f"{len(fh)}")
check("Happiness scores within 0-10", fh["Happiness Score"].between(0, 10).all())
for src, factor in zip(hap_raw, ["Salary", "Work/Life Balance", "Coworkers", "Management", "Upward Mobility", "Learning New Things"]):
    a = raw[src].mean()
    b = fh.loc[fh["Happiness Factor"] == factor, "Happiness Score"].mean()
    check(f"Factor mean matches raw: {factor}", abs(a - b) < 1e-9)

# ---- no nulls where we promise none ----
must_have = ["Job Title", "Industry", "Country", "Education Level", "Salary Band", "Salary Midpoint",
             "Age Group", "Gender", "Switched Careers", "Break-in Difficulty", "Difficulty Score",
             "Survey Date", "Response Quality", "Top Job Priority", "Favorite Language", "Ethnicity"]
check("No nulls in required columns", fs[must_have].notna().all().all(),
      str(fs[must_have].isna().sum()[lambda s: s > 0].to_dict()))
check("No leftover 'Other (Please Specify)' text",
      not any(fs[c].astype(str).str.contains("Please Specify").any() for c in ["Job Title", "Industry", "Country", "Top Job Priority"]))

# ---- referential integrity (every fact value exists in its dimension) ----
ri = [("Job Title", "dim_job"), ("Industry", "dim_industry"), ("Country", "dim_country"),
      ("Education Level", "dim_education"), ("Salary Band", "dim_salary"),
      ("Age Group", "dim_age_group"), ("Break-in Difficulty", "dim_difficulty")]
for col, d in ri:
    check(f"RI fact_survey[{col}] -> {d}", set(fs[col]) <= set(dims[d][col]), str(set(fs[col]) - set(dims[d][col])))
    check(f"{d}[{col}] is unique", dims[d][col].is_unique)
check("RI fact_survey[Survey Date] -> dim_date", set(fs["Survey Date"]) <= set(dims["dim_date"]["Date"]))
check("dim_date is continuous", len(dims["dim_date"]) == (pd.to_datetime(dims["dim_date"]["Date"]).max() - pd.to_datetime(dims["dim_date"]["Date"]).min()).days + 1)
check("RI fact_happiness[Respondent Key] -> fact_survey", set(fh["Respondent Key"]) <= set(fs["Respondent Key"]))
check("RI fact_happiness[Happiness Factor] -> dim_happiness_factor", set(fh["Happiness Factor"]) <= set(dims["dim_happiness_factor"]["Happiness Factor"]))
check("dim_country has a Region for every row", dims["dim_country"]["Region"].notna().all())

# ---- golden KPIs (used again in docs/QA_CHECKLIST.md) ----
check("Golden: respondents = 630", len(fs) == 630)
check("Golden: avg salary midpoint ~ 53,983", round(fs["Salary Midpoint"].mean()) == 53983, str(fs["Salary Midpoint"].mean()))

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
