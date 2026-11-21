# /powerbi

Place the finished `Data_Professional_Survey.pbix` (or the `.pbip` project folder) here.

* `.pbix` files are binary - track them with **Git LFS** (`git lfs track "*.pbix"`).
* For readable diffs and code review, prefer saving as a **Power BI Project** (`.pbip`): the semantic model (TMDL) and report
  (PBIR) become plain-text files.
* Never commit `.pbi/localSettings.json` or `cache.abf` (already in `.gitignore`).
