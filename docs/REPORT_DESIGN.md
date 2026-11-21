# Report Design Specification

Canvas **1280 × 720** (16:9) · Theme `theme/data_professional_theme.json` (View → Themes → Browse for themes) ·
Font Segoe UI · Page background `#0F1B26`, cards `#16293A`.

**Global elements on every page** - a 56 px header band (page title + dynamic subtitle `[Selected Filters Text]`), a left
navigation rail (Page navigator visual, 6 pages), a *Reset filters* button (bookmark) and a *Filters* toggle button (bookmark that
shows/hides the slicer panel).

## Page 1 - Executive Summary
*Question answered: who responded, what do they earn and how satisfied are they?*

| Zone | Visual | Fields |
|---|---|---|
| Top row (5 cards) | Card (new) | `Respondents` · `Avg Salary (Reliable)` · `Career Switchers %` · `Avg Overall Happiness` · `Found It Hard %`; reference label shows `Salary Arrow`, `Salary vs Overall ($)` |
| Left | Slicer panel (toggle bookmark) | `dim_job[Job Title]` · `dim_industry[Industry]` · `dim_country[Region]` · `fact_survey[Gender]` · `dim_education[Education Level]` · `Min Sample Size` |
| Centre-left | Clustered column | Axis `dim_salary[Salary Band]` (sorted by Salary Sort) · Value `Respondents` · colour by `dim_salary[Salary Tier]` |
| Centre-right | Map (bubble) | Location `dim_country[Country]` · Size `Respondents` · Colour saturation `Avg Salary (Reliable)` |
| Bottom-left | Bar | Axis `dim_job[Job Title]` · Value `Respondents` + tooltip page |
| Bottom-right | Text box (dynamic) | `Insight - Top Paying Role` and `Insight - Happiness` |

## Page 2 - Salary Analysis
*What drives pay?*

| Visual | Setup |
|---|---|
| **Dynamic bar chart** | Axis = `Dimension Selector` (field parameter), Value = `Metric Selector`; two slicers let the viewer swap dimension and metric; title bound to `[Title - Metric by Dimension]` |
| **Decomposition tree** | Analyze `Avg Salary`; Explain by Role, Industry, Country, Education, Age Group, Gender |
| **Scatter** | X `Avg Age`, Y `Avg Salary`, Size `Respondents`, Details `dim_job[Job Title]`; sample-size guard via `Avg Salary (Reliable)` |
| **100 % stacked bar** | Axis `dim_education[Education Level]`, Legend `dim_salary[Salary Tier]`, Value `Respondents` |
| **KPI strip** | `Gender Pay Gap % (M vs F)`, `Avg Salary - Male`, `Avg Salary - Female`, `High Earner % (86k+)` |
| **What-if** | Slicer `Salary Threshold` (slider) + card `% At or Above Threshold` |

## Page 3 - Job Satisfaction
*Where are people unhappy, and is money the reason?*

| Visual | Setup |
|---|---|
| **Matrix heat-map** | Rows `dim_job[Job Title]`, Columns `dim_happiness_factor[Happiness Factor]`, Values `Avg Happiness (Factor, Reliable)`; Format → Cell elements → Background colour → *Field value* → `Happiness Color` |
| **100 % stacked bar** | Axis `Happiness Factor`, Legend `fact_happiness[Happiness Category]` (red / amber / green) - shows polarisation, not just the average |
| **Bar** | Axis `Happiness Factor`, Value `Avg Happiness (Factor)` with constant line at overall average |
| **Scatter** | X `Avg Salary (Reliable)`, Y `Avg Overall Happiness`, Details `dim_industry[Industry]`, Size `Respondents` (does a higher-paying industry mean happier people?) |
| **Cards** | `Lowest Scoring Factor`, `Highest Scoring Factor`, `Net Happiness %`, `Straight-liners %` |

## Page 4 - Career Journey
*How hard was it to break in, and what do people want next?*

| Visual | Setup |
|---|---|
| Clustered column | Axis `dim_difficulty[Break-in Difficulty]` (sorted by score), Value `Respondents`, Legend `Switched Careers` |
| Comparison table | Rows: `Switched Careers`; Values: `Respondents`, `Avg Salary`, `Avg Difficulty Score`, `Avg Overall Happiness` |
| Treemap | Group `Top Job Priority`, Value `Respondents` |
| Matrix | Rows `dim_education[Education Level]`, Columns `dim_difficulty[Difficulty Group]`, Values `Share of Respondents %` (row % via *Show value as*) |
| Pareto | Column `Respondents` + line `Industry Cumulative %` on `dim_industry[Industry]`; Top-N slicer + visual filter `Industry Top N Flag = 1` |

## Page 5 - Demographics & Tools

| Visual | Setup |
|---|---|
| Column | `dim_age_group[Age Group]` × `Respondents` |
| Donut | `Gender` × `Respondents` |
| Bar | `Ethnicity` × `Respondents` |
| Bar | `Favorite Language` × `Respondents` with `Avg Salary (Reliable)` as tooltip |
| Table | `dim_country[Region]`, `Country`, `Respondents`, `Avg Salary (Reliable)` with data bars |

## Page 6 - Data Quality & Methodology

| Visual | Setup |
|---|---|
| Combo | Axis `dim_date[Date]`, columns `Respondents`, lines `Cumulative Respondents` (secondary axis) and `Respondents 3-Day Moving Avg` |
| Cards | `Clean Responses %`, `Avg Completion Time (min)`, `Straight-liners %` |
| Text boxes | Source, cleaning rules, salary-midpoint assumption, limitations (copy from `docs/data_quality_report.md`) |

## Hidden pages

| Page | Type | Purpose |
|---|---|---|
| **Role Profile** | *Drillthrough* on `dim_job[Job Title]` (keep all filters) | Right-click any role → profile: KPIs, salary-band distribution, happiness by factor, top industries, back button |
| **Tooltip - Segment** | *Tooltip* page (320 × 240) on `dim_job[Job Title]` and `dim_industry[Industry]` | Mini salary-band column + `Sample Size Label` + `Avg Salary (Reliable)` |

## Interaction & UX checklist

- [ ] Edit interactions: KPI cards **do not** cross-filter other cards; charts cross-**highlight** only where it helps
- [ ] Bookmarks: *Reset filters*, *Show/Hide filters*, one per page navigation target (use Page navigator for the rest)
- [ ] Sync slicers across pages 1-5 (View → Sync slicers) for Role, Industry, Region, Gender
- [ ] Alt text on every visual, logical tab order, title on every visual
- [ ] Colour is never the only signal (arrows, labels and data labels back up colour)
- [ ] Conditional-formatting colours come from measures (`Happiness Color`) so the logic lives in one place
- [ ] Performance Analyzer: every visual < 120 ms on the 630-row model

## Pre-publish QA

Run through `docs/QA_CHECKLIST.md` and compare each KPI with the expected values.
