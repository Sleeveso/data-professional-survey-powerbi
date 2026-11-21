# Power Query (M) scripts

Paste each file into Power BI as a **Blank Query** (Home → Transform data → New Source → Blank Query →
Advanced Editor) and rename the query to the name written in the first comment line.

**Load order** (dependencies): `pDataFolder` → `fn_*` functions → `Raw_Survey` → `dim_salary`, `dim_difficulty`
→ `fact_survey` → `fact_happiness` and all remaining `dim_*` queries.

| Query | Load to model? | Notes |
|-------|:--------------:|-------|
| `pDataFolder`, `fn_*`, `Raw_Survey` | No (disable load) | Parameter, helpers, staging |
| `fact_survey`, `fact_happiness` | Yes | Facts |
| `dim_*` (9) | Yes | Dimensions |

If Power BI shows a *Formula.Firewall* error, set Options → Privacy → **Ignore the Privacy Levels** (all sources are local files).

The cleaning rules are mirrored 1:1 in `scripts/clean_data.py`; the CSVs in `data/processed/` are the expected output
and can be loaded directly if you do not want to run Power Query (see `docs/BUILD_GUIDE.md`, Option B).
