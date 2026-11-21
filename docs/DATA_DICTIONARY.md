# Data Dictionary

Source: `data/raw/Data_Professional_Survey.xlsx` - sheet *Data Professional Survey*, 630 rows × 28 columns, survey window 10-26 Jun 2022.

## fact_survey (630 rows - one per respondent)

| Column | Type | Description / rule |
|---|---|---|
| Respondent Key | Int | Surrogate key (1…630) in source order |
| Respondent ID | Text | Original `Unique ID` |
| Survey Date | Date | Parsed from US `m/d/yyyy` text (America/New_York) |
| Survey Hour | Int | Hour (0-23) the survey was started |
| Time Spent (Sec) | Int | `h:mm:ss` text → seconds |
| Response Quality | Text | `Speeder (<30s)` · `Idle Session (>30 min)` · `Normal` |
| Job Title | Text | Q1 standardised to 11 categories (see rules in `scripts/clean_data.py`) |
| Industry | Text | Q4 standardised to 17 categories |
| Country | Text | Q11 cleaned; typos / truncations fixed |
| Education Level | Text | Q12; blank → `Not Provided` |
| Salary Band | Text | Q3 band exactly as collected |
| Salary Midpoint | Int | Mid-point of the band in USD (`225k+` → 250,000 - **assumption**) |
| Age | Int | Q10; values outside 18-80 set to blank (one value of 92) |
| Age Group | Text | 18-24 · 25-29 · 30-34 · 35-39 · 40-44 · 45+ · Unknown |
| Gender | Text | Q9 (Male / Female - only options in the survey) |
| Ethnicity | Text | Q13, free text mapped to the listed categories where unambiguous; otherwise `Other / Not Specified` |
| Favorite Language | Text | Q5: Python · R · SQL · C/C++ · JavaScript · Java · Excel / VBA · DAX / Power BI · None / Not Applicable · Other |
| Switched Careers | Text | Q2: Yes / No |
| Break-in Difficulty | Text | Q7 (5-point scale) |
| Difficulty Score | Int | 1 = Very Easy … 5 = Very Difficult |
| Top Job Priority | Text | Q8 standardised (Better Salary, Remote Work, Good Work/Life Balance, Good Culture, Growth & Learning, Multiple / All of the Above, Other) |
| Happiness - *factor* (×6) | Int 0-10 | Q6 ratings for Salary, Work/Life Balance, Coworkers, Management, Upward Mobility, Learning New Things; blanks stay blank |
| Overall Happiness | Decimal | Mean of the respondent's available ratings (3 dp) |
| Straight-lined Happiness | Bool | True when every answered rating is identical (possible low-effort response) |

## fact_happiness (3,722 rows - respondent × factor, blanks removed)

| Column | Description |
|---|---|
| Respondent Key | FK → `fact_survey` |
| Happiness Factor | FK → `dim_happiness_factor` |
| Happiness Score | 0-10 |
| Happiness Category | `Unhappy (0-3)` · `Neutral (4-6)` · `Happy (7-10)` |

## Dimensions

| Table | Grain / key | Extra attributes |
|---|---|---|
| dim_job | Job Title | - |
| dim_industry | Industry | - |
| dim_country | Country | Region (World Bank regions) |
| dim_education | Education Level | Education Sort |
| dim_salary | Salary Band | Sort, Min, Max, Midpoint, Tier (Entry / Mid / Senior / Executive) |
| dim_age_group | Age Group | Age Group Sort |
| dim_difficulty | Break-in Difficulty | Difficulty Score, Difficulty Group (Easy / Neutral / Difficult) |
| dim_happiness_factor | Happiness Factor | Factor Sort, Factor Group (Compensation / Environment / Growth) |
| dim_date | Date | Year, Month, Day of Week, Is Weekend, Survey Day Number |

## Columns intentionally dropped

`Email` (constant "anonymous"), `Browser`, `OS`, `City`, `Country` (the empty tracking column - not Q11), `Referrer` - all empty or constant.

See `docs/data_quality_report.md` for the full issue log.
