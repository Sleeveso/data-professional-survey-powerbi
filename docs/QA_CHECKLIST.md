# QA Checklist - verify the report against known-good numbers

Expected values were computed in pandas from `data/processed/*.csv` (`tests/validate_data.py` guards the CSVs themselves).
With **no slicers applied** and *Min Sample Size = 10*, a card / table in Power BI should show:

| Measure | Expected | Notes |
|---|---:|---|
| Respondents | **630** | |
| Avg Salary | **$53,983** | band-midpoint average (53,982.54) |
| Median Salary | **$53,000** | |
| Avg Age | **29.8** | 629 valid ages (one blanked) |
| Female % | **25.7%** | 162 of 630 |
| Career Switchers % | **59.0%** | 372 of 630 |
| Avg Overall Happiness | **5.25** | respondent-level (5.248) |
| Avg Happiness (Factor) | **5.26** | across 3,722 individual ratings |
| Happy % (7-10) | **35.9%** | |
| Unhappy % (0-3) | **27.9%** | |
| Found It Hard % | **31.8%** | Difficult + Very Difficult |
| Avg Difficulty Score | **3.09** | |
| High Earner % (86k+) | **17.9%** | |
| % At or Above Threshold (75,000) | **32.7%** | bands from 66k-85k count as 75,500 |
| Gender Pay Gap % (M vs F) | **-3.0%** | negative = women's average midpoint is higher; not statistically meaningful |
| Avg Completion Time (min) | **2.22** | excludes 2 idle sessions |
| Straight-liners % | **6.0%** | 38 respondents |
| Clean Responses % | **99.5%** | |

## Spot checks by segment

| Filter | Measure | Expected |
|---|---|---:|
| Country = United States | Respondents / Avg Salary | 261 / $79,008 |
| Job Title = Data Analyst | Respondents / Avg Salary | 381 / $55,298 |
| Job Title = Data Scientist | Respondents / Avg Salary | 25 / $94,780 |
| Education = PhD (Min Sample = 10) | Avg Salary (Reliable) | **blank** (n = 5) |
| Education = PhD (Min Sample = 5) | Avg Salary (Reliable) | $129,700 |

## Happiness by factor (Avg Happiness (Factor))

Coworkers **5.86** · Work/Life Balance **5.74** · Learning New Things **5.61** · Management **5.33** · Upward Mobility **4.76** · Salary **4.27**

## Structural checks

- [ ] `fact_survey` = 630 rows · `fact_happiness` = 3,722 rows
- [ ] No relationship shows a "many-to-many" icon; all are * → 1
- [ ] Salary Band slicer is ordered 0-40k … 225k+ (not alphabetically)
- [ ] Education slicer ordered High School → PhD → Not Provided
- [ ] Changing the *Min Sample Size* slicer turns small segments blank (no errors)
- [ ] Drillthrough from a role bar opens *Role Profile* with the same role filtered
