// Query name : fn_CleanJob   (function) - mirrors clean_job() in scripts/clean_data.py
(value as nullable text) as text =>
let
    v      = Text.Trim(value ?? ""),
    listed = {"Data Analyst", "Data Engineer", "Data Scientist", "Database Developer", "Data Architect", "Student/Looking/None"},
    d      = Text.Lower(fn_OtherDetail(v)),
    result =
        if List.Contains(listed, v) then v
        else if d = "" then "Other"
        else if Text.Contains(d, "student") then "Student/Looking/None"
        else if fn_HasAny(d, {"business analy", "business intelligence", "bi developer", "bi analyst", "insights"}) then "Business / BI Analyst"
        else if fn_HasAny(d, {"manager", "director"}) then "Manager / Director"
        else if Text.Contains(d, "analytics engineer") then "Data Engineer"
        else if fn_HasAny(d, {"software", "developer"}) then "Software Developer"
        else if fn_HasAny(d, {"analyst", "analytic"}) then "Other Analyst"
        else "Other"
in
    result
