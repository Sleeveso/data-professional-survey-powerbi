# Build Guide - from this repo to a finished `.pbix` (≈ 45-60 min)

> Power BI Desktop (Windows) is required. The `.pbix` itself is a binary produced by Desktop, so this repo ships everything
> that goes **into** it: cleaned data, Power Query, DAX, theme, model and page specs.

## 0. Prerequisites
- Power BI Desktop (latest) · Python 3.10+ (only if you want to re-run the ETL) · Git
- `git clone <your-repo-url>` and note the full path of the clone folder

## 1. Choose a data path

### Option A - Power Query from the raw workbook (recommended, "refreshable")
1. **Home → Transform data → Manage parameters → New**: name `pDataFolder`, type *Text*, value = your clone path
   (e.g. `C:\Projects\data-professional-survey-powerbi`).
2. For each file in `powerquery/` (in the order of `powerquery/README.md`): **New Source → Blank Query → Advanced Editor**,
   paste, **rename the query** to the name in the first comment line.
3. Right-click `Raw_Survey`, `pDataFolder`, every `fn_*` → untick **Enable load**.
4. **Close & Apply**.

### Option B - load the pre-cleaned CSVs (fastest)
**Get data → Text/CSV** for every file in `data/processed/` (11 files). Keep the file names as table names.

## 2. Model (see `model/data_model.md`)
1. Model view → create the 10 relationships from the table (Power BI auto-detects most; delete any it adds wrongly).
2. Mark `dim_date` as a date table (*Table tools → Mark as date table → Date*).
3. Apply the **sort-by-column** rules, **hide** FK/key columns, set **default summarization** and the Country data category.
4. File → Options → Current file → Data load → turn **Auto date/time off**.

## 3. DAX
1. *Enter data* → blank table named `_Measures` → load → delete the placeholder column.
2. Create parameter tables from `dax/parameter_tables.dax` (6 tables). Rename generated columns as the comments say.
3. Create measures from `dax/measures.dax` (≈ 60). Paste into *New measure*, one block at a time; set the folder and format string from the `// FOLDER / FORMAT` comment.
   *Tip:* Tabular Editor (free v2) can paste the whole file as a script in one go.
4. Validate with `docs/QA_CHECKLIST.md` **before** building visuals.

## 4. Theme
View → Themes → **Browse for themes** → `theme/data_professional_theme.json`.

## 5. Pages
Build the six pages + two hidden pages exactly as described in `docs/REPORT_DESIGN.md`.

## 6. Publish to GitHub
```bash
# optional: save as a Power BI Project for readable diffs
#   File → Save as → .pbip   (enable "Power BI Project (.pbip)" in Preview features)
git lfs install                       # .pbix is binary - track it with LFS
git lfs track "*.pbix"
cp "<your file>.pbix" powerbi/Data_Professional_Survey.pbix
git add . && git commit -m "Add finished Power BI report"
git push
```
Add 3-4 screenshots of the finished pages to `docs/images/` and reference them in the README.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Formula.Firewall` error | Options → Privacy → *Always ignore Privacy Level settings* (all sources are local) |
| `DataSource.NotFound` | `pDataFolder` has a typo or a trailing space; it must be the repo root |
| Salary Band sorted alphabetically | Set *Sort by column* → `Salary Sort` on `dim_salary[Salary Band]` |
| Matrix shows blank for small segments | Intentional - lower the *Min Sample Size* slicer |
| `RANKX` shows nothing in a card | `Salary Rank (Role)` only works when `dim_job[Job Title]` is on the visual |
| `DATESINPERIOD` error | `dim_date` is not marked as a date table |
